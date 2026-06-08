# 52Pi ZP-0187 OLED Setup Guide

This guide sets up the OLED screen from a clean Raspberry Pi OS install through a working `systemd` service.

It uses the working structure we established during setup:

- no hardcoded `/home/pi`
- a dedicated project folder under your real home directory
- a Python virtual environment kept separate from the system install
- a simplified `systemd` service file
- the final `sys_info.py` script with five display rows

## 1. Confirm Your User and Home Folder

The original tutorial assumes the default user is `pi`. On newer Raspberry Pi OS images that is often not true.

Run:

```bash
whoami
echo $HOME
```

Use the output from those commands everywhere this guide says `YOUR_USERNAME` or `/home/YOUR_USERNAME`.

Example:

```bash
whoami
admin

echo $HOME
/home/admin
```

In that case, replace:

- `YOUR_USERNAME` with `admin`
- `/home/YOUR_USERNAME` with `/home/admin`

## 2. Update the System

Install the base packages needed by the OLED example and its dependencies.

```bash
sudo apt update
sudo apt upgrade -y
sudo apt install -y \
  git \
  python3 \
  python3-venv \
  python3-pip \
  python3-dev \
  python3-pil \
  i2c-tools
```

If you are using the OLED from the 52Pi kit, also make sure I2C is enabled:

```bash
sudo raspi-config
```

Then go to:

```text
Interface Options -> I2C -> Enable
```

Add your user to the device groups used by the display and fan hardware:

```bash
sudo usermod -aG gpio,i2c YOUR_USERNAME
```

Reboot after enabling it:

```bash
sudo reboot
```

## 3. Create a Clean Project Folder

Use one dedicated folder for the OLED setup.

```bash
mkdir -p ~/oled
cd ~/oled
```

## 4. Create the Virtual Environment

Create the environment outside the repo so the paths stay easy to understand.

```bash
python3 -m venv venv
source venv/bin/activate
```

You should now see `(venv)` in your shell prompt.

Upgrade `pip` inside the virtual environment:

```bash
pip install --upgrade pip
```

## 5. Get the Example Code

Clone the `luma.examples` repository into the same project folder:

```bash
git clone https://github.com/rm-hull/luma.examples.git
```

Install the local package in editable mode:

```bash
cd ~/oled/luma.examples
pip install -e .
```

If the install asks for extra packages, install them inside the virtual environment, not system-wide.

## 6. Install Python Dependencies

The example script uses `psutil`, so install it in the virtual environment:

```bash
pip install psutil
```

If your install complains about Pillow or other graphics dependencies, the earlier `apt` packages usually cover them.

## 7. Confirm the Example Works Before Systemd

Before making a service, test the script manually.

```bash
cd ~/oled/luma.examples/examples
~/oled/venv/bin/python3 sys_info.py
```

If the OLED lights up and shows data, the wiring and libraries are working.

If it fails, fix it here before moving on. The most useful quick checks are:

```bash
~/oled/venv/bin/python3 -m py_compile ~/oled/luma.examples/examples/sys_info.py
systemctl status minitower_oled.service --no-pager -l
```

## 8. Replace `sys_info.py`

Use the final version below. It keeps the original layout, adds a CPU temperature readout in the first row, and keeps the fifth IP row visible.

Save this as:

```text
~/oled/luma.examples/examples/sys_info.py
```

