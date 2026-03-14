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

ENTRYPOINT ["/entrypoint.sh"]