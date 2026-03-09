import os
import random
import string
import subprocess
import socket
import time
import urllib.request
import re
from concurrent.futures import ThreadPoolExecutor, as_completed


# -------------------------------
# ENV LOADER
# -------------------------------

def load_env(env_file="cluster.env"):
    config = {}

    if not os.path.exists(env_file):
        print(f"[!] Config file '{env_file}' not found. Using defaults.")
        return config

    with open(env_file) as f:
        for line in f:
            line = line.strip()

            if not line or line.startswith("#"):
                continue

            if "=" not in line:
                continue

            key, value = line.split("=", 1)
            config[key.strip()] = value.strip()

    return config


config = load_env()

# -------------------------------
# CONFIGURATION
# -------------------------------

BASE_PORT = int(config.get("START_PORT", 1080))
PROXIES_PER_CONTAINER = int(config.get("PROXIES_PER_CONTAINER", 250))
CONTAINER_COUNT = int(config.get("CONTAINER_COUNT", 12))

USERNAME_PREFIX = config.get("USERNAME_PREFIX", "user")
PASSWORD_LENGTH = int(config.get("PASSWORD_LENGTH", 8))

MEMORY_LIMIT = config.get("CONTAINER_MEMORY", "30m")
CPU_LIMIT = config.get("CONTAINER_CPU", "0.15")

STARTUP_DELAY = int(config.get("STARTUP_DELAY", 15))
INITIALIZATION_TIME = int(config.get("INITIALIZATION_TIME", 60))

VERIFY_SERVICES = config.get(
    "VERIFY_SERVICES",
    "https://api.ipify.org"
).split(",")

DOCKER_IMAGE = "dante-proxy"
PROXY_OUTPUT = "working_proxies.txt"

IP_ADDRESS = None

TEST_PROXIES_PER_CONTAINER = int(config.get("TEST_PROXIES_PER_CONTAINER", 10))
VERIFY_TIMEOUT = int(config.get("VERIFY_TIMEOUT", 8))
VERIFY_CONCURRENCY = int(config.get("VERIFY_CONCURRENCY", 50))


# -------------------------------
# IP DETECTION
# -------------------------------

def detect_public_ip():
    print("[*] Detecting public IP...")

    for service in VERIFY_SERVICES:
        service = service.strip()

        try:
            with urllib.request.urlopen(service, timeout=5) as response:
                ip = response.read().decode().strip()

                if re.match(r"\d+\.\d+\.\d+\.\d+", ip):
                    print(f"[+] Public IP detected: {ip}")
                    return ip

        except Exception:
            continue

    raise RuntimeError("Unable to detect public IP from verification services")


def detect_local_ip():

    try:
        result = subprocess.run(
            "hostname -I",
            shell=True,
            capture_output=True,
            text=True
        )

        local_ip = result.stdout.strip().split()[0]
        print(f"[+] Local interface IP: {local_ip}")
        return local_ip

    except Exception:
        return "unknown"


def check_nat(public_ip, local_ip):

    if local_ip == "unknown":
        return

    if public_ip != local_ip:

        print("\n[WARNING] Your server may be behind NAT.\n")

        print(f"Public IP : {public_ip}")
        print(f"Local IP  : {local_ip}\n")

        print("Incoming connections to proxy ports may fail.")
        print("Check if your hosting provider requires enabling a public IP.\n")


# -------------------------------
# PORT DISCOVERY
# -------------------------------

def is_port_free(port):

    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.settimeout(1)
        return s.connect_ex(("127.0.0.1", port)) != 0


def find_free_ports(count, start_port):

    free_ports = []
    current_port = start_port

    while len(free_ports) < count:

        if is_port_free(current_port):
            free_ports.append(current_port)

        current_port += 1

        if current_port > 65535:
            raise RuntimeError("Unable to allocate enough ports")

    return free_ports


# -------------------------------
# PROXY GENERATION
# -------------------------------

def generate_credentials():

    print("[*] Generating proxy credentials...")

    ports = find_free_ports(PROXIES_PER_CONTAINER * CONTAINER_COUNT, BASE_PORT)

    credentials = []

    for port in ports:

        username = f"{USERNAME_PREFIX}_{''.join(random.choices(string.ascii_letters, k=6))}"

        password = ''.join(
            random.choices(string.ascii_letters + string.digits, k=PASSWORD_LENGTH)
        )

        credentials.append((username, password, port))

    return credentials


def build_users_files(credentials):

    print("[*] Creating users_*.txt files")

    for i in range(CONTAINER_COUNT):

        batch = credentials[i * PROXIES_PER_CONTAINER:(i + 1) * PROXIES_PER_CONTAINER]

        with open(f"users_{i}.txt", "w") as f:

            for user, pwd, port in batch:
                f.write(f"{user}:{pwd}:{port}\n")


# -------------------------------
# DOCKER CLEANUP
# -------------------------------

