FROM alpine:latest

RUN apk update && apk add --no-cache \
    dante-server \
    bash \
    shadow \
    curl \
    && rm -rf /var/cache/apk/*

COPY entrypoint.sh /entrypoint.sh
RUN chmod +x /entrypoint.sh

VOLUME /etc/danted/users.txt

ENTRYPOINT ["/entrypoint.sh"]