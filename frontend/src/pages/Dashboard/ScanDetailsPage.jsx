import { useEffect, useState } from "react";
import { Link, useParams } from "react-router-dom";
import {
  AlertCircle,
  Check,
  Download,
  FileText,
  Loader2,
  Shield,
  X,
} from "lucide-react";

import { PageHeader } from "@/components/PageHeader";
import { SecurityScoreDisplay } from "@/components/SecurityScoreDisplay";
import { Button } from "@/components/ui/button";
import { ScanDetailSkeleton } from "@/components/ui/skeleton";
import {
  Card,
  CardContent,
  CardDescription,
  CardHeader,
  CardTitle,
} from "@/components/ui/card";
import {
  downloadReport,
  generateReport,
  openPdfBlob,
  savePdfBlob,
} from "@/services/reportService";
import { useToast } from "@/context/ToastContext";
import { getApiMessage } from "@/services/api";
import { getScanById } from "@/services/scanService";
import { riskClass } from "@/utils/risk";

const HEADER_LABELS = {
  hsts: "Strict-Transport-Security (HSTS)",
  csp: "Content-Security-Policy (CSP)",
  x_frame_options: "X-Frame-Options",
  x_content_type_options: "X-Content-Type-Options",
  referrer_policy: "Referrer-Policy",
  permissions_policy: "Permissions-Policy",
};

const TLS_LABELS = [
  ["tls_1_0", "TLS 1.0"],
  ["tls_1_1", "TLS 1.1"],
  ["tls_1_2", "TLS 1.2"],
  ["tls_1_3", "TLS 1.3"],
];

function SeverityBadge({ severity }) {
  const colors = {
    Critical: "bg-destructive/20 text-destructive",
    High: "bg-orange-500/20 text-orange-400",
    Medium: "bg-yellow-500/20 text-yellow-500",
    Low: "bg-muted text-muted-foreground",
  };
  return (
    <span
      className={`inline-flex rounded-full px-2.5 py-0.5 text-xs font-medium ${colors[severity] || colors.Low}`}
    >
      {severity}
    </span>
  );
}