```python
#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Copyright (c) 2014-2022 Richard Hull and contributors
# See LICENSE.rst for details.
# PYTHON_ARGCOMPLETE_OK

"""
Display basic system information.

Needs psutil (+ dependencies) installed::

  $ sudo apt-get install python-dev
  $ sudo -H pip install psutil
"""

import os
import signal
import sys
import time
import socket
from pathlib import Path
from datetime import datetime

if os.name != 'posix':
    sys.exit(f'{os.name} platform is not supported')

from demo_opts import get_device
from luma.core.render import canvas
from PIL import ImageFont

try:
    import psutil
except ImportError:
    print("The psutil library was not found. Run 'sudo -H pip install psutil' to install it.")
    sys.exit()


# TODO: custom font bitmaps for up/down arrows
# TODO: Load histogram


class IPAddressChecker:
    def __init__(self, cache_duration_in_seconds=14400):
        """
        :param cache_duration_in_seconds: The duration in seconds to cache the IP address for. Default is 4 hours.
        """
        self._ip_address = None
        self._last_checked = None
        self._cache_duration = cache_duration_in_seconds

    def get_ip_address(self):
        if self._last_checked is None or time.time() - self._last_checked > self._cache_duration:
            self._ip_address = self._retrieve_ip_address()
            self._last_checked = time.time()
        return self._ip_address

    @staticmethod
    def _retrieve_ip_address():
        try:
            with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as s:
                s.connect(("8.8.8.8", 80))  # Google DNS. Probably will never be down.
                return s.getsockname()[0]
        except Exception as e:
            print(f"Error: {e}")
            return ""


def shutdown(signum, frame):
    device.clear()
    sys.exit(0)


signal.signal(signal.SIGTERM, shutdown)
signal.signal(signal.SIGINT, shutdown)


def bytes2human(n):
    """
    >>> bytes2human(10000)
    '9K'
    >>> bytes2human(100001221)
    '95M'
    """
    symbols = ('K', 'M', 'G', 'T', 'P', 'E', 'Z', 'Y')
    prefix = {}
    for i, s in enumerate(symbols):
        prefix[s] = 1 << (i + 1) * 10
    for s in reversed(symbols):
        if n >= prefix[s]:
            value = int(float(n) / prefix[s])
            return '%s%s' % (value, s)
    return f"{n}B"


def cpu_usage():
    uptime = datetime.now() - datetime.fromtimestamp(psutil.boot_time())
    days = uptime.days
    hours, _ = divmod(uptime.seconds, 3600)

    cpu_percent = psutil.cpu_percent(interval=1)

    try:
        with open("/sys/class/thermal/thermal_zone0/temp") as f:
            temp_c = int(f.read().strip()) / 1000
        temp = "%.0f\u00b0" % temp_c
    except Exception:
        temp = "n/a"

    return "CPU: %d%%/%s Up:%dd%dh" % (cpu_percent, temp, days, hours)


def mem_usage():
    usage = psutil.virtual_memory()
    return "RAM: %s/%s (%.0f%%)" % (
        bytes2human(usage.used),
        bytes2human(usage.total),
        usage.percent
    )


def disk_usage(dir):
    usage = psutil.disk_usage(dir)
    return "SD: %s/%s (%.0f%%)" % (
        bytes2human(usage.used),
        bytes2human(usage.total),
        usage.percent
    )


def network(iface):
    stat = psutil.net_io_counters(pernic=True)[iface]
    return "%s: Tx%s, Rx%s" % (
        iface,
        bytes2human(stat.bytes_sent),
        bytes2human(stat.bytes_recv)
    )


def stats(device):
    # use custom font
    font_path = str(Path(__file__).resolve().parent.joinpath('fonts', 'DejaVuSansMono.ttf'))
    font2 = ImageFont.truetype(font_path, 10)
    ascent, descent = font2.getmetrics()
    line_height = ascent + descent

    with canvas(device) as draw:
        draw.rectangle(device.bounding_box, outline="white", fill=None)
        draw.text((2, line_height * 0), cpu_usage(), font=font2, fill="white")

        if device.height >= (line_height * 2):
            draw.text((2, line_height * 1), mem_usage(), font=font2, fill="white")

        if device.height >= (line_height * 3):
            draw.text((2, line_height * 2), disk_usage('/'), font=font2, fill="white")

        try:
            if device.height >= (line_height * 4):
                draw.text((2, line_height * 3), network('wlan0'), font=font2, fill="white")
        except KeyError:
            # no wifi enabled/available
            pass

        if device.height >= (line_height * 4):
            draw.text((2, line_height * 4), "IP: " + ip_address_checker.get_ip_address(), font=font2, fill="white")


def main():
    while True:
        stats(device)
        time.sleep(5)


if __name__ == "__main__":
    try:
        device = get_device()
        ip_address_checker = IPAddressChecker()
        main()
    except KeyboardInterrupt:
        pass
    finally:
        device.clear()
```

