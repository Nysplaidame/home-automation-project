# Isolated GardenKeeper recovery rehearsal

This tool uses synthetic records, a real PostgreSQL dump/restore, copied journal
media and loopback ntfy/CalDAV service doubles. It never loads production config.
It does not certify a production checkpoint, real-user uploads or live integrations.

## Run

Use Python with the GardenKeeper API/worker requirements, pytest, uvicorn and
httpx installed. Start a disposable PostgreSQL 17 instance bound to loopback.
Create two empty databases beginning `garden_rehearsal`, for example
`garden_rehearsal_source` and `garden_rehearsal_restored`.

From PowerShell, use absolute paths for every argument:

```powershell
$env:DATABASE_URL = 'postgresql+psycopg://postgres:TEST_PASSWORD@127.0.0.1:55435/garden_rehearsal_source'
python rehearse.py seed --source-repo C:\source\garden-keeper-app --state-dir C:\scratch\seed --manifest C:\scratch\manifest.json
```

The seed process exits, leaving a cold application checkpoint. With PostgreSQL
client tools (or `docker exec` inside the disposable database container), dump the
source database using `pg_dump -Fc`, restore it into the second empty database
using `pg_restore --exit-on-error --no-owner`, and copy `seed/media` to
`restored/media`. Preserve the manifest beside the checkpoint. Do not copy logs,
credentials or a live `.env` file. The `restored` directory must exist.

```powershell
$env:DATABASE_URL = 'postgresql+psycopg://postgres:TEST_PASSWORD@127.0.0.1:55435/garden_rehearsal_restored'
python rehearse.py verify --source-repo C:\source\garden-keeper-app --state-dir C:\scratch\restored --manifest C:\scratch\manifest.json
```

Verify starts a fresh API process and isolated HTTP services, then checks:

- API readiness and the restored journal's media URL.
- Downloaded photo bytes and SHA-256 against the checkpoint manifest.
- A pending notification delivers once across two successful dispatch passes.
- A fresh calendar worker removes owned stale entries, publishes restored
  records, removes a subsequently cancelled event after another restart and
  preserves an unrelated calendar object.

Read `restored/acceptance.json`. Verification consumes the notification and
cancels the synthetic event: restore a fresh database/media copy before rerunning.
Remove only the disposable databases/container after saving evidence.

## October 3 result

Passed using PostgreSQL 17, separate source/restored databases and a fresh Python
process. A 2,097,220-byte synthetic PNG and its journal URL matched. Notification
dispatch and calendar restart reconciliation passed. This exposed and fixed UTC
notification scheduling and cancelled-event projection issues in GardenKeeper.
Production/full-system recovery remains open in the canonical task list.
