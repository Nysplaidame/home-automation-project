# Immich Rebuild Template

Copy `.env.example` to the untracked, mode-`0600` `.env` on docker-host and
replace `<IMMICH_DB_PASSWORD>` through the secrets workflow.

`UPLOAD_LOCATION` must remain the verified OMV NFS mount
`/mnt/omv/immich`. Stop `immich-server` whenever that mount is absent or resolves
to the local VM filesystem; never allow uploads into an accidental local
fallback directory.

`DB_DATA_LOCATION=./postgres` keeps PostgreSQL data local to VM 103 and it must
be backed up consistently with the OMV media tree. Pin and record the accepted
Immich release before a production update. The machine-learning container may
remain stopped when VM capacity policy requires it; record that as intentional,
not failed health.
