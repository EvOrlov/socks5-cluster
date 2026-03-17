![Ubuntu](https://img.shields.io/badge/Ubuntu-20.04%2B-orange)
![Python](https://img.shields.io/badge/Python-3.x-blue)
![Docker](https://img.shields.io/badge/Docker-required-blue)
![License](https://img.shields.io/badge/License-MIT-green)
![Status](https://img.shields.io/badge/status-stable-brightgreen)

# SOCKS5 Cluster  
#### Resource-Aware • Cheap VPS Friendly
Deploy up to **3000 authenticated SOCKS5 proxies** on a low-cost VPS in **under 3 minutes**.

**Fully automated, reproducible, and optimized** for minimal resources.

A lightweight SOCKS5 proxy cluster designed to run on a **low-cost VPS (2 vCPU + 2GB RAM)**.

**Simple**: the project uses the Python version already included in Ubuntu. **No additional packages are required!**  

&nbsp;

---

## 💡 Why This Project

- Designed for **low-cost VPS (2 vCPU / 2GB RAM)**
- No Kubernetes or orchestration overhead
- Fully reproducible deployment
- Minimal dependencies
- Fast setup (~3 minutes)
- Resource-aware architecture

&nbsp;

---

## ⚡ Performance

- 3000 SOCKS5 proxies deployed
- ~2–3 minutes setup time
- 100% success rate (internal verification)
- ~125 requests/sec under load
- tested with up to 500 concurrent users

See full test results: [tests/performance.md](tests/performance.md)

&nbsp;

---


## 🧾 Requirements

- Ubuntu 20.04+ / 22.04+
- Public IPv4 address
- No NAT / shared IP (dedicated public IP required)
- Root access
- ~2GB RAM recommended

&nbsp;

---


## 📁 Project Structure (important files)

__socks5-cluster__  
│  
├── cluster.env  
├── Dockerfile  
├── entrypoint.sh  
├── generate_proxies.py  
├── prepare_dante_host.sh  
├── all_proxies_ip_port.txt **generated after deploy**  
├── all_proxies_user_pass.txt **generated after deploy**

&nbsp;

---


## 🚀 Quick Start (Fresh VPS)
These steps assume a **clean Ubuntu 20.04+ / 22.04+ server**.  
Deployment usually takes about 2–3 minutes on a typical VPS.

### One-Line Deploy

```bash
apt update && apt install -y git && \
git clone https://github.com/EvOrlov/socks5-cluster.git && \
cd socks5-cluster && \
bash prepare_dante_host.sh && \
python3 generate_proxies.py
```

### Or Step-By-Step Deploy:

### 1️⃣ Connect to your VPS

If your SSH port is default (22):

```bash
ssh root@YOUR_SERVER_IP
```

If your provider uses a custom SSH port (example: 2222):

```bash
ssh root@YOUR_SERVER_IP -p 2222
```
Please ensure that your VPS has a real public IP address provided by your hosting provider. 

### 2️⃣ Update system

```bash
apt update && apt upgrade -y
```

### 3️⃣ Install Git

```bash
apt install git -y
```

### 4️⃣ Clone repository

```bash
git clone https://github.com/EvOrlov/socks5-cluster.git
cd socks5-cluster
```

### 5️⃣ Prepare server (run once)

```bash
bash prepare_dante_host.sh
```

### 6️⃣ Deploy cluster

```bash
python3 generate_proxies.py
```

Deployment completes automatically. Proxy list will be generated at the end. You will be informed about all checks and system resources.

&nbsp;

---


## 📦 What You Get by Default

12 containers  
250 proxies per container  
3000 authenticated SOCKS5 proxies

All new proxies for convenience will be exported to:

> all_proxies_ip_port.txt  
> all_proxies_user_pass.txt


Formats:

> IP:PORT:USERNAME:PASSWORD  
> 185.23.18.136:1080:user_xxx:pass_xxx 
> 
> USERNAME:PASSWORD@IP:PORT  
> user_xxx:pass_xxx@185.23.18.136:1080

Both files contain the same proxies, just in different formats for convenience.  


&nbsp;

---


## ⚙ Configuration

All parameters are inside:

> cluster.env

Example for smaller VPS:

> CONTAINER_COUNT=6  
> PROXIES_PER_CONTAINER=200

You can modify other parameters as needed, but it is recommended to deploy the default configuration first.  
**Each new deployment automatically removes previous containers and output files, then creates a fresh proxy cluster.**

&nbsp;

---


## 🧠 Architecture Decisions
Key design decisions:

- Docker containers isolate proxy batches

- Host network mode for minimal latency

- Sequential container startup for stability

- Resource limits per container

- Multi-source IP verification during deployment

- Automatic cleanup before redeploy

Each container runs the Dante SOCKS5 server and hosts multiple proxy ports.

&nbsp;

---


## 📊 Example Resource Usage

Example resource usage after deployment on a **2GB RAM VPS**:
```
Containers    : 12  
Total proxies : 3000

System status after cluster startup:

Memory usage:
524MB used
1.2GB available

Container RAM usage:
~6MB – 10MB per container
```

The server retains significant resource headroom even with thousands of open proxy ports.

&nbsp;

---


## 🔁 Redeploy

To rebuild the cluster:

```bash
python3 generate_proxies.py
```

The script automatically:

• removes old containers
• rebuilds proxy containers
• verifies proxy availability

&nbsp;

---

## 🎯 Use Cases

- Load testing
- Web scraping infrastructure
- Proxy pool generation
- QA and network testing

&nbsp;

---

## ⚠ Limitations

- Some websites may block proxy traffic (bot protection)
- Not intended for bypassing anti-abuse systems
- Performance depends on VPS network quality

&nbsp;

---


## ⚠ Disclaimer

This project is intended for educational and infrastructure testing purposes.

Always ensure compliance with your hosting provider’s policies.

