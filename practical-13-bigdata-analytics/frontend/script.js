// Practical 13: Big Data Cloud Analytics Frontend Controller

const PRESET_QUERIES = {
    status_codes: {
        title: "HTTP Status Code & Error Rate Distribution",
        sql: `SELECT 
    status_code,
    COUNT(*) as total_occurrences,
    ROUND(COUNT(*) * 100.0 / SUM(COUNT(*)) OVER (), 2) as percentage_of_traffic,
    ROUND(AVG(response_time_ms), 2) as avg_latency_ms
FROM logs
GROUP BY status_code
ORDER BY total_occurrences DESC;`
    },
    top_ips: {
        title: "Top Client IP Addresses by Bandwidth & Egress (DDoS Audit)",
        sql: `SELECT 
    client_ip,
    COUNT(*) as total_requests,
    ROUND(SUM(bytes_sent) / (1024 * 1024), 2) as total_egress_mb,
    ROUND(AVG(bytes_sent), 1) as avg_payload_bytes,
    COUNT(CASE WHEN status_code >= 400 THEN 1 END) as failed_requests
FROM logs
GROUP BY client_ip
ORDER BY total_egress_mb DESC
LIMIT 10;`
    },
    hourly_trends: {
        title: "Hourly Traffic Surge & Latency Profile",
        sql: `SELECT 
    strftime(epoch_ms(timestamp * 1000), '%H:00') as hour_of_day,
    COUNT(*) as requests,
    ROUND(AVG(response_time_ms), 2) as avg_latency_ms,
    ROUND(quantile_cont(response_time_ms, 0.99), 2) as p99_latency_ms,
    ROUND(SUM(bytes_sent) / (1024 * 1024), 2) as traffic_mb
FROM logs
GROUP BY hour_of_day
ORDER BY hour_of_day ASC;`
    }
};

document.addEventListener("DOMContentLoaded", () => {
    fetchStats();
    loadPresetQuery("status_codes");

    document.getElementById("btn-run-race").addEventListener("click", runBenchmarkRace);
    document.getElementById("btn-run-sql").addEventListener("click", executeCurrentSql);
    document.getElementById("btn-regenerate-data").addEventListener("click", regenerateDataset);

    document.querySelectorAll(".btn-preset").forEach(btn => {
        btn.addEventListener("click", (e) => {
            const queryKey = e.target.getAttribute("data-query");
            loadPresetQuery(queryKey);
        });
    });
});

async function fetchStats() {
    try {
        const res = await fetch("/api/stats");
        if (!res.ok) return;
        const data = await res.json();

        document.getElementById("stat-records").textContent = (data.total_records || 0).toLocaleString();
        document.getElementById("stat-csv").textContent = `${data.csv_size_mb} MB`;
        document.getElementById("stat-parquet").textContent = `${data.parquet_size_mb} MB`;
        document.getElementById("stat-reduction").textContent = `${data.storage_reduction_pct}%`;
        document.getElementById("stat-engine").textContent = `DuckDB v${data.duckdb_version}`;
    } catch (err) {
        console.error("Failed to fetch stats:", err);
    }
}

async function runBenchmarkRace() {
    const btn = document.getElementById("btn-run-race");
    const originalText = btn.textContent;
    btn.disabled = true;
    btn.textContent = "⏳ Running MapReduce vs DuckDB Race...";

    try {
        const res = await fetch("/api/benchmark", { method: "POST" });
        if (!res.ok) {
            alert("Benchmark execution failed.");
            return;
        }
        const data = await res.json();

        // Render MapReduce Card
        document.getElementById("mr-time").textContent = `${data.mapreduce.total_ms} ms`;
        document.getElementById("mr-map").textContent = `${data.mapreduce.map_phase_ms} ms`;
        document.getElementById("mr-shuffle").textContent = `${data.mapreduce.shuffle_phase_ms} ms`;
        document.getElementById("mr-reduce").textContent = `${data.mapreduce.reduce_phase_ms} ms`;

        // Render DuckDB Card
        document.getElementById("duck-time").textContent = `${data.duckdb.total_ms} ms`;
        document.getElementById("duck-speedup-badge").textContent = data.duckdb.speedup_vs_mapreduce;
        document.getElementById("stat-speedup").textContent = data.duckdb.speedup_vs_mapreduce;

        // Render Results Table
        renderRaceResults(data.results);

    } catch (err) {
        alert("Error running benchmark: " + err.message);
    } finally {
        btn.disabled = false;
        btn.textContent = originalText;
    }
}

