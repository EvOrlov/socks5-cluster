#!/bin/bash

CONFIG_PATH="/etc/danted.conf"
USERS_FILE="/etc/danted/users.txt"

# Проверка файла пользователей
if [ ! -s "$USERS_FILE" ]; then
    echo "[!] Файл $USERS_FILE пуст или отсутствует."
    exit 1
fi

generate_config() {
    echo "logoutput: stdout"
    echo "resolveprotocol: tcp"
    echo "user.privileged: root"
    echo "user.notprivileged: nobody"
    echo "socksmethod: username"
    echo "clientmethod: none"

    # Генерация internal и external
    while IFS=: read -r login password port; do
        [[ -z "$login" ]] && continue
        adduser -D "$login" && echo "$login:$password" | chpasswd
        echo "internal: 0.0.0.0 port = $port"
    done < "$USERS_FILE"

    echo "external: eth0"
    echo ""

    cat <<EOF
client pass {
  from: 0.0.0.0/0 to: 0.0.0.0/0
  log: connect disconnect error
}
socks pass {
   from: 0.0.0.0/0 to: 0.0.0.0/0
   command: bind connect udpassociate
   log: error # connect disconnect iooperation
}
socks pass {
  from: 0.0.0.0/0 to: 0.0.0.0/0
  command: bindreply udpreply
  log: error # connect disconnect iooperation
}
EOF
}

generate_config > "$CONFIG_PATH"
echo "[i] Запуск sockd с $(wc -l < "$USERS_FILE") пользователями"

exec /usr/sbin/sockd -f "$CONFIG_PATH"
