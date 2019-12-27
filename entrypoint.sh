#! /usr/bin/env bash
set -e

/uwsgi-nginx-entrypoint.sh


# Get the Backend host for Nginx, default to localhost
BACKEND_HOST=${BACKEND_HOST:-'localhost'}

# Get the Backend port for Nginx, default to 5000
BACKEND_PORT=${BACKEND_PORT:-5000}

# Get the listen port for Nginx, default to 80
USE_LISTEN_PORT=${LISTEN_PORT:-80}

# Get the listen port for Nginx, default to 80
USE_LISTEN_PORT=${LISTEN_PORT:-80}

if [ -f /app/nginx.conf ]; then
    cp /app/nginx.conf /etc/nginx/nginx.conf
else
    content_server='server {\n'
    content_server=$content_server"    listen ${USE_LISTEN_PORT};\n"
    content_server=$content_server'    client_body_timeout 15s;\n'
    content_server=$content_server'    client_header_timeout 15s;\n'
    content_server=$content_server'    location @app {\n'
    content_server=$content_server'        include uwsgi_params;\n'
    content_server=$content_server'        uwsgi_pass unix:///tmp/uwsgi.sock;\n'
    content_server=$content_server'    }\n'
    content_server=$content_server'    location /socket.io {\n'
    content_server=$content_server'        proxy_set_header Host $http_host;\n'
    content_server=$content_server'        proxy_set_header X-Real-IP $remote_addr;\n'
    content_server=$content_server'        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;\n'
    content_server=$content_server'        proxy_set_header X-Forwarded-Proto $scheme;\n'
    content_server=$content_server'        proxy_http_version 1.1;\n'
    content_server=$content_server'        proxy_buffering off;\n'
    content_server=$content_server'        proxy_set_header Upgrade $http_upgrade;\n'
    content_server=$content_server'        proxy_set_header Connection "Upgrade";\n'
    content_server=$content_server"        proxy_pass http://${BACKEND_HOST}:${BACKEND_PORT}/socket.io;\n"
    content_server=$content_server'    }\n'

    # Save generated server /etc/nginx/conf.d/nginx.conf
    printf "$content_server" > /etc/nginx/conf.d/nginx.conf
fi

exec "$@"