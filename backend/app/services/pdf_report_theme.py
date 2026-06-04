"""Design tokens for SecureScan AI PDF reports."""
from reportlab.lib import colors

# Brand & surfaces
BRAND_PRIMARY = colors.HexColor("#0891b2")
BRAND_DARK = colors.HexColor("#0f172a")
BRAND_NAVY = colors.HexColor("#1e293b")
BRAND_SLATE = colors.HexColor("#334155")
TEXT_MUTED = colors.HexColor("#64748b")
TEXT_BODY = colors.HexColor("#1e293b")
SURFACE = colors.HexColor("#f8fafc")
SURFACE_CARD = colors.HexColor("#ffffff")
BORDER = colors.HexColor("#e2e8f0")
ACCENT_LINE = colors.HexColor("#06b6d4")

# Severity palette
SEVERITY_COLORS = {
    "Critical": colors.HexColor("#7f1d1d"),
    "High": colors.HexColor("#dc2626"),
    "Medium": colors.HexColor("#ea580c"),
    "Low": colors.HexColor("#2563eb"),
    "Informational": colors.HexColor("#64748b"),
}
SEVERITY_BG = {
    "Critical": colors.HexColor("#fef2f2"),
    "High": colors.HexColor("#fef2f2"),
    "Medium": colors.HexColor("#fff7ed"),
    "Low": colors.HexColor("#eff6ff"),
    "Informational": colors.HexColor("#f8fafc"),
}

# Risk badges
RISK_COLORS = {
    "low": colors.HexColor("#16a34a"),
    "medium": colors.HexColor("#ea580c"),
    "high": colors.HexColor("#dc2626"),
}
RISK_BG = {
    "low": colors.HexColor("#dcfce7"),
    "medium": colors.HexColor("#ffedd5"),
    "high": colors.HexColor("#fee2e2"),
}

STATUS_OK = colors.HexColor("#16a34a")
STATUS_FAIL = colors.HexColor("#dc2626")
CHART_PRESENT = colors.HexColor("#0891b2")
CHART_MISSING = colors.HexColor("#cbd5e1")
TLS_SUPPORTED = colors.HexColor("#0891b2")
TLS_UNSUPPORTED = colors.HexColor("#e2e8f0")

HEADER_LABELS = {
    "hsts": "Strict-Transport-Security (HSTS)",
    "csp": "Content-Security-Policy (CSP)",
    "x_frame_options": "X-Frame-Options",
    "x_content_type_options": "X-Content-Type-Options",
    "referrer_policy": "Referrer-Policy",
    "permissions_policy": "Permissions-Policy",
}

HEADER_META = {
    "hsts": {
        "impact": "Prevents protocol downgrade and cookie hijacking over HTTP.",
        "recommendation": "Set max-age ≥ 31536000; includeSubDomains when appropriate.",
    },
    "csp": {
        "impact": "Reduces XSS and data injection by restricting resource origins.",
        "recommendation": "Deploy a strict policy with default-src and script-src directives.",
    },
    "x_frame_options": {
        "impact": "Mitigates clickjacking by controlling iframe embedding.",
        "recommendation": "Use DENY or SAMEORIGIN for sensitive applications.",
    },
    "x_content_type_options": {
        "impact": "Stops MIME-type sniffing attacks in legacy browsers.",
        "recommendation": "Set to nosniff on all responses.",
    },
    "referrer_policy": {
        "impact": "Limits sensitive URL data leaked via Referer headers.",
        "recommendation": "Use strict-origin-when-cross-origin or stricter.",
    },
    "permissions_policy": {
        "impact": "Restricts browser features (camera, geolocation, etc.).",
        "recommendation": "Explicitly disable unused features via Permissions-Policy.",
    },
}

REPORT_VERSION = "3.0"
