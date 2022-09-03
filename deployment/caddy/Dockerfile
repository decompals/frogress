FROM caddy:2.5.2-alpine

COPY deployment/caddy/Caddyfile /etc/caddy/

COPY deployment/caddy/entrypoint.sh /entrypoint.sh

ENTRYPOINT ["/entrypoint.sh"]
