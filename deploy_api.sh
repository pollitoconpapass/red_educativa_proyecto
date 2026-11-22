#!/usr/bin/env bash
# Sube api/ a la VPS, incluyendo api/.env
#
# Uso:
#   chmod +x ./deploy_api.sh
#   ./deploy_api.sh <usuario> <contraseña> <host>

set -euo pipefail

USUARIO="${1:-}"
PASS="${2:-}"
HOST="${3:-${VPS_HOST:-}}"

if [ -z "$USUARIO" ] || [ -z "$PASS" ] || [ -z "$HOST" ]; then
    echo "Uso: ./deploy_api.sh <usuario> <contraseña> <host>" >&2
    echo "     VPS_HOST=1.2.3.4 ./deploy_api.sh <usuario> <contraseña>" >&2
    exit 1
fi

RAIZ="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
ENV_LOCAL="$RAIZ/api/.env"
DESTINO="/home/$USUARIO/api/"
REMOTO="$USUARIO@$HOST"

if [ ! -f "$ENV_LOCAL" ]; then
    echo "Falta $ENV_LOCAL" >&2
    echo "Créalo con URL, USERNAME, PASSWORD y JWT_SECRET." >&2
    echo "Puedes basarte en el .env de la raíz y añadir JWT_SECRET." >&2
    exit 1
fi

if ! command -v rsync >/dev/null 2>&1; then
    echo "Falta rsync. En Ubuntu: sudo apt install rsync" >&2
    exit 1
fi

if ! command -v sshpass >/dev/null 2>&1; then
    echo "Falta sshpass." >&2
    echo "  Ubuntu: sudo apt install sshpass" >&2
    echo "  macOS:  brew install hudochenkov/sshpass/sshpass" >&2
    exit 1
fi

export SSHPASS="$PASS"
SSH_CMD="sshpass -e ssh -o StrictHostKeyChecking=accept-new -o ConnectTimeout=10"

echo "Subiendo $RAIZ/api/ -> $REMOTO:$DESTINO"
sshpass -e ssh -o StrictHostKeyChecking=accept-new -o ConnectTimeout=10 \
    "$REMOTO" "mkdir -p '$DESTINO'"

# Esta vaina borra en la VPS lo que ya no existe en local, salvo almacenamiento/
rsync -az --delete \
    --exclude '__pycache__/' \
    --exclude '.pytest_cache/' \
    --exclude '.venv/' \
    --exclude 'almacenamiento/' \
    -e "$SSH_CMD" \
    "$RAIZ/api/" "$REMOTO:$DESTINO"

sshpass -e ssh -o StrictHostKeyChecking=accept-new -o ConnectTimeout=10 \
    "$REMOTO" "chmod 600 '$DESTINO.env'"

echo "Listo."
echo "Reinicia el servicio en la VPS:"
echo "  ssh $REMOTO 'sudo systemctl restart edunet-api'"
