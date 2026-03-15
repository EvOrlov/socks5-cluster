#!/bin/bash

set -e

echo "[*] Installing system packages and Docker..."

apt update && apt install -y \
  apt-transport-https \
  ca-certificates \
  curl \
  software-properties-common \
  gnupg \
  lsb-release \
  net-tools \
  htop \
  unzip \
  wget

# Add Docker repository
curl -fsSL https://download.docker.com/linux/ubuntu/gpg | gpg --dearmor -o /usr/share/keyrings/docker-archive-keyring.gpg

echo \
  "deb [arch=$(dpkg --print-architecture) signed-by=/usr/share/keyrings/docker-archive-keyring.gpg] \
  https://download.docker.com/linux/ubuntu \
  $(lsb_release -cs) stable" > /etc/apt/sources.list.d/docker.list

# Install Docker
apt update
apt install -y docker-ce docker-ce-cli containerd.io

systemctl enable docker
systemctl start docker

echo "[*] Docker installed successfully."

# ---------- DOCKER SETTINGS ----------

echo "[*] Configuring /etc/docker/daemon.json..."

mkdir -p /etc/docker

cat > /etc/docker/daemon.json <<EOF
{
  "default-ulimits": {
    "nofile": {
      "Name": "nofile",
      "Hard": 65535,
      "Soft": 65535
    }
  },
  "dns": ["8.8.8.8"],
  "userland-proxy": false,
  "storage-driver": "overlay2",
  "live-restore": true,
  "max-concurrent-downloads": 2
}
EOF

echo "[*] Restarting Docker with new parameters..."
systemctl restart docker

# ---------- SYSTEM TUNING ----------

echo "[*] Applying system limits and network parameters..."

cat >> /etc/sysctl.conf <<EOF

# Dante proxy tuning
net.core.somaxconn=4096
net.core.netdev_max_backlog=65535
net.ipv4.tcp_max_syn_backlog=8192
net.ipv4.tcp_tw_reuse=1
net.ipv4.tcp_fin_timeout=15
net.ipv4.ip_local_port_range=1024 65535
fs.file-max=2097152
kernel.pid_max=65536
EOF

sysctl -p

# PAM-level limits
cat > /etc/security/limits.d/99-nofile.conf <<EOF
* soft nofile 1048576
* hard nofile 1048576
* soft nproc 65535
* hard nproc 65535
EOF

# For interactive sessions
echo "ulimit -n 1048576" >> /etc/profile

# ---------- SWAP (if RAM < 2.5 GB) ----------

total_mem=$(grep MemTotal /proc/meminfo | awk '{print $2}')
if [ "$total_mem" -lt 2500000 ]; then
    echo "[*] Low RAM detected — adding 1GB swap..."
    fallocate -l 1G /swapfile || dd if=/dev/zero of=/swapfile bs=1M count=1024
    chmod 600 /swapfile
    mkswap /swapfile
    swapon /swapfile
    echo '/swapfile none swap sw 0 0' >> /etc/fstab
fi

echo "[*] Checking Docker and swap status:"
docker info | grep -i "driver"
free -m

echo "[*] Host preparation completed successfully."