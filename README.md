
PROJECT KGOSI_VIEW:ENGINEERING DOCUMENTATION

Architect: Lehlohonolo Bokgosi Letebele
Project Type: Distributed Private Cloud & Financial Analytics Cluster
Status: Production (v18 Stable)

1. EXECUTIVE SUMMARY

Objective: To architect a private, offline-capable, distributed cloud cluster for algorithmic financial backtesting without reliance on commercial cloud providers or paid data feeds.

Solution: Engineered a 3-node on-premise cluster utilizing KVM virtualization for compute, NFS for decoupled storage, and a custom Python ETL pipeline to harvest and normalize 15 years of institutional tick data. The system features a custom frontend ("Kgosi_View") mimicking professional trading software behavior.

Key Achievement: Successfully processed over 50GB of raw financial data into a "Single Source of Truth" warehouse, accessible via a high-performance compute node, entirely on repurposed legacy hardware.

2. INFRASTRUCTURE ARCHITECTURE (The Physical Layer)
2.1 Hardware Inventory (The Cluster)

The system is built on a "Scavenger Architecture" philosophy—maximizing performance from disparate, legacy hardware.

Node A (Storage Core): HP "Zombie" Laptop

State: Headless (Broken screen/keyboard ).

OS: Rocky Linux 9 (RHEL derivative) Minimal.

Role: NFS Storage Server, Database Host, KVM Hypervisor (L0).

Storage: 500GB External Seagate SSD (Partitioned Hybrid: Ext4/NTFS).

Network: Gigabit Ethernet (Static IP).

Node B (Compute Unit): Lenovo T540p

OS: Linux Mint (Host) running KVM.

Virtualization: Hosts the worker-vm1 (Nested Rocky Linux 9 VM).

Role: Heavy Computation (Data crunching), App Hosting, Harvester Execution.

Network: Wi-Fi / Ethernet Bridging.

Node C (Command Center): Lenovo T560

OS: Debian 12.

Role: Administration Console, IDE (VS Code Remote), SSH Client, Frontend Display.

3. NETWORK TOPOLOGY (The Connectivity Layer)
3.1 Addressing Strategy

To ensure resilience against router reboots and roaming devices, a hybrid addressing scheme was implemented:

HP Zombie (Server): Hardcoded Static IP (10.0.0.106) configured via nmtui to ensure NFS mount stability.

T540p (Compute): Configured with NetworkManager Profiles.

Profile "Home_Static": Forces static IP when connected to Home SSID.

Profile "Roaming": Reverts to DHCP when detecting University/Public Wi-Fi.

3.2 Access & Security

Bastion Host Logic: The worker-vm1 is isolated on a virtual network (192.168.122.x). Access is granted via SSH ProxyJump through the T540p Host.

Authentication: Password authentication Disabled. Access restricted to Ed25519 SSH Keys with passphrase protection.

Firewall: firewalld configured with strict zones.

Public Zone: Allow SSH (22), Streamlit (8501).

Internal Zone: Allow NFS (2049), RPC-Bind (111).


4. STORAGE ENGINEERING (The Persistence Layer)
4.1 The "Hybrid Drive" Solution

A single physical 1TB drive was engineered to serve multiple tenants:

Partition 1 (/dev/sdb1 - NTFS): "Shared_Storage" for Windows interoperability (Family use).

Partition 2 (/dev/sdb2 - Ext4): "Kgosi_Lab" for Linux permissions, KVM images, and Financial Data.

4.2 Network Attached Storage (NFS) Implementation

To decouple Compute from Storage (Cloud Native Principle), the data does not live on the VM.


Server Config (/etc/exports):

/srv/nfs/army_data *(rw,sync,no_root_squash,insecure)

