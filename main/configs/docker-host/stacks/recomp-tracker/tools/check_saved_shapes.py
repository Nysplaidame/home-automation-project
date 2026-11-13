"""Read-only validation of an existing database; prints section names only."""
import json
import sqlite3
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import app

conn = sqlite3.connect('file:' + sys.argv[1] + '?mode=ro', uri=True)
failed = False
for part, key in app.PART_KEYS.items():
    row = conn.execute('SELECT value FROM kv_store WHERE key=?', (key,)).fetchone()
    if not row:
        continue
    try:
        app.validate_part(part, json.loads(row[0]))
        print(part + ': valid')
    except (ValueError, TypeError) as error:
        failed = True
        print(part + ': ' + str(error))
conn.close()
sys.exit(1 if failed else 0)
