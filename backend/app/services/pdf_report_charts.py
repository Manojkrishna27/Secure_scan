"""ReportLab chart and graphic flowables for PDF reports."""
import math

from reportlab.graphics.charts.barcharts import VerticalBarChart
from reportlab.graphics.charts.piecharts import Pie
from reportlab.graphics.shapes import Circle, Drawing, Line, Rect, String, Wedge
from reportlab.lib import colors
from reportlab.lib.units import inch
from reportlab.platypus import Flowable

from app.services.pdf_report_theme import (
    BRAND_DARK,
    BRAND_PRIMARY,
    CHART_MISSING,
    CHART_PRESENT,
    TLS_SUPPORTED,
    TLS_UNSUPPORTED,
)


class ScoreGaugeFlowable(Flowable):
    """Circular security score gauge (0–100)."""

    def __init__(self, score: int | float, size: float = 1.45 * inch):
        self.score = max(0, min(100, int(score or 0)))
        self.size = size

    def wrap(self, aW, aH):
        return self.size, self.size

    def draw(self):
        c = self.canv
        s = self.size
        cx, cy = s / 2, s / 2
        r = s * 0.38
        # Track
        c.setStrokeColor(colors.HexColor("#e2e8f0"))
        c.setLineWidth(10)
        c.circle(cx, cy, r, stroke=1, fill=0)
        # Arc (score) — start at top (90°), sweep clockwise
        extent = 360 * (self.score / 100.0)
        c.setStrokeColor(BRAND_PRIMARY)
        c.setLineWidth(10)
        c.arc(cx - r, cy - r, cx + r, cy + r, 90, -extent)
        c.setFillColor(BRAND_DARK)
        c.setFont("Helvetica-Bold", 22)
        c.drawCentredString(cx, cy + 4, str(self.score))
        c.setFont("Helvetica", 9)
        c.setFillColor(colors.HexColor("#64748b"))
        c.drawCentredString(cx, cy - 14, "/ 100")


class ShieldLogoFlowable(Flowable):
    """Brand shield mark for cover page."""

    def __init__(self, width: float = 0.9 * inch, height: float = 1.05 * inch):
        self.width = width
        self.height = height

    def wrap(self, aW, aH):
        return self.width, self.height

    def draw(self):
        c = self.canv
        w, h = self.width, self.height
        cx = w / 2
        # Shield path
        p = c.beginPath()
        p.moveTo(cx, h * 0.98)
        p.lineTo(w * 0.92, h * 0.55)
        p.lineTo(w * 0.92, h * 0.28)
        p.curveTo(w * 0.92, h * 0.08, cx, h * 0.02, cx, h * 0.02)
        p.curveTo(cx, h * 0.02, w * 0.08, h * 0.08, w * 0.08, h * 0.28)
        p.lineTo(w * 0.08, h * 0.55)
        p.close()
        c.setFillColor(BRAND_PRIMARY)
        c.setStrokeColor(colors.HexColor("#0e7490"))
        c.setLineWidth(1.2)
        c.drawPath(p, fill=1, stroke=1)
        # Checkmark
        c.setStrokeColor(colors.white)
        c.setLineWidth(2.5)
        c.line(w * 0.32, h * 0.42, w * 0.44, h * 0.32)
        c.line(w * 0.44, h * 0.32, w * 0.68, h * 0.58)


class HeaderCompliancePieFlowable(Flowable):
    """Pie chart: security headers present vs missing."""

    def __init__(self, present: int, missing: int, width=2.4 * inch, height=1.6 * inch):
        self.present = present
        self.missing = missing
        self.width = width
        self.height = height

    def wrap(self, aW, aH):
        return self.width, self.height

    def draw(self):
        d = Drawing(self.width, self.height)
        if self.present + self.missing == 0:
            d.add(
                String(
                    self.width / 2 - 40,
                    self.height / 2,
                    "No header data",
                    fontSize=9,
                )
            )
            d.drawOn(self.canv, 0, 0)
            return
        pie = Pie()
        pie.x = 15
        pie.y = 10
        pie.width = 95
        pie.height = 95
        pie.data = [self.present, self.missing]
        pie.labels = [f"Present ({self.present})", f"Missing ({self.missing})"]
        pie.slices.strokeWidth = 0.5
        pie.slices[0].fillColor = CHART_PRESENT
        pie.slices[1].fillColor = CHART_MISSING
        pie.sideLabels = 1
        d.add(pie)
        d.add(
            String(
                120,
                self.height - 18,
                "Header Compliance",
                fontSize=9,
                fontName="Helvetica-Bold",
                fillColor=BRAND_DARK,
            )
        )
        d.drawOn(self.canv, 0, 0)


