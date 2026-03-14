FROM alpine:latest

# Install required packages
RUN apk add --no-cache \
    dante-server \
    bash \
    iproute2 \
    net-tools \
    curl

# Copy entrypoint script
COPY entrypoint.sh /entrypoint.sh
RUN chmod +x /entrypoint.sh

VOLUME /etc/danted/users.txt

ENTRYPOINT ["/entrypoint.sh"]