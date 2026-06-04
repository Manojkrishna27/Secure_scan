"""SSL certificate analysis."""
import socket
import ssl
from datetime import datetime, timezone
from typing import Any

from cryptography import x509
from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives import hashes
from cryptography.x509.oid import ExtensionOID


def _parse_name_tuple(name_tuple) -> dict[str, str]:
    """Parse subject/issuer from ssl.getpeercert() or cryptography Name."""
    result = {}
    if not name_tuple:
        return result
    for rdn in name_tuple:
        for attr in rdn:
            # stdlib ssl.getpeercert(): (oid_name, value) tuples
            if isinstance(attr, tuple) and len(attr) >= 2:
                key, value = attr[0], attr[1]
            elif hasattr(attr, "oid"):
                key = (
                    attr.oid._name
                    if hasattr(attr.oid, "_name")
                    else str(attr.oid)
                )
                value = attr.value
            else:
                continue
            result[key] = value
    return result


def _format_cert_dict(cert_dict: dict) -> dict[str, Any]:
    subject = _parse_name_tuple(cert_dict.get("subject"))
    issuer = _parse_name_tuple(cert_dict.get("issuer"))

    not_before = cert_dict.get("notBefore")
    not_after = cert_dict.get("notAfter")

    valid_from = None
    valid_to = None
    days_remaining = None
    ssl_status = "invalid"

    if not_after:
        try:
            valid_to = datetime.strptime(not_after, "%b %d %H:%M:%S %Y %Z").replace(
                tzinfo=timezone.utc
            )
            valid_from = (
                datetime.strptime(not_before, "%b %d %H:%M:%S %Y %Z").replace(
                    tzinfo=timezone.utc
                )
                if not_before
                else None
            )
            now = datetime.now(timezone.utc)
            days_remaining = (valid_to - now).days
            if days_remaining < 0:
                ssl_status = "expired"
            else:
                ssl_status = "valid"
        except ValueError:
            ssl_status = "unknown"

    common_name = subject.get("commonName") or subject.get("CN")
    organization = issuer.get("organizationName") or issuer.get("O")

    return {
        "domain_name": common_name,
        "ssl_status": ssl_status,
        "common_name": common_name,
        "issuer": issuer.get("commonName") or organization or "Unknown",
        "organization": organization,
        "serial_number": cert_dict.get("serialNumber"),
        "valid_from": valid_from.isoformat() if valid_from else not_before,
        "valid_to": valid_to.isoformat() if valid_to else not_after,
        "days_remaining": days_remaining,
        "subject": subject,
        "issuer_dict": issuer,
    }


def _parse_der_certificate(der_cert: bytes) -> dict[str, Any]:
    cert = x509.load_der_x509_certificate(der_cert, default_backend())
    try:
        sig_alg = cert.signature_hash_algorithm.name
    except Exception:
        sig_alg = "unknown"
    try:
        pub_key = cert.public_key()
        pub_alg = pub_key.__class__.__name__.replace("_", "").replace("Key", "")
    except Exception:
        pub_alg = "unknown"

    sans = []
    try:
        ext = cert.extensions.get_extension_for_oid(ExtensionOID.SUBJECT_ALTERNATIVE_NAME)
        sans = [x.value for x in ext.value]
    except x509.ExtensionNotFound:
        pass

    return {
        "certificate_version": cert.version.name,
        "signature_algorithm": sig_alg,
        "public_key_algorithm": pub_alg,
        "san_list": sans,
    }


def analyze_certificate_chain(hostname: str, port: int = 443) -> dict[str, Any]:
    """Build certificate chain representation."""
    chain = {"root_ca": None, "intermediate_ca": None, "end_entity": None}
    try:
        pem_cert = ssl.get_server_certificate((hostname, port), timeout=10)
        cert = x509.load_pem_x509_certificate(pem_cert.encode(), default_backend())
        subject = cert.subject.get_attributes_for_oid(x509.oid.NameOID.COMMON_NAME)
        end_cn = subject[0].value if subject else hostname
        chain["end_entity"] = end_cn

        issuer_attrs = cert.issuer.get_attributes_for_oid(x509.oid.NameOID.COMMON_NAME)
        org_attrs = cert.issuer.get_attributes_for_oid(x509.oid.NameOID.ORGANIZATION_NAME)
        intermediate = (
            issuer_attrs[0].value
            if issuer_attrs
            else (org_attrs[0].value if org_attrs else "Unknown Intermediate")
        )
        chain["intermediate_ca"] = intermediate
        chain["root_ca"] = intermediate  # Full chain walk needs extra fetches; simplified
    except Exception:
        chain["end_entity"] = hostname
    return chain


def analyze_ssl(hostname: str, port: int = 443) -> dict[str, Any]:
    """Perform SSL certificate analysis for hostname."""
    context = ssl.create_default_context()
    result: dict[str, Any] = {
        "ssl_status": "error",
        "error": None,
    }

    try:
        with socket.create_connection((hostname, port), timeout=12) as sock:
            with context.wrap_socket(sock, server_hostname=hostname) as ssock:
                cert_dict = ssock.getpeercert()
                der = ssock.getpeercert(binary_form=True)
                tls_version = ssock.version()

        parsed = _format_cert_dict(cert_dict)
        if der:
            parsed.update(_parse_der_certificate(der))

        parsed["tls_version_detected"] = tls_version
        parsed["certificate_chain"] = analyze_certificate_chain(hostname, port)
        return parsed
    except ssl.SSLError as exc:
        result["error"] = str(exc)
        result["ssl_status"] = "invalid"
        result["certificate_chain"] = analyze_certificate_chain(hostname, port)
        return result
    except (socket.timeout, OSError) as exc:
        result["error"] = str(exc)
        result["ssl_status"] = "error"
        return result
