let activeBucket = "production-assets";
let presignTargetKey = null;
let selectedDuration = 10;
let countdownInterval = null;

// DOM Elements
const elStatBuckets = document.getElementById("stat-buckets");
const elStatObjects = document.getElementById("stat-objects");
const elStatStorage = document.getElementById("stat-storage");
const elBadgePriv = document.getElementById("badge-priv-count");
const elBadgePub = document.getElementById("badge-pub-count");
const elBucketList = document.getElementById("bucket-list");
const elCurrentBucketTitle = document.getElementById("current-bucket-title");
const elObjectsTableBody = document.getElementById("objects-table-body");
const elEventLog = document.getElementById("event-log");

const elPresignMonitor = document.getElementById("presign-monitor");
const elCountdownDisplay = document.getElementById("countdown-display");
const elPresignedUrlText = document.getElementById("presigned-url-text");
const elBtnOpenPresigned = document.getElementById("btn-open-presigned");
const elBtnCopyPresigned = document.getElementById("btn-copy-presigned");
const elPresignStatusPill = document.getElementById("presign-status-pill");

// Modals & Forms
const elPresignModal = document.getElementById("presign-modal");
const elModalKeyName = document.getElementById("modal-key-name");
const elBtnModalClose = document.getElementById("btn-modal-close");
const elBtnCancelPresign = document.getElementById("btn-cancel-presign");
const elBtnConfirmPresign = document.getElementById("btn-confirm-presign");

const elBtnNewBucketModal = document.getElementById("btn-new-bucket-modal");
const elNewBucketForm = document.getElementById("new-bucket-form");
const elInputBucketName = document.getElementById("input-bucket-name");
const elSelectBucketClass = document.getElementById("select-bucket-class");
const elBtnConfirmBucket = document.getElementById("btn-confirm-bucket");
const elBtnCancelBucket = document.getElementById("btn-cancel-bucket");

const elDropZone = document.getElementById("drop-zone");
const elFileInput = document.getElementById("file-input");
const elFileNamePreview = document.getElementById("file-name-preview");
const elUploadForm = document.getElementById("upload-form");

function formatBytes(bytes) {
    if (bytes === 0) return "0 B";
    const k = 1024;
    const sizes = ["B", "KB", "MB", "GB"];
    const i = Math.floor(Math.log(bytes) / Math.log(k));
    return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + " " + sizes[i];
}

async function loadStats() {
    try {
        const res = await fetch("/api/stats");
        if (!res.ok) return;
        const data = await res.json();
        elStatBuckets.textContent = data.total_buckets;
        elStatObjects.textContent = data.total_objects;
        elStatStorage.textContent = formatBytes(data.total_bytes);
        elBadgePriv.textContent = `${data.private_objects} Private`;
        elBadgePub.textContent = `${data.public_objects} Public`;
    } catch (err) {
        console.error("Failed to load stats:", err);
    }
}

async function loadBuckets() {
    try {
        const res = await fetch("/api/buckets");
        if (!res.ok) return;
        const data = await res.json();
        elBucketList.innerHTML = "";
        
        let foundActive = false;
        data.buckets.forEach(b => {
            if (b.name === activeBucket) foundActive = true;
            const div = document.createElement("div");
            div.className = `bucket-item ${b.name === activeBucket ? 'active' : ''}`;
            div.innerHTML = `
                <span class="name">🪣 ${b.name}</span>
                <span class="badge ${b.name === activeBucket ? 'badge-public' : 'badge-private'}">${b.object_count} objs</span>
            `;
            div.onclick = () => selectBucket(b.name);
            elBucketList.appendChild(div);
        });

        if (!foundActive && data.buckets.length > 0) {
            selectBucket(data.buckets[0].name);
        } else {
            elCurrentBucketTitle.textContent = activeBucket;
        }
    } catch (err) {
        console.error("Failed to load buckets:", err);
    }
}

function selectBucket(name) {
    activeBucket = name;
    elCurrentBucketTitle.textContent = activeBucket;
    document.querySelectorAll(".bucket-item").forEach(el => {
        el.classList.toggle("active", el.textContent.includes(name));
    });
    loadObjects();
}

async function loadObjects() {
    if (!activeBucket) return;
    try {
        const res = await fetch(`/api/buckets/${encodeURIComponent(activeBucket)}/objects`);
        if (!res.ok) return;
        const data = await res.json();
        renderObjects(data.objects || []);
    } catch (err) {
        console.error("Failed to load objects:", err);
    }
}

