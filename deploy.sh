#!/bin/bash
set -e

echo "========================================"
echo " SOCKS5 Cluster Deployment"
echo "========================================"
echo ""

# --- Check Docker ---

if ! command -v docker &> /dev/null; then
    echo "[ERROR] Docker is not installed."
    echo "Run bootstrap.sh first to prepare the server."
    exit 1
fi

# --- Check Docker daemon ---

if ! docker info > /dev/null 2>&1; then
    echo "[ERROR] Docker daemon is not running."
    echo "Try: sudo systemctl start docker"
    exit 1
fi

# --- Check Python ---

if ! command -v python3 &> /dev/null; then
    echo "[ERROR] Python3 is not installed."
    exit 1
fi

# --- Check cluster.env ---

if [ ! -f cluster.env ]; then
    echo "[ERROR] cluster.env not found."
    exit 1
fi

echo "[INFO] Environment looks good."
echo ""

# --- Run launcher ---

python3 launcher.py

echo ""
echo "========================================"
echo " Deployment finished."
echo "========================================"