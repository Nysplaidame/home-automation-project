"""Frigate 0.17.1 configuration transport with single-owner PUB lifecycle.

Local overlay: the PUB socket is created, used, polled and closed exclusively
by its worker. Callers submit bounded synchronous requests, preserving multipart
ordering across API/MQTT threads. Idle EVENTS drains native connection commands.
ConfigSubscriber below is unchanged from the pinned upstream image.
"""

import multiprocessing as mp
import queue
import threading
from concurrent.futures import Future
from _pickle import UnpicklingError
from multiprocessing.synchronize import Event as MpEvent
from typing import Any

import zmq

SOCKET_PUB_SUB = "ipc:///tmp/cache/config"


class ConfigPublisher:
    """Serialize socket ownership and drain idle connection lifecycle work."""

    def __init__(self) -> None:
        self.stop_event: MpEvent = mp.Event()
        self._requests = queue.Queue(maxsize=64)
        self._lock = threading.Lock()
        self._ready = Future()
        self._closed = False
        self._worker = threading.Thread(target=self._run, name="config-publisher", daemon=True)
        self._worker.start()
        self._ready.result(timeout=5)

    def _run(self) -> None:
        context = zmq.Context()
        socket = None
        current = None
        try:
            socket = context.socket(zmq.PUB)
            socket.setsockopt(zmq.SNDTIMEO, 1000)
            socket.bind(SOCKET_PUB_SUB)
            self._ready.set_result(None)
            while True:
                # EVENTS processes attach/termination commands even when no
                # configuration changes are published. This is the owner thread.
                socket.getsockopt(zmq.EVENTS)
                try:
                    current = self._requests.get(timeout=0.1)
                except queue.Empty:
                    continue
                if current is None:
                    break
                topic, payload, result = current
                socket.send_string(topic, flags=zmq.SNDMORE)
                socket.send_pyobj(payload)
                result.set_result(None)
                current = None
        except Exception as error:
            if not self._ready.done():
                self._ready.set_exception(error)
            if current is not None and not current[2].done():
                current[2].set_exception(error)
            with self._lock:
                self._closed = True
            while True:
                try:
                    pending = self._requests.get_nowait()
                except queue.Empty:
                    break
                if pending is not None and not pending[2].done():
                    pending[2].set_exception(error)
        finally:
            if socket is not None:
                socket.close(linger=0)
            context.destroy(linger=0)

    def publish(self, topic: str, payload: Any) -> None:
        """Return when the complete multipart update has been sent."""
        result = Future()
        with self._lock:
            if self._closed or not self._worker.is_alive():
                raise RuntimeError("Configuration publisher is stopped")
            # Do not block while holding the shutdown lock; reject overload.
            self._requests.put_nowait((topic, payload, result))
        result.result(timeout=5)

    def stop(self) -> None:
        """Finish queued sends and close on the owner thread; safe to repeat."""
        with self._lock:
            if not self._closed:
                self._closed = True
                self.stop_event.set()
                # The worker keeps draining; sentinel insertion is outside lock.
                enqueue_stop = True
            else:
                enqueue_stop = False
        if enqueue_stop:
            self._requests.put(None, timeout=5)
        self._worker.join(timeout=5)
        if self._worker.is_alive():
            raise RuntimeError("Configuration publisher failed to stop")


class ConfigSubscriber:
    """Simplifies receiving an updated config."""

    def __init__(self, topic: str, exact: bool = False) -> None:
        self.topic = topic
        self.exact = exact
        self.context = zmq.Context()
        self.socket = self.context.socket(zmq.SUB)
        self.socket.setsockopt_string(zmq.SUBSCRIBE, topic)
        self.socket.connect(SOCKET_PUB_SUB)

    def check_for_update(self) -> tuple[str, Any] | tuple[None, None]:
        """Returns updated config or None if no update."""
        try:
            topic = self.socket.recv_string(flags=zmq.NOBLOCK)
            obj = self.socket.recv_pyobj()
            if not self.exact or self.topic == topic:
                return (topic, obj)
            else:
                return (None, None)
        except (zmq.ZMQError, UnicodeDecodeError, UnpicklingError):
            return (None, None)

    def stop(self) -> None:
        self.socket.close()
        self.context.destroy()
