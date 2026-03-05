#!/bin/bash

set -e

echo "[*] Установка системных пакетов и Docker..."

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

# Добавление репозитория Docker
curl -fsSL https://download.docker.com/linux/ubuntu/gpg | gpg --dearmor -o /usr/share/keyrings/docker-archive-keyring.gpg

echo \
  "deb [arch=$(dpkg --print-architecture) signed-by=/usr/share/keyrings/docker-archive-keyring.gpg] \
  https://download.docker.com/linux/ubuntu \
  $(lsb_release -cs) stable" > /etc/apt/sources.list.d/docker.list

# Установка Docker
apt update
apt install -y docker-ce docker-ce-cli containerd.io

systemctl enable docker
systemctl start docker

echo "[*] Docker установлен."

# ---------- НАСТРОЙКА DOCKER ----------

echo "[*] Настройка /etc/docker/daemon.json..."

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

echo "[*] Перезапуск Docker с новыми параметрами..."
systemctl restart docker

# ---------- НАСТРОЙКИ СИСТЕМЫ ----------

echo "[*] Применение системных лимитов и сетевых параметров..."

cat >> /etc/sysctl.conf <<EOF

# Dante proxy tuning
net.core.somaxconn=4096
net.ipv4.tcp_tw_reuse=1
net.ipv4.ip_local_port_range=1024 65535
fs.file-max=2097152
kernel.pid_max=65536
EOF

sysctl -p

# Ограничения на уровне PAM
cat > /etc/security/limits.d/99-nofile.conf <<EOF
* soft nofile 1048576
* hard nofile 1048576
* soft nproc 65535
* hard nproc 65535
EOF

# Для интерактивных сессий
echo "ulimit -n 1048576" >> /etc/profile

# ---------- SWAP (если RAM < 2.5 ГБ) ----------

total_mem=$(grep MemTotal /proc/meminfo | awk '{print $2}')
if [ "$total_mem" -lt 2500000 ]; then
    echo "[*] Мало оперативной памяти — добавляю swap (1 ГБ)..."
    fallocate -l 1G /swapfile || dd if=/dev/zero of=/swapfile bs=1M count=1024
    chmod 600 /swapfile
    mkswap /swapfile
    swapon /swapfile
    echo '/swapfile none swap sw 0 0' >> /etc/fstab
fi

echo "[*] Проверка статуса Docker и swap:"
docker info | grep -i "driver"
free -m

echo "[*] Подготовка хоста завершена успешно."
