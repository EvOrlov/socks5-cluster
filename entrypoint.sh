#!/bin/bash

set -e

CONFIG_PATH="/etc/danted.conf"
USERS_FILE="/etc/danted/users.txt"
PASSWD_FILE="/etc/danted/passwd"

if [ ! -s "$USERS_FILE" ]; then
    echo "[!] File $USERS_FILE empty or missing."
    exit 1
fi

echo "[*] Preparing authentication database..."

mkdir -p /etc/danted
: > "$PASSWD_FILE"

while IFS=: read -r login password port; do
    echo "$login:$password" >> "$PASSWD_FILE"
done < "$USERS_FILE"


generate_config() {

cat <<EOF
logoutput: /var/log/danted.log

external: eth0

socksmethod: username
passwdfile: /etc/danted/passwd

user.notprivileged: nobody

client pass {
    from: 0.0.0.0/0 to: 0.0.0.0/0
}

socks pass {
    from: 0.0.0.0/0 to: 0.0.0.0/0
    command: bind connect udpassociate
}
EOF

while IFS=: read -r login password port; do
    echo "internal: 0.0.0.0 port = $port"
done < "$USERS_FILE"

}

generate_config > "$CONFIG_PATH"

echo "[i] Starting Dante..."

exec /usr/sbin/sockd -f "$CONFIG_PATH"