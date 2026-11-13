"""Preflight recipe URLs before handing them to Mealie's fetcher.

Mealie must also restrict redirects and connection-time destinations; this
preflight cannot pin the addresses used by a different process.
"""
from ipaddress import ip_address
import socket
from urllib.parse import urlsplit


def validate_recipe_url(value: str) -> str:
    url = urlsplit(value)
    if url.scheme not in {"http", "https"} or not url.hostname or url.username or url.password:
        raise ValueError("Recipe URL must be HTTP(S), without embedded credentials")
    host = url.hostname.rstrip(".").lower()
    if host == "localhost" or host.endswith((".localhost", ".local", ".internal", ".home", ".home.arpa")):
        raise ValueError("Recipe URL cannot target a local host")
    try:
        address = ip_address(host)
    except ValueError:
        if "." not in host:
            raise ValueError("Recipe URL must use a public host")
        addresses = [ip_address(row[4][0]) for row in socket.getaddrinfo(host, url.port or (443 if url.scheme == "https" else 80), type=socket.SOCK_STREAM)]
    else:
        addresses = [address]
    if not addresses or any(not address.is_global for address in addresses):
        raise ValueError("Recipe URL cannot target private, loopback, or reserved addresses")
    return value
