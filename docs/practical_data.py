# -*- coding: utf-8 -*-
"""
Deep technical & layman data definitions for all 15 Cloud Practical Guides.
"""

PRACTICALS = [
    {
        "num": "01",
        "dir": "practical-01-service-models",
        "title": "Cloud Service Models (IaaS vs PaaS vs SaaS)",
        "subtitle": "NIST SP 800-145 Shared Responsibility & Linux Kernel Exploit Workbench",
        "port": "8080",
        "memory": "~38 MiB",
        "what_is_it": """<p>In traditional IT, you buy a heavy physical server, rack it, plug in power cords, install Linux, and fix cooling fans when they die. In Cloud Computing, you <strong>outsource layers of the technology stack</strong> to a provider.</p>
<p>The <strong>NIST SP 800-145 standard</strong> defines exactly where the boundary lies between <em>what you manage</em> versus <em>what the cloud provider manages</em> across 9 operational tiers.</p>""",
        "analogy_title": "🍕 The Famous Pizza-as-a-Service Analogy",
        "layman_analogy": """<ul>
<li><strong>On-Premises:</strong> Making pizza at home from scratch (you own the oven, buy flour, gas, roll dough, wash dishes).</li>
<li><strong>IaaS:</strong> Renting a commercial kitchen (they give you electricity and oven; you bring sauce, toppings, and bake).</li>
<li><strong>PaaS:</strong> Take-and-bake delivered (they prepare dough and toppings; you just bake it and eat).</li>
<li><strong>SaaS:</strong> Eating at a restaurant (you sit down, eat, pay; you have no clue what oven was used).</li>
</ul>""",
        "use_case": """<p><strong>Netflix</strong> uses IaaS (AWS EC2) for video transcoding because they require low-level Linux kernel optimizations. 
Meanwhile, early-stage startups use PaaS (Heroku, Render, AWS App Runner) to launch in 10 minutes without hiring a $180,000/yr Linux DevOps engineer. 
And every business uses SaaS (Gmail, Slack) because running a private email server costs fortunes in spam filters and maintenance.</p>""",
        "infographic_caption": "NIST 9-Layer Shared Responsibility Stack",
        "svg_infographic": """<svg width="100%" height="135" viewBox="0 0 680 135" xmlns="http://www.w3.org/2000/svg">
<rect width="680" height="135" fill="#f8fafc" rx="8" />
<rect x="220" y="6" width="12" height="12" fill="#2563eb" rx="2" />
<text x="238" y="16" font-family="sans-serif" font-size="9.5" font-weight="600" fill="#1e293b">You Manage (Customer)</text>
<rect x="390" y="6" width="12" height="12" fill="#94a3b8" rx="2" />
<text x="408" y="16" font-family="sans-serif" font-size="9.5" font-weight="600" fill="#1e293b">Cloud Provider Manages</text>
<rect x="25" y="26" width="140" height="95" fill="#ffffff" stroke="#cbd5e1" rx="6" />
<text x="95" y="42" font-family="sans-serif" font-size="10.5" font-weight="700" text-anchor="middle" fill="#0f172a">On-Premises</text>
<rect x="33" y="48" width="124" height="65" fill="#2563eb" rx="4" />
<text x="95" y="84" font-family="sans-serif" font-size="9.5" font-weight="600" text-anchor="middle" fill="#ffffff">All 9 Layers (100% You)</text>
<rect x="180" y="26" width="140" height="95" fill="#ffffff" stroke="#cbd5e1" rx="6" />
<text x="250" y="42" font-family="sans-serif" font-size="10.5" font-weight="700" text-anchor="middle" fill="#0f172a">IaaS (AWS EC2)</text>
<rect x="188" y="48" width="124" height="38" fill="#2563eb" rx="4" />
<text x="250" y="70" font-family="sans-serif" font-size="9" font-weight="600" text-anchor="middle" fill="#ffffff">App, Data, OS, Runtime</text>
<rect x="188" y="88" width="124" height="25" fill="#94a3b8" rx="4" />
<text x="250" y="104" font-family="sans-serif" font-size="8.5" font-weight="600" text-anchor="middle" fill="#ffffff">Hardware & Hypervisor</text>
<rect x="335" y="26" width="140" height="95" fill="#ffffff" stroke="#cbd5e1" rx="6" />
<text x="405" y="42" font-family="sans-serif" font-size="10.5" font-weight="700" text-anchor="middle" fill="#0f172a">PaaS (Heroku)</text>
<rect x="343" y="48" width="124" height="20" fill="#2563eb" rx="4" />
<text x="405" y="62" font-family="sans-serif" font-size="8.5" font-weight="600" text-anchor="middle" fill="#ffffff">App Code & Data</text>
<rect x="343" y="70" width="124" height="43" fill="#94a3b8" rx="4" />
<text x="405" y="94" font-family="sans-serif" font-size="8.5" font-weight="600" text-anchor="middle" fill="#ffffff">OS, Runtime & Hardware</text>
<rect x="490" y="26" width="165" height="95" fill="#ffffff" stroke="#cbd5e1" rx="6" />
<text x="572" y="42" font-family="sans-serif" font-size="10.5" font-weight="700" text-anchor="middle" fill="#0f172a">SaaS (Gmail / M365)</text>
<rect x="498" y="48" width="149" height="15" fill="#2563eb" rx="4" />
<text x="572" y="59" font-family="sans-serif" font-size="8" font-weight="600" text-anchor="middle" fill="#ffffff">User Preferences</text>
<rect x="498" y="65" width="149" height="48" fill="#94a3b8" rx="4" />
<text x="572" y="92" font-family="sans-serif" font-size="8.5" font-weight="600" text-anchor="middle" fill="#ffffff">Everything Managed for You</text>
</svg>""",
        "steps_rows": """<tr>
<td><strong>Step 1</strong></td>
<td>Toggle <strong>"Pizza Analogy"</strong> mode on dashboard</td>
<td>Replaces technical terms with cheese, dough, and kitchen ovens to cement the shared responsibility model.</td>
</tr>
<tr>
<td><strong>Step 2</strong></td>
<td>Simulate <strong>CVE Kernel Exploit</strong> on IaaS VM</td>
<td>Attacks the Linux kernel (CVE-2024-1086). Because YOU control the OS in IaaS, your VM gets hacked until you patch it.</td>
</tr>
<tr>
<td><strong>Step 3</strong></td>
<td>Click <strong>"Apply Security Patch"</strong> on IaaS VM</td>
<td>Simulates running <code>apt-get upgrade</code>. Demonstrates operational burden: if your team sleeps, servers get compromised!</td>
</tr>
<tr>
<td><strong>Step 4</strong></td>
<td>Target the <strong>PaaS Application</strong> with exploit</td>
<td>The simulator returns <strong>IMMUNE</strong>. In PaaS, the cloud provider automatically patches the underlying host kernel for you.</td>
</tr>
<tr>
<td><strong>Step 5</strong></td>
<td>Use <strong>Architecture Decision Wizard</strong></td>
<td>Answers questions on budget and compliance to receive an algorithmic NIST model recommendation (IaaS, PaaS, or SaaS).</td>
</tr>""",
        "takeaway_lead": "More Control = More Work.",
        "takeaway_body": "In IaaS you have total power over the server, but you are responsible at 3:00 AM when hackers exploit an unpatched Linux bug. In PaaS, you sacrifice root access, but the cloud provider handles security updates, backups, and OS scaling for you.",
        "viva_boxes": """<div class="q-box">
<div class="q-title">Q1: Under Shared Responsibility, who patches the OS in IaaS vs PaaS?</div>
<div class="q-ans"><strong>Answer:</strong> In <strong>IaaS</strong>, the customer is 100% responsible for OS security patches. In <strong>PaaS</strong>, the cloud provider patches the OS and runtime automatically; the customer only manages code and data.</div>
</div>
<div class="q-box">
<div class="q-title">Q2: Why wouldn't an enterprise put 100% of their workloads in SaaS?</div>
<div class="q-ans"><strong>Answer:</strong> SaaS offers zero low-level code customization. If you need custom algorithms, proprietary databases, or strict hardware residency, SaaS cannot support it; you must choose IaaS or PaaS.</div>
</div>
<div class="q-box">
<div class="q-title">Q3: How does the Pizza analogy map to on-demand cloud elasticity?</div>
<div class="q-ans"><strong>Answer:</strong> If 100 surprise guests show up, making 100 pizzas at home (On-Prem) is impossible. Calling a pizzeria to deliver 100 pizzas (SaaS / Cloud) scales immediately without buying 20 extra ovens.</div>
</div>"""
    },
    {
        "num": "02",
        "dir": "practical-02-vm-lifecycle",
        "title": "Virtual Machine Lifecycle & Hypervisor",
        "subtitle": "Type-1 vs Type-2 Hypervisors & vCPU/vRAM Overcommit Engine",
        "port": "8080",
        "memory": "~34 MiB",
        "what_is_it": """<p>A physical computer has one CPU, one block of RAM, and one hard drive. <strong>Virtualization</strong> tricks multiple operating systems into sharing that single physical machine as if each had its own private hardware.</p>
<p>The <strong>Hypervisor</strong> (Virtual Machine Monitor) is the master traffic cop managing this illusion, slicing physical chips into virtual CPUs (vCPUs) and virtual RAM (vRAM).</p>""",
        "analogy_title": "🏨 The Hotel Overbooking & Apartment Analogy",
        "layman_analogy": """<ul>
<li><strong>Physical Server:</strong> A large apartment complex.</li>
<li><strong>Hypervisor:</strong> The building superintendent who divides large floors into private studio units (Virtual Machines).</li>
<li><strong>Type-1 (Bare Metal):</strong> Building rooms directly on concrete foundations (VMware ESXi / KVM)—blazing fast, zero waste.</li>
<li><strong>Type-2 (Hosted):</strong> Building wooden partitions inside an already furnished living room (VirtualBox on Windows)—slower.</li>
<li><strong>Overcommit:</strong> Hotels sell 105 rooms when they only have 100, knowing 10 guests will not show up. Cloud hypervisors allocate 32 vCPUs on a 16-core chip because VMs rarely hit 100% simultaneously!</li>
</ul>""",
        "use_case": """<p><strong>Amazon Web Services (AWS Nitro)</strong> and <strong>Google Cloud (Borg/KVM)</strong> run millions of customer VMs on shared physical servers. 
Without hypervisor overcommitment, AWS would have to purchase 4x more physical servers, making cloud computing 400% more expensive for startups.</p>""",
        "infographic_caption": "Type-1 Bare Metal vs Type-2 Hosted Hypervisor Architecture",
        "svg_infographic": """<svg width="100%" height="135" viewBox="0 0 680 135" xmlns="http://www.w3.org/2000/svg">
<rect width="680" height="135" fill="#f8fafc" rx="8" />
<!-- Type 1 Box -->
<rect x="30" y="15" width="295" height="108" fill="#ffffff" stroke="#cbd5e1" rx="6" />
<text x="177" y="32" font-family="sans-serif" font-size="11" font-weight="700" text-anchor="middle" fill="#0f172a">Type-1 Hypervisor (Bare-Metal)</text>
<rect x="45" y="40" width="125" height="22" fill="#eff6ff" stroke="#bfdbfe" rx="3" /><text x="107" y="55" font-family="sans-serif" font-size="9" font-weight="600" text-anchor="middle" fill="#1d4ed8">Guest VM 1 (Linux)</text>
<rect x="185" y="40" width="125" height="22" fill="#eff6ff" stroke="#bfdbfe" rx="3" /><text x="247" y="55" font-family="sans-serif" font-size="9" font-weight="600" text-anchor="middle" fill="#1d4ed8">Guest VM 2 (Win)</text>
<rect x="45" y="68" width="265" height="24" fill="#2563eb" rx="4" /><text x="177" y="84" font-family="sans-serif" font-size="10" font-weight="700" text-anchor="middle" fill="#ffffff">Hypervisor (KVM / ESXi / Nitro)</text>
<rect x="45" y="96" width="265" height="20" fill="#334155" rx="3" /><text x="177" y="110" font-family="sans-serif" font-size="9.5" font-weight="600" text-anchor="middle" fill="#ffffff">Physical Hardware (CPU / RAM / Disk)</text>
<!-- Type 2 Box -->
<rect x="355" y="15" width="295" height="108" fill="#ffffff" stroke="#cbd5e1" rx="6" />
<text x="502" y="32" font-family="sans-serif" font-size="11" font-weight="700" text-anchor="middle" fill="#0f172a">Type-2 Hypervisor (Hosted)</text>
<rect x="370" y="40" width="125" height="18" fill="#fef2f2" stroke="#fecaca" rx="3" /><text x="432" y="53" font-family="sans-serif" font-size="8.5" font-weight="600" text-anchor="middle" fill="#dc2626">Guest VM 1</text>
<rect x="510" y="40" width="125" height="18" fill="#fef2f2" stroke="#fecaca" rx="3" /><text x="572" y="53" font-family="sans-serif" font-size="8.5" font-weight="600" text-anchor="middle" fill="#dc2626">Guest VM 2</text>
<rect x="370" y="62" width="265" height="18" fill="#f59e0b" rx="3" /><text x="502" y="75" font-family="sans-serif" font-size="9" font-weight="700" text-anchor="middle" fill="#ffffff">Hypervisor (VirtualBox / VMware Workstation)</text>
<rect x="370" y="83" width="265" height="18" fill="#475569" rx="3" /><text x="502" y="96" font-family="sans-serif" font-size="9" font-weight="600" text-anchor="middle" fill="#ffffff">Host Operating System (macOS / Windows)</text>
<rect x="370" y="104" width="265" height="14" fill="#334155" rx="2" /><text x="502" y="115" font-family="sans-serif" font-size="8.5" font-weight="600" text-anchor="middle" fill="#ffffff">Physical Hardware</text>
</svg>""",
        "steps_rows": """<tr>
<td><strong>Step 1</strong></td>
<td>Click <strong>"Provision VM"</strong> with 2 vCPUs & 4GB RAM</td>
<td>The hypervisor creates a virtual machine descriptor, reserves memory pages in the host RAM, and generates a virtual MAC address.</td>
</tr>
<tr>
<td><strong>Step 2</strong></td>
<td>Click <strong>"Power On"</strong></td>
<td>The hypervisor initializes a virtual BIOS, loads the kernel image into virtual RAM, and begins executing virtual CPU instructions.</td>
</tr>
<tr>
<td><strong>Step 3</strong></td>
<td>Click <strong>"Pause VM"</strong></td>
<td>Instantly freezes execution by saving CPU register states into host RAM; 0% CPU cycles are consumed while paused.</td>
</tr>
<tr>
<td><strong>Step 4</strong></td>
<td>Slide Overcommit Ratio to <strong>2.5x</strong></td>
<td>Allocates 40 vCPUs across only 16 physical cores. Demonstrates how cloud providers squeeze maximum profit out of hardware.</td>
</tr>
<tr>
<td><strong>Step 5</strong></td>
<td>Click <strong>"Destroy VM"</strong></td>
<td>Releases all host RAM pages and CPU schedulers back to the general resource pool cleanly.</td>
</tr>""",
        "takeaway_lead": "Hardware is Static, Virtualization is Elastic.",
        "takeaway_body": "Hypervisors turn physical compute into a fluid software pool. Overcommitment allows providers to safely sell more compute than physically exists, driving down cloud costs worldwide.",
        "viva_boxes": """<div class="q-box">
<div class="q-title">Q1: What is the main performance difference between Type-1 and Type-2 hypervisors?</div>
<div class="q-ans"><strong>Answer:</strong> Type-1 runs directly on raw bare metal with zero host OS overhead (~1-2% virtualization tax). Type-2 runs on top of a desktop OS (Windows/macOS), adding a heavy second abstraction layer that causes higher latency.</div>
</div>
<div class="q-box">
<div class="q-title">Q2: What is CPU overcommitment and why does it rarely crash the host?</div>
<div class="q-ans"><strong>Answer:</strong> Overcommitment is assigning more vCPUs than physical cores. It works because enterprise workloads rarely spike simultaneously; the Linux CFS scheduler multiplexes threads so idle VMs yield time to active VMs.</div>
</div>
<div class="q-box">
<div class="q-title">Q3: What happens when a VM is Paused vs Stopped?</div>
<div class="q-ans"><strong>Answer:</strong> When <strong>Paused</strong>, the VM's state remains in RAM (resumes in 1 millisecond). When <strong>Stopped</strong>, RAM is freed and state is flushed to disk (requires full OS boot upon restart).</div>
</div>"""
    },
    {
        "num": "03",
        "dir": "practical-03-containerization-docker",
        "title": "Docker Containerization & Linux Cgroups",
        "subtitle": "Kernel Cgroups v2 Quotas, OverlayFS CoW & Namespace Isolation",
        "port": "8080",
        "memory": "~36 MiB",
        "what_is_it": """<p>Virtual Machines virtualize the <strong>hardware</strong> (running an entire 5 GB guest OS with its own kernel). <strong>Docker Containers</strong> virtualize only the <strong>operating system user space</strong>.</p>
<p>Containers share the host Linux kernel directly, starting in milliseconds instead of minutes and using megabytes of RAM instead of gigabytes, secured by <strong>Linux Namespaces</strong> and <strong>Cgroups v2</strong>.</p>""",
        "analogy_title": "🚢 Shipping Containers & Water Meters",
        "layman_analogy": """<ul>
<li><strong>Virtual Machine:</strong> Building a whole standalone house inside a warehouse (own plumbing, wiring, and furnace).</li>
<li><strong>Docker Container:</strong> A standardized steel shipping container sharing the cargo ship's deck and engine.</li>
<li><strong>Linux Namespaces (Blindfolds):</strong> Put blindfolds on processes so Container A can only see its own files, network port, and process IDs.</li>
<li><strong>Linux Cgroups (Meters & Governors):</strong> Strict water and electricity meters. If Container A tries to drink more than 128 MB of RAM, the Linux Out-Of-Memory (OOM) Killer immediately terminates it to save the ship!</li>
</ul>""",
        "use_case": """<p><strong>Spotify</strong> and <strong>Uber</strong> run tens of thousands of microservices in Docker containers. 
If each microservice required a full Virtual Machine, their servers would crash under the weight of thousands of duplicate operating systems.</p>""",
        "infographic_caption": "Linux Kernel Namespace Isolation & Cgroups v2 Resource Governors",
        "svg_infographic": """<svg width="100%" height="135" viewBox="0 0 680 135" xmlns="http://www.w3.org/2000/svg">
<rect width="680" height="135" fill="#f8fafc" rx="8" />
<rect x="35" y="15" width="280" height="75" fill="#ffffff" stroke="#cbd5e1" rx="6" />
<text x="175" y="32" font-family="sans-serif" font-size="10.5" font-weight="700" text-anchor="middle" fill="#0f172a">Container A (Web Microservice)</text>
<rect x="45" y="42" width="125" height="18" fill="#eff6ff" stroke="#bfdbfe" rx="3" /><text x="107" y="55" font-family="sans-serif" font-size="8.5" font-weight="600" text-anchor="middle" fill="#1d4ed8">PID & NET Namespace</text>
<rect x="180" y="42" width="125" height="18" fill="#fef3c7" stroke="#fde68a" rx="3" /><text x="242" y="55" font-family="sans-serif" font-size="8.5" font-weight="600" text-anchor="middle" fill="#b45309">Cgroups: 0.5 CPU / 128M</text>
<text x="175" y="78" font-family="sans-serif" font-size="8" fill="#64748b" text-anchor="middle">OverlayFS (Read-Only Base + Writable Top Layer)</text>
<rect x="365" y="15" width="280" height="75" fill="#ffffff" stroke="#cbd5e1" rx="6" />
<text x="505" y="32" font-family="sans-serif" font-size="10.5" font-weight="700" text-anchor="middle" fill="#0f172a">Container B (Worker Daemon)</text>
<rect x="375" y="42" width="125" height="18" fill="#eff6ff" stroke="#bfdbfe" rx="3" /><text x="437" y="55" font-family="sans-serif" font-size="8.5" font-weight="600" text-anchor="middle" fill="#1d4ed8">Isolated Mount & IPC</text>
<rect x="510" y="42" width="125" height="18" fill="#fef3c7" stroke="#fde68a" rx="3" /><text x="572" y="55" font-family="sans-serif" font-size="8.5" font-weight="600" text-anchor="middle" fill="#b45309">Cgroups: 0.2 CPU / 64M</text>
<text x="505" y="78" font-family="sans-serif" font-size="8" fill="#64748b" text-anchor="middle">Shared Image Layers (Zero Duplicate Disk Space)</text>
<rect x="35" y="96" width="610" height="28" fill="#0f172a" rx="4" />
<text x="340" y="114" font-family="sans-serif" font-size="10" font-weight="700" text-anchor="middle" fill="#ffffff">Shared Host Linux Kernel (Namespaces • Cgroups v2 • OverlayFS)</text>
</svg>""",
        "steps_rows": """<tr>
<td><strong>Step 1</strong></td>
<td>Inspect <strong>Cgroup Quotas</strong></td>
<td>View <code>/sys/fs/cgroup/cpu.max</code> (set to 50,000 / 100,000 = 0.50 CPU cores) and <code>memory.max</code> (128 MB).</td>
</tr>
<tr>
<td><strong>Step 2</strong></td>
<td>Click <strong>"Inject CPU Stress"</strong></td>
<td>Spins up an infinite math loop. Watch CPU usage spike to exactly 50.0% and hit the kernel ceiling without affecting host speed.</td>
</tr>
<tr>
<td><strong>Step 3</strong></td>
<td>Click <strong>"Inject Memory Leak"</strong></td>
<td>Allocates RAM in a runaway loop. At 128 MB, the Linux kernel OOM Killer immediately sends <code>SIGKILL</code> (Exit Code 137).</td>
</tr>
<tr>
<td><strong>Step 4</strong></td>
<td>Inspect <strong>OverlayFS Layers</strong></td>
<td>Demonstrates how 10 containers sharing the same Ubuntu image consume 0 extra megabytes of storage using Copy-on-Write.</td>
</tr>""",
        "takeaway_lead": "Containers are Just Isolated Linux Processes.",
        "takeaway_body": "There is no 'Docker computer.' A container is a standard Linux process wearing namespace blindfolds and governed by cgroup resource meters.",
        "viva_boxes": """<div class="q-box">
<div class="q-title">Q1: What is the fundamental difference between a Docker Container and a Virtual Machine?</div>
<div class="q-ans"><strong>Answer:</strong> A VM packages an entire guest operating system with a virtualized kernel and hardware. A container shares the host Linux kernel and isolates processes using kernel namespaces and cgroups.</div>
</div>
<div class="q-box">
<div class="q-title">Q2: What happens when a container exceeds its memory limit vs its CPU limit?</div>
<div class="q-ans"><strong>Answer:</strong> Exceeding <strong>CPU</strong> results in soft throttling (the process slows down). Exceeding <strong>Memory</strong> triggers the Linux OOM Killer to instantly terminate the container with Exit Code 137.</div>
</div>
<div class="q-box">
<div class="q-title">Q3: How does OverlayFS Copy-on-Write (CoW) save storage?</div>
<div class="q-ans"><strong>Answer:</strong> Base image layers are read-only and shared across all containers. New files or modifications are written only to a thin writable top layer unique to that container.</div>
</div>"""
    },
    {
        "num": "04",
        "dir": "practical-04-k8s-orchestration",
        "title": "Kubernetes Pod Orchestration & Self-Healing",
        "subtitle": "Declarative Desired State, Etcd Reconciler & Chaos Pod Terminator",
        "port": "8080",
        "memory": "~39 MiB",
        "what_is_it": """<p>Running a single Docker container is easy, but what happens when it crashes at 3:00 AM? Or when user traffic jumps 10x? <strong>Kubernetes (K8s)</strong> is the container orchestrator that automates scaling, recovery, and deployment.</p>
<p>You declare your <strong>Desired State</strong> in YAML (e.g. <code>replicas: 3</code>), and the <strong>Control Plane Reconciler Loop</strong> continuously forces the actual real-world state to match.</p>""",
        "analogy_title": "✈️ The Commercial Airliner Autopilot Analogy",
        "layman_analogy": """<ul>
<li><strong>Docker:</strong> Flying a drone with manual joysticks—if a gust of wind hits, it crashes unless a human reacts.</li>
<li><strong>Kubernetes:</strong> Commercial airplane autopilot. You set the dial to: <em>"Maintain 30,000 feet with 3 engines running"</em>.</li>
<li><strong>Self-Healing:</strong> If engine #2 catches fire (Pod Crash), the autopilot detects <code>Actual (2) != Desired (3)</code> and immediately restarts a new engine in 2 seconds—without human panic.</li>
<li><strong>Liveness Probe:</strong> Doctor checking the pilot's pulse (if flatlined, replace them).</li>
<li><strong>Readiness Probe:</strong> Doctor checking if pilot is coughing (if sick, take them off the controls until recovered).</li>
</ul>""",
        "use_case": """<p><strong>Pokemon GO</strong> and <strong>Target</strong> handle hundreds of millions of user requests. 
When servers crash during peak shopping hours, Kubernetes self-healing restarts failed pods in seconds, preventing catastrophic site outages and revenue loss.</p>""",
        "infographic_caption": "Kubernetes Control Plane Continuous Reconciliation Loop",
        "svg_infographic": """<svg width="100%" height="135" viewBox="0 0 680 135" xmlns="http://www.w3.org/2000/svg">
<rect width="680" height="135" fill="#f8fafc" rx="8" />
<rect x="25" y="15" width="220" height="105" fill="#ffffff" stroke="#cbd5e1" rx="6" />
<text x="135" y="32" font-family="sans-serif" font-size="10.5" font-weight="700" text-anchor="middle" fill="#0f172a">K8s Control Plane</text>
<rect x="35" y="42" width="200" height="18" fill="#eff6ff" stroke="#bfdbfe" rx="3" /><text x="135" y="55" font-family="sans-serif" font-size="8.5" font-weight="600" text-anchor="middle" fill="#1d4ed8">kube-apiserver & etcd database</text>
<rect x="35" y="65" width="200" height="18" fill="#fef3c7" stroke="#fde68a" rx="3" /><text x="135" y="78" font-family="sans-serif" font-size="8.5" font-weight="600" text-anchor="middle" fill="#b45309">ReplicaSet Controller Manager</text>
<rect x="35" y="88" width="200" height="22" fill="#2563eb" rx="3" /><text x="135" y="103" font-family="sans-serif" font-size="9" font-weight="700" text-anchor="middle" fill="#ffffff">Reconciler: Desired (3) == Actual (3)</text>
<!-- Arrow -->
<path d="M 255 67 L 285 67" stroke="#2563eb" stroke-width="2.5" marker-end="url(#arrow)" fill="none" />
<!-- Worker Nodes -->
<rect x="295" y="15" width="360" height="105" fill="#ffffff" stroke="#cbd5e1" rx="6" />
<text x="475" y="32" font-family="sans-serif" font-size="10.5" font-weight="700" text-anchor="middle" fill="#0f172a">Cluster Worker Nodes & Pod Pool</text>
<rect x="310" y="45" width="100" height="60" fill="#f0fdf4" stroke="#86efac" rx="4" />
<text x="360" y="65" font-family="sans-serif" font-size="9" font-weight="700" text-anchor="middle" fill="#15803d">Pod 1 (Live)</text>
<text x="360" y="82" font-family="sans-serif" font-size="8" fill="#64748b" text-anchor="middle">IP: 10.244.1.12</text>
<text x="360" y="96" font-family="sans-serif" font-size="8" fill="#15803d" text-anchor="middle">Probe: 200 OK</text>
<rect x="425" y="45" width="100" height="60" fill="#f0fdf4" stroke="#86efac" rx="4" />
<text x="475" y="65" font-family="sans-serif" font-size="9" font-weight="700" text-anchor="middle" fill="#15803d">Pod 2 (Live)</text>
<text x="475" y="82" font-family="sans-serif" font-size="8" fill="#64748b" text-anchor="middle">IP: 10.244.1.13</text>
<text x="475" y="96" font-family="sans-serif" font-size="8" fill="#15803d" text-anchor="middle">Probe: 200 OK</text>
<rect x="540" y="45" width="100" height="60" fill="#fef2f2" stroke="#fca5a5" rx="4" />
<text x="590" y="65" font-family="sans-serif" font-size="9" font-weight="700" text-anchor="middle" fill="#dc2626">Pod 3 (Killed)</text>
<text x="590" y="80" font-family="sans-serif" font-size="8" fill="#dc2626" text-anchor="middle">CrashLoop</text>
<text x="590" y="96" font-family="sans-serif" font-size="8" font-weight="600" fill="#2563eb" text-anchor="middle">Auto-Replacing!</text>
</svg>""",
        "steps_rows": """<tr>
<td><strong>Step 1</strong></td>
<td>View <strong>Cluster Topology</strong></td>
<td>See 3 healthy pods running across worker nodes, registered in the simulated etcd database.</td>
</tr>
<tr>
<td><strong>Step 2</strong></td>
<td>Click <strong>"⚡ Kill Pod"</strong></td>
<td>Kills an active container. Watch the controller detect deficit and launch a replacement pod in under 2 seconds!</td>
</tr>
<tr>
<td><strong>Step 3</strong></td>
<td>Click <strong>"🚀 Rollout v2.0.0"</strong></td>
<td>Executes zero-downtime rolling update: spins up v2 pod first, verifies readiness, and drains v1 safely.</td>
</tr>
<tr>
<td><strong>Step 4</strong></td>
<td>Click <strong>"Fail Liveness Probe"</strong></td>
<td>Simulates application deadlock; Kubelet detects probe timeout, issues restart, and increments restart count.</td>
</tr>
<tr>
<td><strong>Step 5</strong></td>
<td>Send <strong>Client Traffic</strong></td>
<td>Sends HTTP requests through NodePort 30080 and observes round-robin distribution across healthy pod IPs.</td>
</tr>""",
        "takeaway_lead": "Declare the 'What', Let K8s Figure Out the 'How'.",
        "takeaway_body": "You never tell Kubernetes to start a specific container manually. You tell it 'I want 3 replicas alive at all times', and its self-healing engine works tirelessly 24/7 to maintain that reality.",
        "viva_boxes": """<div class="q-box">
<div class="q-title">Q1: What is the core responsibility of the Kubernetes Reconciliation Loop?</div>
<div class="q-ans"><strong>Answer:</strong> It compares the <strong>Actual State</strong> reported by worker nodes with the <strong>Desired State</strong> stored in etcd. If any divergence exists (e.g. fewer pods than requested), it takes corrective action.</div>
</div>
<div class="q-box">
<div class="q-title">Q2: What is the difference between a Liveness Probe and a Readiness Probe?</div>
<div class="q-ans"><strong>Answer:</strong> <strong>Liveness</strong> checks if the app is alive (fails = Kubelet restarts container). <strong>Readiness</strong> checks if the app can handle traffic (fails = Kube-proxy removes pod IP from Service endpoints).</div>
</div>
<div class="q-box">
<div class="q-title">Q3: How does Kubernetes achieve Zero-Downtime Rolling Updates?</div>
<div class="q-ans"><strong>Answer:</strong> Using <code>maxSurge</code> and <code>maxUnavailable</code>: it spins up a new version pod first, waits for readiness to pass, shifts user traffic, and only then terminates the old version pod.</div>
</div>"""
    }
]

