"""Professional cybersecurity audit PDF — ReportLab v3 design."""
import os
from datetime import datetime
from typing import Any
from xml.sax.saxutils import escape

from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER, TA_LEFT
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.lib.units import inch
from reportlab.platypus import (
    PageBreak,
    Paragraph,
    SimpleDocTemplate,
    Spacer,
    Table,
    TableStyle,
)

from app.services.pdf_report_charts import (
    CertificateChainFlowable,
    HeaderCompliancePieFlowable,
    ScoreGaugeFlowable,
    TLSBarChartFlowable,
)
from app.services.pdf_report_theme import (
    BORDER,
    BRAND_DARK,
    BRAND_NAVY,
    BRAND_PRIMARY,
    BRAND_SLATE,
    HEADER_LABELS,
    HEADER_META,
    REPORT_VERSION,
    RISK_BG,
    RISK_COLORS,
    SEVERITY_BG,
    SEVERITY_COLORS,
    STATUS_FAIL,
    STATUS_OK,
    SURFACE,
    SURFACE_CARD,
    TEXT_BODY,
    TEXT_MUTED,
)

PAGE_W, PAGE_H = A4
MARGIN_L = 0.6 * inch
MARGIN_R = 0.6 * inch
MARGIN_T = 0.75 * inch
MARGIN_B = 0.85 * inch
CONTENT_W = PAGE_W - MARGIN_L - MARGIN_R


def _esc(value: Any, max_len: int | None = None) -> str:
    if value is None or value == "":
        return "—"
    text = escape(str(value))
    if max_len and len(text) > max_len:
        return text[: max_len - 3] + "..."
    return text


def _fmt_dt(value: Any) -> str:
    if not value:
        return "—"
    if isinstance(value, datetime):
        return value.strftime("%Y-%m-%d %H:%M:%S UTC")
    try:
        return datetime.fromisoformat(str(value).replace("Z", "+00:00")).strftime(
            "%Y-%m-%d %H:%M:%S UTC"
        )
    except (ValueError, TypeError):
        return _esc(value)


def _color_hex(color) -> str:
    h = color.hexval()
    return f"#{h[2:]}" if str(h).startswith("0x") else str(h)


def _risk_key(risk_level: str | None) -> str:
    if not risk_level:
        return "medium"
    r = str(risk_level).lower()
    if "low" in r:
        return "low"
    if "high" in r:
        return "high"
    return "medium"


def _severity_key(sev: str | None) -> str:
    if not sev:
        return "Low"
    s = str(sev).strip().title()
    if s in SEVERITY_COLORS:
        return s
    if "crit" in s.lower():
        return "Critical"
    if "high" in s.lower():
        return "High"
    if "med" in s.lower():
        return "Medium"
    if "info" in s.lower():
        return "Informational"
    return "Low"


