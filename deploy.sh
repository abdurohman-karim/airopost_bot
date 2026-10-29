#!/usr/bin/env bash
# Выкладка бота на сервер. Запускать с вашего компьютера из папки проекта:
#   ./deploy.sh root@79.132.143.211
# Пароль (или ключ) SSH вводите вы сами. Повторный запуск = обновление.
set -euo pipefail

HOST="${1:?Использование: ./deploy.sh user@host}"
DIR=/home/bots/airopost
SERVICE=airopost-bot
SSH_OPTS="-o ControlMaster=auto -o ControlPath=/tmp/airopost-deploy-%r@%h:%p -o ControlPersist=120"

cd "$(dirname "$0")"
run() { ssh $SSH_OPTS "$HOST" "$@"; }

run "mkdir -p $DIR"
# На сервер едет только нужное для работы; .env, data/ и .venv/ на сервере не трогаются
rsync -az --delete -e "ssh $SSH_OPTS" --exclude '__pycache__' \
    bot requirements.txt .env.example "$SERVICE.service" "$HOST:$DIR/"

run "DIR=$DIR SERVICE=$SERVICE bash -s" <<'REMOTE'
set -euo pipefail
cd "$DIR"

if ! python3 -c 'import sys; sys.exit(sys.version_info < (3, 10))'; then
    echo ">>> Нужен Python 3.10+, на сервере $(python3 --version 2>&1)"
    exit 1
fi

if [ ! -x .venv/bin/pip ]; then
    if ! python3 -m venv .venv 2>/dev/null; then
        apt-get update -qq && apt-get install -y -qq python3-venv
        python3 -m venv .venv
    fi
fi

# Зависимости ставятся только когда requirements.txt изменился
REQ_HASH=$(sha256sum requirements.txt | cut -d' ' -f1)
if [ "$(cat .venv/.requirements.sha256 2>/dev/null)" != "$REQ_HASH" ]; then
    .venv/bin/pip install -q --upgrade pip
    .venv/bin/pip install -q -r requirements.txt
    echo "$REQ_HASH" > .venv/.requirements.sha256
fi

if [ ! -f .env ]; then
    cp .env.example .env
    chmod 600 .env
fi
if ! grep -q '^BOT_TOKEN=.' .env; then
    echo
    echo ">>> Впишите BOT_TOKEN (и при желании ADMIN_IDS, IQAIR_API_KEY) в $DIR/.env:"
    echo ">>>   nano $DIR/.env"
    echo ">>> затем запустите ./deploy.sh ещё раз."
    exit 0
fi

cp "$SERVICE.service" "/etc/systemd/system/$SERVICE.service"
systemctl daemon-reload
systemctl enable "$SERVICE" >/dev/null 2>&1
systemctl restart "$SERVICE"
sleep 3
systemctl --no-pager --lines=15 status "$SERVICE" || true
REMOTE
