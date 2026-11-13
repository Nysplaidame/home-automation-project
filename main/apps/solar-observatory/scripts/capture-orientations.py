"""Explicit fixture generation only; needs spiceypy==8.2.0, never a runtime dependency."""
import hashlib
import json
from pathlib import Path
import urllib.request

import spiceypy as spice

root = Path(__file__).resolve().parent.parent
cache = root / ".cache" / "orientation-kernels"
cache.mkdir(parents=True, exist_ok=True)
sources = []
for folder, name in [("pck", "pck00011.tpc"), ("lsk", "naif0012.tls")]:
    url = f"https://naif.jpl.nasa.gov/pub/naif/generic_kernels/{folder}/{name}"
    path = cache / name
    urllib.request.urlretrieve(url, path)
    sources.append({"url": url, "sha256": hashlib.sha256(path.read_bytes()).hexdigest()})
    spice.furnsh(str(path))

dates = ["2017-01-01T00:00:00", "2020-02-29T12:34:56", "2024-04-08T18:00:00",
         "2026-10-04T00:00:00", "2026-10-04T01:00:00", "2026-10-04T02:00:00",
         "2026-12-31T23:59:59", "2027-06-30T23:59:59"]
samples = []
for date in dates:
    et = spice.str2et(date.replace("T", " ") + " UTC")
    for body in ["earth", "moon"]:
        matrix = spice.pxform("IAU_" + body.upper(), "J2000", et)
        samples.append({"utc": date + "Z", "body": body, "tdbSeconds": et,
                        "axes": {axis: matrix[:, i].tolist() for i, axis in enumerate("xyz")}})
fixture = {"generator": f"SpiceyPy {spice.__version__} / {spice.tkvrsn('TOOLKIT')}",
           "model": "IAU_EARTH / IAU_MOON text-PCK, not precision EOP or binary lunar PCK",
           "sources": sources, "samples": samples}
(root / "tests" / "fixtures" / "orientations.json").write_text(
    json.dumps(fixture, indent=2) + "\n", encoding="utf-8")
spice.kclear()
print(f"Captured {len(samples)} independent SPICE orientation samples")
