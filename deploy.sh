#!/bin/bash

set -e

echo "========================================"
echo " SOCKS5 Cluster Deployment"
echo "========================================"

if [ ! -f cluster.env ]; then
echo "cluster.env not found"
exit 1
fi

export $(grep -v '^#' cluster.env | xargs)

echo "[INFO] Loading configuration..."

PUBLIC_IP=$(curl -s https://api.ipify.org)

echo "[HOST] Public IP detected: $PUBLIC_IP"

echo "[CONFIG] Containers: $CONTAINER_COUNT"
echo "[CONFIG] Proxies per container: $PROXIES_PER_CONTAINER"

echo "[CLEANUP] Removing old containers..."

docker rm -f $(docker ps -aq) 2>/dev/null || true

echo "[DOCKER] Building image..."

docker build -t socks5-cluster .

echo "[INIT] Generating proxy credentials..."

python3 generate_proxies.py

PORT=$START_PORT

for ((c=1;c<=CONTAINER_COUNT;c++))
do

FILE="build/users_${c}.txt"

START=$PORT
END=$((PORT + PROXIES_PER_CONTAINER - 1))

echo "[CLUSTER] Starting container $c ($START-$END)"

docker run -d \
--name socks$c \
--network host \
--memory=$CONTAINER_MEMORY \
--cpus=$CONTAINER_CPU \
--cap-add=NET_ADMIN \
--cap-add=NET_RAW \
-v $(pwd)/$FILE:/etc/danted/users.txt \
socks5-cluster

sleep $STARTUP_DELAY

echo "[VERIFY] Testing sample proxies..."

SERVICE=$(echo $VERIFY_SERVICES | cut -d',' -f1)

head -n 2 $FILE | while IFS=: read -r user pass port
do

RESULT=$(curl -s --max-time 10 --socks5 $user:$pass@$PUBLIC_IP:$port $SERVICE || true)

if [[ "$RESULT" != "" ]]; then
echo "[OK] $user@$port"
else
echo "[FAIL] $user@$port"
fi

done

PORT=$((PORT + PROXIES_PER_CONTAINER))

sleep 2

done

echo ""
echo "[SUCCESS] SOCKS5 cluster deployed"
echo "Server IP: $PUBLIC_IP"