#!/bin/bash
set -e

echo "========================================"
echo " SOCKS5 Cluster Host Preparation"
echo "========================================"

echo "[STEP 1] Installing system packages..."
apt update
apt install -y \
  apt-transport-https \
  ca-certificates \
  curl \
  software-properties-common \
  gnupg \
  lsb-release \
  net-tools \
  htop \
  git

echo "[STEP 2] Installing Docker..."

curl -fsSL https://download.docker.com/linux/ubuntu/gpg | gpg --dearmor -o /usr/share/keyrings/docker-archive-keyring.gpg

echo \
"deb [arch=$(dpkg --print-architecture) signed-by=/usr/share/keyrings/docker-archive-keyring.gpg] \
https://download.docker.com/linux/ubuntu \
$(lsb_release -cs) stable" \
> /etc/apt/sources.list.d/docker.list

apt update
apt install -y docker-ce docker-ce-cli containerd.io

systemctl enable docker
systemctl start docker

echo "[STEP 3] Applying system tuning..."

cat >> /etc/sysctl.conf <<EOF

# SOCKS5 cluster tuning
net.core.somaxconn=4096
net.ipv4.tcp_tw_reuse=1
net.ipv4.ip_local_port_range=1024 65535
fs.file-max=2097152
kernel.pid_max=65536
EOF

sysctl -p

echo "[STEP 4] Setting file descriptor limits..."

cat > /etc/security/limits.d/99-nofile.conf <<EOF
* soft nofile 1048576
* hard nofile 1048576
* soft nproc 65535
* hard nproc 65535
EOF

echo "[STEP 5] Checking memory and adding swap if needed..."

TOTAL_MEM=$(grep MemTotal /proc/meminfo | awk '{print $2}')

if [ "$TOTAL_MEM" -lt 2500000 ]; then
    echo "[INFO] Low RAM detected. Adding 1GB swap..."
    fallocate -l 1G /swapfile || dd if=/dev/zero of=/swapfile bs=1M count=1024
    chmod 600 /swapfile
    mkswap /swapfile
    swapon /swapfile
    echo '/swapfile none swap sw 0 0' >> /etc/fstab
fi

echo "[DONE] Host preparation completed."