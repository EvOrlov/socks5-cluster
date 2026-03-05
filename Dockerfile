FROM alpine:latest

RUN apk update && apk add --no-cache \
    dante-server \
    bash \
    iproute2 \
    net-tools \
    shadow \
    tcpdump \
    bind-tools \
    curl \
    && rm -rf /var/cache/apk/*

COPY entrypoint.sh /entrypoint.sh
RUN chmod +x /entrypoint.sh

# Точка монтирования для users.txt
VOLUME /etc/danted/users.txt

ENTRYPOINT ["/entrypoint.sh"]