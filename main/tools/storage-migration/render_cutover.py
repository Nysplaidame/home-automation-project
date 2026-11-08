"""Render reviewable future configuration; never edits or deploys live files."""
import argparse
import ast
import difflib
import json
from pathlib import Path
import uuid

HERE = Path(__file__).resolve().parent
MAIN = HERE.parents[1]
OLD_Y = "fdb92af7-371c-4793-8d98-ff47e961498d"
OLD_Z = "a216b8bb-708e-4342-a5be-a415cdc465fa"


def replace_once(text, old, new):
    if old not in text and text.count(new) == 1:
        return text  # This canonical source has already crossed its cutover.
    if text.count(old) != 1:
        raise ValueError("Source changed; refusing an ambiguous replacement: " + old)
    return text.replace(old, new, 1)


def render(media_uuid, output):
    media_uuid = str(uuid.UUID(media_uuid))
    if media_uuid in {OLD_Y, OLD_Z}:
        raise ValueError("Expected the new Media array filesystem UUID")
    output = Path(output)
    if output.exists() or output.is_symlink():
        raise ValueError("Output directory must be new")
    root = "/srv/dev-disk-by-uuid-" + media_uuid
    contract = json.loads((HERE / "cutover-contract.json").read_text(encoding="utf-8"))
    artifacts = {}
    options = "rw,_netdev,nofail,x-systemd.automount,x-systemd.idle-timeout=300,x-systemd.mount-timeout=30s,vers=3,hard,proto=tcp,timeo=50,retrans=2"
    mounts = {"z": [], "y": []}
    expected_mounts = {}
    exports = []
    for row in contract["exports"]:
        row["backing_path"] = root + "/" + row["relative"]
        source = contract["server"] + ":/export/" + row["name"]
        row["source"] = source
        squash = "root_squash" if row["root_squash"] else "no_root_squash"
        exports.append(f"/export/{row['name']} {row['client']}(rw,sync,no_subtree_check,{squash},sec=sys)")
        if row["client"] == "192.168.20.102":
            mounts[row["phase"]].append(f"{source} {row['mount']} nfs {options} 0 0")
            expected_mounts[row["mount"]] = source
    contract["media_uuid"] = media_uuid
    contract["media_root"] = root
    contract["pseudo_root_clients"] = ["192.168.10.10", "192.168.20.101", "192.168.20.102"]
    artifacts["desired-omv-contract.json"] = json.dumps(contract, indent=2)
    for phase, lines in mounts.items():
        artifacts[f"docker-host-{phase}.fstab"] = "\n".join(lines) + "\n"
    artifacts["exports.reference"] = "\n".join(exports) + "\n"
    artifacts["expected-docker-mounts.json"] = json.dumps(expected_mounts, indent=2)
    calibre_path = "configs/docker-host/stacks/calibre-web/docker-compose.yml"
    calibre = (MAIN / calibre_path).read_text(encoding="utf-8")
    changed_calibre = replace_once(calibre, "/mnt/omv/media/books/calibre-library:/books", "/mnt/omv/calibre-library:/books")
    artifacts["calibre-web.compose.patch"] = "".join(difflib.unified_diff(
        calibre.splitlines(keepends=True), changed_calibre.splitlines(keepends=True),
        fromfile="a/main/" + calibre_path, tofile="b/main/" + calibre_path))
    old = "/srv/dev-disk-by-uuid-" + OLD_Y
    script = (MAIN / "configs/omv/system/omv-config-backup.sh").read_text(encoding="utf-8")
    script = script.replace(old + "/backups/configs/omv-config", root + "/backups/configs/omv-config")
    begin = script.index("mount_source=")
    end = script.index("\numask 077", begin)
    script = script[:begin] + (
        f'actual_uuid=$(findmnt -rn --mountpoint "{root}" -o UUID 2>/dev/null || true)\n'
        f'test "$actual_uuid" = "{media_uuid}" || {{ echo "Wrong or missing Media filesystem" >&2; exit 3; }}\n'
    ) + script[end:]
    artifacts["omv-config-backup.sh"] = script
    service = (MAIN / "configs/omv/system/omv-config-backup.service").read_text(encoding="utf-8")
    service = service.replace(old + "/backups/configs", root + "/backups/configs")
    artifacts["omv-config-backup.service"] = service.replace("to md0", "to Media mirror")
    media_backup = (MAIN / "configs/docker-host/system/mediamtx-config-backup.sh").read_text(encoding="utf-8")
    artifacts["mediamtx-config-backup.sh"] = replace_once(
        media_backup, "192.168.40.50:" + old + "/backups/docker-host",
        "192.168.40.50:/export/backups-docker-host")
    artifacts["backup-client-commands.txt"] = (
        "# Proxmox: preserve storage ID, schedules and retention\n"
        "pvesm set omv-backups --export /export/backups-proxmox\n"
        "# Home Assistant: preserve logical name, backup usage and default selection\n"
        "ha mounts update nas_backups --type nfs --usage backup --server 192.168.40.50 --path /export/backups-home-assistant\n"
        "ha mounts reload nas_backups\n")
    collector_path = "configs/omv/system/omv-health-snapshot.py"
    collector = (MAIN / collector_path).read_text(encoding="utf-8")
    datasets = [node for node in ast.parse(collector).body if isinstance(node, ast.Assign)
                and any(isinstance(t, ast.Name) and t.id == "DATASETS" for t in node.targets)]
    if len(datasets) != 1:
        raise ValueError("Collector dataset contract changed; review before rendering")
    current_media_uuid = ast.literal_eval(datasets[0].value)["14tb"]
    uuid.UUID(current_media_uuid)
    changed = replace_once(collector, current_media_uuid, media_uuid)
    artifacts["omv-health-snapshot.patch"] = "".join(difflib.unified_diff(
        collector.splitlines(keepends=True), changed.splitlines(keepends=True),
        fromfile="a/main/" + collector_path, tofile="b/main/" + collector_path))
    diagnostics_path = "apps/troubleshooting-dashboard/additional-routes.js"
    diagnostics = (MAIN / diagnostics_path).read_text(encoding="utf-8")
    changed = diagnostics
    mount_paths = list(expected_mounts)
    changed = replace_once(changed, "findmnt -T /mnt/omv/immich; findmnt -T /mnt/omv/media",
                           "; ".join("findmnt --mountpoint " + name for name in mount_paths))
    changed = replace_once(changed,
        "df -h /mnt/omv/immich /mnt/omv/media; df -i /mnt/omv/immich /mnt/omv/media",
        "df -h " + " ".join(mount_paths) + "; df -i " + " ".join(mount_paths))
    old_command = "findmnt -T /mnt/omv/media; df -h /mnt/omv/media"
    if changed.count(old_command) not in {0, 3}:
        raise ValueError("Diagnostics media commands changed; review before rendering")
    for paths in (["/mnt/omv/media/jellyfin", "/mnt/omv/media/comics", "/mnt/omv/calibre-library"],
                  ["/mnt/omv/media/incoming"], ["/mnt/omv/media/phone-recordings"]):
        new_command = "; ".join("findmnt --mountpoint " + p for p in paths) + "; df -h " + " ".join(paths)
        if old_command in changed:
            changed = changed.replace(old_command, new_command, 1)
        elif changed.count(new_command) != 1:
            raise ValueError("Already-cut-over diagnostics command changed")
    artifacts["troubleshooting-storage.patch"] = "".join(difflib.unified_diff(
        diagnostics.splitlines(keepends=True), changed.splitlines(keepends=True),
        fromfile="a/main/" + diagnostics_path, tofile="b/main/" + diagnostics_path))
    for label, backing in (("Print", "/srv/dev-disk-by-uuid-" + OLD_Y), ("Media", root)):
        artifacts[f"srv-filebrowser-{label}.mount"] = (
            f"[Unit]\nDescription=Filebrowser {label} dataset view\nRequiresMountsFor={backing}\n"
            "Before=container-filebrowser-app.service\n\n[Mount]\n"
            f"What={backing}\nWhere=/srv/filebrowser/{label}\nType=none\nOptions=bind\n\n"
            "[Install]\nWantedBy=multi-user.target\n")
    artifacts["filebrowser-storage.conf"] = (
        "[Unit]\nRequires=srv-filebrowser-Print.mount srv-filebrowser-Media.mount\n"
        "After=srv-filebrowser-Print.mount srv-filebrowser-Media.mount\n"
        "BindsTo=srv-filebrowser-Print.mount srv-filebrowser-Media.mount\n\n"
        "[Service]\nExecStartPre=/usr/bin/python3 /usr/local/sbin/assert-local-storage.py /etc/household-storage/filebrowser-mounts.json\n")
    artifacts["filebrowser-mounts.json"] = json.dumps({
        "/srv/dev-disk-by-uuid-" + OLD_Y: OLD_Y, root: media_uuid,
        "/srv/filebrowser/Print": OLD_Y, "/srv/filebrowser/Media": media_uuid,
    }, indent=2)
    artifacts["filebrowser-view.json"] = json.dumps({
        "sharedfolder_name": "filebrowser-view", "root_filesystem_mountpoint": "/",
        "relative_path": "srv/filebrowser/", "requires_installed_plugin": "openmediavault-sharerootfs",
        "filebrowser_sharedfolderref": "resolve UUID of the new filebrowser-view shared folder",
        "container_source_path_unchanged": "/srv/", "admin_scope_unchanged": {"name": "/srv", "scope": "/"},
        "preserve": ["existing account, authentication, port 3670, certificate, persistent /var/lib/filebrowser"],
        "preflight": "reconfirm the single admin account and scopes; do not carry this assumption across new accounts"
    }, indent=2)
    artifacts = {name: body for name, body in artifacts.items()
                 if body or not name.endswith(".patch")}
    output.mkdir(mode=0o700)
    for name, body in artifacts.items():
        (output / name).write_text(body, encoding="utf-8", newline="\n")
    return sorted(artifacts)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--media-uuid", required=True)
    parser.add_argument("--output", required=True)
    args = parser.parse_args()
    print(json.dumps(render(args.media_uuid, args.output), indent=2))
