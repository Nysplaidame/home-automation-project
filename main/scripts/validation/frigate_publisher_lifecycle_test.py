#!/usr/bin/env python3
"""Test the deployed publisher class on isolated IPC; never production config.

Run with Frigate Python/pyzmq. Optional --churn measures native RSS over 3600
subscriber reconnects with the actual repaired class and no forced GC/trim.
"""
import argparse
import concurrent.futures
import importlib.util
import json
import os
import tempfile
import time
import unittest
from pathlib import Path

import zmq

MODULE = None


def rss():
    return int(Path('/proc/self/statm').read_text().split()[1]) * os.sysconf('SC_PAGE_SIZE')


class LifecycleTests(unittest.TestCase):
    def setUp(self):
        self.directory = tempfile.TemporaryDirectory(prefix='frigate-publisher-test-')
        MODULE.SOCKET_PUB_SUB = 'ipc://' + self.directory.name + '/config'
        self.publisher = MODULE.ConfigPublisher()
        self.subscriber = MODULE.ConfigSubscriber('test/')
        time.sleep(.3)

    def tearDown(self):
        self.subscriber.stop()
        self.publisher.stop()
        self.directory.cleanup()

    def test_concurrent_multipart_delivery(self):
        def send(number):
            self.publisher.publish('test/' + str(number), {'number': number})
        with concurrent.futures.ThreadPoolExecutor(max_workers=8) as pool:
            list(pool.map(send, range(100)))
        seen = set()
        deadline = time.monotonic() + 3
        while len(seen) < 100 and time.monotonic() < deadline:
            topic, payload = self.subscriber.check_for_update()
            if topic is None:
                time.sleep(.01)
                continue
            self.assertEqual(topic, 'test/' + str(payload['number']))
            seen.add(payload['number'])
        self.assertEqual(seen, set(range(100)))

    def test_shutdown_and_reject_post_stop(self):
        self.publisher.stop()
        self.publisher.stop()
        self.assertFalse(self.publisher._worker.is_alive())
        with self.assertRaises(RuntimeError):
            self.publisher.publish('test/closed', {})

    def test_bind_failure_propagates(self):
        MODULE.SOCKET_PUB_SUB = 'ipc:///nonexistent/frigate-test/config'
        with self.assertRaises(zmq.ZMQError):
            MODULE.ConfigPublisher()


def churn():
    with tempfile.TemporaryDirectory(prefix='frigate-publisher-churn-') as directory:
        MODULE.SOCKET_PUB_SUB = 'ipc://' + directory + '/config'
        publisher = MODULE.ConfigPublisher()
        values = []
        try:
            for batch in range(6):
                for _ in range(600):
                    subscriber = MODULE.ConfigSubscriber('test/')
                    time.sleep(.003)
                    subscriber.stop()
                time.sleep(.5)
                values.append(rss())
            publisher.publish('test/after-churn', {'healthy': True})
        finally:
            publisher.stop()
        result = {'reconnects': 3600, 'rss_bytes_per_batch': values,
                  'growth_after_warmup_bytes': max(values[1:]) - values[0]}
        print(json.dumps(result))
        # The original retained ~13KiB per reconnect in the bounded reproduction.
        # Allow 8MiB allocator noise; reject sustained unbounded native growth.
        if result['growth_after_warmup_bytes'] > 8 * 1024 * 1024:
            raise SystemExit('Publisher retained excessive memory after warmup')


def live_churn():
    """Read-only subscriptions to the live publisher; no config messages sent."""
    main_pid = next(int(path.name) for path in Path('/proc').iterdir()
                    if path.name.isdigit() and (path / 'cmdline').exists()
                    and b'python3\x00-u\x00-m\x00frigate\x00' == (path / 'cmdline').read_bytes())
    def main_rss():
        return int(Path(f'/proc/{main_pid}/statm').read_text().split()[1]) * os.sysconf('SC_PAGE_SIZE')
    values = [main_rss()]
    for _ in range(6):
        for _ in range(2000):
            subscriber = MODULE.ConfigSubscriber('config/cameras')
            time.sleep(.003)
            subscriber.stop()
        time.sleep(.5)
        values.append(main_rss())
    print(json.dumps({'live_reconnects':12000, 'main_rss_bytes':values,
                      'growth_bytes':max(values[1:])-values[0]}))
    if max(values[1:])-values[0] > 64*1024*1024:
        raise SystemExit('Live publisher memory grew excessively; investigate before resizing')


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--module', default='/opt/frigate/frigate/comms/config_updater.py')
    parser.add_argument('--churn', action='store_true')
    parser.add_argument('--live-churn', action='store_true',
                        help='Explicit read-only churn against the live config endpoint')
    args = parser.parse_args()
    spec = importlib.util.spec_from_file_location('publisher_under_test', args.module)
    MODULE = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(MODULE)
    if args.live_churn:
        live_churn()
        raise SystemExit(0)
    result = unittest.TextTestRunner(verbosity=2).run(unittest.defaultTestLoader.loadTestsFromTestCase(LifecycleTests))
    if not result.wasSuccessful():
        raise SystemExit(1)
    if args.churn:
        churn()
