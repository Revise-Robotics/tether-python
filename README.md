# Tether

Lightweight JSON-RPC client for Arduino over serial.

Pair with [tether-arduino](https://github.com/Revise-Robotics/tether-arduino) on the device side.

## Install

```
pip install tether
```

## Usage

```python
from tether import Tether

device = Tether("/dev/ttyACM0")
device.ping()          # {"command": "ping", "status": "pong"}
device.get_a2()        # {"command": "get_a2", "raw": 512, "voltage": 2.5}
device.set_focus(0.5)  # positional arg sent as "value"
```

## License

MIT
