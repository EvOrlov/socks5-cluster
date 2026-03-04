#!/bin/bash

CONFIG_PATH="/etc/danted.conf"
USERS_FILE="/etc/danted/users.txt"

echo "[INIT] Starting Dante SOCKS5 container..."

if [ ! -s "$USERS_FILE" ]; then
    echo "[ERROR] Users file not found or empty: $USERS_FILE"
    exit 1
fi

generate_config() {
    echo "logoutput: /var/log/dante.log"
    echo "resolveprotocol: tcp"
    echo "user.privileged: root"
    echo "user.notprivileged: nobody"
    echo "socksmethod: username"
    echo "clientmethod: none"

    while IFS=: read -r login password port; do
        [ -z "$login" ] && continue
        adduser -D "$login" >/dev/null 2>&1
        echo "$login:$password" | chpasswd
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
  log: error
}

socks pass {
  from: 0.0.0.0/0 to: 0.0.0.0/0
  command: bindreply udpreply
  log: error
}
EOF
}

generate_config > "$CONFIG_PATH"

USER_COUNT=$(wc -l < "$USERS_FILE")
echo "[INIT] Generated configuration for $USER_COUNT proxies"
echo "[INIT] Launching sockd..."

exec /usr/sbin/sockd -f "$CONFIG_PATH"