function renderObjects(objects) {
    elObjectsTableBody.innerHTML = "";
    if (objects.length === 0) {
        elObjectsTableBody.innerHTML = `<tr><td colspan="6" class="text-center text-muted" style="padding: 24px;">No objects found in this bucket. Upload a file above.</td></tr>`;
        return;
    }

    objects.forEach(obj => {
        const tr = document.createElement("tr");
        const isPrivate = obj.acl === "private";
        const directUrl = `/s3/${encodeURIComponent(obj.bucket)}/${encodeURIComponent(obj.key)}`;

        tr.innerHTML = `
            <td><strong>${obj.key}</strong></td>
            <td>${formatBytes(obj.size)}</td>
            <td>
                <span class="badge ${isPrivate ? 'badge-private' : 'badge-public'}">
                    ${isPrivate ? '🔒 Private' : '🌐 Public-Read'}
                </span>
            </td>
            <td>${obj.storage_class}</td>
            <td style="font-size: 0.75rem; color: #64748b;">${new Date(obj.last_modified).toLocaleTimeString()}</td>
            <td class="action-cell">
                <a href="${directUrl}" target="_blank" class="btn btn-sm btn-outline" title="Attempt Direct S3 Download">
                    ${isPrivate ? 'Direct (403)' : 'Open (200)'}
                </a>
                <button class="btn btn-sm btn-secondary" onclick="toggleAcl('${obj.key}', '${isPrivate ? 'public-read' : 'private'}')">
                    ${isPrivate ? 'Make Public' : 'Make Private'}
                </button>
                <button class="btn btn-sm btn-primary" onclick="openPresignModal('${obj.key}')">
                    Presign URL ⏳
                </button>
                <button class="btn btn-sm btn-outline" style="color: #ef4444;" onclick="deleteObject('${obj.key}')">
                    Delete
                </button>
            </td>
        `;
        elObjectsTableBody.appendChild(tr);
    });
}

async function toggleAcl(key, newAcl) {
    try {
        const res = await fetch(`/api/buckets/${encodeURIComponent(activeBucket)}/objects/${encodeURIComponent(key)}/acl`, {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ acl: newAcl })
        });
        if (res.ok) {
            loadObjects();
            loadStats();
            loadEvents();
        }
    } catch (err) {
        console.error("Failed to update ACL:", err);
    }
}

async function deleteObject(key) {
    if (!confirm(`Delete object ${key}?`)) return;
    try {
        const res = await fetch(`/api/buckets/${encodeURIComponent(activeBucket)}/objects/${encodeURIComponent(key)}`, {
            method: "DELETE"
        });
        if (res.ok) {
            loadObjects();
            loadStats();
            loadEvents();
        }
    } catch (err) {
        console.error("Failed to delete object:", err);
    }
}

async function loadEvents() {
    try {
        const res = await fetch("/api/events");
        if (!res.ok) return;
        const data = await res.json();
        elEventLog.innerHTML = "";
        data.events.forEach(ev => {
            const isDenied = ev.status.includes("403") || ev.status.includes("Denied");
            const div = document.createElement("div");
            div.className = `log-entry ${isDenied ? 'denied' : ''}`;
            div.innerHTML = `
                <span class="time">[${ev.timestamp}]</span>
                <span class="action">${ev.action}</span>
                <span class="details">${ev.bucket}${ev.key ? '/' + ev.key : ''} &rarr; ${ev.status} (${ev.details})</span>
            `;
            elEventLog.appendChild(div);
        });
    } catch (err) {
        console.error("Failed to load events:", err);
    }
}

// Modal Handlers
function openPresignModal(key) {
    presignTargetKey = key;
    elModalKeyName.textContent = key;
    elPresignModal.classList.remove("hidden");
}

function closePresignModal() {
    elPresignModal.classList.add("hidden");
    presignTargetKey = null;
}

document.querySelectorAll(".btn-duration").forEach(btn => {
    btn.onclick = () => {
        document.querySelectorAll(".btn-duration").forEach(b => b.classList.remove("active"));
        btn.classList.add("active");
        selectedDuration = parseInt(btn.dataset.seconds, 10);
    };
});

elBtnModalClose.onclick = closePresignModal;
elBtnCancelPresign.onclick = closePresignModal;

elBtnConfirmPresign.onclick = async () => {
    if (!presignTargetKey) return;
    try {
        const res = await fetch(`/api/buckets/${encodeURIComponent(activeBucket)}/objects/${encodeURIComponent(presignTargetKey)}/presign`, {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ expires_in: selectedDuration })
        });
        if (!res.ok) return;
        const data = await res.json();
        closePresignModal();
        startPresignMonitor(data);
        loadEvents();
    } catch (err) {
        console.error("Failed to generate presigned URL:", err);
    }
};

