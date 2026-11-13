#!/usr/bin/env python3
"""Tiny logging reverse proxy for llama-server (stdlib only). Run inside CT 114 during a test window.

  python3 capture_proxy.py --listen 8081 --target http://127.0.0.1:8083 --out /root/captured.jsonl

Forwards every request unchanged and appends each POST /v1/chat/completions body (plus timings from
the response) as one JSON line, so real Home Assistant requests can be replayed with replay_bench.py.
"""
import argparse
import json
import time
import urllib.request
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer

args = None


class Handler(BaseHTTPRequestHandler):
    protocol_version = "HTTP/1.0"

    def _forward(self):
        body = None
        if self.command == "POST":
            body = self.rfile.read(int(self.headers.get("Content-Length") or 0))
        req = urllib.request.Request(
            args.target + self.path, data=body, method=self.command,
            headers={k: v for k, v in self.headers.items() if k.lower() not in ("host", "content-length")},
        )
        t0 = time.time()
        try:
            with urllib.request.urlopen(req, timeout=600) as r:
                data, status, ctype = r.read(), r.status, r.headers.get("Content-Type", "application/json")
        except urllib.error.HTTPError as e:
            data, status, ctype = e.read(), e.code, e.headers.get("Content-Type", "application/json")
        self.send_response(status)
        self.send_header("Content-Type", ctype)
        self.send_header("Content-Length", str(len(data)))
        self.end_headers()
        self.wfile.write(data)
        if body and self.path.startswith("/v1/chat/completions"):
            try:
                resp = json.loads(data)
                timings = resp.get("timings")
                usage = resp.get("usage")
            except Exception:
                timings = usage = None
            with open(args.out, "a", encoding="utf-8") as f:
                f.write(json.dumps({"t": t0, "wall": round(time.time() - t0, 2), "request": json.loads(body),
                                    "timings": timings, "usage": usage}) + "\n")

    do_GET = do_POST = _forward

    def log_message(self, *a):
        pass


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--listen", type=int, default=8081)
    ap.add_argument("--target", default="http://127.0.0.1:8083")
    ap.add_argument("--out", default="/root/captured.jsonl")
    args = ap.parse_args()
    ThreadingHTTPServer(("0.0.0.0", args.listen), Handler).serve_forever()