export default function ScanDetailsPage() {
  const toast = useToast();
  const { id } = useParams();
  const [scan, setScan] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");
  const [pdfLoading, setPdfLoading] = useState(false);
  const [pdfDownloadingId, setPdfDownloadingId] = useState(null);
  const [pdfMessage, setPdfMessage] = useState("");
  const [pdfError, setPdfError] = useState(false);

  useEffect(() => {
    (async () => {
      try {
        const data = await getScanById(id);
        setScan(data);
      } catch (err) {
        setError(getApiMessage(err, "Failed to load scan."));
      } finally {
        setLoading(false);
      }
    })();
  }, [id]);

  if (loading) {
    return <ScanDetailSkeleton />;
  }

  if (error || !scan) {
    return (
      <div className="space-y-4">
        <p className="text-destructive">{error || "Scan not found"}</p>
        <Button asChild variant="outline">
          <Link to="/scans">Back to history</Link>
        </Button>
      </div>
    );
  }

  const tls = scan.tls_versions || {};
  const aiRecs = scan.ai_recommendations || [];
  const aiRisk = scan.ai_risk_assessment || {};

  const handleGeneratePdf = async () => {
    setPdfLoading(true);
    setPdfMessage("");
    setPdfError(false);
    try {
      const { report } = await generateReport(id);
      setPdfMessage("PDF generated — opening in new tab.");
      toast.success("PDF report generated.");
      const updated = await getScanById(id);
      setScan(updated);
      if (report) {
        setPdfDownloadingId(report.id);
        const response = await downloadReport(report.id);
        openPdfBlob(response.data);
      }
    } catch (err) {
      const msg = getApiMessage(err, "Failed to generate report. Please try again.");
      setPdfMessage(msg);
      setPdfError(true);
      toast.error(msg);
    } finally {
      setPdfLoading(false);
      setPdfDownloadingId(null);
    }
  };

  const handleDownloadExisting = async (reportId, name) => {
    setPdfDownloadingId(reportId);
    setPdfMessage("");
    setPdfError(false);
    try {
      const response = await downloadReport(reportId);
      savePdfBlob(response.data, name);
      toast.success("Download started.");
    } catch (err) {
      const msg = getApiMessage(err, "Download failed. Please try again.");
      setPdfMessage(msg);
      setPdfError(true);
      toast.error(msg);
    } finally {
      setPdfDownloadingId(null);
    }
  };

  const handleViewExisting = async (reportId) => {
    setPdfDownloadingId(reportId);
    setPdfMessage("");
    setPdfError(false);
    try {
      const response = await downloadReport(reportId);
      openPdfBlob(response.data);
      toast.success("Opening PDF in new tab.");
    } catch (err) {
      const msg = getApiMessage(err, "Failed to open PDF. Please try again.");
      setPdfMessage(msg);
      setPdfError(true);
      toast.error(msg);
    } finally {
      setPdfDownloadingId(null);
    }
  };

  return (
    <div className="space-y-6">
      <PageHeader
        title={scan.url}
        description={`Scanned ${scan.scan_date ? new Date(scan.scan_date).toLocaleString() : "—"}`}
      >
        <Button onClick={handleGeneratePdf} disabled={pdfLoading}>
          {pdfLoading ? (
            <Loader2 className="h-4 w-4 animate-spin" />
          ) : (
            <FileText className="h-4 w-4" />
          )}
          Generate PDF
        </Button>
        <Button variant="outline" asChild>
          <Link to="/scans">Scan history</Link>
        </Button>
      </PageHeader>
      {pdfMessage && (
        <p
          role="alert"
          className={`text-sm rounded-md px-3 py-2 ${
            pdfError
              ? "bg-destructive/10 text-destructive"
              : "bg-primary/10 text-primary"
          }`}
        >
          {pdfMessage}
        </p>
      )}
      {(scan.reports || []).length > 0 && (
        <Card className="saas-card">
          <CardHeader>
            <CardTitle className="text-base">Generated reports</CardTitle>
          </CardHeader>
          <CardContent className="space-y-2">
            {scan.reports.map((r) => (
              <div key={r.id} className="flex items-center justify-between gap-3 rounded-lg border border-border/60 bg-muted/20 px-3 py-2">
                <span className="text-sm truncate max-w-xs font-medium" title={r.report_name}>
                  {r.report_name}
                </span>
                <div className="flex gap-2 shrink-0">
                  <Button
                    variant="default"
                    size="sm"
                    disabled={pdfDownloadingId === r.id}
                    onClick={() => handleViewExisting(r.id)}
                  >
                    {pdfDownloadingId === r.id ? (
                      <Loader2 className="h-3 w-3 animate-spin" />
                    ) : (
                      <FileText className="h-3 w-3" />
                    )}
                    View PDF
                  </Button>
                  <Button
                    variant="outline"
                    size="sm"
                    disabled={pdfDownloadingId === r.id}
                    onClick={() => handleDownloadExisting(r.id, r.report_name)}
                  >
                    <Download className="h-3 w-3" />
                    Download
                  </Button>
                </div>
              </div>
            ))}
          </CardContent>
        </Card>
      )}

      <Card className="saas-card border-primary/25 bg-gradient-to-br from-primary/5 to-transparent">
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <Shield className="h-5 w-5 text-primary" />
            Security score
          </CardTitle>
        </CardHeader>
        <CardContent>
          <SecurityScoreDisplay
            score={scan.security_score}
            grade={scan.grade}
            riskLevel={scan.risk_level}
          />
        </CardContent>
      </Card>

      <Card>
        <CardHeader>
          <CardTitle>Risk assessment</CardTitle>
          <CardDescription>Overall posture based on score and findings</CardDescription>
        </CardHeader>
        <CardContent className="space-y-4">
          <RiskMeter score={scan.security_score} riskLevel={scan.risk_level} />
          <div className="grid gap-3 sm:grid-cols-2 text-sm">
            <RiskFactor
              label="SSL certificate"
              ok={scan.ssl_status === "valid"}
              detail={scan.ssl_status || "unknown"}
            />
            <RiskFactor
              label="Certificate expiry"
              ok={scan.days_remaining != null && scan.days_remaining > 30}
              detail={
                scan.days_remaining != null
                  ? `${scan.days_remaining} days remaining`
                  : "unknown"
              }
            />
            <RiskFactor
              label="Modern TLS (1.2/1.3)"
              ok={tls.tls_1_2 || tls.tls_1_3}
              detail={scan.tls_version || "—"}
            />
            <RiskFactor
              label="Insecure TLS (1.0/1.1)"
              ok={!tls.tls_1_0 && !tls.tls_1_1}
              detail={
                tls.tls_1_0 || tls.tls_1_1 ? "Deprecated protocols enabled" : "None detected"
              }
            />
            <RiskFactor
              label="Security headers"
              ok={countPresentHeaders(scan.security_headers) >= 4}
              detail={`${countPresentHeaders(scan.security_headers)}/6 present`}
            />
            <RiskFactor
              label="Open findings"
              ok={(scan.findings?.length || 0) === 0}
              detail={`${scan.findings?.length || 0} issue(s)`}
            />
          </div>
          <p className="text-xs text-muted-foreground border-t border-border/60 pt-3">
            Scoring: SSL valid +30 · TLS 1.3 +20 · TLS 1.2 +10 · Headers up to +30 ·
            Cert &gt;30 days +10 (max 100). Risk: 90–100 Low · 70–89 Medium · 0–69 High.
          </p>
        </CardContent>
      </Card>

      {scan.ai_summary && (
        <Card className="border-primary/20">
          <CardHeader>
            <CardTitle>AI security summary</CardTitle>
            <CardDescription>Rule-based security auditor</CardDescription>
          </CardHeader>
          <CardContent className="space-y-3 text-sm">
            <p>{scan.ai_summary}</p>
            {aiRisk.risk_level && (
              <p>
                <span className="font-medium">AI risk level:</span>{" "}
                <span className="text-primary">{aiRisk.risk_level}</span> —{" "}
                {aiRisk.summary}
              </p>
            )}
          </CardContent>
        </Card>
      )}

      {aiRecs.length > 0 && (
        <Card>
          <CardHeader>
            <CardTitle>AI recommendations</CardTitle>
            <CardDescription>Prioritized remediation guidance</CardDescription>
          </CardHeader>
          <CardContent className="space-y-6">
            {["High", "Medium", "Low"].map((priority) => {
              const items = aiRecs.filter((r) => r.priority === priority);
              if (!items.length) return null;
              return (
                <div key={priority}>
                  <h4 className="mb-2 font-semibold text-sm">{priority} priority</h4>
                  <ul className="space-y-3">
                    {items.map((item, idx) => (
                      <li
                        key={idx}
                        className="rounded-md border border-border/60 p-3 text-sm"
                      >
                        <p className="font-medium">{item.title}</p>
                        <p className="text-muted-foreground mt-1">{item.description}</p>
                      </li>
                    ))}
                  </ul>
                </div>
              );
            })}
          </CardContent>
        </Card>
      )}

      <div className="grid gap-6 lg:grid-cols-2">
        <Card>
          <CardHeader>
            <CardTitle>SSL certificate</CardTitle>
            <CardDescription>Status: {scan.ssl_status}</CardDescription>
          </CardHeader>
          <CardContent className="space-y-2 text-sm">
            <Row label="Issuer" value={scan.issuer} />
            <Row label="Common name" value={scan.common_name} />
            <Row label="Organization" value={scan.organization} />
            <Row label="Valid from" value={formatDate(scan.valid_from)} />
            <Row label="Expiry date" value={formatDate(scan.valid_to)} />
            <Row
              label="Days remaining"
              value={
                scan.days_remaining != null ? String(scan.days_remaining) : "—"
              }
            />
            <Row label="Serial number" value={scan.serial_number} />
            <Row label="Signature algorithm" value={scan.signature_algorithm} />
            <Row label="Public key" value={scan.public_key_algorithm} />
          </CardContent>
        </Card>

        <Card>
          <CardHeader>
            <CardTitle>TLS analysis</CardTitle>
            <CardDescription>Highest: {scan.tls_version || "—"}</CardDescription>
          </CardHeader>
          <CardContent className="space-y-3">
            {TLS_LABELS.map(([key, label]) => (
              <div key={key} className="flex items-center justify-between text-sm">
                <span>{label}</span>
                {tls[key] ? (
                  <Check className="h-5 w-5 text-green-500" aria-label="supported" />
                ) : (
                  <X className="h-5 w-5 text-destructive" aria-label="not supported" />
                )}
              </div>
            ))}
          </CardContent>
        </Card>
      </div>

      <Card>
        <CardHeader>
          <CardTitle>Certificate chain</CardTitle>
        </CardHeader>
        <CardContent className="space-y-2 text-sm font-mono">
          <Row label="Root CA" value={scan.certificate_chain?.root_ca} />
          <Row label="Intermediate CA" value={scan.certificate_chain?.intermediate_ca} />
          <Row label="End entity" value={scan.certificate_chain?.end_entity} />
        </CardContent>
      </Card>

      <Card>
        <CardHeader>
          <CardTitle>Security headers</CardTitle>
        </CardHeader>
        <CardContent>
          <div className="saas-table-wrap">
            <table className="saas-table min-w-[400px]">
              <thead>
                <tr>
                  <th>Header</th>
                  <th>Status</th>
                </tr>
              </thead>
              <tbody>
                {Object.entries(HEADER_LABELS).map(([key, label]) => {
                  const present = scan.security_headers?.[key];
                  return (
                    <tr key={key}>
                      <td>{label}</td>
                      <td>
                        {present ? (
                          <span className="inline-flex items-center gap-1 text-green-500">
                            <Check className="h-3.5 w-3.5" /> Present
                          </span>
                        ) : (
                          <span className="inline-flex items-center gap-1 text-destructive">
                            <AlertCircle className="h-3.5 w-3.5" /> Missing
                          </span>
                        )}
                      </td>
                    </tr>
                  );
                })}
              </tbody>
            </table>
          </div>
        </CardContent>
      </Card>

      <Card>
        <CardHeader>
          <CardTitle>Findings &amp; recommendations</CardTitle>
          <CardDescription>{scan.findings?.length || 0} issue(s) identified</CardDescription>
        </CardHeader>
        <CardContent className="space-y-4">
          {(scan.findings || []).length === 0 ? (
            <div className="flex items-center gap-3 rounded-lg border border-green-500/20 bg-green-500/5 p-4 text-sm">
              <Check className="h-5 w-5 text-green-500 shrink-0" />
              <p>No critical findings detected — strong security posture.</p>
            </div>
          ) : (
            scan.findings.map((f, i) => (
              <div
                key={i}
                className="rounded-lg border border-border/60 bg-muted/20 p-4 space-y-2"
              >
                <div className="flex items-center gap-2">
                  <SeverityBadge severity={f.severity} />
                  <h4 className="font-medium">{f.title}</h4>
                </div>
                <p className="text-sm text-muted-foreground">
                  <span className="font-medium text-foreground">Recommendation: </span>
                  {f.recommendation}
                </p>
              </div>
            ))
          )}
        </CardContent>
      </Card>
    </div>
  );
}

