#!/usr/bin/env bash
set -euo pipefail

APP_SRC="${1:-/root/transferportal}"
APP_DIR="/opt/transferportal"

if [[ "$(id -u)" -ne 0 ]]; then
  echo "Run as root on the OMV host." >&2
  exit 1
fi

id transferportal >/dev/null 2>&1 || useradd --system --home-dir /var/lib/transferportal --shell /usr/sbin/nologin transferportal
install -d -o transferportal -g transferportal -m 0750 /var/lib/transferportal /var/log/transferportal
install -d -o root -g transferportal -m 0750 /etc/transferportal
install -d -o root -g root -m 0755 /usr/local/lib/transferportal
install -d -o root -g root -m 0755 "$APP_DIR"

rsync -a --delete \
  --exclude '.venv' \
  --exclude '__pycache__' \
  "$APP_SRC"/ "$APP_DIR"/

python3 -m venv "$APP_DIR/venv"
"$APP_DIR/venv/bin/python" -m pip install --upgrade pip
"$APP_DIR/venv/bin/python" -m pip install "$APP_DIR"

install -o root -g root -m 0755 "$APP_DIR/packaging/root-helper" /usr/local/lib/transferportal/root-helper
if [[ ! -f /etc/transferportal/config.yaml ]]; then
  install -o root -g transferportal -m 0660 "$APP_DIR/packaging/examples/config.yaml" /etc/transferportal/config.yaml
fi
chown root:transferportal /etc/transferportal/config.yaml
chmod 0660 /etc/transferportal/config.yaml
if [[ ! -f /etc/transferportal/session.secret ]]; then
  umask 0077
  python3 - <<'PY' >/etc/transferportal/session.secret
import secrets
print(secrets.token_urlsafe(48))
PY
  chown root:transferportal /etc/transferportal/session.secret
  chmod 0640 /etc/transferportal/session.secret
fi
if [[ ! -f /etc/transferportal/transferportal.env ]]; then
  install -o root -g transferportal -m 0640 "$APP_DIR/packaging/examples/transferportal.env.example" /etc/transferportal/transferportal.env
fi

install -o root -g root -m 0644 "$APP_DIR/packaging/systemd/transferportal.service" /etc/systemd/system/transferportal.service
install -o root -g root -m 0440 "$APP_DIR/packaging/sudoers/transferportal" /etc/sudoers.d/transferportal
visudo -cf /etc/sudoers.d/transferportal
systemctl daemon-reload
systemctl enable transferportal

echo "Installed. Edit /etc/transferportal/transferportal.env, then run: systemctl start transferportal"
