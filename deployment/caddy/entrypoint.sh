#!/usr/bin/env sh

BE_HOST=${BACKEND_HOST:-frogress}
BE_PORT=${BACKEND_PORT:-8000}

CADDY_DOMAIN=${DOMAIN_NAME:-progress.deco.mp}

IS_PROD=${PRODUCTION:-YES}

until nc -z ${BE_HOST} ${BE_PORT} > /dev/null; do
    echo "Waiting for backend to become available on ${BE_HOST}:${BE_PORT}..."
    sleep 1
done

if [[ "${IS_PROD}" == "YES" ]]; then
    echo "Frogress API available at https://${CADDY_DOMAIN}"
    sed -i "s/__DOMAIN_NAME__/${CADDY_DOMAIN}/g" /etc/caddy/Caddyfile
else
    echo "Frogress API available at http://localhost:80"
    sed -i "s/__DOMAIN_NAME__/:80/g" /etc/caddy/Caddyfile
fi

sed -i "s/__BACKEND_HOST__/${BE_HOST}/g" /etc/caddy/Caddyfile
sed -i "s/__BACKEND_PORT__/${BE_PORT}/g" /etc/caddy/Caddyfile

/usr/bin/caddy run --config /etc/caddy/Caddyfile --adapter caddyfile
