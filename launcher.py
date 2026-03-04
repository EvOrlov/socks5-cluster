import os
import socket
import subprocess
import time
import random
import string
from datetime import datetime


# ===============================
# Utility / Logging
# ===============================

def log(section, message):
    print(f"[{section}] {message}")


def run(cmd):
    return subprocess.run(cmd, shell=True, capture_output=True, text=True)


# ===============================
# Config Loader
# ===============================

def load_env(path="cluster.env"):
    config = {}

    if not os.path.exists(path):
        raise FileNotFoundError("cluster.env not found")

    with open(path) as f:
        for line in f:
            line = line.strip()
            if not line or line.startswith("#"):
                continue
            if "=" not in line:
                continue
            key, value = line.split("=", 1)
            config[key.strip()] = value.strip()

    return config


def parse_services(value):
    if not value:
        return []
    return [s.strip() for s in value.split(",") if s.strip()]


# ===============================
# Public IP Detection
# ===============================

def detect_public_ip(services):
    for url in services:
        try:
            result = subprocess.run(
                ["curl", "-s", "--max-time", "5", url],
                capture_output=True,
                text=True
            )
            ip = result.stdout.strip()
            if is_valid_ip(ip):
                log("HOST", f"Public IP detected: {ip} (via {url})")
                return ip
        except Exception:
            continue

    raise RuntimeError("Failed to detect public IP from all services.")


def is_valid_ip(ip):
    try:
        socket.inet_aton(ip)
        return True
    except:
        return False


# ===============================
# Docker Cleanup
# ===============================

def full_docker_cleanup():
    log("CLEANUP", "Stopping existing containers...")

    containers = run("docker ps -aq").stdout.strip().splitlines()

    if containers:
        run(f"docker stop {' '.join(containers)}")
        time.sleep(3)
        run(f"docker rm -f {' '.join(containers)}")

    run("docker network prune -f")
    run("docker image prune -af")
    run("docker volume prune -f")
    run("docker system prune -af")

    log("CLEANUP", "Docker environment cleaned.")


# ===============================
# System Health
# ===============================

def get_cpu_usage():
    return float(run("grep 'cpu ' /proc/stat").stdout.split()[1])


def get_free_ram_mb():
    meminfo = run("grep MemAvailable /proc/meminfo").stdout
    if meminfo:
        return int(meminfo.split()[1]) // 1024
    return 0


def check_system_health(min_free_ram_mb, max_cpu_percent):
    free_ram = get_free_ram_mb()
    cpu_usage = float(run("awk '{print $1}' /proc/loadavg").stdout.strip())

    log("HEALTH", f"Free RAM: {free_ram} MB | Load Avg: {cpu_usage}")

    if free_ram < min_free_ram_mb:
        return False
    if cpu_usage * 100 > max_cpu_percent:
        return False

    return True


# ===============================
# Port Allocation
# ===============================

def is_port_free(port):
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.settimeout(1)
        return s.connect_ex(("127.0.0.1", port)) != 0


def find_free_ports(count, start_port):
    ports = []
    current = start_port

    while len(ports) < count:
        if current > 65535:
            raise RuntimeError("Not enough free ports available.")
        if is_port_free(current):
            ports.append(current)
        current += 1

    return ports


# ===============================
# Credential Generation
# ===============================

def generate_credentials(container_count, proxies_per_container, base_port):
    total = container_count * proxies_per_container
    ports = find_free_ports(total, base_port)

    credentials = []

    for port in ports:
        user = "user_" + "".join(random.choices(string.ascii_lowercase, k=6))
        pwd = "".join(random.choices(string.ascii_letters + string.digits, k=10))
        credentials.append((user, pwd, port))

    return credentials


# ===============================
# Users File Builder
# ===============================

def build_users_files(credentials, container_count, proxies_per_container):
    for i in range(container_count):
        batch = credentials[i * proxies_per_container:(i + 1) * proxies_per_container]
        with open(f"users_{i}.txt", "w") as f:
            for user, pwd, port in batch:
                f.write(f"{user}:{pwd}:{port}\n")


# ===============================
# Docker Build & Launch
# ===============================