print("Loaded base practicals 01-04. Adding practicals 05-15...")

PRACTICALS.extend([
    {
        "num": "05",
        "dir": "practical-05-cloud-networking-vpc",
        "title": "Cloud Networking: Dual-Tier VPC & Routing",
        "subtitle": "Public/Private Subnets, NAT Gateway & Stateful Security Groups",
        "port": "8080",
        "memory": "~35 MiB",
        "what_is_it": """<p>In the cloud, you cannot connect databases directly to the public internet, or automated hacker bots will breach them within minutes. A <strong>Virtual Private Cloud (VPC)</strong> is an isolated virtual network that isolates your infrastructure.</p>
<p>By dividing your network into <strong>Public Subnets</strong> (for internet-facing web servers) and <strong>Private Subnets</strong> (for confidential databases), you enforce zero-trust network boundaries.</p>""",
        "analogy_title": "🏰 The Gated Community & Bank Vault Analogy",
        "layman_analogy": """<ul>
<li><strong>VPC:</strong> A high-security gated residential community with a single perimeter wall.</li>
<li><strong>Public Subnet:</strong> The visitor lobby and parking lot—anyone from the highway can drive in.</li>
<li><strong>Private Subnet:</strong> The underground bank vault—has ZERO doors to the outside world.</li>
<li><strong>NAT Gateway:</strong> The security guard who runs outside to fetch grocery deliveries for people inside the vault, without ever letting delivery drivers step inside.</li>
<li><strong>Security Group:</strong> A personal bodyguard standing at each apartment door (Stateful: if you let a visitor in, you let them leave).</li>
</ul>""",
        "use_case": """<p><strong>Fintech companies (Stripe, Robinhood)</strong> store credit cards and bank balances inside private VPC subnets. 
Even if their web frontend gets compromised, the database cannot be reached directly from the internet because no route or public IP exists.</p>""",
        "infographic_caption": "Dual-Tier VPC Packet Flow: Public Web Tier to Private Database Tier",
        "svg_infographic": """<svg width="100%" height="135" viewBox="0 0 680 135" xmlns="http://www.w3.org/2000/svg">
<rect width="680" height="135" fill="#f8fafc" rx="8" />
<rect x="20" y="45" width="80" height="45" fill="#eff6ff" stroke="#bfdbfe" rx="4" />
<text x="60" y="65" font-family="sans-serif" font-size="9" font-weight="700" text-anchor="middle" fill="#1d4ed8">Internet</text>
<text x="60" y="78" font-family="sans-serif" font-size="8" fill="#64748b" text-anchor="middle">0.0.0.0/0</text>
<path d="M 105 67 L 135 67" stroke="#2563eb" stroke-width="2" fill="none" />
<rect x="140" y="45" width="70" height="45" fill="#fef3c7" stroke="#fde68a" rx="4" />
<text x="175" y="65" font-family="sans-serif" font-size="9" font-weight="700" text-anchor="middle" fill="#b45309">IGW</text>
<text x="175" y="78" font-family="sans-serif" font-size="7.5" fill="#64748b" text-anchor="middle">Gateway</text>
<!-- VPC Box -->
<rect x="225" y="12" width="435" height="112" fill="#ffffff" stroke="#2563eb" stroke-width="1.5" stroke-dasharray="4" rx="6" />
<text x="240" y="28" font-family="sans-serif" font-size="9.5" font-weight="700" fill="#2563eb">VPC (10.0.0.0/16)</text>
<!-- Public Subnet -->
<rect x="240" y="35" width="185" height="80" fill="#f0fdf4" stroke="#86efac" rx="4" />
<text x="332" y="52" font-family="sans-serif" font-size="9" font-weight="700" text-anchor="middle" fill="#15803d">Public Subnet (10.0.1.0/24)</text>
<rect x="250" y="60" width="80" height="45" fill="#ffffff" stroke="#cbd5e1" rx="3" />
<text x="290" y="78" font-family="sans-serif" font-size="8.5" font-weight="700" text-anchor="middle" fill="#0f172a">Web Server</text>
<text x="290" y="92" font-family="sans-serif" font-size="7.5" fill="#64748b" text-anchor="middle">Port 80/443</text>
<rect x="340" y="60" width="75" height="45" fill="#ffffff" stroke="#cbd5e1" rx="3" />
<text x="377" y="78" font-family="sans-serif" font-size="8.5" font-weight="700" text-anchor="middle" fill="#b45309">NAT Gate</text>
<text x="377" y="92" font-family="sans-serif" font-size="7.5" fill="#64748b" text-anchor="middle">Egress Only</text>
<!-- Private Subnet -->
<rect x="445" y="35" width="200" height="80" fill="#fef2f2" stroke="#fca5a5" rx="4" />
<text x="545" y="52" font-family="sans-serif" font-size="9" font-weight="700" text-anchor="middle" fill="#dc2626">Private Subnet (10.0.2.0/24)</text>
<rect x="460" y="60" width="170" height="45" fill="#ffffff" stroke="#cbd5e1" rx="3" />
<text x="545" y="78" font-family="sans-serif" font-size="8.5" font-weight="700" text-anchor="middle" fill="#dc2626">Database (PostgreSQL)</text>
<text x="545" y="92" font-family="sans-serif" font-size="7.5" fill="#64748b" text-anchor="middle">NO Public IP • SG: Allow 5432 from Web</text>
</svg>""",
        "steps_rows": """<tr>
<td><strong>Step 1</strong></td>
<td>Calculate <strong>CIDR Subnets</strong> (/24 vs /28)</td>
<td>Inspect how 10.0.0.0/16 provides 65,536 addresses, divided into 256-host subnet pools.</td>
</tr>
<tr>
<td><strong>Step 2</strong></td>
<td>Send <strong>Internet Traffic to Web Tier</strong></td>
<td>Packet arrives at IGW, passes Route Table, evaluates Security Group port 80 rule, and reaches web server.</td>
</tr>
<tr>
<td><strong>Step 3</strong></td>
<td>Attempt <strong>Direct Internet Ingress to DB</strong></td>
<td>Packet is immediately rejected: no route to private subnet exists in the Internet Gateway.</td>
</tr>
<tr>
<td><strong>Step 4</strong></td>
<td>Initiate <strong>DB Software Update via NAT</strong></td>
<td>DB talks outbound to internet via NAT Gateway. Internet sees only the NAT IP, keeping the DB completely hidden.</td>
</tr>
<tr>
<td><strong>Step 5</strong></td>
<td>Toggle <strong>Security Group Rule</strong></td>
<td>Disable port 5432; observe how web-to-database connections are instantly blocked by the stateful firewall.</td>
</tr>""",
        "takeaway_lead": "Isolation is the Foundation of Cloud Security.",
        "takeaway_body": "Never give a database a public IP address. By placing sensitive assets in private subnets behind NAT gateways, you eliminate 99.9% of external attack vectors.",
        "viva_boxes": """<div class="q-box">
<div class="q-title">Q1: What is the primary difference between an Internet Gateway (IGW) and a NAT Gateway?</div>
<div class="q-ans"><strong>Answer:</strong> An <strong>IGW</strong> enables two-way communication (ingress and egress) between public subnets and the internet. A <strong>NAT Gateway</strong> allows private instances to initiate outbound connections without allowing incoming traffic.</div>
</div>
<div class="q-box">
<div class="q-title">Q2: What is the difference between a Security Group and a NACL?</div>
<div class="q-ans"><strong>Answer:</strong> <strong>Security Groups</strong> are stateful and operate at the virtual network interface/instance level. <strong>NACLs</strong> are stateless and operate at the subnet boundary.</div>
</div>
<div class="q-box">
<div class="q-title">Q3: How many usable IP addresses are in an AWS /28 subnet?</div>
<div class="q-ans"><strong>Answer:</strong> 11 usable IPs (16 total minus 5 addresses reserved by cloud providers for network, router, DNS, future use, and broadcast).</div>
</div>"""
    },
    {
        "num": "06",
        "dir": "practical-06-object-storage-s3",
        "title": "Cloud Object Storage: S3 & Presigned URLs",
        "subtitle": "REST API, HMAC Expiring Signatures & Automated Lifecycle Tiering",
        "port": "8080",
        "memory": "~37 MiB",
        "what_is_it": """<p>Traditional file systems organize files in folders and directories on a specific hard drive. <strong>Cloud Object Storage (Amazon S3 / Google Cloud Storage)</strong> treats data as flat 'objects' stored in buckets, accessible worldwide via simple HTTP REST requests (<code>GET</code>, <code>PUT</code>, <code>DELETE</code>).</p>
<p>Each object consists of raw data, a unique Key, and customizable metadata, scaling to exabytes of data with 99.999999999% (11 9's) durability.</p>""",
        "analogy_title": "🚗 The Infinite Airport Valet Parking Analogy",
        "layman_analogy": """<ul>
<li><strong>Hard Drive (Block):</strong> A notebook with numbered pages—you must know page 40 to write.</li>
<li><strong>Folder (File):</strong> A physical filing cabinet with nested paper folders.</li>
<li><strong>Object Storage (S3):</strong> An infinite valet parking lot. You hand them your car (file); they give you a claim ticket (URL/Key) and record metadata (make, color). You don't care which garage or city it sits in.</li>
<li><strong>Presigned URL:</strong> Giving a friend a temporary digital barcode that unlocks one specific suitcase for only 15 minutes, without giving them your master house keys.</li>
<li><strong>Lifecycle Rules:</strong> Moving last year's luggage from the luxury front desk (Standard) to cold underground salt mines (Glacier) to save 90% on costs.</li>
</ul>""",
        "use_case": """<p><strong>Instagram</strong> and <strong>Dropbox</strong> store billions of user photos and video clips in S3 buckets. 
When a user uploads a photo, Instagram generates a temporary S3 Presigned URL, allowing the mobile app to upload directly to S3 without choking Instagram's web servers.</p>""",
        "infographic_caption": "S3 Bucket Architecture: Presigned URLs & Tiered Lifecycle Archival",
        "svg_infographic": """<svg width="100%" height="135" viewBox="0 0 680 135" xmlns="http://www.w3.org/2000/svg">
<rect width="680" height="135" fill="#f8fafc" rx="8" />
<rect x="25" y="35" width="130" height="70" fill="#ffffff" stroke="#cbd5e1" rx="4" />
<text x="90" y="55" font-family="sans-serif" font-size="9.5" font-weight="700" text-anchor="middle" fill="#0f172a">Client Device</text>
<rect x="35" y="65" width="110" height="25" fill="#eff6ff" stroke="#bfdbfe" rx="3" />
<text x="90" y="81" font-family="sans-serif" font-size="8" font-weight="600" text-anchor="middle" fill="#1d4ed8">Mobile / Web App</text>
<path d="M 160 55 L 210 55" stroke="#059669" stroke-width="2" />
<text x="185" y="48" font-family="sans-serif" font-size="7.5" font-weight="700" fill="#059669" text-anchor="middle">PUT / GET</text>
<rect x="215" y="15" width="440" height="105" fill="#ffffff" stroke="#059669" stroke-width="1.5" rx="6" />
<text x="235" y="32" font-family="sans-serif" font-size="10" font-weight="700" fill="#059669">Amazon S3 Bucket: "cloud-media-vault"</text>
<!-- Tier 1 -->
<rect x="230" y="42" width="125" height="65" fill="#ecfdf5" stroke="#a7f3d0" rx="4" />
<text x="292" y="60" font-family="sans-serif" font-size="9" font-weight="700" text-anchor="middle" fill="#065f46">S3 Standard</text>
<text x="292" y="75" font-family="sans-serif" font-size="7.5" fill="#64748b" text-anchor="middle">Hot Tier • Active Use</text>
<text x="292" y="90" font-family="sans-serif" font-size="8" font-weight="600" fill="#059669" text-anchor="middle">$0.023 / GB-month</text>
<!-- Arrow -->
<path d="M 360 75 L 380 75" stroke="#94a3b8" stroke-width="2" />
<!-- Tier 2 -->
<rect x="385" y="42" width="125" height="65" fill="#fffbeb" stroke="#fde68a" rx="4" />
<text x="447" y="60" font-family="sans-serif" font-size="9" font-weight="700" text-anchor="middle" fill="#92400e">Infrequent (IA)</text>
<text x="447" y="75" font-family="sans-serif" font-size="7.5" fill="#64748b" text-anchor="middle">After 30 Days Idle</text>
<text x="447" y="90" font-family="sans-serif" font-size="8" font-weight="600" fill="#d97706" text-anchor="middle">$0.0125 / GB-month</text>
<!-- Arrow -->
<path d="M 515 75 L 535 75" stroke="#94a3b8" stroke-width="2" />
<!-- Tier 3 -->
<rect x="540" y="42" width="105" height="65" fill="#f1f5f9" stroke="#cbd5e1" rx="4" />
<text x="592" y="60" font-family="sans-serif" font-size="9" font-weight="700" text-anchor="middle" fill="#334155">Glacier Deep</text>
<text x="592" y="75" font-family="sans-serif" font-size="7.5" fill="#64748b" text-anchor="middle">After 90 Days</text>
<text x="592" y="90" font-family="sans-serif" font-size="8" font-weight="600" fill="#475569" text-anchor="middle">$0.00099 / GB</text>
</svg>""",
        "steps_rows": """<tr>
<td><strong>Step 1</strong></td>
<td>Create S3 Bucket <code>my-cloud-bucket</code></td>
<td>Creates a unique namespace bucket with public access block and CORS headers.</td>
</tr>
<tr>
<td><strong>Step 2</strong></td>
<td>Upload File via <code>PUT /api/upload</code></td>
<td>Calculates MD5 hash, stores binary payload, records metadata, and issues an Amazon-style ETag.</td>
</tr>
<tr>
<td><strong>Step 3</strong></td>
<td>Generate <strong>Presigned URL</strong> (60s TTL)</td>
<td>Computes an HMAC-SHA256 signature containing expiration timestamp, allowing zero-credential downloads.</td>
</tr>
<tr>
<td><strong>Step 4</strong></td>
<td>Test Expired URL (Wait 60s)</td>
<td>Simulator verifies signature timestamp; returns <code>403 SignatureDoesNotMatch (Request Expired)</code>.</td>
</tr>
<tr>
<td><strong>Step 5</strong></td>
<td>Trigger <strong>Lifecycle Rule</strong></td>
<td>Transitions old files from Standard to Glacier, reducing simulated monthly cost by 95.7%.</td>
</tr>""",
        "takeaway_lead": "Storage is Infinite, Bandwidth is Not.",
        "takeaway_body": "Presigned URLs offload heavy uploads and downloads directly to S3 storage, preventing web servers from choking on gigabytes of file transfers.",
        "viva_boxes": """<div class="q-box">
<div class="q-title">Q1: What is the difference between Block Storage (EBS) and Object Storage (S3)?</div>
<div class="q-ans"><strong>Answer:</strong> <strong>Block storage</strong> acts like a raw hard drive attached to a single VM (needed for OS booting and high-IOPS databases). <strong>Object storage</strong> is a global HTTP-based flat repository for unstructured files (images, backups).</div>
</div>
<div class="q-box">
<div class="q-title">Q2: How does a Presigned URL securely authenticate without sharing AWS secret keys?</div>
<div class="q-ans"><strong>Answer:</strong> The server computes an HMAC-SHA256 signature combining the HTTP verb, bucket, object key, expiration timestamp, and secret access key. S3 independently validates the signature mathematically.</div>
</div>
<div class="q-box">
<div class="q-title">Q3: What are S3 Lifecycle policies and why are they critical?</div>
<div class="q-ans"><strong>Answer:</strong> Automated rules that transition aging objects to cheaper storage classes (e.g. Standard to Glacier) and delete old versions, saving up to 90% on long-term data storage costs.</div>
</div>"""
    },
    {
        "num": "07",
        "dir": "practical-07-iam-access-control",
        "title": "Cloud Identity & Access Management (IAM)",
        "subtitle": "RBAC Roles, AWS JSON Policy Engine & Least Privilege Auditing",
        "port": "8080",
        "memory": "~33 MiB",
        "what_is_it": """<p>In cloud computing, a single leaked credential can bankrupt a company. <strong>Identity and Access Management (IAM)</strong> controls <em>who</em> is authenticated (Users/Roles) and <em>what actions</em> they are authorized to perform across resources.</p>
<p>Cloud IAM relies on <strong>JSON Policies</strong> evaluated with strict precedence: <strong>Explicit Deny > Explicit Allow > Default (Implicit) Deny</strong>.</p>""",
        "analogy_title": "💳 The Corporate Keycard & Security Badge Analogy",
        "layman_analogy": """<ul>
<li><strong>User:</strong> A specific employee (Alice).</li>
<li><strong>Role:</strong> A security hat you put on temporarily (e.g. 'Emergency Firefighter').</li>
<li><strong>Policy:</strong> A laminated rule card: <em>'Alice can drink from water fountain, but CANNOT touch the power breaker.'</em></li>
<li><strong>The Golden Rule:</strong> If one badge says <em>'Alice can enter all doors'</em> (Allow), but another says <em>'Nobody enters server room on weekends'</em> (Explicit Deny), <strong>Explicit Deny ALWAYS wins!</strong></li>
<li><strong>Least Privilege:</strong> Never hand an intern master building keys when all they need is a keycard to the supply closet.</li>
</ul>""",
        "use_case": """<p>The infamous <strong>Capital One breach ($80M fine)</strong> happened because a server was assigned a bloated IAM role with wildcard permissions (<code>s3:*</code>). 
Applying the Principle of Least Privilege prevents a compromised frontend server from accessing financial databases.</p>""",
        "infographic_caption": "AWS-Style IAM Policy Evaluation Logic & Precedence Hierarchy",
        "svg_infographic": """<svg width="100%" height="135" viewBox="0 0 680 135" xmlns="http://www.w3.org/2000/svg">
<rect width="680" height="135" fill="#f8fafc" rx="8" />
<rect x="25" y="45" width="115" height="50" fill="#ffffff" stroke="#cbd5e1" rx="4" />
<text x="82" y="65" font-family="sans-serif" font-size="9.5" font-weight="700" text-anchor="middle" fill="#0f172a">API Request</text>
<text x="82" y="80" font-family="sans-serif" font-size="7.5" fill="#64748b" text-anchor="middle">s3:DeleteBucket</text>
<path d="M 145 70 L 175 70" stroke="#2563eb" stroke-width="2" />
<!-- Decision 1 -->
<polygon points="215,40 255,70 215,100 175,70" fill="#fee2e2" stroke="#fca5a5" />
<text x="215" y="68" font-family="sans-serif" font-size="8" font-weight="700" text-anchor="middle" fill="#991b1b">Explicit</text>
<text x="215" y="78" font-family="sans-serif" font-size="8" font-weight="700" text-anchor="middle" fill="#991b1b">Deny?</text>
<!-- Yes Deny -->
<path d="M 215 100 L 215 115 L 590 115" stroke="#dc2626" stroke-width="2" stroke-dasharray="3" fill="none" />
<text x="225" y="112" font-family="sans-serif" font-size="8" fill="#dc2626">YES</text>
<!-- No -> Check Allow -->
<path d="M 255 70 L 295 70" stroke="#2563eb" stroke-width="2" />
<text x="275" y="65" font-family="sans-serif" font-size="8" fill="#15803d">NO</text>
<polygon points="345,40 385,70 345,100 305,70" fill="#dcfce7" stroke="#86efac" />
<text x="345" y="68" font-family="sans-serif" font-size="8" font-weight="700" text-anchor="middle" fill="#166534">Explicit</text>
<text x="345" y="78" font-family="sans-serif" font-size="8" font-weight="700" text-anchor="middle" fill="#166534">Allow?</text>
<!-- Yes Allow -->
<path d="M 385 70 L 485 70" stroke="#059669" stroke-width="2" />
<text x="430" y="65" font-family="sans-serif" font-size="8" fill="#059669">YES</text>
<rect x="490" y="52" width="75" height="35" fill="#ecfdf5" stroke="#a7f3d0" rx="4" />
<text x="527" y="73" font-family="sans-serif" font-size="9" font-weight="700" text-anchor="middle" fill="#059669">ALLOW</text>
<!-- No Allow -> Default Deny -->
<path d="M 345 100 L 345 115 L 590 115" stroke="#dc2626" stroke-width="2" stroke-dasharray="3" fill="none" />
<text x="355" y="112" font-family="sans-serif" font-size="8" fill="#dc2626">NO</text>
<rect x="590" y="52" width="75" height="65" fill="#fef2f2" stroke="#fca5a5" rx="4" />
<text x="627" y="90" font-family="sans-serif" font-size="10" font-weight="700" text-anchor="middle" fill="#dc2626">DENY</text>
</svg>""",
        "steps_rows": """<tr>
<td><strong>Step 1</strong></td>
<td>Select <strong>Junior Dev Role</strong></td>
<td>Loads AWS JSON policy containing <code>Effect: Allow, Action: s3:GetObject</code> only.</td>
</tr>
<tr>
<td><strong>Step 2</strong></td>
<td>Attempt <code>s3:DeleteBucket</code></td>
<td>Policy engine tests rule; finds no explicit allow, defaults to <strong>Implicit Deny</strong>.</td>
</tr>
<tr>
<td><strong>Step 3</strong></td>
<td>Add <strong>Explicit Deny</strong> Policy Rule</td>
<td>Appends <code>Effect: Deny, Action: s3:*</code> to user; watch it immediately override all admin privileges!</td>
</tr>
<tr>
<td><strong>Step 4</strong></td>
<td>Run <strong>AssumeRole</strong> Simulation</td>
<td>Demonstrates temporary credential generation with 1-hour session tokens via AWS STS.</td>
</tr>
<tr>
<td><strong>Step 5</strong></td>
<td>Run <strong>Least-Privilege Security Audit</strong></td>
<td>Scans active permissions, identifies 5 unused high-risk permissions, and recommends hardened JSON policy.</td>
</tr>""",
        "takeaway_lead": "Default to No, Deny Overrides All.",
        "takeaway_body": "In secure cloud architecture, permissions are never granted by default. If a policy has a single Explicit Deny, no amount of Allow rules can unlock that door.",
        "viva_boxes": """<div class="q-box">
<div class="q-title">Q1: Explain the IAM Policy Evaluation Logic order in AWS/Cloud.</div>
<div class="q-ans"><strong>Answer:</strong> 1. By default, all requests are implicitly denied. 2. An explicit deny overrides everything (if matched, request denied). 3. If no deny, an explicit allow grants access. 4. If neither, it remains denied.</div>
</div>
<div class="q-box">
<div class="q-title">Q2: What is the difference between an IAM User and an IAM Role?</div>
<div class="q-ans"><strong>Answer:</strong> An <strong>IAM User</strong> has permanent long-term credentials (password, access keys) associated with a single human. An <strong>IAM Role</strong> has no credentials and is assumed dynamically by trusted entities with temporary short-lived tokens.</div>
</div>
<div class="q-box">
<div class="q-title">Q3: What is the Principle of Least Privilege?</div>
<div class="q-ans"><strong>Answer:</strong> Granting only the exact minimal set of permissions required to perform a specific task, for only the duration needed, minimizing blast radius if credentials leak.</div>
</div>"""
    },
    {
        "num": "08",
        "dir": "practical-08-cloud-security",
        "title": "Cloud Security: WAF, DDoS & KMS Encryption",
        "subtitle": "Token-Bucket Rate Limiter, SQLi/XSS WAF & AES-256 Envelope Encryption",
        "port": "8080",
        "memory": "~36 MiB",
        "what_is_it": """<p>Cloud applications face relentless automated cyberattacks. <strong>Web Application Firewalls (WAF)</strong> inspect HTTP traffic to block SQL injection and Cross-Site Scripting (XSS), while <strong>DDoS Token-Bucket Limiters</strong> throttle malicious traffic floods.</p>
<p>For sensitive data at rest, <strong>KMS Envelope Encryption</strong> uses a two-tier hierarchy: customer data is encrypted with a fast Data Encryption Key (DEK), which is then protected under a hardware-secured Customer Master Key (CMK).</p>""",
        "analogy_title": "🛡️ The TSA Scanner & Dual-Key Vault Analogy",
        "layman_analogy": """<ul>
<li><strong>DDoS Attack:</strong> 10,000 prank callers jamming a pizza restaurant's phones so real customers cannot order.</li>
<li><strong>Token-Bucket Limiter:</strong> A nightclub bouncer who only lets 10 people in per second; excess people wait outside (HTTP 429).</li>
<li><strong>WAF:</strong> The airport baggage scanner looking for dangerous weapons (SQL injection <code>' OR 1=1 --</code> and XSS <code>&lt;script&gt;</code>).</li>
<li><strong>Envelope Encryption:</strong> Locking your jewelry inside a small steel lockbox with Key A (Data Key). You then lock Key A inside a massive titanium bank vault with Master Key B (KMS Master Key). Even if thieves steal the lockbox, it is useless without Key B!</li>
</ul>""",
        "use_case": """<p><strong>Cloudflare</strong> and <strong>AWS WAF</strong> mitigate multi-terabit DDoS attacks daily. 
Healthcare and banking systems use KMS Envelope Encryption to comply with HIPAA and PCI-DSS, guaranteeing that rogue cloud datacenter technicians cannot read patient records.</p>""",
        "infographic_caption": "Three-Tier Cloud Defense: Rate Limiter, WAF & KMS Envelope Encryption",
        "svg_infographic": """<svg width="100%" height="135" viewBox="0 0 680 135" xmlns="http://www.w3.org/2000/svg">
<rect width="680" height="135" fill="#f8fafc" rx="8" />
<rect x="25" y="30" width="100" height="80" fill="#fee2e2" stroke="#fca5a5" rx="4" />
<text x="75" y="52" font-family="sans-serif" font-size="9" font-weight="700" text-anchor="middle" fill="#dc2626">Web Traffic</text>
<text x="75" y="70" font-family="sans-serif" font-size="7.5" fill="#dc2626" text-anchor="middle">Legit + DDoS</text>
<text x="75" y="85" font-family="sans-serif" font-size="7.5" fill="#dc2626" text-anchor="middle">+ SQLi Attacks</text>
<path d="M 130 70 L 155 70" stroke="#dc2626" stroke-width="2" />
<!-- Layer 1 -->
<rect x="160" y="30" width="145" height="80" fill="#fffbeb" stroke="#fde68a" rx="4" />
<text x="232" y="52" font-family="sans-serif" font-size="9.5" font-weight="700" text-anchor="middle" fill="#b45309">1. Token Bucket</text>
<text x="232" y="70" font-family="sans-serif" font-size="8" fill="#64748b" text-anchor="middle">Capacity: 20 tokens</text>
<text x="232" y="85" font-family="sans-serif" font-size="8" font-weight="600" fill="#d97706" text-anchor="middle">DDoS Flood -> 429 Throttle</text>
<path d="M 310 70 L 335 70" stroke="#059669" stroke-width="2" />
<!-- Layer 2 -->
<rect x="340" y="30" width="145" height="80" fill="#eff6ff" stroke="#bfdbfe" rx="4" />
<text x="412" y="52" font-family="sans-serif" font-size="9.5" font-weight="700" text-anchor="middle" fill="#1d4ed8">2. WAF Inspector</text>
<text x="412" y="70" font-family="sans-serif" font-size="8" fill="#64748b" text-anchor="middle">Regex Signatures</text>
<text x="412" y="85" font-family="sans-serif" font-size="8" font-weight="600" fill="#2563eb" text-anchor="middle">Blocks SQLi & XSS (403)</text>
<path d="M 490 70 L 515 70" stroke="#059669" stroke-width="2" />
<!-- Layer 3 -->
<rect x="520" y="30" width="140" height="80" fill="#ecfdf5" stroke="#86efac" rx="4" />
<text x="590" y="52" font-family="sans-serif" font-size="9.5" font-weight="700" text-anchor="middle" fill="#15803d">3. KMS Encryption</text>
<text x="590" y="70" font-family="sans-serif" font-size="8" fill="#64748b" text-anchor="middle">AES-256-GCM + DEK</text>
<text x="590" y="85" font-family="sans-serif" font-size="8" font-weight="600" fill="#059669" text-anchor="middle">Encrypted at Rest</text>
</svg>""",
        "steps_rows": """<tr>
<td><strong>Step 1</strong></td>
<td>Send <strong>Simulated SQL Injection Attack</strong></td>
<td>Payload <code>' UNION SELECT username, password FROM users --</code> is inspected by WAF engine and blocked (HTTP 403).</td>
</tr>
<tr>
<td><strong>Step 2</strong></td>
<td>Send <strong>XSS Attack Payload</strong></td>
<td>Payload <code>&lt;script&gt;alert(document.cookie)&lt;/script&gt;</code> is blocked by WAF input sanitization filter.</td>
</tr>
<tr>
<td><strong>Step 3</strong></td>
<td>Launch <strong>DDoS Traffic Flood</strong> (100 reqs/sec)</td>
<td>Exhausts token bucket capacity; server returns <code>HTTP 429 Too Many Requests</code> with <code>Retry-After</code> header.</td>
</tr>
<tr>
<td><strong>Step 4</strong></td>
<td>Generate <strong>KMS Master Key & Data Key</strong></td>
<td>Generates 256-bit AES plaintext key for high-speed local encryption, and encrypts it with the master KMS key.</td>
</tr>
<tr>
<td><strong>Step 5</strong></td>
<td>Perform <strong>Envelope Encryption & Decryption</strong></td>
<td>Encrypts sensitive record with DEK, discards plaintext DEK from memory, and verifies zero-loss decryption.</td>
</tr>""",
        "takeaway_lead": "Defense in Depth: Protect Edge, App & Storage.",
        "takeaway_body": "Rate limit at the perimeter (DDoS), sanitize at the application layer (WAF), and encrypt at the storage layer (KMS). If one layer fails, the next layer prevents catastrophic data compromise.",
        "viva_boxes": """<div class="q-box">
<div class="q-title">Q1: How does a Token Bucket rate limiter mitigate DDoS traffic?</div>
<div class="q-ans"><strong>Answer:</strong> Tokens refill at a fixed rate (e.g. 10/sec). Each request consumes 1 token. When the bucket is empty, burst traffic is immediately rejected with HTTP 429 without loading backend application servers.</div>
</div>
<div class="q-box">
<div class="q-title">Q2: Why use Envelope Encryption instead of encrypting everything with the master key?</div>
<div class="q-ans"><strong>Answer:</strong> Encrypting large files over network calls to a central KMS creates massive network latency and bottlenecks. Envelope encryption encrypts data locally at CPU speeds using a fast DEK, with only the small key sent to KMS.</div>
</div>
<div class="q-box">
<div class="q-title">Q3: What attack vector does a Web Application Firewall (WAF) inspect that standard firewalls miss?</div>
<div class="q-ans"><strong>Answer:</strong> Standard firewalls inspect Layer 3/4 (IP addresses, TCP ports). A WAF inspects Layer 7 (HTTP bodies, query strings, cookies, headers) to detect application exploits like SQLi and XSS.</div>
</div>"""
    },
    {
        "num": "09",
        "dir": "practical-09-openstack-private-cloud",
        "title": "OpenStack Private Cloud & Resource Quotas",
        "subtitle": "Nova, Neutron, Keystone & Multi-Tenant Resource Governance",
        "port": "8080",
        "memory": "~35 MiB",
        "what_is_it": """<p>While public clouds (AWS, GCP) are rented from tech giants, many telecom providers, governments, and banks run on-premises datacenters. <strong>OpenStack</strong> is the leading open-source software suite that turns private physical hardware into an AWS-like cloud.</p>
<p>OpenStack coordinates compute (<strong>Nova</strong>), networking (<strong>Neutron</strong>), identity (<strong>Keystone</strong>), and storage (<strong>Cinder</strong>) with strict <strong>Tenant Quotas</strong> to prevent noisy neighbors from exhausting resources.</p>""",
        "analogy_title": "🏢 Building Your Own Private Hotel Chain",
        "layman_analogy": """<ul>
<li><strong>Public Cloud (AWS):</strong> Renting rooms in a commercial hotel chain—convenient, but you pay every month forever and don't own the wires.</li>
<li><strong>OpenStack:</strong> A DIY architectural blueprint kit to build your own private automated hotel inside your own warehouse.</li>
<li><strong>Nova:</strong> The room manager who assigns virtual rooms (VMs) on physical floors.</li>
<li><strong>Neutron:</strong> The plumber and electrician setting up private intercoms and water pipes (Subnets and Routers).</li>
<li><strong>Keystone:</strong> The front desk concierge verifying employee ID badges and granting temporary room keys.</li>
<li><strong>Tenant Quotas:</strong> Strict monthly allowances: Marketing gets 8 cores, Engineering gets 32 cores, preventing one team from hogging the whole building.</li>
</ul>""",
        "use_case": """<p><strong>AT&T</strong>, <strong>Verizon</strong>, and <strong>CERN (the Large Hadron Collider)</strong> run OpenStack across hundreds of thousands of CPU cores to analyze petabytes of scientific and 5G network data without paying millions in public cloud egress bills.</p>""",
        "infographic_caption": "OpenStack Core Service Architecture & Multi-Tenant Quota Enforcer",
        "svg_infographic": """<svg width="100%" height="135" viewBox="0 0 680 135" xmlns="http://www.w3.org/2000/svg">
<rect width="680" height="135" fill="#f8fafc" rx="8" />
<rect x="25" y="15" width="630" height="24" fill="#0f172a" rx="4" />
<text x="340" y="31" font-family="sans-serif" font-size="10" font-weight="700" text-anchor="middle" fill="#ffffff">OpenStack Horizon Web Dashboard / CLI API Gateway</text>
<rect x="35" y="48" width="135" height="50" fill="#eff6ff" stroke="#bfdbfe" rx="4" />
<text x="102" y="68" font-family="sans-serif" font-size="9.5" font-weight="700" text-anchor="middle" fill="#1d4ed8">Keystone</text>
<text x="102" y="83" font-family="sans-serif" font-size="8" fill="#64748b" text-anchor="middle">Auth & RBAC Tokens</text>
<rect x="190" y="48" width="135" height="50" fill="#fef3c7" stroke="#fde68a" rx="4" />
<text x="257" y="68" font-family="sans-serif" font-size="9.5" font-weight="700" text-anchor="middle" fill="#b45309">Nova Compute</text>
<text x="257" y="83" font-family="sans-serif" font-size="8" fill="#64748b" text-anchor="middle">VM Schedulers & KVM</text>
<rect x="345" y="48" width="135" height="50" fill="#f0fdf4" stroke="#86efac" rx="4" />
<text x="412" y="68" font-family="sans-serif" font-size="9.5" font-weight="700" text-anchor="middle" fill="#15803d">Neutron Network</text>
<text x="412" y="83" font-family="sans-serif" font-size="8" fill="#64748b" text-anchor="middle">Software-Defined Net</text>
<rect x="500" y="48" width="145" height="50" fill="#fef2f2" stroke="#fca5a5" rx="4" />
<text x="572" y="68" font-family="sans-serif" font-size="9.5" font-weight="700" text-anchor="middle" fill="#dc2626">Tenant Quotas</text>
<text x="572" y="83" font-family="sans-serif" font-size="8" font-weight="600" fill="#dc2626" text-anchor="middle">Max 16 Cores / 32GB</text>
<rect x="25" y="105" width="630" height="20" fill="#334155" rx="3" />
<text x="340" y="119" font-family="sans-serif" font-size="8.5" font-weight="600" text-anchor="middle" fill="#ffffff">Underlying Physical Bare-Metal Server Racks & Storage Arrays</text>
</svg>""",
        "steps_rows": """<tr>
<td><strong>Step 1</strong></td>
<td>Authenticate with <strong>Keystone</strong></td>
<td>Acquires a scoped Keystone auth token for tenant project <code>finance-dev</code>.</td>
</tr>
<tr>
<td><strong>Step 2</strong></td>
<td>Inspect <strong>Tenant Quotas</strong></td>
<td>Observes quota ceilings: 8 vCPUs, 16 GB RAM, 2 Floating IPs allocated to this project.</td>
</tr>
<tr>
<td><strong>Step 3</strong></td>
<td>Launch Nova VM (2 vCPU, 4GB)</td>
<td>Nova scheduler locates available compute node, allocates hypervisor slices, and boots instance.</td>
</tr>
<tr>
<td><strong>Step 4</strong></td>
<td>Attach <strong>Neutron Floating IP</strong></td>
<td>Associates public routing NAT to the private VM port.</td>
</tr>
<tr>
<td><strong>Step 5</strong></td>
<td>Attempt <strong>Over-Quota Launch</strong> (10 vCPUs)</td>
<td>Simulator intercepts request: <code>HTTP 413 QuotaExceeded: Requested 10 vCPUs, quota remaining is 6</code>.</td>
</tr>""",
        "takeaway_lead": "Governance is Essential in Multi-Tenant Clouds.",
        "takeaway_body": "Without hard quotas, a single buggy script from one team can exhaust all physical CPU and RAM in a private datacenter, crashing mission-critical enterprise systems.",
        "viva_boxes": """<div class="q-box">
<div class="q-title">Q1: Name the 4 core foundational services of OpenStack and their roles.</div>
<div class="q-ans"><strong>Answer:</strong> 1. <strong>Keystone:</strong> Identity and auth. 2. <strong>Nova:</strong> Compute provisioning and VM lifecycle. 3. <strong>Neutron:</strong> Virtual software-defined networking. 4. <strong>Glance:</strong> VM disk image catalog.</div>
</div>
<div class="q-box">
<div class="q-title">Q2: Why do organizations choose OpenStack over AWS or Azure?</div>
<div class="q-ans"><strong>Answer:</strong> Data sovereignty, regulatory compliance (banking/military), predictable amortized costs for massive steady-state compute workloads, and eliminating cloud provider vendor lock-in.</div>
</div>
<div class="q-box">
<div class="q-title">Q3: What happens when a tenant attempts to exceed its OpenStack resource quota?</div>
<div class="q-ans"><strong>Answer:</strong> The API service immediately rejects the provisioning call with HTTP 413 (Over Limit / Quota Exceeded) before any underlying hypervisor or storage resources are reserved.</div>
</div>"""
    },
    {
        "num": "10",
        "dir": "practical-10-cloud-autoscaling",
        "title": "Horizontal Pod & Container Auto-Scaling Engine",
        "subtitle": "Live Scaling Formula, Cooldown Flapping Guard & Dynamic Load Balancer",
        "port": "8080",
        "memory": "~42 MiB",
        "what_is_it": """<p>Web traffic is inherently unpredictable. During normal hours you need 2 servers, but during a Black Friday flash sale you suddenly need 10 servers. <strong>Horizontal Auto-Scaling</strong> automatically adds or removes container instances in real time based on live CPU load.</p>
<p>The autoscaling engine calculates: $\text{Desired} = \lceil \text{Current} \times (\text{Metric} / \text{Target}) \rceil$, reinforced by a <strong>Cooldown Flapping Guard</strong> to prevent thrashing.</p>""",
        "analogy_title": "🛒 The Supermarket Cashier Lines on Black Friday",
        "layman_analogy": """<ul>
<li><strong>Vertical Scaling (Scale Up):</strong> Hiring one giant superhuman cashier who can scan 10 items/sec. Eventually, physical limits are reached and the human collapses.</li>
<li><strong>Horizontal Scaling (Scale Out):</strong> Opening 4 extra cashier checkout counters when customer lines get long, and closing them when the store is empty.</li>
<li><strong>The Autoscaling Brain:</strong> Constantly counting shoppers in line. If average queue exceeds 70%, it immediately opens counter #3 and counter #4.</li>
<li><strong>Cooldown Flapping Guard:</strong> If you open a new counter, you don't fire them 5 seconds later just because one customer walked away. You wait a 10-second cooldown period to prevent erratic flapping!</li>
</ul>""",
        "use_case": """<p><strong>Amazon</strong> and <strong>Ticketmaster</strong> rely on horizontal autoscaling. 
When Taylor Swift concert tickets drop, traffic surges 5,000% in 3 seconds. Autoscaling rapidly provisions hundreds of containers to absorb the shock, saving millions in lost ticket sales.</p>""",
        "infographic_caption": "Horizontal Autoscaling Feedback Loop: Traffic Surge, Metric Evaluation & Nginx Upstream",
        "svg_infographic": """<svg width="100%" height="135" viewBox="0 0 680 135" xmlns="http://www.w3.org/2000/svg">
<rect width="680" height="135" fill="#f8fafc" rx="8" />
<rect x="25" y="35" width="110" height="70" fill="#fee2e2" stroke="#fca5a5" rx="4" />
<text x="80" y="55" font-family="sans-serif" font-size="9.5" font-weight="700" text-anchor="middle" fill="#dc2626">Incoming Traffic</text>
<text x="80" y="70" font-family="sans-serif" font-size="8" fill="#dc2626" text-anchor="middle">⚡ Flash Sale</text>
<text x="80" y="85" font-family="sans-serif" font-size="8" font-weight="600" fill="#dc2626" text-anchor="middle">85 reqs / min</text>
<path d="M 140 70 L 175 70" stroke="#dc2626" stroke-width="2" />
<!-- Nginx -->
<rect x="180" y="35" width="130" height="70" fill="#ffffff" stroke="#2563eb" stroke-width="1.5" rx="4" />
<text x="245" y="55" font-family="sans-serif" font-size="9.5" font-weight="700" text-anchor="middle" fill="#2563eb">Nginx Load Balancer</text>
<text x="245" y="70" font-family="sans-serif" font-size="8" fill="#64748b" text-anchor="middle">Round-Robin</text>
<text x="245" y="85" font-family="sans-serif" font-size="8" font-weight="600" fill="#059669" text-anchor="middle">Live upstream re-hash</text>
<!-- Container Pool -->
<rect x="340" y="15" width="165" height="105" fill="#f0fdf4" stroke="#86efac" rx="6" />
<text x="422" y="32" font-family="sans-serif" font-size="9.5" font-weight="700" text-anchor="middle" fill="#15803d">Active Container Pool (N=4)</text>
<rect x="350" y="42" width="70" height="24" fill="#ffffff" stroke="#cbd5e1" rx="3" /><text x="385" y="58" font-family="sans-serif" font-size="8" font-weight="600" text-anchor="middle" fill="#0f172a">app-1 (Live)</text>
<rect x="425" y="42" width="70" height="24" fill="#ffffff" stroke="#cbd5e1" rx="3" /><text x="460" y="58" font-family="sans-serif" font-size="8" font-weight="600" text-anchor="middle" fill="#0f172a">app-2 (Live)</text>
<rect x="350" y="72" width="70" height="24" fill="#ffffff" stroke="#2563eb" rx="3" /><text x="385" y="88" font-family="sans-serif" font-size="8" font-weight="600" text-anchor="middle" fill="#2563eb">app-3 (Scaled)</text>
<rect x="425" y="72" width="70" height="24" fill="#ffffff" stroke="#2563eb" rx="3" /><text x="460" y="88" font-family="sans-serif" font-size="8" font-weight="600" text-anchor="middle" fill="#2563eb">app-4 (Scaled)</text>
<!-- Autoscaler Daemon -->
<rect x="525" y="15" width="135" height="105" fill="#fef3c7" stroke="#fde68a" rx="6" />
<text x="592" y="32" font-family="sans-serif" font-size="9.5" font-weight="700" text-anchor="middle" fill="#b45309">Autoscaler Brain</text>
<text x="592" y="50" font-family="sans-serif" font-size="7.5" fill="#64748b" text-anchor="middle">Metric: 82% &gt; 70%</text>
<text x="592" y="65" font-family="sans-serif" font-size="8" font-weight="700" fill="#b45309" text-anchor="middle">Formula: ceil(2 * 1.17)</text>
<text x="592" y="80" font-family="sans-serif" font-size="7.5" fill="#15803d" text-anchor="middle">Action: SCALE OUT</text>
<text x="592" y="100" font-family="sans-serif" font-size="8" font-weight="700" fill="#dc2626" text-anchor="middle">Cooldown: 10s Guard</text>
</svg>""",
        "steps_rows": """<tr>
<td><strong>Step 1</strong></td>
<td>Run <strong>Steady Baseline</strong> (20 req/min)</td>
<td>App-1 and App-2 handle traffic at 50% capacity; pool remains stable at minimum 2 instances.</td>
</tr>
<tr>
<td><strong>Step 2</strong></td>
<td>Click <strong>"⚡ Flash Sale" Preset</strong></td>
<td>Simulates instant traffic surge to 85 reqs/min. Average pool utilization spikes past 80% threshold.</td>
</tr>
<tr>
<td><strong>Step 3</strong></td>
<td>Watch <strong>Dynamic Scale-Out</strong></td>
<td>Autoscaler calculates target replicas = 4, spawns <code>app-3</code> and <code>app-4</code>, and reloads Nginx upstream with zero dropped connections.</td>
</tr>
<tr>
<td><strong>Step 4</strong></td>
<td>Observe <strong>Cooldown Flapping Guard</strong></td>
<td>Autoscaler enters 10-second anti-thrashing cooldown; ignores minor metric dips to prevent container flapping.</td>
</tr>
<tr>
<td><strong>Step 5</strong></td>
<td>Click <strong>"🌙 Midnight Drop"</strong></td>
<td>Traffic drops to 0. After cooldown expiration, autoscaler gracefully terminates surplus containers back to baseline 2.</td>
</tr>""",
        "takeaway_lead": "Pay for What You Use, Scale for What You Need.",
        "takeaway_body": "Horizontal autoscaling is the ultimate promise of the cloud: handle 100,000 customers during flash sales, and automatically scale down to zero/minimum at 3:00 AM to eliminate wasted compute costs.",
        "viva_boxes": """<div class="q-box">
<div class="q-title">Q1: Explain the mathematical formula used by Kubernetes HPA and cloud autoscalers.</div>
<div class="q-ans"><strong>Answer:</strong> $\text{Desired Replicas} = \lceil \text{Current Replicas} \times (\text{Current Metric Value} / \text{Target Metric Value}) \rceil$. For example: $2 \times (85\% / 70\%) = \lceil 2.42 \rceil = 3$ replicas.</div>
</div>
<div class="q-box">
<div class="q-title">Q2: What is 'Flapping' (Thrashing) and how does a cooldown timer prevent it?</div>
<div class="q-ans"><strong>Answer:</strong> Flapping occurs when a system repeatedly scales out and in due to small metric fluctuations. A cooldown period enforces a mandatory pause between scaling events so metrics stabilize.</div>
</div>
<div class="q-box">
<div class="q-title">Q3: Why is horizontal scaling preferred over vertical scaling in distributed cloud systems?</div>
<div class="q-ans"><strong>Answer:</strong> Horizontal scaling has no physical hardware ceiling, offers built-in high availability (if 1 container dies, others continue serving), and allows granular, cost-efficient resource allocation.</div>
</div>"""
    }
])

