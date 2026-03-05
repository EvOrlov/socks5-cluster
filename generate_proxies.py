import os
import random
import string
import subprocess
import socket
import time
# import psutil
from datetime import datetime

# Конфигурация
BASE_PORT = 1080
PROXIES_PER_CONTAINER = 250
CONTAINER_COUNT = 12
DOCKER_IMAGE = "dante-proxy"
IP_ADDRESS = "103.27.156.97"
PROXY_OUTPUT = "working_proxies.txt"

# Лимиты ресурсов
MEMORY_LIMIT = "30m"
CPU_LIMIT = "0.15"
STARTUP_DELAY = 15
INITIALIZATION_TIME = 60


def full_docker_cleanup():
    """Полная очистка всех Docker-объектов"""
    print("[*] Полная очистка Docker-окружения...")

    # Получаем все контейнеры
    result = subprocess.run("docker ps -aq", shell=True, capture_output=True, text=True)
    container_ids = result.stdout.strip().splitlines()

    if container_ids:
        print(f"[.] Остановка {len(container_ids)} контейнеров...")
        subprocess.run(f"docker stop {' '.join(container_ids)}", shell=True)

        # Ждём до 10 секунд, пока все контейнеры не остановятся
        for i in range(10):
            result = subprocess.run("docker ps -q", shell=True, capture_output=True, text=True)
            if not result.stdout.strip():
                break
            print(f"[.] Ожидание остановки контейнеров ({i+1}/10)...")
            time.sleep(1)

        # Теперь можно удалять
        print("[.] Удаление остановленных контейнеров...")
        subprocess.run(f"docker rm -f {' '.join(container_ids)}", shell=True)

    # Остальное – очистка мусора
    cleanup_cmds = [
        "docker network prune -f",
        "docker image prune -af",
        "docker volume prune -f",
        "docker system prune -af",
        "sync; echo 3 | sudo tee /proc/sys/vm/drop_caches >/dev/null"
    ]

    for cmd in cleanup_cmds:
        subprocess.run(cmd, shell=True)

    print("[+] Docker-окружение полностью очищено")


def reset_network():
    """Сброс сетевого стека Docker"""
    subprocess.run("sudo systemctl restart docker", shell=True)
    # subprocess.run("sudo iptables -t nat -F", shell=True)
    time.sleep(5)


def generate_credentials():
    """Генерирует учетные данные со свободными портами"""
    ports = find_free_ports(PROXIES_PER_CONTAINER * CONTAINER_COUNT, BASE_PORT)
    return [
        (f"user_{''.join(random.choices(string.ascii_letters, k=6))}",
         ''.join(random.choices(string.ascii_letters + string.digits, k=10)),
         port)
        for port in ports
    ]


def cleanup_environment():
    """Полная очистка окружения"""
    print("[*] Очистка старых контейнеров...")
    full_docker_cleanup()
    reset_network()

    print("[*] Удаление временных файлов...")
    for i in range(CONTAINER_COUNT):
        try:
            os.remove(f"users_{i}.txt")
        except FileNotFoundError:
            pass


def build_users_files(credentials):
    """Создает файлы с пользователями для каждого контейнера"""
    print("[*] Генерация users_*.txt")
    for i in range(CONTAINER_COUNT):
        batch = credentials[i * PROXIES_PER_CONTAINER:(i + 1) * PROXIES_PER_CONTAINER]
        with open(f"users_{i}.txt", "w") as f:
            for user, pwd, port in batch:
                f.write(f"{user}:{pwd}:{port}\n")


def find_free_ports(count, start_port):
    """Находит count свободных портов"""
    free_ports = []
    current_port = start_port

    while len(free_ports) < count:
        if is_port_free(current_port):
            free_ports.append(current_port)
        current_port += 1
        if current_port > 65535:
            raise ValueError("Не удалось найти достаточное количество свободных портов")

    return free_ports


def is_port_free(port):
    """Проверяет доступность порта"""
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.settimeout(1)
        return s.connect_ex(("127.0.0.1", port)) != 0


def check_system_limits():
    """Проверяет доступные системные ресурсы"""
    # Проверка свободных файловых дескрипторов
    with open("/proc/sys/fs/file-nr") as f:
        used = int(f.read().split()[0])
        if used > 0.8 * 2097152:  # 80% от file-max
            return False

    # Проверка количества процессов
    proc_count = int(subprocess.run("ps -e --no-headers | wc -l",
                                    shell=True, capture_output=True).stdout)
    if proc_count > 0.7 * 65536:  # 70% от pid_max
        return False

    return True