class PDFGenerator:
    """Enterprise-style security assessment PDF (Qualys / Nessus inspired)."""

    def __init__(self, output_path: str):
        self.output_path = output_path
        os.makedirs(os.path.dirname(output_path) or ".", exist_ok=True)
        self.styles = getSampleStyleSheet()
        self._setup_styles()
        self.story: list = []
        self._domain = ""
        self._generated_at = datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S UTC")

    def _setup_styles(self):
        entries = [
            ("CoverBrand", 11, BRAND_PRIMARY, "Helvetica-Bold", TA_LEFT, 4, None),
            ("CoverTitle", 24, colors.white, "Helvetica-Bold", TA_LEFT, 10, None),
            ("CoverSubtitle", 13, colors.HexColor("#94a3b8"), "Helvetica", TA_LEFT, 16, None),
            ("SectionTitle", 14, BRAND_DARK, "Helvetica-Bold", TA_LEFT, 10, 14),
            ("SectionSub", 10, BRAND_SLATE, "Helvetica-Bold", TA_LEFT, 8, 6),
            ("Body", 9, TEXT_BODY, "Helvetica", TA_LEFT, 6, 12),
            ("BodySmall", 8, TEXT_MUTED, "Helvetica", TA_LEFT, 4, 11),
            ("CardLabel", 7, TEXT_MUTED, "Helvetica", TA_LEFT, 2, 10),
            ("CardValue", 10, BRAND_DARK, "Helvetica-Bold", TA_LEFT, 2, 12),
            ("TableHead", 8, colors.white, "Helvetica-Bold", TA_CENTER, 6, 10),
            ("TableCell", 8, TEXT_BODY, "Helvetica", TA_LEFT, 5, 11),
            ("FindingTitle", 10, BRAND_DARK, "Helvetica-Bold", TA_LEFT, 4, 12),
            ("MutedCenter", 8, TEXT_MUTED, "Helvetica", TA_CENTER, 4, 10),
        ]
        for name, size, color, font, align, after, leading in entries:
            kw = dict(
                name=name,
                fontSize=size,
                textColor=color,
                fontName=font,
                alignment=align,
                spaceAfter=after,
            )
            if leading:
                kw["leading"] = leading
            self.styles.add(ParagraphStyle(**kw))

    def generate(self, scan: dict[str, Any], ai: dict[str, Any]) -> str:
        self._domain = scan.get("domain") or scan.get("url") or "unknown"
        self._cover_scan = scan
        doc = SimpleDocTemplate(
            self.output_path,
            pagesize=A4,
            leftMargin=MARGIN_L,
            rightMargin=MARGIN_R,
            topMargin=MARGIN_T,
            bottomMargin=MARGIN_B,
            title=f"SecureScan AI — {self._domain}",
            author="SecureScan AI",
        )
        self.story = [PageBreak()]
        self._executive_dashboard(scan, ai)
        self.story.append(PageBreak())
        self._ssl_certificate_cards(scan)
        self._certificate_chain(scan)
        self._tls_section(scan)
        self._headers_compliance_table(scan)
        self.story.append(PageBreak())
        self._findings_cards(scan)
        self._recommendations_section(scan, ai)
        self._appendix(scan)
        doc.build(
            self.story,
            onFirstPage=self._on_page,
            onLaterPages=self._on_page,
        )
        return self.output_path

    # ── Page chrome ──────────────────────────────────────────────

    def _on_page(self, canvas, doc):
        n = canvas.getPageNumber()
        if n == 1:
            self._paint_cover(canvas, getattr(self, "_cover_scan", {}))
        else:
            self._paint_header_bar(canvas)
        self._paint_footer(canvas)

    def _paint_header_bar(self, canvas):
        canvas.saveState()
        canvas.setFillColor(SURFACE)
        canvas.rect(0, PAGE_H - 0.42 * inch, PAGE_W, 0.42 * inch, fill=1, stroke=0)
        canvas.setFillColor(BRAND_PRIMARY)
        canvas.rect(0, PAGE_H - 0.42 * inch, PAGE_W, 3, fill=1, stroke=0)
        canvas.setFillColor(BRAND_DARK)
        canvas.setFont("Helvetica-Bold", 9)
        canvas.drawString(MARGIN_L, PAGE_H - 0.28 * inch, "SecureScan AI")
        canvas.setFillColor(TEXT_MUTED)
        canvas.setFont("Helvetica", 8)
        canvas.drawRightString(
            PAGE_W - MARGIN_R,
            PAGE_H - 0.28 * inch,
            "Confidential Security Assessment",
        )
        canvas.restoreState()

    def _paint_footer(self, canvas):
        canvas.saveState()
        y = 0.38 * inch
        canvas.setStrokeColor(BORDER)
        canvas.setLineWidth(0.5)
        canvas.line(MARGIN_L, y + 14, PAGE_W - MARGIN_R, y + 14)
        canvas.setFont("Helvetica", 7)
        canvas.setFillColor(TEXT_MUTED)
        canvas.drawString(
            MARGIN_L,
            y,
            f"SecureScan AI  |  {self._domain}  |  Generated {self._generated_at}",
        )
        canvas.drawCentredString(
            PAGE_W / 2,
            y,
            "Confidential Security Assessment",
        )
        canvas.drawRightString(
            PAGE_W - MARGIN_R,
            y,
            f"Page {canvas.getPageNumber()}",
        )
        canvas.restoreState()

    def _paint_cover(self, canvas, scan: dict):
        score = scan.get("security_score", "—")
        grade = scan.get("grade", "—")
        risk = scan.get("risk_level", "—")
        url = scan.get("url") or scan.get("domain") or self._domain
        rk = _risk_key(risk)

        canvas.saveState()
        # Background
        canvas.setFillColor(BRAND_DARK)
        canvas.rect(0, 0, PAGE_W, PAGE_H, fill=1, stroke=0)
        canvas.setFillColor(BRAND_NAVY)
        canvas.rect(0, PAGE_H * 0.55, PAGE_W, PAGE_H * 0.45, fill=1, stroke=0)
        # Accent band
        canvas.setFillColor(BRAND_PRIMARY)
        canvas.rect(0, PAGE_H - 1.35 * inch, PAGE_W, 4, fill=1, stroke=0)

        # Shield (drawn inline)
        sx, sy = MARGIN_L, PAGE_H - 2.1 * inch
        sw, sh = 0.75 * inch, 0.88 * inch
        cx = sx + sw / 2
        p = canvas.beginPath()
        p.moveTo(cx, sy + sh)
        p.lineTo(sx + sw, sy + sh * 0.52)
        p.lineTo(sx + sw, sy + sh * 0.22)
        p.curveTo(sx + sw, sy, cx, sy + sh * 0.02, cx, sy + sh * 0.02)
        p.curveTo(cx, sy + sh * 0.02, sx, sy, sx, sy + sh * 0.22)
        p.lineTo(sx, sy + sh * 0.52)
        p.close()
        canvas.setFillColor(BRAND_PRIMARY)
        canvas.setStrokeColor(colors.HexColor("#0e7490"))
        canvas.drawPath(p, fill=1, stroke=1)
        canvas.setStrokeColor(colors.white)
        canvas.setLineWidth(2)
        canvas.line(sx + sw * 0.28, sy + sh * 0.38, sx + sw * 0.4, sy + sh * 0.28)
        canvas.line(sx + sw * 0.4, sy + sh * 0.28, sx + sw * 0.62, sy + sh * 0.5)

        # Brand & title
        canvas.setFillColor(BRAND_PRIMARY)
        canvas.setFont("Helvetica-Bold", 12)
        canvas.drawString(MARGIN_L + sw + 14, PAGE_H - 1.55 * inch, "SecureScan AI")
        canvas.setFillColor(colors.white)
        canvas.setFont("Helvetica-Bold", 26)
        canvas.drawString(MARGIN_L, PAGE_H - 2.05 * inch, "Website Security")
        canvas.drawString(MARGIN_L, PAGE_H - 2.45 * inch, "Assessment Report")

        canvas.setFillColor(colors.HexColor("#94a3b8"))
        canvas.setFont("Helvetica", 11)
        canvas.drawString(MARGIN_L, PAGE_H - 2.85 * inch, "Target")
        canvas.setFillColor(colors.white)
        canvas.setFont("Helvetica-Bold", 14)
        target = str(url)[:70]
        canvas.drawString(MARGIN_L, PAGE_H - 3.1 * inch, target)

        canvas.setFont("Helvetica", 10)
        canvas.setFillColor(colors.HexColor("#94a3b8"))
        canvas.drawString(MARGIN_L, PAGE_H - 3.45 * inch, f"Generated {self._generated_at}")
        canvas.drawString(MARGIN_L, PAGE_H - 3.65 * inch, f"Scan date {_fmt_dt(scan.get('scan_date'))}")

        # Score panel
        panel_y = 1.35 * inch
        panel_h = 2.35 * inch
        canvas.setFillColor(colors.HexColor("#1e293b"))
        canvas.roundRect(MARGIN_L, panel_y, CONTENT_W, panel_h, 10, fill=1, stroke=0)
        canvas.setStrokeColor(BRAND_PRIMARY)
        canvas.setLineWidth(1)
        canvas.roundRect(MARGIN_L, panel_y, CONTENT_W, panel_h, 10, fill=0, stroke=1)

        col_w = CONTENT_W / 3
        metrics = [
            ("Security Score", f"{score} / 100"),
            ("Grade", str(grade)),
            ("Risk Level", str(risk)),
        ]
        for i, (label, value) in enumerate(metrics):
            x = MARGIN_L + col_w * i + col_w / 2
            canvas.setFillColor(colors.HexColor("#64748b"))
            canvas.setFont("Helvetica", 9)
            canvas.drawCentredString(x, panel_y + panel_h - 0.45 * inch, label)
            if i == 2:
                canvas.setFillColor(RISK_COLORS.get(rk, RISK_COLORS["medium"]))
            else:
                canvas.setFillColor(colors.white)
            canvas.setFont("Helvetica-Bold", 22 if i == 0 else 20)
            canvas.drawCentredString(x, panel_y + 0.75 * inch, str(value))

        # Risk badge underline
        badge_x = MARGIN_L + col_w * 2.5
        canvas.setFillColor(RISK_BG.get(rk, RISK_BG["medium"]))
        canvas.roundRect(badge_x - 55, panel_y + 0.35 * inch, 110, 22, 4, fill=1, stroke=0)

        canvas.setFillColor(colors.HexColor("#475569"))
        canvas.setFont("Helvetica", 8)
        canvas.drawCentredString(
            PAGE_W / 2,
            0.65 * inch,
            "Automated assessment — validate findings before remediation. For authorized use only.",
        )
        canvas.restoreState()

    # ── Content sections ─────────────────────────────────────────

    def _section(self, title: str, subtitle: str | None = None):
        self.story.append(Paragraph(title, self.styles["SectionTitle"]))
        if subtitle:
            self.story.append(Paragraph(subtitle, self.styles["BodySmall"]))
        self.story.append(Spacer(1, 0.08 * inch))

    def _executive_dashboard(self, scan: dict, ai: dict):
        self._section(
            "Executive Security Dashboard",
            "At-a-glance posture summary for leadership and engineering teams.",
        )

        score = int(scan.get("security_score") or 0)
        risk = scan.get("risk_level") or "—"
        rk = _risk_key(risk)
        headers = scan.get("security_headers") or {}
        header_present = sum(1 for v in headers.values() if v)
        header_missing = len(HEADER_LABELS) - header_present
        findings = scan.get("findings") or []

        gauge = ScoreGaugeFlowable(score)
        risk_para = Paragraph(
            f'<font color="{_color_hex(RISK_COLORS[rk])}"><b>{_esc(risk)}</b></font>',
            self.styles["CardValue"],
        )
        stats = [
            ["SSL Status", _esc(scan.get("ssl_status"))],
            ["TLS Version", _esc(scan.get("tls_version"))],
            ["Days Remaining", str(scan.get("days_remaining") if scan.get("days_remaining") is not None else "—")],
            ["Open Findings", str(len(findings))],
            ["Headers Present", f"{header_present} / {len(HEADER_LABELS)}"],
        ]
        stat_rows = []
        for label, val in stats:
            stat_rows.append([
                Paragraph(f'<font color="#64748b">{label}</font>', self.styles["CardLabel"]),
                Paragraph(f"<b>{val}</b>", self.styles["CardValue"]),
            ])
        stats_table = Table(stat_rows, colWidths=[1.4 * inch, 1.5 * inch])
        stats_table.setStyle(
            TableStyle([
                ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
                ("TOPPADDING", (0, 0), (-1, -1), 5),
                ("BOTTOMPADDING", (0, 0), (-1, -1), 5),
            ])
        )

        dash_top = Table(
            [[gauge, [risk_para, Spacer(1, 6), stats_table]]],
            colWidths=[1.65 * inch, CONTENT_W - 1.65 * inch],
        )
        dash_top.setStyle(TableStyle([
            ("VALIGN", (0, 0), (-1, -1), "TOP"),
            ("LEFTPADDING", (0, 0), (-1, -1), 0),
            ("BACKGROUND", (1, 0), (1, 0), SURFACE),
            ("BOX", (1, 0), (1, 0), 0.5, BORDER),
            ("ROUNDEDCORNERS", [6, 6, 6, 6]),
        ]))
        self.story.append(dash_top)
        self.story.append(Spacer(1, 0.2 * inch))

        summary = ai.get("security_summary") or scan.get("ai_summary")
        if summary:
            self.story.append(Paragraph("Executive Summary", self.styles["SectionSub"]))
            self.story.append(Paragraph(_esc(summary), self.styles["Body"]))

        self.story.append(Spacer(1, 0.15 * inch))
        self.story.append(Paragraph("Visual Analytics", self.styles["SectionSub"]))
        charts = Table(
            [[HeaderCompliancePieFlowable(header_present, header_missing), TLSBarChartFlowable(scan.get("tls_versions") or {})]],
            colWidths=[CONTENT_W / 2, CONTENT_W / 2],
        )
        charts.setStyle(TableStyle([("VALIGN", (0, 0), (-1, -1), "TOP")]))
        self.story.append(charts)

    def _ssl_certificate_cards(self, scan: dict):
        self._section("SSL Certificate Analysis", "Trust, validity, and cryptographic details.")
        chain = scan.get("certificate_chain") or {}
        chain_ok = "Valid" if any(chain.values()) else "Unknown"
        fields = [
            ("Issuer", _esc(scan.get("issuer"), 60)),
            ("Common Name", _esc(scan.get("common_name"))),
            ("Expiry Date", _fmt_dt(scan.get("valid_to"))),
            ("Days Remaining", str(scan.get("days_remaining") if scan.get("days_remaining") is not None else "—")),
            ("Signature Algorithm", _esc(scan.get("signature_algorithm"))),
            ("Certificate Version", _esc(scan.get("certificate_version"))),
            ("Chain Status", chain_ok),
            ("Organization", _esc(scan.get("organization"), 50)),
        ]
        rows = []
        for i in range(0, len(fields), 2):
            pair = fields[i : i + 2]
            row = []
            for label, val in pair:
                cell = [
                    Paragraph(label, self.styles["CardLabel"]),
                    Paragraph(f"<b>{val}</b>", self.styles["CardValue"]),
                ]
                row.append(cell)
            if len(pair) == 1:
                row.append(["", ""])
            rows.append(row)

        card_table = Table(rows, colWidths=[CONTENT_W / 2, CONTENT_W / 2])
        card_table.setStyle(
            TableStyle([
                ("BACKGROUND", (0, 0), (-1, -1), SURFACE_CARD),
                ("BOX", (0, 0), (-1, -1), 0.5, BORDER),
                ("INNERGRID", (0, 0), (-1, -1), 0.25, BORDER),
                ("VALIGN", (0, 0), (-1, -1), "TOP"),
                ("LEFTPADDING", (0, 0), (-1, -1), 10),
                ("RIGHTPADDING", (0, 0), (-1, -1), 10),
                ("TOPPADDING", (0, 0), (-1, -1), 8),
                ("BOTTOMPADDING", (0, 0), (-1, -1), 8),
            ])
        )
        self.story.append(card_table)

    def _certificate_chain(self, scan: dict):
        chain = scan.get("certificate_chain") or {}
        if not any(chain.values()):
            return
        self.story.append(Spacer(1, 0.15 * inch))
        self._section("Certificate Chain of Trust", "End-to-end PKI hierarchy.")
        self.story.append(CertificateChainFlowable(chain, width=CONTENT_W))

    def _tls_section(self, scan: dict):
        self.story.append(Spacer(1, 0.12 * inch))
        self._section("TLS Protocol Configuration", "Supported protocol versions and hardening guidance.")
        tls = scan.get("tls_versions") or {}
        rows = [["Protocol", "Status", "Security Guidance"]]
        guidance = {
            "TLS 1.0": ("Deprecated", "Disable — vulnerable to POODLE/BEAST."),
            "TLS 1.1": ("Deprecated", "Disable — insufficient for modern compliance."),
            "TLS 1.2": ("Acceptable", "Minimum recommended for production workloads."),
            "TLS 1.3": ("Recommended", "Preferred — improved handshake and cipher agility."),
        }
        mapping = [
            ("TLS 1.0", "tls_1_0"),
            ("TLS 1.1", "tls_1_1"),
            ("TLS 1.2", "tls_1_2"),
            ("TLS 1.3", "tls_1_3"),
        ]
        for label, key in mapping:
            supported = tls.get(key)
            status = "✓ Supported" if supported else "✗ Not Supported"
            g = guidance[label][1]
            rows.append([label, status, g])
        self._styled_table(rows, [1.0 * inch, 1.1 * inch, CONTENT_W - 2.1 * inch], status_col=1)

    def _headers_compliance_table(self, scan: dict):
        self.story.append(Spacer(1, 0.12 * inch))
        self._section(
            "HTTP Security Headers Compliance",
            "Browser-enforced protections against common web attacks.",
        )
        headers = scan.get("security_headers") or {}
        rows = [["Header", "Status", "Impact", "Recommendation"]]
        for key, label in HEADER_LABELS.items():
            present = headers.get(key)
            meta = HEADER_META.get(key, {})
            status = "✓ Present" if present else "✗ Missing"
            rows.append([
                label,
                status,
                meta.get("impact", "—"),
                meta.get("recommendation", "—"),
            ])
        self._styled_table(
            rows,
            [1.55 * inch, 0.75 * inch, 1.85 * inch, CONTENT_W - 4.15 * inch],
            status_col=1,
        )

    def _findings_cards(self, scan: dict):
        self._section("Security Findings", "Prioritized issues requiring remediation.")
        findings = scan.get("findings") or []
        if not findings:
            self.story.append(
                Paragraph(
                    "<b>No open findings</b> — maintain controls and re-assess on a scheduled basis.",
                    self.styles["Body"],
                )
            )
            return

        for idx, f in enumerate(findings, 1):
            sev = _severity_key(f.get("severity"))
            sev_color = SEVERITY_COLORS.get(sev, SEVERITY_COLORS["Low"])
            bg = SEVERITY_BG.get(sev, SEVERITY_BG["Low"])
            title = _esc(f.get("title"))
            rec = _esc(f.get("recommendation"))
            impact = rec.split(".")[0] + "." if rec and rec != "—" else "Security posture may be degraded until remediated."

            badge = Paragraph(
                f'<font color="{_color_hex(sev_color)}"><b>{sev.upper()}</b></font>',
                self.styles["FindingTitle"],
            )
            body = Paragraph(
                f"<b>{title}</b><br/><br/>"
                f"<font color='#64748b'>Impact:</font> {impact}<br/>"
                f"<font color='#64748b'>Recommendation:</font> {rec}",
                self.styles["Body"],
            )
            card = Table([[badge, body]], colWidths=[0.95 * inch, CONTENT_W - 0.95 * inch])
            card.setStyle(
                TableStyle([
                    ("BACKGROUND", (0, 0), (-1, -1), bg),
                    ("BOX", (0, 0), (-1, -1), 0.5, BORDER),
                    ("LINEBEFORE", (0, 0), (0, -1), 4, sev_color),
                    ("VALIGN", (0, 0), (-1, -1), "TOP"),
                    ("LEFTPADDING", (0, 0), (-1, -1), 10),
                    ("RIGHTPADDING", (0, 0), (-1, -1), 10),
                    ("TOPPADDING", (0, 0), (-1, -1), 10),
                    ("BOTTOMPADDING", (0, 0), (-1, -1), 10),
                ])
            )
            self.story.append(card)
            self.story.append(Spacer(1, 0.1 * inch))

    def _recommendations_section(self, scan: dict, ai: dict):
        self.story.append(PageBreak())
        self._section(
            "Remediation Roadmap",
            "AI-assisted prioritization — High, Medium, and Low priority actions.",
        )
        recs = ai.get("recommendations") or scan.get("ai_recommendations") or []
        if not recs:
            self.story.append(
                Paragraph("No additional recommendations beyond scan findings.", self.styles["Body"])
            )
            return

        priority_titles = {
            "High": "High Priority Actions",
            "Medium": "Medium Priority Actions",
            "Low": "Low Priority Actions",
        }
        for priority in ("High", "Medium", "Low"):
            items = [r for r in recs if r.get("priority") == priority]
            if not items:
                continue
            self.story.append(Paragraph(priority_titles[priority], self.styles["SectionSub"]))
            for item in items:
                title = _esc(item.get("title"))
                why = _esc(item.get("description"))
                card = Table(
                    [[
                        Paragraph(f"<b>{title}</b>", self.styles["FindingTitle"]),
                        Paragraph(
                            f"<font color='#64748b'><b>Why it matters:</b></font> {why}<br/>"
                            f"<font color='#64748b'><b>Remediation:</b></font> {why}",
                            self.styles["Body"],
                        ),
                    ]],
                    colWidths=[CONTENT_W],
                )
                card.setStyle(
                    TableStyle([
                        ("BACKGROUND", (0, 0), (-1, -1), SURFACE),
                        ("BOX", (0, 0), (-1, -1), 0.5, BORDER),
                        ("LEFTPADDING", (0, 0), (-1, -1), 12),
                        ("RIGHTPADDING", (0, 0), (-1, -1), 12),
                        ("TOPPADDING", (0, 0), (-1, -1), 10),
                        ("BOTTOMPADDING", (0, 0), (-1, -1), 10),
                    ])
                )
                self.story.append(card)
                self.story.append(Spacer(1, 0.08 * inch))

    def _appendix(self, scan: dict):
        self.story.append(Spacer(1, 0.15 * inch))
        self._section("Appendix", "Scan metadata and report provenance.")
        rows = [
            ["Scan ID", _esc(scan.get("id"))],
            ["Target URL", _esc(scan.get("url"), 80)],
            ["Domain", _esc(scan.get("domain"))],
            ["Scan timestamp", _fmt_dt(scan.get("scan_date"))],
            ["Report generated", self._generated_at],
            ["Assessment tool", "SecureScan AI Automated Scanner"],
            ["Report version", REPORT_VERSION],
        ]
        self._styled_table([[r[0], r[1]] for r in rows], [1.5 * inch, CONTENT_W - 1.5 * inch])

    # ── Table helpers ──────────────────────────────────────────

    def _styled_table(self, rows, col_widths, status_col: int | None = None):
        wrapped = []
        for r_idx, row in enumerate(rows):
            style = self.styles["TableHead"] if r_idx == 0 else self.styles["TableCell"]
            wrapped.append([Paragraph(str(c), style) for c in row])
        t = Table(wrapped, colWidths=col_widths, repeatRows=1)
        cmds = [
            ("BACKGROUND", (0, 0), (-1, 0), BRAND_DARK),
            ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
            ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
            ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.white, SURFACE]),
            ("BOX", (0, 0), (-1, -1), 0.4, BORDER),
            ("INNERGRID", (0, 0), (-1, -1), 0.25, BORDER),
            ("VALIGN", (0, 0), (-1, -1), "TOP"),
            ("LEFTPADDING", (0, 0), (-1, -1), 8),
            ("RIGHTPADDING", (0, 0), (-1, -1), 8),
            ("TOPPADDING", (0, 0), (-1, -1), 6),
            ("BOTTOMPADDING", (0, 0), (-1, -1), 6),
        ]
        if status_col is not None:
            for r in range(1, len(rows)):
                cell = str(rows[r][status_col])
                color = STATUS_OK if "✓" in cell or "Supported" in cell else STATUS_FAIL
                cmds.append(("TEXTCOLOR", (status_col, r), (status_col, r), color))
        t.setStyle(TableStyle(cmds))
        self.story.append(t)
        self.story.append(Spacer(1, 0.12 * inch))
