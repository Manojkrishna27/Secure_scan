import { useEffect, useState } from "react";
import { Link, useNavigate } from "react-router-dom";
import { Download, Eye, FileText, Loader2, Trash2 } from "lucide-react";

import { EmptyState } from "@/components/EmptyState";
import { PageHeader } from "@/components/PageHeader";
import { Button } from "@/components/ui/button";
import { TableSkeleton } from "@/components/ui/skeleton";
import {
  Card,
  CardContent,
  CardDescription,
  CardHeader,
  CardTitle,
} from "@/components/ui/card";
import {
  deleteReport,
  downloadReport,
  getReports,
  savePdfBlob,
} from "@/services/reportService";
import { getApiMessage } from "@/services/api";

export default function ReportsPage() {
  const navigate = useNavigate();
  const [reports, setReports] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");
  const [downloadingId, setDownloadingId] = useState(null);

  const load = async () => {
    setLoading(true);
    try {
      setReports(await getReports());
    } catch (err) {
      setError(getApiMessage(err, "Failed to load reports."));
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    load();
  }, []);

  const handleDownload = async (report) => {
    setDownloadingId(report.id);
    try {
      const response = await downloadReport(report.id);
      savePdfBlob(response.data, report.report_name || "securescan-report.pdf");
    } catch (err) {
      alert(getApiMessage(err, "Download failed."));
    } finally {
      setDownloadingId(null);
    }
  };

  const handleDelete = async (id) => {
    if (!window.confirm("Delete this report?")) return;
    try {
      await deleteReport(id);
      setReports((prev) => prev.filter((r) => r.id !== id));
    } catch (err) {
      alert(getApiMessage(err, "Delete failed."));
    }
  };

  if (loading) {
    return (
      <div className="space-y-6">
        <PageHeader title="Reports" description="Loading report history…" />
        <TableSkeleton rows={5} cols={5} />
      </div>
    );
  }

  return (
    <div className="space-y-6">
      <PageHeader
        title="Reports"
        description="PDF security assessments generated from your scans"
      />

      {error && <p className="text-sm text-destructive">{error}</p>}

      <Card>
        <CardHeader>
          <CardTitle>Report history</CardTitle>
          <CardDescription>{reports.length} report(s)</CardDescription>
        </CardHeader>
        <CardContent>
          {reports.length === 0 ? (
            <EmptyState
              icon={FileText}
              title="No reports generated"
              description="Complete a scan and generate a PDF report to build your compliance library."
              actionLabel="Go to dashboard"
              onAction={() => navigate("/dashboard")}
            />
          ) : (
            <div className="saas-table-wrap">
            <table className="saas-table">
              <thead>
                <tr>
                  <th>Report</th>
                  <th>Domain</th>
                  <th>Score</th>
                  <th>Created</th>
                  <th>Actions</th>
                </tr>
              </thead>
              <tbody>
                {reports.map((report) => (
                  <tr key={report.id}>
                    <td className="max-w-xs truncate font-medium">{report.report_name}</td>
                    <td>{report.domain || "—"}</td>
                    <td>
                      {report.security_score != null
                        ? `${report.security_score}/100`
                        : "—"}
                    </td>
                    <td className="text-muted-foreground">
                      {report.created_at
                        ? new Date(report.created_at).toLocaleString()
                        : "—"}
                    </td>
                    <td>
                      <div className="flex flex-wrap gap-2">
                        {report.scan_id && (
                          <Button variant="outline" size="sm" asChild>
                            <Link to={`/scan/${report.scan_id}`}>
                              <Eye className="h-3 w-3" />
                              View scan
                            </Link>
                          </Button>
                        )}
                        <Button
                          variant="outline"
                          size="sm"
                          disabled={downloadingId === report.id}
                          onClick={() => handleDownload(report)}
                        >
                          {downloadingId === report.id ? (
                            <Loader2 className="h-3 w-3 animate-spin" />
                          ) : (
                            <Download className="h-3 w-3" />
                          )}
                          Download
                        </Button>
                        <Button
                          variant="ghost"
                          size="icon"
                          onClick={() => handleDelete(report.id)}
                          aria-label="Delete report"
                        >
                          <Trash2 className="h-4 w-4 text-destructive" />
                        </Button>
                      </div>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
            </div>
          )}
        </CardContent>
      </Card>
    </div>
  );
}
