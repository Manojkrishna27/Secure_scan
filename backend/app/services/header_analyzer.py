"""HTTP security header analysis."""
from typing import Any

import requests

HEADER_KEYS = {
    "hsts": "Strict-Transport-Security",
    "csp": "Content-Security-Policy",
    "x_frame_options": "X-Frame-Options",
    "x_content_type_options": "X-Content-Type-Options",
    "referrer_policy": "Referrer-Policy",
    "permissions_policy": "Permissions-Policy",
}


def analyze_security_headers(url: str) -> dict[str, Any]:
    """Fetch URL and analyze security headers."""
    result: dict[str, Any] = {
        "headers": {key: False for key in HEADER_KEYS},
        "header_values": {},
        "present_count": 0,
        "error": None,
    }

    try:
        response = requests.get(
            url,
            timeout=15,
            allow_redirects=True,
            headers={"User-Agent": "SecureScan-AI/1.0"},
        )
        headers_lower = {k.lower(): v for k, v in response.headers.items()}

        for key, header_name in HEADER_KEYS.items():
            value = headers_lower.get(header_name.lower())
            present = value is not None and len(str(value).strip()) > 0
            result["headers"][key] = present
            if present:
                result["header_values"][key] = str(value)[:500]
                result["present_count"] += 1

        result["status_code"] = response.status_code
        result["final_url"] = str(response.url)
    except requests.RequestException as exc:
        result["error"] = str(exc)

    return result