## 9. Create the Service Script

Create a small shell wrapper that starts the example with the virtual environment Python.

```bash
nano ~/start_oled.sh
```

Paste this in, replacing `YOUR_USERNAME`:

```bash
#!/bin/bash
cd /home/YOUR_USERNAME/oled/luma.examples/examples
/home/YOUR_USERNAME/oled/venv/bin/python3 sys_info.py
```

Make it executable:

```bash
chmod +x ~/start_oled.sh
```

## 10. Create the `systemd` Service

Create or edit the service file:

```bash
sudo nano /etc/systemd/system/minitower_oled.service
```

Use this version:

```ini
[Unit]
Description=Minitower OLED service
After=multi-user.target

[Service]
Type=simple
User=YOUR_USERNAME
WorkingDirectory=/home/YOUR_USERNAME/oled/luma.examples/examples
ExecStart=/home/YOUR_USERNAME/start_oled.sh
Restart=on-failure

[Install]
WantedBy=multi-user.target
```

Notes:

- `DefaultDependencies=no` is not needed
- `StartLimitIntervalSec=60` and `StartLimitBurst=5` are optional, but we left them out for a cleaner setup
- `RemainAfterExit=yes` should be removed for this kind of long-running script

## 11. Enable and Start the Service

Reload `systemd`, enable the service, and start it:

```bash
sudo systemctl daemon-reload
sudo systemctl enable minitower_oled.service
sudo systemctl restart minitower_oled.service
```

Check the status:

```bash
systemctl status minitower_oled.service --no-pager -l
```

If the display goes blank, check the logs:

```bash
sudo journalctl -b -u minitower_oled.service -n 100 --no-pager
```

## 12. What the Screen Shows

The final layout is:

```text
CPU: x%/x° Up:xdxh
RAM: ...
SD: ...
wlan0: Tx..., Rx...
IP: ...
```

The IP row only appears if the display has enough vertical space.

## 13. Useful Fixes We Learned Along the Way

### If the screen is blank

Run:

```bash
~/oled/venv/bin/python3 -m py_compile ~/oled/luma.examples/examples/sys_info.py
```

Then run the script manually:

```bash
cd ~/oled/luma.examples/examples
~/oled/venv/bin/python3 sys_info.py
```

If the manual run throws an indentation error, the issue is usually mixed tabs and spaces.

### If the IP line disappears

The script originally skipped the IP line if the Wi-Fi interface lookup failed. The final version keeps the IP line outside that `try` block so the IP can still render.

### If `/home/pi` does not exist

That just means your Pi is using a different login name. Use `whoami` and `echo $HOME`, then replace every hardcoded `/home/pi` path with your real home directory.

## 14. Optional Cleanup

If you created mistaken environments or folders while following the old tutorial, you can remove only the ones you no longer need.

Check what exists first:

```bash
find ~ -maxdepth 4 -type d \( -name "venv" -o -name "luma.examples" \)
```

Only delete a path once you are sure it is the wrong one.

## 15. Summary

The working setup is:

- project folder in `~/oled`
- virtual environment in `~/oled/venv`
- repo clone in `~/oled/luma.examples`
- final script at `~/oled/luma.examples/examples/sys_info.py`
- service file at `/etc/systemd/system/minitower_oled.service`
- startup wrapper at `~/start_oled.sh`

That structure is simple, repeatable, and avoids the original tutorial’s confusing `/home/pi` assumptions.
