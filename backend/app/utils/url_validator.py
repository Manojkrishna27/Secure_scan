"""URL validation and SSRF protection."""
import ipaddress
import re
import socket
from urllib.parse import urlparse

BLOCKED_HOSTNAMES = frozenset(
    {
        "localhost",
        "localhost.localdomain",
        "127.0.0.1",
        "0.0.0.0",
        "::1",
    }
)

PRIVATE_NETWORKS = (
    ipaddress.ip_network("10.0.0.0/8"),
    ipaddress.ip_network("172.16.0.0/12"),
    ipaddress.ip_network("192.168.0.0/16"),
    ipaddress.ip_network("127.0.0.0/8"),
    ipaddress.ip_network("169.254.0.0/16"),
    ipaddress.ip_network("0.0.0.0/8"),
    ipaddress.ip_network("::1/128"),
    ipaddress.ip_network("fc00::/7"),
)


def _is_private_ip(ip_str: str) -> bool:
    try:
        ip = ipaddress.ip_address(ip_str)
    except ValueError:
        return False  # Not an IP address (e.g. hostname)
    if ip.is_loopback or ip.is_private or ip.is_link_local or ip.is_reserved:
        return True
    for network in PRIVATE_NETWORKS:
        if ip in network:
            return True
    return False


def _resolve_host_ips(hostname: str) -> list[str]:
    try:
        results = socket.getaddrinfo(hostname, None)
        return list({item[4][0] for item in results})
    except socket.gaierror as exc:
        raise ValueError(f"Unable to resolve hostname: {hostname}") from exc


def normalize_and_validate_url(url: str) -> tuple[str, str, str]:
    """
    Validate URL and return (normalized_url, hostname, domain).
    Raises ValueError on invalid or blocked targets.
    """
    if not url or not str(url).strip():
        raise ValueError("URL is required.")

    raw = str(url).strip()
    if not re.match(r"^https?://", raw, re.IGNORECASE):
        raw = f"https://{raw}"

    parsed = urlparse(raw)
    if parsed.scheme not in ("https", "http"):
        raise ValueError("Only http and https URLs are allowed.")

    hostname = (parsed.hostname or "").lower().rstrip(".")
    if not hostname:
        raise ValueError("Invalid URL: missing hostname.")

    if hostname in BLOCKED_HOSTNAMES:
        raise ValueError("Scanning localhost and loopback addresses is not allowed.")

    if hostname.endswith(".localhost") or hostname.endswith(".local"):
        raise ValueError("Scanning local domains is not allowed.")

    # Block literal private IPs in URL
    if _is_private_ip(hostname):
        raise ValueError("Scanning private or reserved IP addresses is not allowed.")

    # Block private IPs from DNS resolution (SSRF)
    for ip in _resolve_host_ips(hostname):
        if _is_private_ip(ip):
            raise ValueError(
                "Target resolves to a private or reserved IP address. Scan blocked."
            )

    port = parsed.port
    if port and port not in (80, 443, 8080, 8443):
        raise ValueError("Port not allowed for security scans.")

    # Prefer HTTPS for scans
    if parsed.scheme == "http":
        normalized = f"https://{hostname}"
        if port and port not in (80, 443):
            normalized = f"https://{hostname}:{port}"
    else:
        normalized = f"https://{hostname}"
        if port and port != 443:
            normalized = f"https://{hostname}:{port}"

    domain = hostname.split(":")[0]
    return normalized, hostname, domain
