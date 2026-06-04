import { useEffect, useState } from "react";
import { useNavigate } from "react-router-dom";
import {
  Activity,
  Globe,
  Loader2,
  Plus,
  RefreshCw,
  Trash2,
} from "lucide-react";

import { EmptyState } from "@/components/EmptyState";
import { PageHeader } from "@/components/PageHeader";
import { Button } from "@/components/ui/button";
import { CardSkeleton, TableSkeleton } from "@/components/ui/skeleton";
import { riskClass } from "@/utils/risk";
import {
  Card,
  CardContent,
  CardDescription,
  CardHeader,
  CardTitle,
} from "@/components/ui/card";
import {
  addDomain,
  deleteDomain,
  getDomains,
  runScan,
  updateDomain,
} from "@/services/monitoringService";
import { getApiMessage } from "@/services/api";
import { cn } from "@/utils/cn";

function formatDate(iso) {
  if (!iso) return "—";
  return new Date(iso).toLocaleString();
}

export default function MonitoringPage() {
  const navigate = useNavigate();
  const [domains, setDomains] = useState([]);
  const [domainInput, setDomainInput] = useState("");
  const [frequency, setFrequency] = useState("daily");
  const [loading, setLoading] = useState(true);
  const [adding, setAdding] = useState(false);
  const [scanningId, setScanningId] = useState(null);
  const [error, setError] = useState("");

  const load = async () => {
    setLoading(true);
    try {
      const list = await getDomains();
      setDomains(list);
    } catch (err) {
      setError(getApiMessage(err, "Failed to load monitored domains."));
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    load();
  }, []);

  const handleAdd = async (e) => {
    e.preventDefault();
    setError("");
    setAdding(true);
    try {
      await addDomain(domainInput, frequency);
      setDomainInput("");
      await load();
    } catch (err) {
      setError(getApiMessage(err, "Failed to add domain."));
    } finally {
      setAdding(false);
    }
  };

  const handleScan = async (id) => {
    setScanningId(id);
    setError("");
    try {
      const result = await runScan(id);
      await load();
      if (result.scan_id) {
        navigate(`/scan/${result.scan_id}`);
      }
    } catch (err) {
      setError(getApiMessage(err, "Scan failed."));
    } finally {
      setScanningId(null);
    }
  };

  const handleToggleActive = async (d) => {
    try {
      await updateDomain(d.id, { is_active: !d.is_active });
      await load();
    } catch (err) {
      setError(getApiMessage(err, "Update failed."));
    }
  };

  const handleFrequency = async (d, freq) => {
    try {
      await updateDomain(d.id, { monitoring_frequency: freq });
      await load();
    } catch (err) {
      setError(getApiMessage(err, "Update failed."));
    }
  };

  const handleDelete = async (id) => {
    if (!window.confirm("Remove this domain from monitoring?")) return;
    try {
      await deleteDomain(id);
      await load();
    } catch (err) {
      setError(getApiMessage(err, "Delete failed."));
    }
  };

  if (loading && domains.length === 0) {
    return (
      <div className="space-y-8">
        <PageHeader title="Domain monitoring" description="Loading watchlist…" />
        <CardSkeleton lines={2} />
        <TableSkeleton rows={4} cols={7} />
      </div>
    );
  }

  return (
    <div className="space-y-8">
      <PageHeader
        title="Domain monitoring"
        description="Track SSL expiry, security scores, TLS, and header changes over time."
      />

      <Card className="saas-card">
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <Plus className="h-5 w-5" />
            Add domain
          </CardTitle>
          <CardDescription>Example: github.com, google.com</CardDescription>
        </CardHeader>
        <CardContent>
          <form onSubmit={handleAdd} className="flex flex-col gap-4 sm:flex-row">
            <input
              type="text"
              value={domainInput}
              onChange={(e) => setDomainInput(e.target.value)}
              placeholder="github.com"
              className="saas-input flex-1"
              required
            />
            <select
              value={frequency}
              onChange={(e) => setFrequency(e.target.value)}
              className="h-11 rounded-md border border-input bg-background px-3 text-sm"
            >
              <option value="daily">Daily</option>
              <option value="weekly">Weekly</option>
            </select>
            <Button type="submit" disabled={adding}>
              {adding ? (
                <>
                  <Loader2 className="h-4 w-4 animate-spin" />
                  Adding...
                </>
              ) : (
                "Add domain"
              )}
            </Button>
          </form>
          {error && <p className="mt-3 text-sm text-destructive">{error}</p>}
        </CardContent>
      </Card>

      <Card>
        <CardHeader>
          <CardTitle>Monitored domains</CardTitle>
          <CardDescription>
            {domains.length} domain{domains.length !== 1 ? "s" : ""} on your watchlist
          </CardDescription>
        </CardHeader>
        <CardContent>
          {domains.length === 0 ? (
            <EmptyState
              icon={Globe}
              title="No monitored domains"
              description="Add a domain above to receive scheduled scans and security alerts."
            />
          ) : (
            <div className="saas-table-wrap">
              <table className="saas-table">
                <thead>
                  <tr>
                    <th>Domain</th>
                    <th>Status</th>
                    <th>Frequency</th>
                    <th>Score</th>
                    <th>Risk</th>
                    <th>Last scan</th>
                    <th>Actions</th>
                  </tr>
                </thead>
                <tbody>
                  {domains.map((d) => (
                    <tr key={d.id}>
                      <td className="font-medium">{d.domain}</td>
                      <td>
                        <span
                          className={
                            d.is_active
                              ? "inline-flex rounded-full bg-green-500/15 px-2 py-0.5 text-xs font-medium text-green-500"
                              : "inline-flex rounded-full bg-muted px-2 py-0.5 text-xs text-muted-foreground"
                          }
                        >
                          {d.is_active ? "Active" : "Paused"}
                        </span>
                      </td>
                      <td>
                        <select
                          value={d.monitoring_frequency}
                          onChange={(e) => handleFrequency(d, e.target.value)}
                          className="rounded border border-input bg-background px-2 py-1 text-xs"
                        >
                          <option value="daily">Daily</option>
                          <option value="weekly">Weekly</option>
                        </select>
                      </td>
                      <td>
                        {d.current_score != null ? `${d.current_score}/100` : "—"}
                      </td>
                      <td className={cn("capitalize font-medium", riskClass(d.current_risk_level))}>
                        {d.current_risk_level || "—"}
                      </td>
                      <td className="text-muted-foreground text-xs">
                        {formatDate(d.last_scan_at)}
                      </td>
                      <td>
                        <div className="flex flex-wrap gap-2">
                          <Button
                            size="sm"
                            variant="outline"
                            disabled={scanningId === d.id || !d.is_active}
                            onClick={() => handleScan(d.id)}
                          >
                            {scanningId === d.id ? (
                              <Loader2 className="h-4 w-4 animate-spin" />
                            ) : (
                              <RefreshCw className="h-4 w-4" />
                            )}
                            <span className="ml-1 hidden sm:inline">Scan</span>
                          </Button>
                          <Button
                            size="sm"
                            variant="ghost"
                            onClick={() => handleToggleActive(d)}
                          >
                            {d.is_active ? "Pause" : "Resume"}
                          </Button>
                          <Button
                            size="sm"
                            variant="ghost"
                            className="text-destructive"
                            onClick={() => handleDelete(d.id)}
                          >
                            <Trash2 className="h-4 w-4" />
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
