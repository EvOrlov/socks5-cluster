#!/bin/bash

CONFIG_PATH="/etc/danted.conf"
USERS_FILE="/etc/danted/users.txt"

if [ ! -s "$USERS_FILE" ]; then
    echo "[ERROR] users.txt not found"
    exit 1
fi

mkdir -p /var/log
touch /var/log/danted.log

echo "[INIT] Generating Dante configuration..."

cat <<EOF > $CONFIG_PATH
logoutput: /var/log/danted.log

internal: 0.0.0.0 port = 1080
external: eth0

method: username

user.privileged: root
user.notprivileged: nobody
user.libwrap: nobody

EOF

while IFS=: read -r login password port
do

[ -z "$login" ] && continue

adduser -D "$login"
echo "$login:$password" | chpasswd

echo "internal: 0.0.0.0 port = $port" >> $CONFIG_PATH

cat <<EORULE >> $CONFIG_PATH

client pass {
    from: 0.0.0.0/0 to: 0.0.0.0/0 port = $port
    log: connect error
    method: username
}

pass {
    from: 0.0.0.0/0 to: 0.0.0.0/0 port = $port
    protocol: tcp udp
    log: connect error
    method: username
    username: "$login"
}

EORULE

done < "$USERS_FILE"

echo "[INFO] Dante config created"
echo "[INFO] Starting SOCKS server"

exec /usr/sbin/sockd -f $CONFIG_PATH