#!/bin/bash

# === ПАРАМЕТРЫ ===
NUM_PROXIES=1000                # Сколько прокси создать
START_PORT=10000                # С какого порта начинать
USERNAME_PREFIX="user"         # Префикс логина
PASSWORD_LENGTH=10              # Длина пароля

CONFIG_DIR="./build"
CONF_FILE="$CONFIG_DIR/danted.conf"
PASSWD_FILE="$CONFIG_DIR/users.txt"

# === ПОДГОТОВКА ===
mkdir -p "$CONFIG_DIR"
rm -f "$CONF_FILE" "$PASSWD_FILE"

# === ОБЩАЯ ЧАСТЬ КОНФИГА ===
cat <<EOF > "$CONF_FILE"
logoutput: /var/log/danted.log
internal: 0.0.0.0 port = $START_PORT
external: eth0

method: username
user.privileged: root
user.notprivileged: nobody
user.libwrap: nobody

EOF

# === СОЗДАНИЕ ПРОКСИ ===
for ((i=0; i<$NUM_PROXIES; i++)); do
    PORT=$((START_PORT + i))
    USER="$USERNAME_PREFIX$i"
    PASS=$(openssl rand -hex $((PASSWORD_LENGTH/2)))

    echo "$USER:$PASS" >> "$PASSWD_FILE"

    # Открываем порт
    echo "internal: 0.0.0.0 port = $PORT" >> "$CONF_FILE"

    cat <<EORULE >> "$CONF_FILE"
client pass {
    from: 0.0.0.0/0 to: 0.0.0.0/0 port = $PORT
    log: connect error
    method: username
}

pass {
    from: 0.0.0.0/0 to: 0.0.0.0/0 port = $PORT
    protocol: tcp udp
    log: connect error
    method: username
    username: "$USER"
}
EORULE

done

# === ВЫВОД ===
echo "Сгенерировано $NUM_PROXIES прокси."
echo "Файл конфигурации: $CONF_FILE"
echo "Пользователи: $PASSWD_FILE"

# === ПРИМЕР ДОКЕР-КОМАНДЫ ===
echo "Запуск Dante (пример):"
echo "docker run --rm -d --network=host -v \"$CONFIG_DIR/danted.conf:/etc/danted.conf\" \"jedisct1/dante\""