def build_docker_image():
    """Собирает Docker образ"""
    print("[*] Сборка образа Dante...")
    result = subprocess.run(
        "docker build -t dante-proxy .",
        shell=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE
    )
    if result.returncode != 0:
        print("[!] Ошибка сборки образа:")
        print(result.stderr.decode())
        return False
    return True


def test_proxy(ip, port, user, password):
    """Проверяет работоспособность прокси"""
    try:
        result = subprocess.run(
            ["curl", "-x", f"socks5h://{user}:{password}@{ip}:{port}",
             "--max-time", "10", "https://api.ipify.org"],
            stdout=subprocess.PIPE,
            stderr=subprocess.DEVNULL
        )
        return result.stdout.decode().strip() == ip
    except:
        return False


def check_system_health():
    # mem = psutil.virtual_memory()
    # cpu = psutil.cpu_percent(interval=0.1)
    # print(f"[*] Нагрузка: CPU {cpu}% | RAM {mem.used/1024/1024:.0f}/{mem.total/1024/1024:.0f}MB")
    # return cpu < 85 and mem.available > 300 * 1024 * 1024  # 300MB свободно
    pass


def verify_proxies(credentials):
    """Проверяет прокси и сохраняет результаты"""
    print("[*] Тестирование прокси...")

    # Сохраняем ВСЕ прокси
    with open(PROXY_OUTPUT, "w") as f:
        for user, pwd, port in credentials:
            f.write(f"{IP_ADDRESS}:{port}:{user}:{pwd}\n")

    # Проверяем первые 3 из каждого контейнера
    working = []
    for i in range(CONTAINER_COUNT):
        batch = credentials[i * PROXIES_PER_CONTAINER:(i + 1) * PROXIES_PER_CONTAINER]
        for j, (user, pwd, port) in enumerate(batch[:3]):
            if test_proxy(IP_ADDRESS, port, user, pwd):
                print(f"[+] OK: {user}:{pwd}@{IP_ADDRESS}:{port}")
                working.append(f"{IP_ADDRESS}:{port}:{user}:{pwd}")
            else:
                print(f"[-] FAIL: {user}@{IP_ADDRESS}:{port}")
            time.sleep(0.5)

    print(f"[*] Проверено: {3 * CONTAINER_COUNT} | Рабочих: {len(working)}")
    print(f"[*] Все {len(credentials)} прокси сохранены в {PROXY_OUTPUT}")


def launch_containers(credentials):
    """Запускает контейнеры с контролем ресурсов"""
    if not build_docker_image():
        return False

    for i in range(CONTAINER_COUNT):
        if not check_system_limits():
            print("[!] Достигнуты системные лимиты. Жду 30 сек...")
            time.sleep(30)
            continue

        batch = credentials[i * PROXIES_PER_CONTAINER:(i + 1) * PROXIES_PER_CONTAINER]
        users_file = f"users_{i}.txt"
        container_name = f"socks-batch-{i}"

        # Запуск контейнера
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
            print(f"[+] Контейнер {i + 1}/{CONTAINER_COUNT} запущен (порты {batch[0][2]}-{batch[-1][2]})")
            time.sleep(STARTUP_DELAY)
        else:
            print(f"[!] Ошибка запуска контейнера {i + 1}")

    return True




def main():
    print("[*] Инициализация генератора прокси...")
    print(f"[*] Конфигурация: {CONTAINER_COUNT} контейнеров по {PROXIES_PER_CONTAINER} прокси")

    try:
        # Подготовка
        credentials = generate_credentials()
        cleanup_environment()
        build_users_files(credentials)

        # Запуск
        if not launch_containers(credentials):
            print("[!] Критическая ошибка при запуске")
            return

        print(f"[*] Ожидание инициализации ({INITIALIZATION_TIME} сек)...")
        time.sleep(INITIALIZATION_TIME)

        # Проверка и сохранение
        verify_proxies(credentials)

    except Exception as e:
        print(f"[!] Ошибка: {str(e)}")
    finally:
        print("[*] Завершение работы")


if __name__ == "__main__":
    main()