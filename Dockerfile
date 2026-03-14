FROM alpine:latest

# Install required packages
RUN apk update && apk add --no-cache \
    dante-server \
    bash \
    iproute2 \
    net-tools \
    curl \
    && rm -rf /var/cache/apk/*

# Copy entrypoint script
COPY entrypoint.sh /entrypoint.sh
RUN chmod +x /entrypoint.sh

ENTRYPOINT ["/entrypoint.sh"]