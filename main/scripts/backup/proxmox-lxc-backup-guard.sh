#!/bin/sh
# Audit and optionally clear stale Proxmox LXC backup/snapshot state.
# Run on: Proxmox host.
# Default mode is read-only. Use --apply only after reviewing the audit output.

set -eu

APPLY=0
CTS="111 114"

usage() {
    cat <<'EOF'
Usage: proxmox-lxc-backup-guard.sh [--apply] [CTID ...]

Audits Proxmox LXC guests for stale backup/snapshot locks and leftover vzdump
snapshot markers. In read-only mode it prints findings and suggested actions.
With --apply it refuses to run if backup/snapshot processes are active, then
clears only known backup-related locks and the standard vzdump snapshot marker.

Examples:
  ./proxmox-lxc-backup-guard.sh
  ./proxmox-lxc-backup-guard.sh --apply 111
EOF
}

while [ "$#" -gt 0 ]; do
    case "$1" in
        --apply)
            APPLY=1
            shift
            ;;
        -h|--help)
            usage
            exit 0
            ;;
        *)
            CTS="$*"
            break
            ;;
    esac
done

need_cmd() {
    if ! command -v "$1" >/dev/null 2>&1; then
        echo "ERROR: required command not found: $1" >&2
        exit 2
    fi
}

need_cmd pct
need_cmd pgrep

active_jobs() {
    pgrep -af '(^|[ /])(vzdump|vzdump\.pl|snapshot-delete|lxc-usernsexec|pct[[:space:]].*(snapshot|delsnapshot|restore|unlock))' \
        | grep -v 'proxmox-lxc-backup-guard.sh' \
        | grep -v 'pgrep -af' || true
}

ACTIVE="$(active_jobs)"

if [ -n "$ACTIVE" ]; then
    echo "Active backup/snapshot-related process found:"
    echo "$ACTIVE"
    if [ "$APPLY" -eq 1 ]; then
        echo "Refusing --apply while a matching process is active." >&2
        exit 3
    fi
    echo
fi

EXIT_STATUS=0

for CTID in $CTS; do
    echo "== CT $CTID =="

    if ! pct status "$CTID" >/dev/null 2>&1; then
        echo "WARN: CT $CTID does not exist or pct cannot read it."
        EXIT_STATUS=1
        echo
        continue
    fi

    CONFIG="$(pct config "$CTID" 2>/dev/null || true)"
    LOCK="$(printf '%s\n' "$CONFIG" | awk '/^lock:/ {print $2; exit}')"

    SNAPSHOTS="$(pct listsnapshot "$CTID" 2>/dev/null || true)"
    HAS_VZDUMP=0
    if printf '%s\n' "$SNAPSHOTS" | awk '{print $1}' | grep -qx 'vzdump'; then
        HAS_VZDUMP=1
    fi

    STATUS="$(pct status "$CTID" 2>/dev/null | awk '{print $2}')"
    echo "status: ${STATUS:-unknown}"
    echo "lock: ${LOCK:-none}"
    if [ "$HAS_VZDUMP" -eq 1 ]; then
        echo "snapshot: vzdump marker present"
    else
        echo "snapshot: no vzdump marker"
    fi

    case "${LOCK:-}" in
        "")
            ;;
        backup|snapshot|snapshot-delete)
            if [ "$APPLY" -eq 1 ]; then
                echo "action: pct unlock $CTID"
                pct unlock "$CTID"
            else
                echo "suggested: pct unlock $CTID, only after confirming no active vzdump/snapshot job"
            fi
            ;;
        *)
            echo "WARN: non-backup lock '${LOCK}' found; manual review required."
            EXIT_STATUS=1
            ;;
    esac

    if [ "$HAS_VZDUMP" -eq 1 ]; then
        if [ "$APPLY" -eq 1 ]; then
            echo "action: pct delsnapshot $CTID vzdump --force"
            pct delsnapshot "$CTID" vzdump --force
        else
            echo "suggested: pct delsnapshot $CTID vzdump --force, only after confirming the snapshot is stale"
        fi
    fi

    echo
done

exit "$EXIT_STATUS"