def cleanup_cluster():

    print("[*] Cleaning previous cluster containers...")

    result = subprocess.run(
        "docker ps -a --filter 'name=socks-batch' --format '{{.ID}}'",
        shell=True,
        capture_output=True,
        text=True
    )

    containers = result.stdout.strip().splitlines()

    if containers:

        subprocess.run(
            f"docker rm -f {' '.join(containers)}",
            shell=True
        )

        print(f"[+] Removed {len(containers)} old containers")

    else:

        print("[*] No old containers found")


# -------------------------------
# DOCKER BUILD
# -------------------------------

def build_docker_image():

    print("[*] Building Docker image...")

    result = subprocess.run(
        f"docker build -t {DOCKER_IMAGE} .",
        shell=True
    )

    if result.returncode != 0:

        raise RuntimeError("Docker image build failed")


# -------------------------------
# CONTAINER LAUNCH
# -------------------------------

def launch_containers(credentials):

    build_docker_image()

    for i in range(CONTAINER_COUNT):

        batch = credentials[i * PROXIES_PER_CONTAINER:(i + 1) * PROXIES_PER_CONTAINER]

        users_file = f"users_{i}.txt"

        container_name = f"socks-batch-{i+1}"

        cmd = (
            f"docker run -d --name {container_name} "
            f"--cap-add=NET_RAW --cap-add=NET_ADMIN "
            f"--memory={MEMORY_LIMIT} --cpus={CPU_LIMIT} "
            f"--network host "
            f"-v $(pwd)/{users_file}:/etc/danted/users.txt "
            f"{DOCKER_IMAGE}"
        )

        result = subprocess.run(cmd, shell=True)

        if result.returncode == 0:

            print(
                f"[+] Container {i+1}/{CONTAINER_COUNT} "
                f"started (ports {batch[0][2]}-{batch[-1][2]})"
            )

        else:

            print(f"[!] Failed to start container {i+1}")

        time.sleep(STARTUP_DELAY)


# -------------------------------
# PROXY TEST
# -------------------------------

def test_single_proxy(proxy):

    cmd = f"curl --socks5 {proxy} -s --max-time {VERIFY_TIMEOUT} {VERIFY_SERVICES[0]}"

    result = subprocess.run(
        cmd,
        shell=True,
        capture_output=True
    )

    return result.returncode == 0

def verify_proxies(credentials):

    print("[*] Testing proxies...\n")

    proxies = []

    for container_index in range(CONTAINER_COUNT):

        for i in range(TEST_PROXIES_PER_CONTAINER):
            index = container_index * PROXIES_PER_CONTAINER + i

            user, password, port = credentials[index]

            proxy = f"{user}:{password}@{IP_ADDRESS}:{port}"

            proxies.append(proxy)

    working = []

    with ThreadPoolExecutor(max_workers=VERIFY_CONCURRENCY) as executor:

        future_map = {executor.submit(test_single_proxy, p): p for p in proxies}

        for future in as_completed(future_map):

            proxy = future_map[future]

            try:

                if future.result():

                    print(f"[+] OK: {proxy}")

                    working.append(proxy)

                else:

                    print(f"[-] FAIL: {proxy}")

            except Exception:

                print(f"[-] ERROR: {proxy}")

    print(f"[*] Checking {len(proxies)} proxies with {VERIFY_CONCURRENCY} workers\n")

    with open(PROXY_OUTPUT, "w") as f:

        for proxy in working:
            f.write(proxy + "\n")

    print(f"[*] All working proxies saved to {PROXY_OUTPUT}")

# -------------------------------
# WAIT FOR CONTAINERS READY
# -------------------------------

def wait_for_containers():

    print("[*] Waiting for containers to become ready...")

    timeout = 180
    start = time.time()

    while True:

        result = subprocess.run(
            "docker ps --filter 'name=socks-batch' --format '{{.Names}}'",
            shell=True,
            capture_output=True,
            text=True
        )

        running = result.stdout.strip().splitlines()

        if len(running) == CONTAINER_COUNT:
            print(f"[+] All {CONTAINER_COUNT} containers running")
            break

        if time.time() - start > timeout:
            raise RuntimeError("Timeout waiting for containers")

        print(f"[*] Containers running: {len(running)}/{CONTAINER_COUNT}")
        time.sleep(3)

    print("[*] Allowing services to finish initialization...\n")
    time.sleep(10)

# -------------------------------
# MAIN PIPELINE
# -------------------------------

def main():

    global IP_ADDRESS

    print()
    print("=" * 32)
    print(" SOCKS5 CLUSTER DEPLOYMENT")
    print("=" * 32)
    print()

    try:

        public_ip = detect_public_ip()
        local_ip = detect_local_ip()

        check_nat(public_ip, local_ip)

        IP_ADDRESS = public_ip

        credentials = generate_credentials()

        cleanup_cluster()

        build_users_files(credentials)

        launch_containers(credentials)

        wait_for_containers()

        verify_proxies(credentials)

    except Exception as e:

        print(f"[!] Deployment failed: {e}")

    finally:

        print("\n[*] Deployment finished\n")


if __name__ == "__main__":
    main()