(Note: The insecure flag was critical to allow connections from NAT'd VMs using high source ports).


Client Config (/etc/fstab):

10.0.0.106:/srv/nfs/army_data  /mnt/kgosi_view_data  nfs  defaults  0  0

Outcome: The Worker VM2(T560) perceives a local 500GB drive, allowing for seamless reading/writing of massive datasets without local storage constraints.



5. DATA PIPELINE ENGINEERING (The ETL Layer)
5.1 The "Atomic Data" Strategy

Philosophy: Store data at the highest possible granularity (1-Minute Tick Data) to allow mathematical reconstruction of any timeframe (4H, Daily, Weekly) without data loss or "weekend gaps."

Source of Truth: All data is stored as SYMBOL_1M.csv (e.g., EURUSD_1M.csv).

Timezone Normalization: All timestamps are converted to UTC and stripped of timezone offsets to prevent Pandas comparison errors.

5.2 The Harvester Evolution

The data acquisition system evolved through three iterations to overcome API limits and anti-bot defenses:

The Yahoo Attempt (v1): Failed due to request throttling and lack of deep history (limited to 7 days of 1M data).

The Dukascopy Node (v2): Utilized a Node.js wrapper. Failed due to high latency causing timeouts on the multi-threaded download connection.

The "Nuclear" Scraper (v3 - Final):

Target: HistData.com (Repository of 10+ years of tick data).

Method: A custom Python requests script mimicking a human browser user-agent.

Mechanism: Direct HTTP POST requests to retrieval endpoints, downloading ZIP archives year-by-year.

Resilience: Implemented subprocess calls to bypass Python library limitations.

5.3 The Refinery (Data Transformation)

Raw data arrives as yearly ZIP archives containing messy ASCII text files. The Refinery Script (process_raw_v3.py) automates the cleanup:

Recursion: Hunts down .zip or .csv files in nested subdirectories.

Grouping: Identifies assets (e.g., merging 2010.zip, 2011.zip ... 2024.zip for EURUSD).

Cleaning: Parses custom date formats (YYYYMMDD HHMMSS), removes delimiters, and sorts chronologically.

Serialization: Writes a single, optimized CSV to the NFS share.



6. SOFTWARE ARCHITECTURE (Kgosi_View App)

Application: Kgosi_View (v20)
Framework: Streamlit (Python) + Plotly.js (Visualization).

6.1 Core Features

The Time Machine: A "Replay" mode that slices the Pandas DataFrame to hide future data, simulating real-time market conditions.

Hybrid Rendering: Utilizes @st.fragment (Partial Re-rendering) to update the chart in milliseconds without reloading the entire web page, preventing "scroll jumping."

TradingView UX: Custom CSS injection overrides Streamlit's default styling to enforce a "Dark Mode" financial terminal aesthetic (Top Toolbar, Bottom Playback Deck, Right-side Control Panel).

Multi-Axis Overlays: A dynamic loop that assigns independent Y-Axes to overlay assets (e.g., Bitcoin vs. Gold), allowing for correlation analysis without scaling distortion.

6.2 State Management

The application uses a persistent session_state engine to track:

Virtual Wallet: Balance, Equity, and PnL.

Trade Log: A JSON-based journal (trades.json) that persists across reboots.

Cursor Position: The current point in time for the simulation.

7. DEVOPS & AUTOMATION
7.1 Infrastructure as Code (Ansible)

Playbook: worker_setup.yml
Inventory: inventory.ini
Instead of manual configuration, the Worker VM is provisioned via Ansible. The playbook automates:

Package Management: Installing Git, Python3, and NFS Utils.

Environment: Upgrading pip and installing Financial libraries (Pandas, Yfinance).

Connectivity: Configuring firewalld to open Port 8501 (Streamlit).

Storage: creating the Mount Point and binding the NFS share.

7.2 Service Orchestration (Systemd)

The application runs as a background daemon, ensuring high availability.

Unit File: /etc/systemd/system/kgosi_view.service

Configuration:

Restart=always (Self-healing if it crashes).

--server.runOnSave true (Enables Hot-Reloading for VS Code development).

User=moeletsi (Runs as unprivileged user for security).


7.3 Version Control (Git)

Repo: Kgosi_View_Financial_Engine

Workflow: Code is edited on the T560 via VS Code Remote SSH, saved directly to the VM, and pushed to GitHub via SSH Deploy Keys.

Safety: .gitignore policies explicitly block the 50GB data/ folder to prevent leaking proprietary datasets.

8. FUTURE ROADMAP (2026+)

iSCSI Storage SAN: Move from File-Level (NFS) to Block-Level (iSCSI) storage to support Steam Library streaming for the "Gaming Node."

Containerization: Containerize app.py into a Docker Image for portability across any Linux server.

Observability: Deploy Prometheus & Grafana to monitor cluster health (CPU Temp, Disk Usage) alongside financial metrics.

End of Master Documentation.
Verified System Architecture for Project Kgosi_View.