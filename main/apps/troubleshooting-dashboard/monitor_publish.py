#!/usr/bin/env python3
"""Independent metrics publication; does not change the alert collector."""
import subprocess

body = subprocess.check_output(["/usr/bin/python3", "/usr/local/sbin/troubleshooting-monitor-reader.py"], timeout=7)
subprocess.run(["/usr/bin/ssh", "-F", "/dev/null", "-o", "BatchMode=yes", "-o", "ConnectTimeout=3", "-o", "StrictHostKeyChecking=yes", "-o", "IdentitiesOnly=yes", "-o", "UserKnownHostsFile=/etc/troubleshooting-publish/known_hosts", "-i", "/etc/troubleshooting-publish/key", "troubleshooting-api@192.168.20.102"], input=body, check=True, timeout=8)