// Presigned URL Live Countdown Monitor
function startPresignMonitor(data) {
    if (countdownInterval) clearInterval(countdownInterval);

    elPresignMonitor.classList.remove("hidden");
    elPresignMonitor.classList.remove("expired");
    elPresignStatusPill.className = "badge badge-active";
    elPresignStatusPill.textContent = "VALID & AUTHORIZED";

    const fullUrl = window.location.origin + data.url;
    elPresignedUrlText.textContent = fullUrl;
    elBtnOpenPresigned.href = data.url;

    elBtnCopyPresigned.onclick = () => {
        navigator.clipboard.writeText(fullUrl);
        elBtnCopyPresigned.textContent = "Copied!";
        setTimeout(() => elBtnCopyPresigned.textContent = "Copy Link", 2000);
    };

    let remaining = data.expires_in;
    elCountdownDisplay.textContent = `${remaining}s remaining`;

    countdownInterval = setInterval(() => {
        remaining -= 1;
        if (remaining > 0) {
            elCountdownDisplay.textContent = `${remaining}s remaining`;
        } else {
            clearInterval(countdownInterval);
            elCountdownDisplay.textContent = "EXPIRED (0s)";
            elPresignMonitor.classList.add("expired");
            elPresignStatusPill.className = "badge badge-expired";
            elPresignStatusPill.textContent = "EXPIRED (403 EXPECTED)";
            elBtnOpenPresigned.textContent = "Test Expired Link (403) ↗";
        }
    }, 1000);
}

// Inline Bucket Form
elBtnNewBucketModal.onclick = () => {
    elNewBucketForm.classList.toggle("hidden");
    elInputBucketName.focus();
};

elBtnCancelBucket.onclick = () => {
    elNewBucketForm.classList.add("hidden");
    elInputBucketName.value = "";
};

elBtnConfirmBucket.onclick = async () => {
    const name = elInputBucketName.value.trim();
    const sclass = elSelectBucketClass.value;
    if (!name) return;
    try {
        const res = await fetch("/api/buckets", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ name, storage_class: sclass })
        });
        if (res.ok) {
            elNewBucketForm.classList.add("hidden");
            elInputBucketName.value = "";
            await loadBuckets();
            selectBucket(name.toLowerCase());
            loadStats();
            loadEvents();
        }
    } catch (err) {
        console.error("Failed to create bucket:", err);
    }
};

// Drag and drop handlers
elDropZone.onclick = () => elFileInput.click();
elFileInput.onchange = () => {
    if (elFileInput.files.length > 0) {
        elFileNamePreview.textContent = `Selected: ${elFileInput.files[0].name} (${formatBytes(elFileInput.files[0].size)})`;
    }
};

elDropZone.ondragover = (e) => {
    e.preventDefault();
    elDropZone.classList.add("dragover");
};

elDropZone.ondragleave = () => elDropZone.classList.remove("dragover");

elDropZone.ondrop = (e) => {
    e.preventDefault();
    elDropZone.classList.remove("dragover");
    if (e.dataTransfer.files.length > 0) {
        elFileInput.files = e.dataTransfer.files;
        elFileNamePreview.textContent = `Selected: ${elFileInput.files[0].name} (${formatBytes(elFileInput.files[0].size)})`;
    }
};

elUploadForm.onsubmit = async (e) => {
    e.preventDefault();
    if (!elFileInput.files || elFileInput.files.length === 0) {
        alert("Please select a file to upload");
        return;
    }

    const formData = new FormData();
    formData.append("file", elFileInput.files[0]);
    const acl = document.querySelector('input[name="upload-acl"]:checked').value;
    formData.append("acl", acl);
    formData.append("storage_class", document.getElementById("upload-storage-class").value);

    try {
        const res = await fetch(`/api/buckets/${encodeURIComponent(activeBucket)}/objects`, {
            method: "POST",
            body: formData
        });
        if (res.ok) {
            elFileInput.value = "";
            elFileNamePreview.textContent = "No file selected";
            loadObjects();
            loadStats();
            loadEvents();
        } else {
            const err = await res.json();
            alert("Upload failed: " + (err.error || "Unknown error"));
        }
    } catch (err) {
        console.error("Upload error:", err);
    }
};

document.getElementById("btn-refresh-objects").onclick = loadObjects;
document.getElementById("btn-clear-events").onclick = loadEvents;

// Initialize
window.addEventListener("DOMContentLoaded", () => {
    loadStats();
    loadBuckets();
    loadEvents();
    setInterval(loadEvents, 5000);
});