function Row({ label, value }) {
  return (
    <div className="flex justify-between gap-4 border-b border-border/40 py-1.5 last:border-0">
      <span className="text-muted-foreground">{label}</span>
      <span className="text-right font-medium break-all">{value || "—"}</span>
    </div>
  );
}

function formatDate(iso) {
  if (!iso) return "—";
  try {
    return new Date(iso).toLocaleString();
  } catch {
    return iso;
  }
}

function countPresentHeaders(headers) {
  if (!headers) return 0;
  return Object.values(headers).filter(Boolean).length;
}

function RiskMeter({ score, riskLevel }) {
  const pct = Math.min(100, Math.max(0, score || 0));
  return (
    <div className="space-y-2">
      <div className="flex justify-between text-sm">
        <span className="text-muted-foreground">Security score</span>
        <span className={`font-medium ${riskClass(riskLevel)}`}>{riskLevel}</span>
      </div>
      <div className="h-3 w-full overflow-hidden rounded-full bg-secondary">
        <div
          className="h-full rounded-full bg-primary transition-all"
          style={{ width: `${pct}%` }}
        />
      </div>
    </div>
  );
}

function RiskFactor({ label, ok, detail }) {
  return (
    <div className="flex items-start gap-2 rounded-md border border-border/50 p-3">
      {ok ? (
        <Check className="h-4 w-4 shrink-0 text-green-500 mt-0.5" />
      ) : (
        <X className="h-4 w-4 shrink-0 text-destructive mt-0.5" />
      )}
      <div>
        <p className="font-medium">{label}</p>
        <p className="text-muted-foreground text-xs">{detail}</p>
      </div>
    </div>
  );
}