def build_image():
    log("DOCKER", "Building image...")
    result = run("docker build -t dante-proxy .")
    if result.returncode != 0:
        print(result.stderr)
        raise RuntimeError("Docker build failed.")
    log("DOCKER", "Image built successfully.")


def launch_containers(config, credentials, public_ip, verify_services):
    container_count = int(config["CONTAINER_COUNT"])
    proxies_per_container = int(config["PROXIES_PER_CONTAINER"])

    memory_limit = config["MEMORY_LIMIT"]
    cpu_limit = config["CPU_LIMIT"]

    startup_delay = int(config["STARTUP_DELAY"])
    verify_timeout = config["VERIFY_TIMEOUT"]

    working_samples = 0
    total_samples = 0

    for i in range(container_count):
        batch = credentials[i * proxies_per_container:(i + 1) * proxies_per_container]
        users_file = f"users_{i}.txt"
        container_name = f"socks-batch-{i}"

        cmd = (
            f"docker run -d --name {container_name} "
            f"--memory={memory_limit} --cpus={cpu_limit} "
            f"--network host "
            f"-v $(pwd)/{users_file}:/etc/danted/users.txt "
            f"dante-proxy"
        )

        result = run(cmd)

        if result.returncode == 0:
            log("CLUSTER", f"Container {i+1}/{container_count} started "
                           f"(ports {batch[0][2]}-{batch[-1][2]})")
        else:
            log("ERROR", f"Failed to start container {i+1}")
            continue

        time.sleep(startup_delay)

        if verify_services:
            log("VERIFY", f"Testing sample proxies for container {i+1}...")

            for idx, service in enumerate(verify_services):
                if idx >= len(batch):
                    break

                user, pwd, port = batch[idx]

                result = subprocess.run(
                    [
                        "curl",
                        "-s",
                        "--max-time",
                        verify_timeout,
                        "-x",
                        f"socks5h://{user}:{pwd}@{public_ip}:{port}",
                        service
                    ],
                    capture_output=True,
                    text=True
                )

                returned_ip = result.stdout.strip()
                total_samples += 1

                if returned_ip == public_ip:
                    log("VERIFY", f"[OK] {user}@{port}")
                    working_samples += 1
                else:
                    log("VERIFY", f"[FAIL] {user}@{port}")

        while not check_system_health(
                int(config["MIN_FREE_RAM_MB"]),
                int(config["MAX_CPU_PERCENT"])):
            log("HEALTH", "System under pressure. Waiting 20s...")
            time.sleep(20)

    return working_samples, total_samples


# ===============================
# Export Proxies
# ===============================

def export_proxies(credentials, public_ip):
    os.makedirs("output", exist_ok=True)
    path = "output/proxies.txt"

    with open(path, "w") as f:
        for user, pwd, port in credentials:
            f.write(f"{public_ip}:{port}:{user}:{pwd}\n")

    log("EXPORT", f"All proxies saved to {path}")


# ===============================
# Main
# ===============================

def main():
    log("INIT", "SOCKS5 Cluster Deployment Started")

    config = load_env()

    verify_services = parse_services(config.get("VERIFY_SERVICES", ""))

    public_ip_services = verify_services or [
        "https://api.ipify.org",
        "https://ifconfig.me/ip"
    ]

    public_ip = detect_public_ip(public_ip_services)

    container_count = int(config["CONTAINER_COUNT"])
    proxies_per_container = int(config["PROXIES_PER_CONTAINER"])
    base_port = int(config["BASE_PORT"])

    log("CONFIG",
        f"Containers: {container_count} | "
        f"Proxies per container: {proxies_per_container} | "
        f"Total: {container_count * proxies_per_container}")

    full_docker_cleanup()

    credentials = generate_credentials(
        container_count,
        proxies_per_container,
        base_port
    )

    build_users_files(credentials, container_count, proxies_per_container)

    build_image()

    working, total = launch_containers(
        config,
        credentials,
        public_ip,
        verify_services
    )

    export_proxies(credentials, public_ip)

    log("SUMMARY", f"Sample verification: {working}/{total} successful")
    log("DONE", "Cluster deployment completed successfully.")


if __name__ == "__main__":
    main()