print("Loaded practicals 01-10. Adding practicals 11-15...")

PRACTICALS.extend([
    {
        "num": "11",
        "dir": "practical-11-cloud-migration",
        "title": "Cloud Data Migration: 6-Rs & Parity",
        "subtitle": "Gartner 6-Rs Framework, Online Streaming & SHA-256 Parity Verification",
        "port": "8080",
        "memory": "~35 MiB",
        "what_is_it": """<p>Migrating enterprise workloads from legacy on-premises datacenters to the cloud is a high-stakes engineering endeavor. <strong>Gartner's 6-Rs Migration Framework</strong> provides the strategic roadmap for classifying every application.</p>
<p>To guarantee that financial and customer records are not corrupted during transit, <strong>Cryptographic SHA-256 Parity Verification</strong> mathematically checks bit-level data integrity.</p>""",
        "analogy_title": "🚚 Moving Houses with Certified Security Movers",
        "layman_analogy": """<ul>
<li><strong>Rehost (Lift & Shift):</strong> Loading your old furniture into a moving truck as-is without changing anything.</li>
<li><strong>Replatform (Lift & Reshape):</strong> Moving your furniture, but swapping out your old stove for modern gas cooking.</li>
<li><strong>Refactor (Cloud Native):</strong> Throwing out the old blueprints and building an automated smart house from scratch.</li>
<li><strong>Repurchase:</strong> Throwing out your old DVD player and subscribing to Netflix (switching to SaaS).</li>
<li><strong>Retain:</strong> Leaving the heavy antique piano in your old basement because moving it breaks it.</li>
<li><strong>Retire:</strong> Throwing out junk boxes you haven't opened in 5 years.</li>
<li><strong>Cryptographic Parity:</strong> Stamping a tamper-proof wax seal (SHA-256 hash) on every box before moving. If the seal matches at the new house, mathematical certainty guarantees not a single coin was lost!</li>
</ul>""",
        "use_case": """<p><strong>General Electric (GE)</strong> migrated over 9,000 workloads to AWS, saving $14M annually. 
Using automated SHA-256 bit-level hashing guaranteed that terabytes of aviation turbine telemetry were transferred with zero data loss.</p>""",
        "infographic_caption": "Gartner 6-Rs Strategy Pipeline & Cryptographic Parity Verification Engine",
        "svg_infographic": """<svg width="100%" height="135" viewBox="0 0 680 135" xmlns="http://www.w3.org/2000/svg">
<rect width="680" height="135" fill="#f8fafc" rx="8" />
<rect x="25" y="25" width="135" height="85" fill="#ffffff" stroke="#cbd5e1" rx="4" />
<text x="92" y="45" font-family="sans-serif" font-size="9.5" font-weight="700" text-anchor="middle" fill="#0f172a">On-Premises Data</text>
<text x="92" y="62" font-family="sans-serif" font-size="8" fill="#64748b" text-anchor="middle">Source: Oracle / NAS</text>
<rect x="35" y="72" width="115" height="25" fill="#eff6ff" stroke="#bfdbfe" rx="3" />
<text x="92" y="88" font-family="sans-serif" font-size="7.5" font-weight="700" text-anchor="middle" fill="#1d4ed8">SHA-256: 7a8f...9b2c</text>
<path d="M 165 67 L 200 67" stroke="#2563eb" stroke-width="2" />
<!-- 6-Rs Engine -->
<rect x="205" y="20" width="155" height="95" fill="#fef3c7" stroke="#fde68a" rx="6" />
<text x="282" y="38" font-family="sans-serif" font-size="9.5" font-weight="700" text-anchor="middle" fill="#b45309">Gartner 6-Rs Engine</text>
<text x="282" y="55" font-family="sans-serif" font-size="7.5" fill="#64748b" text-anchor="middle">• Rehost (Lift & Shift)</text>
<text x="282" y="70" font-family="sans-serif" font-size="7.5" fill="#64748b" text-anchor="middle">• Replatform • Refactor</text>
<text x="282" y="85" font-family="sans-serif" font-size="7.5" fill="#64748b" text-anchor="middle">• Repurchase • Retain</text>
<text x="282" y="100" font-family="sans-serif" font-size="7.5" font-weight="700" fill="#dc2626" text-anchor="middle">• Retire (Sunset 20%)</text>
<path d="M 365 67 L 400 67" stroke="#059669" stroke-width="2" />
<!-- Parity Validator -->
<rect x="405" y="20" width="130" height="95" fill="#ecfdf5" stroke="#86efac" rx="6" />
<text x="470" y="38" font-family="sans-serif" font-size="9" font-weight="700" text-anchor="middle" fill="#047857">Online Migration</text>
<text x="470" y="55" font-family="sans-serif" font-size="7.5" fill="#64748b" text-anchor="middle">Chunked Stream</text>
<text x="470" y="70" font-family="sans-serif" font-size="8" font-weight="600" fill="#059669" text-anchor="middle">100% Bit Parity</text>
<text x="470" y="90" font-family="sans-serif" font-size="7.5" font-weight="700" fill="#047857" text-anchor="middle">0 Byte Corruption</text>
<path d="M 540 67 L 565 67" stroke="#059669" stroke-width="2" />
<!-- Target Cloud -->
<rect x="570" y="25" width="95" height="85" fill="#ffffff" stroke="#cbd5e1" rx="4" />
<text x="617" y="45" font-family="sans-serif" font-size="9.5" font-weight="700" text-anchor="middle" fill="#0f172a">Cloud Target</text>
<text x="617" y="62" font-family="sans-serif" font-size="7.5" fill="#64748b" text-anchor="middle">AWS S3 / RDS</text>
<rect x="578" y="72" width="79" height="25" fill="#ecfdf5" stroke="#a7f3d0" rx="3" />
<text x="617" y="88" font-family="sans-serif" font-size="7.5" font-weight="700" text-anchor="middle" fill="#059669">MATCH: OK</text>
</svg>""",
        "steps_rows": """<tr>
<td><strong>Step 1</strong></td>
<td>Run <strong>6-Rs Decision Assessment</strong></td>
<td>Evaluates enterprise workload criteria (licensing, architecture, tech debt) to select Rehost, Replatform, or Refactor.</td>
</tr>
<tr>
<td><strong>Step 2</strong></td>
<td>Initiate <strong>Online Chunked Streaming</strong></td>
<td>Streams 50MB customer dataset across virtual network in 5MB encrypted chunks with real-time transfer progress.</td>
</tr>
<tr>
<td><strong>Step 3</strong></td>
<td>Calculate <strong>Source vs Target SHA-256</strong></td>
<td>Computes cryptographic hashes at both ends: <code>Source Hash == Target Hash</code> confirms 100% zero bit rot.</td>
</tr>
<tr>
<td><strong>Step 4</strong></td>
<td>Simulate <strong>Network Packet Corruption</strong></td>
<td>Flips 1 bit in transit; parity validator immediately detects hash mismatch, rejects bad block, and requests retransmit.</td>
</tr>
<tr>
<td><strong>Step 5</strong></td>
<td>Review <strong>TCO Cost Savings Calculator</strong></td>
<td>Compares on-prem hardware depreciation and electricity costs against elastic cloud pricing, demonstrating 42% ROI.</td>
</tr>""",
        "takeaway_lead": "Trust, but Mathematically Verify.",
        "takeaway_body": "Never assume a multi-terabyte data migration was successful just because the progress bar says 100%. SHA-256 cryptographic parity is the only acceptable proof of zero data corruption in mission-critical migrations.",
        "viva_boxes": """<div class="q-box">
<div class="q-title">Q1: Explain the difference between Rehosting and Refactoring in Gartner's 6-Rs.</div>
<div class="q-ans"><strong>Answer:</strong> <strong>Rehosting (Lift & Shift)</strong> moves apps to cloud VMs without architectural changes (fastest, lowest immediate effort). <strong>Refactoring</strong> rewrites applications to be cloud-native (microservices, serverless), delivering maximum long-term elasticity and lowest operational cost.</div>
</div>
<div class="q-box">
<div class="q-title">Q2: Why is SHA-256 hashing essential during large database migrations?</div>
<div class="q-ans"><strong>Answer:</strong> Network timeouts or disk driver glitches can flip random bits (silent data corruption). A SHA-256 hash guarantees that every single bit at the destination matches the source exactly.</div>
</div>
<div class="q-box">
<div class="q-title">Q3: What does the 'Retire' strategy mean in cloud rationalization?</div>
<div class="q-ans"><strong>Answer:</strong> Discovery audits often reveal that 10-20% of legacy enterprise servers run obsolete software that nobody uses. Retiring (turning them off) yields instant savings with zero migration effort.</div>
</div>"""
    },
    {
        "num": "12",
        "dir": "practical-12-serverless-lambda",
        "title": "Serverless Computing & Event-Driven FaaS",
        "subtitle": "Micro-VM Cold Starts (280ms) vs Warm (12ms) & Micro-Billing",
        "port": "8080",
        "memory": "~34 MiB",
        "what_is_it": """<p>In traditional cloud computing, you pay for virtual servers 24 hours a day, even when they sit completely idle with zero traffic. <strong>Serverless Computing (AWS Lambda / Cloud Functions)</strong> executes code strictly on demand in response to events.</p>
<p>When an event arrives, a lightweight micro-VM spins up in milliseconds, runs your function, and vanishes. You pay only for exact execution time down to the millisecond: <strong>Zero Traffic = Zero Cost</strong>.</p>""",
        "analogy_title": "🛴 The Electric Rental Scooter vs Car Lease",
        "layman_analogy": """<ul>
<li><strong>Virtual Machine (EC2):</strong> Leasing a car for $500/month. Even when parked in your garage while you sleep, you pay every single second.</li>
<li><strong>Serverless (Lambda):</strong> Renting an on-demand electric scooter on the street. You unlock it, ride for 45 seconds, pay $0.002, and walk away. When no one is riding, you pay exactly $0.00!</li>
<li><strong>Cold Start (280ms):</strong> The scooter was turned off. The system has to wake up the micro-VM, download your code, and warm the engine before the first ride.</li>
<li><strong>Warm Start (12ms):</strong> The scooter engine is still humming from the previous rider 5 seconds ago—instant acceleration!</li>
<li><strong>Micro-Billing:</strong> Paying $0.0000166667 per gigabyte-second of compute.</li>
</ul>""",
        "use_case": """<p><strong>Coca-Cola</strong> switched their global vending machine payment processing to AWS Lambda. 
Instead of paying millions for 24/7 idle servers, they only pay for the 200 milliseconds it takes to authorize a customer's credit card swipe.</p>""",
        "infographic_caption": "Serverless Event Lifecycle: Cold Start Micro-VM Boot vs Warm Container Reuse",
        "svg_infographic": """<svg width="100%" height="135" viewBox="0 0 680 135" xmlns="http://www.w3.org/2000/svg">
<rect width="680" height="135" fill="#f8fafc" rx="8" />
<rect x="25" y="35" width="100" height="70" fill="#ffffff" stroke="#cbd5e1" rx="4" />
<text x="75" y="55" font-family="sans-serif" font-size="9.5" font-weight="700" text-anchor="middle" fill="#0f172a">Event Trigger</text>
<text x="75" y="72" font-family="sans-serif" font-size="8" fill="#64748b" text-anchor="middle">HTTP / S3 Upload</text>
<text x="75" y="87" font-family="sans-serif" font-size="7.5" fill="#64748b" text-anchor="middle">Cron Timer</text>
<path d="M 130 70 L 165 70" stroke="#2563eb" stroke-width="2" />
<!-- Cold Start Path -->
<rect x="170" y="15" width="235" height="50" fill="#fee2e2" stroke="#fca5a5" rx="4" />
<text x="287" y="32" font-family="sans-serif" font-size="9" font-weight="700" text-anchor="middle" fill="#dc2626">Cold Start (~280ms Virtualization Tax)</text>
<text x="287" y="48" font-family="sans-serif" font-size="7.5" fill="#64748b" text-anchor="middle">1. Allocate Micro-VM  2. Init Runtime  3. Load Code</text>
<!-- Warm Start Path -->
<rect x="170" y="72" width="235" height="50" fill="#ecfdf5" stroke="#86efac" rx="4" />
<text x="287" y="89" font-family="sans-serif" font-size="9" font-weight="700" text-anchor="middle" fill="#047857">Warm Start (~12ms Instant Reuse)</text>
<text x="287" y="105" font-family="sans-serif" font-size="7.5" fill="#64748b" text-anchor="middle">Reuses already initialized container memory</text>
<path d="M 410 70 L 440 70" stroke="#059669" stroke-width="2" />
<!-- Micro-Billing Meter -->
<rect x="445" y="20" width="210" height="95" fill="#ffffff" stroke="#2563eb" stroke-width="1.5" rx="6" />
<text x="550" y="40" font-family="sans-serif" font-size="10" font-weight="700" text-anchor="middle" fill="#2563eb">Micro-Billing Engine</text>
<text x="550" y="60" font-family="sans-serif" font-size="8" fill="#64748b" text-anchor="middle">Duration: 42ms | Memory: 128MB</text>
<text x="550" y="80" font-family="sans-serif" font-size="11" font-weight="700" fill="#059669" text-anchor="middle">$0.00000084 billed</text>
<text x="550" y="100" font-family="sans-serif" font-size="7.5" fill="#64748b" text-anchor="middle">Idle Cost between events = $0.0000</text>
</svg>""",
        "steps_rows": """<tr>
<td><strong>Step 1</strong></td>
<td>Trigger <strong>Cold Invocation</strong> (POST /api/invoke)</td>
<td>Simulator spins up cold runtime, executes function, and logs total latency (280ms cold start + 14ms compute).</td>
</tr>
<tr>
<td><strong>Step 2</strong></td>
<td>Trigger Immediate <strong>Second Invocation</strong></td>
<td>Container reuse keeps memory warm; execution completes in <strong>12ms</strong> (a 95% latency reduction!).</td>
</tr>
<tr>
<td><strong>Step 3</strong></td>
<td>Simulate <strong>Concurrent Event Burst</strong> (50 events)</td>
<td>Serverless control plane instantly scales from 1 to 50 parallel isolated micro-VMs without manual provisioning.</td>
</tr>
<tr>
<td><strong>Step 4</strong></td>
<td>Inspect <strong>Micro-Billing Cost Calculator</strong></td>
<td>Calculates 1 million invocations at 128MB: total cloud bill is just <strong>$0.20</strong> vs $35/month for a 24/7 VM.</td>
</tr>""",
        "takeaway_lead": "The Greenest & Cheapest Server is the One That Doesn't Exist.",
        "takeaway_body": "Serverless shifts the entire infrastructure burden to the cloud provider. If nobody visits your website at 4:00 AM, you pay zero dollars and consume zero electricity.",
        "viva_boxes": """<div class="q-box">
<div class="q-title">Q1: What is a Serverless 'Cold Start' and what causes it?</div>
<div class="q-ans"><strong>Answer:</strong> When a function is called after being idle, the cloud provider must allocate hardware, initialize a micro-VM (e.g. AWS Firecracker), boot the language runtime (Node/Python), and load code, adding 100-400ms latency.</div>
</div>
<div class="q-box">
<div class="q-title">Q2: How does the Serverless billing model differ from traditional IaaS VMs?</div>
<div class="q-ans"><strong>Answer:</strong> IaaS bills per hour or second that a virtual machine is powered on, regardless of CPU utilization. Serverless bills strictly for the active execution duration in milliseconds multiplied by memory allocated.</div>
</div>
<div class="q-box">
<div class="q-title">Q3: When is Serverless NOT the right architectural choice?</div>
<div class="q-ans"><strong>Answer:</strong> For continuous, high-throughput steady-state workloads (e.g. video rendering 24/7 or low-latency high-frequency trading), running dedicated VMs or Kubernetes pods is significantly cheaper and avoids cold start spikes.</div>
</div>"""
    },
    {
        "num": "13",
        "dir": "practical-13-bigdata-analytics",
        "title": "Cloud Big Data: MapReduce vs Columnar",
        "subtitle": "Distributed Map/Shuffle/Reduce vs Vectorized SIMD Parquet Queries",
        "port": "8080",
        "memory": "~38 MiB",
        "what_is_it": """<p>Processing gigabytes or terabytes of cloud data row-by-row on a single machine is impossibly slow. <strong>MapReduce</strong> pioneered distributed computing by splitting large datasets across clusters using Map, Shuffle, and Reduce phases.</p>
<p>Modern analytical engines (Snowflake, BigQuery, ClickHouse) use <strong>Vectorized Columnar Storage (Apache Parquet)</strong>, reading only the necessary columns and applying CPU SIMD instructions to process millions of rows per second.</p>""",
        "analogy_title": "📚 Library Book Sorting vs Phonebook Lookup",
        "layman_analogy": """<ul>
<li><strong>Row-Oriented (CSV):</strong> Writing a phonebook as full sentences: <em>'John Doe lives at 123 Elm St and has phone 555-0192.'</em> If you just want to find all 555 area codes, you are forced to read every person's name and home address into RAM!</li>
<li><strong>Columnar (Parquet):</strong> Storing all names together, all addresses together, and all phone numbers together. To analyze phone numbers, your CPU reads ONLY the phone column, skipping 90% of the disk!</li>
<li><strong>MapReduce:</strong> Handing a 1,000-page book to 10 people (Map: count words on each page), passing index cards to a central table (Shuffle), and adding totals together (Reduce).</li>
<li><strong>SIMD Vectorization:</strong> Asking your CPU to do 8 math calculations in a single heartbeat instead of 1 by 1.</li>
</ul>""",
        "use_case": """<p><strong>Netflix</strong> analyzes billions of user viewing events every night to update recommendations. 
Switching from raw CSV to compressed Parquet columnar storage reduced their Amazon S3 storage footprint by 80% and accelerated query speeds by 20x.</p>""",
        "infographic_caption": "Row-Oriented CSV Layout vs Columnar Parquet Layout & SIMD Vector Processing",
        "svg_infographic": """<svg width="100%" height="135" viewBox="0 0 680 135" xmlns="http://www.w3.org/2000/svg">
<rect width="680" height="135" fill="#f8fafc" rx="8" />
<!-- Row Oriented -->
<rect x="25" y="15" width="300" height="105" fill="#ffffff" stroke="#cbd5e1" rx="6" />
<text x="175" y="32" font-family="sans-serif" font-size="10.5" font-weight="700" text-anchor="middle" fill="#dc2626">Row-Oriented Storage (CSV / MySQL)</text>
<rect x="35" y="42" width="280" height="20" fill="#fee2e2" stroke="#fca5a5" rx="3" /><text x="175" y="56" font-family="sans-serif" font-size="7.5" fill="#0f172a" text-anchor="middle">Row 1: ID=1 | Alice | US | Age=29 | Amount=$450</text>
<rect x="35" y="66" width="280" height="20" fill="#fee2e2" stroke="#fca5a5" rx="3" /><text x="175" y="80" font-family="sans-serif" font-size="7.5" fill="#0f172a" text-anchor="middle">Row 2: ID=2 | Bob   | UK | Age=34 | Amount=$120</text>
<text x="175" y="105" font-family="sans-serif" font-size="8" font-weight="600" fill="#dc2626" text-anchor="middle">Query: "SUM(Amount)" -> Must read ALL columns from disk!</text>
<!-- Columnar Oriented -->
<rect x="345" y="15" width="310" height="105" fill="#ffffff" stroke="#059669" stroke-width="1.5" rx="6" />
<text x="500" y="32" font-family="sans-serif" font-size="10.5" font-weight="700" text-anchor="middle" fill="#047857">Columnar Storage (Apache Parquet)</text>
<rect x="355" y="42" width="60" height="45" fill="#ecfdf5" stroke="#a7f3d0" rx="3" /><text x="385" y="58" font-family="sans-serif" font-size="7.5" font-weight="600" text-anchor="middle" fill="#065f46">Col: ID</text><text x="385" y="75" font-family="sans-serif" font-size="7" fill="#64748b" text-anchor="middle">[1, 2, 3]</text>
<rect x="420" y="42" width="65" height="45" fill="#ecfdf5" stroke="#a7f3d0" rx="3" /><text x="452" y="58" font-family="sans-serif" font-size="7.5" font-weight="600" text-anchor="middle" fill="#065f46">Col: Name</text><text x="452" y="75" font-family="sans-serif" font-size="7" fill="#64748b" text-anchor="middle">[Alice, Bob]</text>
<rect x="490" y="42" width="75" height="45" fill="#eff6ff" stroke="#bfdbfe" rx="3" /><text x="527" y="58" font-family="sans-serif" font-size="7.5" font-weight="700" text-anchor="middle" fill="#1d4ed8">Col: Amount</text><text x="527" y="75" font-family="sans-serif" font-size="8" font-weight="700" fill="#2563eb" text-anchor="middle">[$450, $120]</text>
<rect x="570" y="42" width="75" height="45" fill="#fef3c7" stroke="#fde68a" rx="3" /><text x="607" y="58" font-family="sans-serif" font-size="7.5" font-weight="700" text-anchor="middle" fill="#b45309">SIMD Vector</text><text x="607" y="75" font-family="sans-serif" font-size="7" fill="#b45309" text-anchor="middle">8 sums / cycle</text>
<text x="500" y="105" font-family="sans-serif" font-size="8" font-weight="700" fill="#059669" text-anchor="middle">Query: Reads ONLY "Amount" column -> 80% I/O skipped!</text>
</svg>""",
        "steps_rows": """<tr>
<td><strong>Step 1</strong></td>
<td>Generate <strong>100,000-Row Dataset</strong></td>
<td>Simulates an enterprise e-commerce transaction log with user IDs, timestamps, categories, and purchase amounts.</td>
</tr>
<tr>
<td><strong>Step 2</strong></td>
<td>Run <strong>MapReduce Pipeline</strong></td>
<td>Executes Map stage (extracting categories), Shuffle/Sort stage, and Reduce stage (summing revenue per category).</td>
</tr>
<tr>
<td><strong>Step 3</strong></td>
<td>Execute <strong>Vectorized Columnar Query</strong></td>
<td>Queries the same dataset stored in Parquet format; columnar engine skips 80% of unused columns and applies SIMD math.</td>
</tr>
<tr>
<td><strong>Step 4</strong></td>
<td>Compare <strong>Benchmark Metrics</strong></td>
<td>Observes <strong>8x faster execution</strong> and <strong>72% smaller disk footprint</strong> due to column dictionary encoding and Snappy compression.</td>
</tr>""",
        "takeaway_lead": "The Fastest I/O is the I/O You Never Read.",
        "takeaway_body": "By physically organizing data on disk in columns rather than rows, analytical databases skip 90% of file data, transforming queries that took 30 minutes into sub-second interactive answers.",
        "viva_boxes": """<div class="q-box">
<div class="q-title">Q1: Why is Columnar storage drastically faster than Row storage for analytical queries?</div>
<div class="q-ans"><strong>Answer:</strong> Analytical queries usually aggregate only 2-3 columns out of 50. Columnar storage reads strictly those 2 columns from disk, whereas row storage must read the entire table row into memory.</div>
</div>
<div class="q-box">
<div class="q-title">Q2: Describe the three core phases of the MapReduce paradigm.</div>
<div class="q-ans"><strong>Answer:</strong> 1. <strong>Map:</strong> Filters and transforms chunks of data into intermediate key-value pairs. 2. <strong>Shuffle & Sort:</strong> Groups all values sharing the same key together. 3. <strong>Reduce:</strong> Aggregates or computes final summaries per key.</div>
</div>
<div class="q-box">
<div class="q-title">Q3: Why does columnar data achieve much higher compression ratios?</div>
<div class="q-ans"><strong>Answer:</strong> All values in a column share the exact same data type (e.g. all integers or timestamps). Similar adjacent values compress extremely efficiently using Run-Length Encoding and Dictionary compression.</div>
</div>"""
    },
    {
        "num": "14",
        "dir": "practical-14-multicloud-terraform",
        "title": "Multi-Cloud Infrastructure as Code (Terraform)",
        "subtitle": "Declarative HCL Blueprints, DAG Dependency Resolution & State Drift",
        "port": "8080",
        "memory": "~35 MiB",
        "what_is_it": """<p>Configuring cloud resources by clicking buttons in web consoles is error-prone, unrepeatable, and dangerous. <strong>Infrastructure as Code (IaC)</strong> allows you to define your entire multi-cloud architecture (VPCs, VMs, Databases) in human-readable code files.</p>
<p><strong>HashiCorp Terraform</strong> reads declarative code, builds a <strong>Directed Acyclic Graph (DAG)</strong> to calculate dependency order, and maintains state in <code>terraform.tfstate</code>.</p>""",
        "analogy_title": "📐 The Architectural Blueprint & Lego Manual",
        "layman_analogy": """<ul>
<li><strong>ClickOps (Web Console):</strong> Building a house by hand without blueprints. You will forget what wire went where, make mistakes, and nobody can duplicate it.</li>
<li><strong>Terraform (IaC):</strong> A computerized 3D architectural blueprint (<code>main.tf</code>). You describe: <em>'I want 1 VPC, 2 Subnets, and 1 Database.'</em></li>
<li><strong>DAG Graph:</strong> Terraform analyzes your blueprint and figures out the build order automatically: you cannot plug in the toaster before building the wall outlet!</li>
<li><strong>State File (<code>.tfstate</code>):</strong> The single source of truth recording what exists in the physical cloud right now.</li>
<li><strong>State Drift:</strong> If an engineer logs into AWS at 2:00 AM and manually deletes a firewall rule, Terraform's next <code>plan</code> instantly detects the unauthorized change and alerts you!</li>
</ul>""",
        "use_case": """<p><strong>Airbnb</strong> provisions thousands of cloud instances across AWS and GCP using Terraform. 
When creating a complete staging environment for QA testing, Terraform spins up the entire global infrastructure in 8 minutes with zero human configuration errors.</p>""",
        "infographic_caption": "Terraform Infrastructure Lifecycle: Code -> DAG Graph -> State & Drift Engine",
        "svg_infographic": """<svg width="100%" height="135" viewBox="0 0 680 135" xmlns="http://www.w3.org/2000/svg">
<rect width="680" height="135" fill="#f8fafc" rx="8" />
<rect x="25" y="30" width="135" height="75" fill="#ffffff" stroke="#cbd5e1" rx="4" />
<text x="92" y="50" font-family="sans-serif" font-size="9.5" font-weight="700" text-anchor="middle" fill="#0f172a">1. Declarative Code</text>
<text x="92" y="68" font-family="sans-serif" font-size="8" fill="#64748b" text-anchor="middle">main.tf (HCL)</text>
<text x="92" y="82" font-family="sans-serif" font-size="7.5" fill="#2563eb" text-anchor="middle">resource "aws_vpc" {}</text>
<path d="M 165 67 L 195 67" stroke="#2563eb" stroke-width="2" />
<!-- DAG Graph -->
<rect x="200" y="20" width="145" height="95" fill="#eff6ff" stroke="#bfdbfe" rx="6" />
<text x="272" y="38" font-family="sans-serif" font-size="9.5" font-weight="700" text-anchor="middle" fill="#1d4ed8">2. DAG Graph Resolver</text>
<circle cx="235" cy="65" r="10" fill="#2563eb" /><text x="235" y="68" font-size="7" font-weight="700" fill="#fff" text-anchor="middle">VPC</text>
<path d="M 245 65 L 265 65" stroke="#2563eb" stroke-width="1.5" />
<circle cx="275" cy="65" r="10" fill="#2563eb" /><text x="275" y="68" font-size="6" font-weight="700" fill="#fff" text-anchor="middle">Subnet</text>
<path d="M 285 65 L 300 65" stroke="#2563eb" stroke-width="1.5" />
<circle cx="310" cy="65" r="10" fill="#059669" /><text x="310" y="68" font-size="7" font-weight="700" fill="#fff" text-anchor="middle">VM</text>
<text x="272" y="98" font-family="sans-serif" font-size="7.5" fill="#64748b" text-anchor="middle">Calculates Parallel Order</text>
<path d="M 350 67 L 380 67" stroke="#059669" stroke-width="2" />
<!-- Lifecycle -->
<rect x="385" y="20" width="130" height="95" fill="#f0fdf4" stroke="#86efac" rx="6" />
<text x="450" y="38" font-family="sans-serif" font-size="9" font-weight="700" text-anchor="middle" fill="#047857">3. Plan & Apply</text>
<text x="450" y="55" font-family="sans-serif" font-size="7.5" fill="#64748b" text-anchor="middle">Plan: +3 to add, ~0</text>
<text x="450" y="70" font-family="sans-serif" font-size="7.5" fill="#64748b" text-anchor="middle">Apply: Provisions Cloud</text>
<text x="450" y="90" font-family="sans-serif" font-size="8" font-weight="700" fill="#059669" text-anchor="middle">Multi-Cloud Ready</text>
<path d="M 520 67 L 545 67" stroke="#059669" stroke-width="2" />
<!-- State & Drift -->
<rect x="550" y="25" width="105" height="85" fill="#ffffff" stroke="#cbd5e1" rx="4" />
<text x="602" y="45" font-family="sans-serif" font-size="9" font-weight="700" text-anchor="middle" fill="#0f172a">State File</text>
<text x="602" y="60" font-family="sans-serif" font-size="7" fill="#64748b" text-anchor="middle">terraform.tfstate</text>
<rect x="558" y="72" width="88" height="25" fill="#fef2f2" stroke="#fca5a5" rx="3" />
<text x="602" y="88" font-family="sans-serif" font-size="7.5" font-weight="700" text-anchor="middle" fill="#dc2626">Drift Alert (0)</text>
</svg>""",
        "steps_rows": """<tr>
<td><strong>Step 1</strong></td>
<td>Inspect <strong>Declarative HCL File</strong></td>
<td>View <code>main.tf</code> declaring a VPC, public subnet, security group, and virtual compute instance.</td>
</tr>
<tr>
<td><strong>Step 2</strong></td>
<td>Run <code>terraform plan</code></td>
<td>Terraform builds the DAG dependency graph, compares state with cloud reality, and outputs: <code>Plan: 4 to add, 0 to change, 0 to destroy</code>.</td>
</tr>
<tr>
<td><strong>Step 3</strong></td>
<td>Run <code>terraform apply</code></td>
<td>Provisions resources in correct topological sequence and saves state mapping into <code>terraform.tfstate</code>.</td>
</tr>
<tr>
<td><strong>Step 4</strong></td>
<td>Inject <strong>Out-of-Band State Drift</strong></td>
<td>Simulates an admin deleting a firewall rule in the AWS console behind Terraform's back.</td>
</tr>
<tr>
<td><strong>Step 5</strong></td>
<td>Run <strong>Drift Detection Scan</strong></td>
<td>Terraform flags deviation immediately and proposes automated remediation to bring cloud reality back to code.</td>
</tr>""",
        "takeaway_lead": "Code is the Single Source of Truth.",
        "takeaway_body": "If infrastructure is not committed to Git in code, it does not exist. Infrastructure as Code turns cloud setups into version-controlled, testable, and completely reproducible software artifacts.",
        "viva_boxes": """<div class="q-box">
<div class="q-title">Q1: What is the purpose of the Terraform State File (<code>terraform.tfstate</code>)?</div>
<div class="q-ans"><strong>Answer:</strong> It maps your code configuration to real-world cloud resource IDs and attributes. Without state, Terraform cannot know what was already provisioned or calculate what needs updating.</div>
</div>
<div class="q-box">
<div class="q-title">Q2: How does Terraform use a Directed Acyclic Graph (DAG)?</div>
<div class="q-ans"><strong>Answer:</strong> It maps resource dependencies (e.g. Subnet depends on VPC; VM depends on Subnet). Resources with no mutual dependencies are automatically created in parallel to maximize deployment speed.</div>
</div>
<div class="q-box">
<div class="q-title">Q3: What is 'State Drift' and how do you remediate it?</div>
<div class="q-ans"><strong>Answer:</strong> State drift occurs when someone alters cloud resources manually outside Terraform. Running <code>terraform plan</code> detects the drift, and <code>terraform apply</code> reconciles reality back to the code.</div>
</div>"""
    },
    {
        "num": "15",
        "dir": "practical-15-edge-computing-mqtt",
        "title": "Edge Computing & IoT Telemetry Broker",
        "subtitle": "Mosquitto MQTT Pub/Sub & 85% Bandwidth Reduction Edge Filtering",
        "port": "8080",
        "memory": "~37 MiB",
        "what_is_it": """<p>Connecting millions of industrial sensors directly to distant cloud datacenters causes high network latency, expensive internet bandwidth bills, and fatal delays during emergencies. <strong>Edge Computing</strong> processes and filters data physically near where it is generated.</p>
<p>Using the lightweight <strong>MQTT (Message Queuing Telemetry Transport)</strong> protocol, local edge gateways filter out 85% of repetitive baseline noise and forward only critical anomalies to the cloud.</p>""",
        "analogy_title": "🏭 The Smart Factory Sensor & Emergency Brake",
        "layman_analogy": """<ul>
<li><strong>Cloud-Only IoT:</strong> A factory motor sends 1,000 temperature readings every second across the internet to an AWS datacenter 2,000 miles away. If the internet Wi-Fi blips for 2 seconds, the motor overheats and explodes before the cloud can respond!</li>
<li><strong>Edge Computing:</strong> A small computer (Raspberry Pi or Edge Gateway) sits physically bolted next to the motor. It evaluates readings locally in 1 millisecond.</li>
<li><strong>Edge Filtering:</strong> Normal reading (70°C) is discarded locally. Only when temperature hits 95°C does it instantly trigger emergency brakes and alert the cloud!</li>
<li><strong>MQTT vs HTTP:</strong> HTTP headers are heavy (~1,000 bytes per request). MQTT packet headers are tiny (just 2 bytes), making it ideal for battery-powered sensors.</li>
</ul>""",
        "use_case": """<p><strong>Tesla Autopilot</strong> and <strong>Boeing Aircraft</strong> use edge computing. 
An autonomous car cannot wait for a 4G cell tower connection to a cloud server to decide whether to hit the brakes for a pedestrian—it must make life-or-death decisions locally at the edge in 2 milliseconds.</p>""",
        "infographic_caption": "Edge Gateway Anomaly Filter & Mosquitto MQTT Broker Telemetry Stream",
        "svg_infographic": """<svg width="100%" height="135" viewBox="0 0 680 135" xmlns="http://www.w3.org/2000/svg">
<rect width="680" height="135" fill="#f8fafc" rx="8" />
<rect x="25" y="25" width="130" height="85" fill="#ffffff" stroke="#cbd5e1" rx="4" />
<text x="90" y="45" font-family="sans-serif" font-size="9.5" font-weight="700" text-anchor="middle" fill="#0f172a">IoT Sensor Fleet</text>
<text x="90" y="62" font-family="sans-serif" font-size="7.5" fill="#64748b" text-anchor="middle">Temp / Vibration</text>
<text x="90" y="78" font-family="sans-serif" font-size="8" font-weight="600" fill="#dc2626" text-anchor="middle">100 msgs / sec</text>
<text x="90" y="94" font-family="sans-serif" font-size="7" fill="#64748b" text-anchor="middle">Raw Telemetry</text>
<path d="M 160 67 L 190 67" stroke="#2563eb" stroke-width="2" />
<!-- MQTT Broker -->
<rect x="195" y="20" width="145" height="95" fill="#eff6ff" stroke="#bfdbfe" rx="6" />
<text x="267" y="38" font-family="sans-serif" font-size="9" font-weight="700" text-anchor="middle" fill="#1d4ed8">Eclipse Mosquitto</text>
<text x="267" y="55" font-family="sans-serif" font-size="8" fill="#64748b" text-anchor="middle">MQTT Broker (Port 1883)</text>
<text x="267" y="70" font-family="sans-serif" font-size="7.5" fill="#64748b" text-anchor="middle">Topic: sensors/telemetry</text>
<text x="267" y="90" font-family="sans-serif" font-size="8" font-weight="600" fill="#2563eb" text-anchor="middle">Pub/Sub • QoS 1</text>
<path d="M 345 67 L 375 67" stroke="#059669" stroke-width="2" />
<!-- Edge Gateway -->
<rect x="380" y="20" width="145" height="95" fill="#f0fdf4" stroke="#86efac" rx="6" />
<text x="452" y="38" font-family="sans-serif" font-size="9" font-weight="700" text-anchor="middle" fill="#047857">Local Edge Gateway</text>
<text x="452" y="55" font-family="sans-serif" font-size="7.5" fill="#64748b" text-anchor="middle">Local Anomaly Filter</text>
<text x="452" y="72" font-family="sans-serif" font-size="8" font-weight="700" fill="#059669" text-anchor="middle">85% Bandwidth Saved!</text>
<text x="452" y="92" font-family="sans-serif" font-size="7.5" fill="#64748b" text-anchor="middle">Discards steady 70°C noise</text>
<path d="M 530 67 L 555 67" stroke="#dc2626" stroke-width="2" />
<!-- Cloud Ingestion -->
<rect x="560" y="25" width="95" height="85" fill="#ffffff" stroke="#cbd5e1" rx="4" />
<text x="607" y="45" font-family="sans-serif" font-size="9" font-weight="700" text-anchor="middle" fill="#0f172a">Cloud Tier</text>
<text x="607" y="62" font-family="sans-serif" font-size="7" fill="#64748b" text-anchor="middle">AWS IoT Core</text>
<rect x="568" y="72" width="79" height="25" fill="#fef2f2" stroke="#fca5a5" rx="3" />
<text x="607" y="88" font-family="sans-serif" font-size="7.5" font-weight="700" text-anchor="middle" fill="#dc2626">Anomalies Only</text>
</svg>""",
        "steps_rows": """<tr>
<td><strong>Step 1</strong></td>
<td>Connect to <strong>Mosquitto MQTT Broker</strong></td>
<td>Simulated edge sensors establish persistent TCP sockets to Mosquitto broker on port 1883.</td>
</tr>
<tr>
<td><strong>Step 2</strong></td>
<td>Stream <strong>Raw Sensor Telemetry</strong></td>
<td>Sensors publish temperature readings every 100ms. In Cloud-Only mode, observe high network bandwidth consumption.</td>
</tr>
<tr>
<td><strong>Step 3</strong></td>
<td>Toggle <strong>Edge Anomaly Filter</strong></td>
<td>Activates local filtering algorithm: steady 70°C readings are acknowledged and discarded at the edge gateway.</td>
</tr>
<tr>
<td><strong>Step 4</strong></td>
<td>Observe <strong>85% Bandwidth Reduction</strong></td>
<td>Real-time telemetry meter proves that only 15% of packets are transmitted to cloud storage, slashing cellular bandwidth bills.</td>
</tr>
<tr>
<td><strong>Step 5</strong></td>
<td>Inject <strong>Critical Overheat Anomaly</strong> (98°C)</td>
<td>Edge gateway immediately detects threshold violation and triggers instantaneous cloud alert in &lt; 2 milliseconds.</td>
</tr>""",
        "takeaway_lead": "Process Locally, Aggregate Globally.",
        "takeaway_body": "Not all data belongs in the cloud. Edge computing filters high-frequency noise at the physical source, ensuring instant millisecond emergency response and saving millions in cellular bandwidth costs.",
        "viva_boxes": """<div class="q-box">
<div class="q-title">Q1: Why is MQTT preferred over HTTP for IoT edge communication?</div>
<div class="q-ans"><strong>Answer:</strong> MQTT has tiny 2-byte header overhead (vs ~1KB in HTTP), maintains lightweight persistent connections, and uses an asynchronous pub/sub model ideal for low-bandwidth, battery-powered sensors.</div>
</div>
<div class="q-box">
<div class="q-title">Q2: What is the primary benefit of Edge Computing over pure Cloud Computing?</div>
<div class="q-ans"><strong>Answer:</strong> Drastically reduced latency (sub-millisecond local processing), massive network bandwidth savings (filtering repetitive noise before transit), and offline operational continuity during internet outages.</div>
</div>
<div class="q-box">
<div class="q-title">Q3: Explain MQTT Quality of Service (QoS) levels 0, 1, and 2.</div>
<div class="q-ans"><strong>Answer:</strong> <strong>QoS 0:</strong> At most once (fire and forget, no ack). <strong>QoS 1:</strong> At least once (guaranteed delivery with ack, possible duplicates). <strong>QoS 2:</strong> Exactly once (four-step handshake, zero duplicates).</div>
</div>"""
    }
])

print(f"Total practicals defined: {len(PRACTICALS)}")
