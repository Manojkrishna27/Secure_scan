"""TLS protocol version detection."""
import socket
import ssl
from typing import Any


def _probe_tls(hostname: str, port: int, context: ssl.SSLContext) -> bool:
    try:
        ctx = ssl.SSLContext(context.protocol)
        ctx.check_hostname = False
        ctx.verify_mode = ssl.CERT_NONE
        if hasattr(ssl, "TLSVersion"):
            if context.minimum_version:
                ctx.minimum_version = context.minimum_version
            if context.maximum_version:
                ctx.maximum_version = context.maximum_version
        with socket.create_connection((hostname, port), timeout=8) as sock:
            with ctx.wrap_socket(sock, server_hostname=hostname) as _:
                return True
    except Exception:
        return False


def analyze_tls(hostname: str, port: int = 443) -> dict[str, Any]:
    """Detect supported TLS protocol versions."""
    results = {
        "tls_1_0": False,
        "tls_1_1": False,
        "tls_1_2": False,
        "tls_1_3": False,
        "highest_version": None,
        "insecure_enabled": [],
    }

    probes = []

    if hasattr(ssl, "TLSVersion"):
        probes = [
            ("tls_1_0", ssl.TLSVersion.TLSv1),
            ("tls_1_1", ssl.TLSVersion.TLSv1_1),
            ("tls_1_2", ssl.TLSVersion.TLSv1_2),
            ("tls_1_3", ssl.TLSVersion.TLSv1_3),
        ]
        for key, version in probes:
            try:
                ctx = ssl.SSLContext(ssl.PROTOCOL_TLS_CLIENT)
                ctx.check_hostname = False
                ctx.verify_mode = ssl.CERT_NONE
                ctx.minimum_version = version
                ctx.maximum_version = version
                with socket.create_connection((hostname, port), timeout=8) as sock:
                    with ctx.wrap_socket(sock, server_hostname=hostname) as ssock:
                        results[key] = True
                        ver = ssock.version()
                        if not results["highest_version"]:
                            results["highest_version"] = ver
            except Exception:
                results[key] = False
    else:
        # Fallback: infer from default connection
        try:
            ctx = ssl.create_default_context()
            with socket.create_connection((hostname, port), timeout=8) as sock:
                with ctx.wrap_socket(sock, server_hostname=hostname) as ssock:
                    ver = ssock.version() or ""
                    results["tls_1_2"] = "TLSv1.2" in ver or "TLSv1.3" in ver
                    results["tls_1_3"] = "TLSv1.3" in ver
                    results["highest_version"] = ver
        except Exception:
            pass

    version_order = [
        ("tls_1_3", "TLSv1.3"),
        ("tls_1_2", "TLSv1.2"),
        ("tls_1_1", "TLSv1.1"),
        ("tls_1_0", "TLSv1"),
    ]
    for key, label in version_order:
        if results[key]:
            results["highest_version"] = label
            break

    for insecure in ("tls_1_0", "tls_1_1"):
        if results[insecure]:
            results["insecure_enabled"].append(insecure)

    return results
