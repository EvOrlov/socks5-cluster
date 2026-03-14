#!/bin/bash

# Exit on any error
set -e

CONFIG_PATH="/etc/danted/danted.conf"
USERS_FILE="/etc/danted/users.txt"
PASSWD_FILE="/etc/danted/passwd"

# === Check for required users file ===
if [ ! -s "$USERS_FILE" ]; then
    echo "[!] File $USERS_FILE is empty or missing."
    exit 1
fi

echo "[*] Preparing authentication database..."

mkdir -p /etc/danted

# Clear previous password file
: > "$PASSWD_FILE"

# Generate password database from users.txt
while IFS=: read -r login password port; do
    echo "$login:$password" >> "$PASSWD_FILE"
done < "$USERS_FILE"

# === Generate dante configuration ===
generate_config() {
cat <<EOF
# Dante server configuration
logoutput: /var/log/dante.log

internal: 0.0.0.0 port = 0
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

# Add per-user internal ports
while IFS=: read -r login password port; do
    echo "internal: 0.0.0.0 port = $port"
done < "$USERS_FILE"
}

# Write final configuration
generate_config > "$CONFIG_PATH"

echo "[i] Starting Dante..."
exec /usr/sbin/sockd -f "$CONFIG_PATH"