function renderRaceResults(results) {
    const tbody = document.getElementById("race-results-body");
    tbody.innerHTML = "";

    results.forEach(row => {
        const tr = document.createElement("tr");
        tr.innerHTML = `
            <td><code>${row.endpoint}</code></td>
            <td><strong>${row.method}</strong></td>
            <td>${(row.requests || 0).toLocaleString()}</td>
            <td>${row.avg_latency} ms</td>
            <td>${row.p95_latency} ms</td>
            <td>${row.traffic_mb} MB</td>
            <td style="color: ${row.errors > 0 ? '#ef4444' : '#10b981'}; font-weight: 600;">${(row.errors || 0).toLocaleString()}</td>
        `;
        tbody.appendChild(tr);
    });
}

function loadPresetQuery(queryKey) {
    const query = PRESET_QUERIES[queryKey];
    if (!query) return;

    document.getElementById("sql-query-title").textContent = query.title;
    document.getElementById("sql-input").value = query.sql;
    executeCurrentSql();
}

async function executeCurrentSql() {
    const sql = document.getElementById("sql-input").value;
    const durationPill = document.getElementById("sql-duration-pill");
    durationPill.textContent = "Executing...";

    try {
        const res = await fetch("/api/query/custom", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ sql })
        });
        const data = await res.json();

        if (!res.ok) {
            durationPill.textContent = "Syntax Error";
            durationPill.className = "pill pill-gray";
            alert(`Query Execution Error: ${data.error}`);
            return;
        }

        durationPill.textContent = `Executed in ${data.duration_ms} ms`;
        durationPill.className = "pill pill-green";
        renderSqlResults(data.columns, data.rows);

    } catch (err) {
        durationPill.textContent = "Execution Failed";
        alert("Error executing query: " + err.message);
    }
}

function renderSqlResults(columns, rows) {
    const thead = document.getElementById("sql-table-head");
    const tbody = document.getElementById("sql-table-body");

    // Build header
    thead.innerHTML = `<tr>${columns.map(col => `<th>${col}</th>`).join("")}</tr>`;

    // Build rows
    if (!rows || rows.length === 0) {
        tbody.innerHTML = `<tr><td colspan="${columns.length}" class="text-center text-muted">Query returned 0 rows.</td></tr>`;
        return;
    }

    tbody.innerHTML = rows.map(row => `
        <tr>
            ${columns.map(col => {
                const val = row[col];
                return `<td>${val !== null && val !== undefined ? val : 'NULL'}</td>`;
            }).join("")}
        </tr>
    `).join("");
}

async function regenerateDataset() {
    const select = document.getElementById("dataset-scale-select");
    const rows = parseInt(select.value, 10);
    const statusMsg = document.getElementById("regen-status");
    const btn = document.getElementById("btn-regenerate-data");

    btn.disabled = true;
    statusMsg.textContent = `Regenerating ${rows.toLocaleString()} records & Parquet file...`;

    try {
        const res = await fetch("/api/dataset/regenerate", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ rows })
        });
        const data = await res.json();
        fetchStats();
        statusMsg.textContent = `✓ Generated ${data.total_records.toLocaleString()} rows (${data.csv_size_mb} MB CSV, ${data.parquet_size_mb} MB Parquet)`;
    } catch (err) {
        statusMsg.textContent = "Failed to regenerate dataset: " + err.message;
    } finally {
        btn.disabled = false;
    }
}