class TLSBarChartFlowable(Flowable):
    """Bar chart for TLS version support."""

    def __init__(self, tls_versions: dict, width=2.8 * inch, height=1.65 * inch):
        self.tls = tls_versions or {}
        self.width = width
        self.height = height

    def wrap(self, aW, aH):
        return self.width, self.height

    def draw(self):
        labels = ["1.0", "1.1", "1.2", "1.3"]
        keys = ["tls_1_0", "tls_1_1", "tls_1_2", "tls_1_3"]
        values = [1 if self.tls.get(k) else 0 for k in keys]

        d = Drawing(self.width, self.height)
        bc = VerticalBarChart()
        bc.x = 35
        bc.y = 25
        bc.height = 95
        bc.width = 155
        bc.data = [values]
        bc.categoryAxis.categoryNames = labels
        bc.categoryAxis.labels.boxAnchor = "n"
        bc.categoryAxis.labels.fontSize = 8
        bc.valueAxis.valueMin = 0
        bc.valueAxis.valueMax = 1
        bc.valueAxis.valueStep = 1
        bc.valueAxis.labels.fontSize = 7
        bc.bars[0].fillColor = TLS_SUPPORTED
        bc.bars[0].strokeColor = TLS_SUPPORTED
        bc.barWidth = 18
        d.add(bc)
        d.add(
            String(
                35,
                self.height - 14,
                "TLS Protocol Support",
                fontSize=9,
                fontName="Helvetica-Bold",
                fillColor=BRAND_DARK,
            )
        )
        d.drawOn(self.canv, 0, 0)


class CertificateChainFlowable(Flowable):
    """Visual chain: Root → Intermediate → End entity."""

    def __init__(self, chain: dict, width=6.5 * inch, height=2.2 * inch):
        self.chain = chain or {}
        self.width = width
        self.height = height

    def wrap(self, aW, aH):
        return self.width, min(self.height, aH or self.height)

    def draw(self):
        c = self.canv
        w, h = self.width, self.height
        nodes = [
            ("Root CA", self.chain.get("root_ca") or "—"),
            ("Intermediate CA", self.chain.get("intermediate_ca") or "—"),
            ("Website Certificate", self.chain.get("end_entity") or "—"),
        ]
        box_h = 0.52 * inch
        gap = 0.28 * inch
        bw = w - 0.2 * inch
        x0 = 0.1 * inch
        y = h - box_h - 0.1 * inch

        for i, (role, value) in enumerate(nodes):
            c.setFillColor(colors.HexColor("#f8fafc"))
            c.setStrokeColor(colors.HexColor("#cbd5e1"))
            c.setLineWidth(0.8)
            c.roundRect(x0, y, bw, box_h, 6, fill=1, stroke=1)
            c.setFillColor(BRAND_PRIMARY)
            c.circle(x0 + 14, y + box_h / 2, 6, fill=1, stroke=0)
            c.setFillColor(BRAND_DARK)
            c.setFont("Helvetica-Bold", 8)
            c.drawString(x0 + 28, y + box_h - 14, role)
            c.setFont("Helvetica", 7)
            c.setFillColor(colors.HexColor("#475569"))
            text = str(value)[:90]
            c.drawString(x0 + 28, y + 8, text)
            if i < len(nodes) - 1:
                mid_x = x0 + bw / 2
                c.setStrokeColor(BRAND_PRIMARY)
                c.setLineWidth(1.5)
                c.line(mid_x, y, mid_x, y - gap + 4)
                # arrow head
                ay = y - gap
                c.line(mid_x, ay, mid_x - 4, ay + 6)
                c.line(mid_x, ay, mid_x + 4, ay + 6)
            y -= box_h + gap
