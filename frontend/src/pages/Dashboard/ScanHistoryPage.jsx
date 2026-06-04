import { useEffect, useState } from "react";
import { Link, useNavigate } from "react-router-dom";
import { ScanSearch, Trash2 } from "lucide-react";

import { EmptyState } from "@/components/EmptyState";
import { PageHeader } from "@/components/PageHeader";
import { Button } from "@/components/ui/button";
import {
  Card,
  CardContent,
  CardDescription,
  CardHeader,
  CardTitle,
} from "@/components/ui/card";
import { TableSkeleton } from "@/components/ui/skeleton";
import { getApiMessage } from "@/services/api";
import { deleteScan, getScans } from "@/services/scanService";
import { riskClass } from "@/utils/risk";

export default function ScanHistoryPage() {
  const navigate = useNavigate();
  const [scans, setScans] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");

  const load = async () => {
    setLoading(true);
    try {
      const data = await getScans();
      setScans(data);
    } catch (err) {
      setError(getApiMessage(err, "Failed to load scans."));
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    load();
  }, []);

  const handleDelete = async (id) => {
    if (!window.confirm("Delete this scan?")) return;
    try {
      await deleteScan(id);
      setScans((prev) => prev.filter((s) => s.id !== id));
    } catch (err) {
      alert(getApiMessage(err, "Delete failed."));
    }
  };

  if (loading) {
    return (
      <div className="space-y-6">
        <PageHeader title="Scan history" description="Loading scans…" />
        <TableSkeleton rows={6} cols={5} />
      </div>
    );
  }

  return (
    <div className="space-y-6">
      <PageHeader
        title="Scan history"
        description="All your previous security assessments"
      />

      {error && (
        <p role="alert" className="text-sm text-destructive rounded-md bg-destructive/10 px-3 py-2">
          {error}
        </p>
      )}

      <Card className="saas-card">
        <CardHeader>
          <CardTitle>Scans</CardTitle>
          <CardDescription>{scans.length} total</CardDescription>
        </CardHeader>
        <CardContent>
          {scans.length === 0 ? (
            <EmptyState
              icon={ScanSearch}
              title="No scans available"
              description="Run a security scan from your dashboard to start building history."
              actionLabel="New scan"
              onAction={() => navigate("/dashboard")}
            />
          ) : (
            <div className="saas-table-wrap">
              <table className="saas-table">
                <thead>
                  <tr>
                    <th>URL</th>
                    <th>Score</th>
                    <th>Risk level</th>
                    <th>Date</th>
                    <th>Actions</th>
                  </tr>
                </thead>
                <tbody>
                  {scans.map((scan) => (
                    <tr key={scan.id}>
                      <td className="max-w-[200px] truncate font-medium sm:max-w-xs">
                        {scan.url}
                      </td>
                      <td className="tabular-nums">
                        {scan.security_score}/100
                        {scan.grade && (
                          <span className="ml-1 text-muted-foreground">({scan.grade})</span>
                        )}
                      </td>
                      <td className={riskClass(scan.risk_level)}>
                        {scan.risk_level}
                      </td>
                      <td className="text-muted-foreground text-xs whitespace-nowrap">
                        {scan.scan_date
                          ? new Date(scan.scan_date).toLocaleString()
                          : "—"}
                      </td>
                      <td>
                        <div className="flex gap-2">
                          <Button variant="outline" size="sm" asChild>
                            <Link to={`/scan/${scan.id}`}>Details</Link>
                          </Button>
                          <Button
                            variant="ghost"
                            size="icon"
                            onClick={() => handleDelete(scan.id)}
                            aria-label={`Delete scan ${scan.url}`}
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
