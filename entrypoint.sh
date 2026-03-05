#!/bin/bash

CONFIG_PATH="/etc/danted.conf"
USERS_FILE="/etc/danted/users.txt"

if [ ! -s "$USERS_FILE" ]; then
    echo "[ERROR] users.txt not found or empty"
    exit 1
fi

echo "[INIT] Generating Dante configuration..."

cat <<EOF > $CONFIG_PATH
logoutput: /var/log/danted.log
external: eth0

socksmethod: username
clientmethod: none

user.privileged: root
user.notprivileged: nobody
EOF

while IFS=: read -r login password port
do

if [ -z "$login" ]; then
continue
fi

adduser -D "$login"
echo "$login:$password" | chpasswd

cat <<EORULE >> $CONFIG_PATH

internal: 0.0.0.0 port = $port

client pass {
    from: 0.0.0.0/0 to: 0.0.0.0/0
    port = $port
    log: connect error
}

socks pass {
    from: 0.0.0.0/0 to: 0.0.0.0/0
    port = $port
    protocol: tcp udp
    username: "$login"
    log: connect disconnect error
}

EORULE

done < "$USERS_FILE"

echo "[INFO] Dante config created."
echo "[INFO] Starting SOCKS server..."

exec /usr/sbin/sockd -f "$CONFIG_PATH"