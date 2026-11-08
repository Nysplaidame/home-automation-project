#!/bin/sh
set -eu

DEST_ROOT="${DEST_ROOT:-/srv/dev-disk-by-uuid-a8843f98-c937-48a8-aefa-4cd0fb80667c/backups/configs/omv-config}"
timestamp=$(date -u +%Y%m%dT%H%M%SZ)
runs_dir="${DEST_ROOT}/runs"
tmp_dir="${runs_dir}/.${timestamp}.tmp"
final_dir="${runs_dir}/${timestamp}"

case "$DEST_ROOT" in
  /srv/dev-disk-by-uuid-a8843f98-c937-48a8-aefa-4cd0fb80667c/backups/configs/omv-config) ;;
  *) echo "Refusing unexpected destination: $DEST_ROOT" >&2; exit 2 ;;
esac

actual_uuid=$(findmnt -rn --mountpoint "/srv/dev-disk-by-uuid-a8843f98-c937-48a8-aefa-4cd0fb80667c" -o UUID 2>/dev/null || true)
test "$actual_uuid" = "a8843f98-c937-48a8-aefa-4cd0fb80667c" || { echo "Wrong or missing Media filesystem" >&2; exit 3; }

umask 077
install -d -m 0700 "$runs_dir"
test ! -e "$tmp_dir"
test ! -e "$final_dir"
install -d -m 0700 "$tmp_dir"

cp -a /etc/openmediavault/config.xml "$tmp_dir/config.xml"
cp -a /etc/exports "$tmp_dir/exports"
cp -a /etc/exports.d "$tmp_dir/exports.d"
cp -a /etc/fstab "$tmp_dir/fstab"
exportfs -v > "$tmp_dir/exportfs-v.txt"
showmount -e 127.0.0.1 > "$tmp_dir/showmount-e.txt"
findmnt -rn -o TARGET,SOURCE,FSTYPE,OPTIONS > "$tmp_dir/findmnt.txt"
omv-confdbadm read --prettify conf.service.nfs > "$tmp_dir/nfs-service.json"
omv-confdbadm read --prettify conf.service.nfs.share > "$tmp_dir/nfs-shares.json"
omv-confdbadm read --prettify conf.system.sharedfolder > "$tmp_dir/sharedfolders.json"

(
  cd "$tmp_dir"
  find . -type f ! -name SHA256SUMS -print0 \
    | sort -z \
    | xargs -0 sha256sum > SHA256SUMS
)

chmod -R go-rwx "$tmp_dir"
mv "$tmp_dir" "$final_dir"
ln -sfn "runs/${timestamp}" "${DEST_ROOT}/latest.new"
mv -Tf "${DEST_ROOT}/latest.new" "${DEST_ROOT}/latest"

printf 'OMV config backup complete: %s\n' "$final_dir"
