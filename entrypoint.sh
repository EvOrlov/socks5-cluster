#!/bin/bash

set -e

CONFIG_PATH="/etc/danted/danted.conf"
USERS_FILE="/etc/danted/users.txt"
PASSWD_FILE="/etc/danted/passwd"

# Check users file
if [ ! -s "$USERS_FILE" ]; then
    echo "[!] File $USERS_FILE is empty or missing."
    exit 1
fi

echo "[*] Preparing authentication database..."

mkdir -p /etc/danted
: > "$PASSWD_FILE"

# Generate passwd file (login:password)
while IFS=: read -r login password port; do
    echo "$login:$password" >> "$PASSWD_FILE"
done < "$USERS_FILE"

generate_config() {

cat <<EOF
logoutput: /var/log/dante.log

external: eth0

socksmethod: username
user.notprivileged: nobody

client pass {
    from: 0.0.0.0/0 to: 0.0.0.0/0
}

socks pass {
    from: 0.0.0.0/0 to: 0.0.0.0/0
    command: bind connect udpassociate
}
EOF

# Add listening ports
while IFS=: read -r login password port; do
    if [ -n "$port" ]; then
        echo "internal: 0.0.0.0 port = $port"
    fi
done < "$USERS_FILE"

}

generate_config > "$CONFIG_PATH"

echo "[i] Dante config:"
cat "$CONFIG_PATH"

echo "[i] Starting Dante..."

exec /usr/sbin/sockd -f "$CONFIG_PATH"