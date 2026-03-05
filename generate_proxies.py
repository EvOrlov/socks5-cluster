import os
import random
import string

CONTAINER_COUNT = int(os.getenv("CONTAINER_COUNT"))
PROXIES_PER_CONTAINER = int(os.getenv("PROXIES_PER_CONTAINER"))
START_PORT = int(os.getenv("START_PORT"))
USERNAME_PREFIX = os.getenv("USERNAME_PREFIX")
PASSWORD_LENGTH = int(os.getenv("PASSWORD_LENGTH"))

BUILD_DIR = "build"

os.makedirs(BUILD_DIR, exist_ok=True)

def random_password(length):
    chars = string.ascii_lowercase + string.digits
    return ''.join(random.choice(chars) for _ in range(length))

port = START_PORT

for container_id in range(1, CONTAINER_COUNT + 1):

    path = f"{BUILD_DIR}/users_{container_id}.txt"

    with open(path, "w") as f:

        for i in range(PROXIES_PER_CONTAINER):

            user = f"{USERNAME_PREFIX}_{container_id}_{i}"
            password = random_password(PASSWORD_LENGTH)

            f.write(f"{user}:{password}:{port}\n")

            port += 1

print("Proxy user files generated.")