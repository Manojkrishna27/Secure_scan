"""Security scoring engine."""


def calculate_security_score(
    ssl_status: str,
    tls_versions: dict,
    headers: dict,
    days_remaining: int | None,
) -> int:
    score = 0

    if ssl_status == "valid":
        score += 30
    elif ssl_status == "expired":
        score += 5

    if tls_versions.get("tls_1_3"):
        score += 20
    elif tls_versions.get("tls_1_2"):
        score += 10

    header_flags = headers if isinstance(headers, dict) else {}
    present = sum(1 for v in header_flags.values() if v)
    score += min(30, present * 5)

    if days_remaining is not None and days_remaining > 30:
        score += 10

    return min(100, max(0, score))


def score_to_risk_level(score: int) -> str:
    if score >= 90:
        return "Low Risk"
    if score >= 70:
        return "Medium Risk"
    return "High Risk"


def score_to_grade(score: int) -> str:
    if score >= 97:
        return "A+"
    if score >= 93:
        return "A"
    if score >= 90:
        return "A-"
    if score >= 87:
        return "B+"
    if score >= 83:
        return "B"
    if score >= 80:
        return "B-"
    if score >= 77:
        return "C+"
    if score >= 73:
        return "C"
    if score >= 70:
        return "C-"
    if score >= 60:
        return "D"
    return "F"
