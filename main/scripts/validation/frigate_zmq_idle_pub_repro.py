#!/usr/bin/env python3
"""Reproduce idle ZeroMQ PUB connection retention without production sockets.

Run with Frigate's existing Python/pyzmq, in a separate process. The default
experiment takes about 15 seconds. It creates one unique /tmp IPC endpoint,
compares 600 subscriber reconnects with/without publisher event polling, and
prints RSS only. No camera, MQTT, database, or production socket is accessed.
Results depend on allocator/platform; compare deltas rather than fixed limits.
"""

import argparse
import ctypes
import json
import os
import time
import uuid

import zmq


def run(iterations: int) -> dict:
    libc = ctypes.CDLL(None)
    libc.malloc_trim.argtypes = [ctypes.c_size_t]
    libc.malloc_trim.restype = ctypes.c_int
    socket_path = f"/tmp/frigate-zmq-repro-{uuid.uuid4()}"
    context = zmq.Context()
    publisher = context.socket(zmq.PUB)
    publisher.bind(f"ipc://{socket_path}")

    def rss() -> int:
        with open("/proc/self/statm") as handle:
            return int(handle.read().split()[1]) * os.sysconf("SC_PAGE_SIZE")

    def poll() -> None:
        # EVENTS processes internal attach/terminate commands, without sending
        # configuration payloads. Always called on this socket's owner thread.
        publisher.getsockopt(zmq.EVENTS)

    def churn(process_events: bool) -> None:
        for _ in range(iterations):
            child_context = zmq.Context()
            subscriber = child_context.socket(zmq.SUB)
            try:
                subscriber.setsockopt(zmq.SUBSCRIBE, b"config/cameras/test")
                subscriber.connect(f"ipc://{socket_path}")
                time.sleep(0.01)
            finally:
                subscriber.close(linger=0)
                child_context.destroy(linger=0)
            if process_events:
                poll()
                time.sleep(0.002)
                poll()
        time.sleep(0.3)

    try:
        baseline = rss()
        churn(False)
        retained = rss()
        for _ in range(3):
            poll()
            time.sleep(0.4)
        libc.malloc_trim(0)
        drained = rss()
        churn(True)
        libc.malloc_trim(0)
        return {
            "pyzmq": zmq.__version__,
            "libzmq": zmq.zmq_version(),
            "iterations_per_case": iterations,
            "rss_bytes": {
                "baseline": baseline,
                "idle_publisher_after_churn": retained,
                "after_events_and_trim": drained,
                "regular_events_after_churn": rss(),
            },
        }
    finally:
        publisher.close(linger=0)
        context.destroy(linger=0)
        try:
            os.unlink(socket_path)
        except FileNotFoundError:
            pass


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--iterations", type=int, default=600)
    args = parser.parse_args()
    if not 1 <= args.iterations <= 5000:
        parser.error("--iterations must be between 1 and 5000")
    print(json.dumps(run(args.iterations), indent=2))
