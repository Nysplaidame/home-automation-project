# Transfer Portal Cheat Sheet

Use this when copying data between two OMV-attached disks on the NAS itself.
It is a local disk-to-disk copy workflow, not a network transfer.

## Portal paths

- Source: `/srv/transferportal/source`
- Destination: `/srv/transferportal/destination`

## Start

```bash
rsync -aHAX --numeric-ids --info=progress2 /srv/transferportal/source/ /srv/transferportal/destination/
```

Backgrounded with a log:

```bash
nohup rsync -aHAX --numeric-ids --info=progress2 /srv/transferportal/source/ /srv/transferportal/destination/ >/tmp/transferportal-rsync.log 2>&1 &
```

## Monitor

```bash
pgrep -af 'rsync'
tail -f /tmp/transferportal-rsync.log
du -sh /srv/transferportal/source /srv/transferportal/destination
```

## Verify

```bash
find /srv/transferportal/source -type f | wc -l
find /srv/transferportal/destination -type f | wc -l
```

If the counts match and `rsync` exited cleanly, the copy is complete.

## If interrupted

- Finished files remain on the destination.
- In-progress files are normally temporary until complete.
- Run the same `rsync` command again to resume the comparison and copy.
- For large files where preserving partial progress matters, add
  `--partial-dir=.rsync-partial`.
