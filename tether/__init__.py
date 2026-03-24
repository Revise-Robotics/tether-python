"""Tether — lightweight Python client for Tether Arduino RPC."""

__version__ = "0.1.0"
__all__ = ["Tether", "TetherError", "TetherTimeout"]

import json
import time

import serial


class TetherError(Exception):
    """Raised when the Arduino returns an error response."""


class TetherTimeout(TetherError):
    """Raised when no response is received within the timeout."""


class Tether:
    """
    JSON-RPC client for an Arduino running the Tether library.

    Usage:
        device = Tether("/dev/ttyACM0")
        device.ping()              # {"command": "ping", "status": "pong"}
        device.get_a2()            # {"command": "get_a2", "raw": 0, "voltage": 0.0}
        device.set_focus(0.5)      # positional arg sent as "value"
        device.set_focus(value=0.5, zoom=3)  # kwargs sent as-is
    """

    def __init__(self, serial_port="/dev/ttyACM0", baud=9600, timeout=5.0):
        self._timeout = timeout
        self._ser = serial.Serial(serial_port, baud, timeout=timeout)
        # Arduino resets on serial open — wait for boot
        time.sleep(2)
        self._ser.reset_input_buffer()

    def close(self):
        if self._ser and self._ser.is_open:
            self._ser.close()

    def __enter__(self):
        return self

    def __exit__(self, *args):
        self.close()

    def call(self, command, *args, **kwargs):
        """
        Send a command and return the parsed response dict.

        Positional args: first arg is sent as "value".
        Keyword args: sent as named fields in the JSON payload.
        """
        payload = {"command": command}

        if args:
            payload["value"] = args[0]

        payload.update(kwargs)

        line = json.dumps(payload, separators=(",", ":")) + "\n"
        self._ser.write(line.encode())

        # Read response line
        raw = self._ser.readline()
        if not raw:
            raise TetherTimeout(f"No response for '{command}' within {self._timeout}s")

        raw = raw.decode().strip()
        if not raw:
            raise TetherTimeout(f"Empty response for '{command}'")

        resp = json.loads(raw)

        if "error" in resp:
            raise TetherError(resp["error"])

        return resp

    def __getattr__(self, name):
        """Dynamic RPC: device.any_command(...) sends that command to the Arduino."""
        if name.startswith("_"):
            raise AttributeError(name)

        def rpc_call(*args, **kwargs):
            return self.call(name, *args, **kwargs)

        return rpc_call

    def __repr__(self):
        port = self._ser.port if self._ser else "closed"
        return f"Tether({port!r})"
