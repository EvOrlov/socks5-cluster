# SOCKS5 Cluster  
Resource-Aware, Cheap VPS Friendly

A lightweight SOCKS5 proxy cluster designed to run even on a low-cost VPS (2 vCPU + 2GB RAM).

---

## 🚀 Quick Start (New VPS Users)

### 1️⃣ Connect to your VPS

If your SSH port is default (22):

```bash
ssh root@YOUR_SERVER_IP
```

If your provider uses a custom SSH port (example: 2222):

```bash
ssh root@YOUR_SERVER_IP -p 2222
```

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
bash bootstrap.sh
```

### 6️⃣ Deploy cluster

```bash
bash deploy.sh
```

Time to drink a coffee ☕


### 📦 What You Get

12 containers  
250 proxies per container  
3000 authenticated SOCKS5 proxies

Exported to:

> output/proxies.txt

Exported to:

> output/proxies.txt

Format:

> IP:PORT:USERNAME:PASSWORD

### ⚙ Configuration

All parameters are inside:

> cluster.env

Example for smaller VPS:

> CONTAINER_COUNT=6  
> PROXIES_PER_CONTAINER=200

### 🧠 Architecture Decisions

- Uses --network host

- Sequential container startup

- Strict per-container resource limits

- Multi-source IP verification

- Safe redeploy cleanup

### ⚠ Disclaimer

For educational and infrastructure testing purposes only.
Ensure compliance with your hosting provider’s policies.