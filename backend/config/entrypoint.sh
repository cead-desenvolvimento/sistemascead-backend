#!/bin/sh

STATIC_DIR="/app/cead/staticfiles"

echo "[Entrypoint] Verificando se é necessário rodar collectstatic..."

if [ -z "$(ls -A $STATIC_DIR)" ]; then
    echo "[Entrypoint] staticfiles está vazio. Executando collectstatic..."
    python manage.py collectstatic --noinput
else
    echo "[Entrypoint] staticfiles já contém arquivos. Ignorando collectstatic."
fi

echo "[Entrypoint] Iniciando Gunicorn..."
exec gunicorn cead.wsgi:application \
    --bind=0.0.0.0:8000 \
    --preload \
    --access-logfile=/app/logs/access.log \
    --error-logfile=/app/logs/error.log
