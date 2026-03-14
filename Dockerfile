FROM alpine:3.19

RUN apk add --no-cache \
    dante-server \
    bash \
    iproute2 \
    net-tools \
    curl

COPY entrypoint.sh /entrypoint.sh

RUN chmod +x /entrypoint.sh

VOLUME ["/etc/danted"]

ENTRYPOINT ["/entrypoint.sh"]