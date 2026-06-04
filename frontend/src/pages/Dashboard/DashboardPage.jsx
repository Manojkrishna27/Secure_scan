import { useEffect, useState } from "react";
import { useNavigate } from "react-router-dom";
import {
  AlertTriangle,
  FileText,
  Globe,
  Loader2,
  ScanSearch,
  ShieldAlert,
  ShieldCheck,
} from "lucide-react";
import {
  Line,
  LineChart,
  ResponsiveContainer,
  Tooltip,
  XAxis,
  YAxis,
} from "recharts";

import { Button } from "@/components/ui/button";
import {
  Card,
  CardContent,
  CardDescription,
  CardHeader,
  CardTitle,
} from "@/components/ui/card";
import { EmptyState } from "@/components/EmptyState";
import { PageHeader } from "@/components/PageHeader";
import { StatCard } from "@/components/StatCard";
import { CardSkeleton, ChartSkeleton, PageHeaderSkeleton } from "@/components/ui/skeleton";
import { useAuth } from "@/context/AuthContext";
import { useToast } from "@/context/ToastContext";
import { getApiMessage } from "@/services/api";
import {
  getMonitoringSummary,
  getMonitoringTrends,
} from "@/services/monitoringService";
import { getNotifications } from "@/services/notificationService";
import { getReports } from "@/services/reportService";
import { getScans, startScan } from "@/services/scanService";

export default function DashboardPage() {
  const { user } = useAuth();
  const navigate = useNavigate();
  const toast = useToast();
  const [url, setUrl] = useState("https://");
  const [error, setError] = useState("");
  const [loadError, setLoadError] = useState("");
  const [pageLoading, setPageLoading] = useState(true);
  const [loading, setLoading] = useState(false);
  const [recentScans, setRecentScans] = useState([]);
  const [recentReports, setRecentReports] = useState([]);
  const [stats, setStats] = useState({
    totalScans: 0,
    avgScore: "—",
    totalReports: 0,
    trendData: [],
  });
  const [monitoring, setMonitoring] = useState({
    total_monitored: 0,
    high_risk_domains: 0,
    ssl_expiring_soon: 0,
  });
  const [recentAlerts, setRecentAlerts] = useState([]);

  const loadDashboard = async () => {
    setLoadError("");
    setPageLoading(true);
    try {
      const [scans, reports, monSummary, trends, notifications] =
        await Promise.all([
          getScans(),
          getReports(),
          getMonitoringSummary().catch(() => ({
            total_monitored: 0,
            high_risk_domains: 0,
            ssl_expiring_soon: 0,
          })),
          getMonitoringTrends(12).catch(() => []),
          getNotifications(5).catch(() => []),
        ]);
      setRecentScans(scans.slice(0, 5));
      setRecentReports(reports.slice(0, 5));
      setMonitoring(monSummary);
      setRecentAlerts(notifications);
      const totalScans = scans.length;
      const avgScore =
        totalScans > 0
          ? Math.round(
              scans.reduce((a, s) => a + (s.security_score || 0), 0) / totalScans
            )
          : "—";
      let trendData = trends.map((t, i) => ({
        name: new Date(t.scan_date).toLocaleDateString(undefined, {
          month: "short",
          day: "numeric",
        }) || `#${i + 1}`,
        score: t.score || 0,
      }));
      if (trendData.length < 2) {
        trendData = [...scans]
          .reverse()
          .slice(-8)
          .map((s, i) => ({
            name: `#${i + 1}`,
            score: s.security_score || 0,
          }));
      }
      setStats({
        totalScans,
        avgScore,
        totalReports: reports.length,
        trendData,
      });
    } catch (err) {
      setLoadError(getApiMessage(err, "Failed to load dashboard data."));
    } finally {
      setPageLoading(false);
    }
  };

  useEffect(() => {
    loadDashboard();
  }, []);

  const handleScan = async (e) => {
    e.preventDefault();
    setError("");
    setLoading(true);
    try {
      const { scan } = await startScan(url);
      toast.success("Scan completed successfully.");
      navigate(`/scan/${scan.id}`);
    } catch (err) {
      const msg = getApiMessage(err, "Scan failed. Please try again.");
      setError(msg);
      toast.error(msg);
    } finally {
      setLoading(false);
    }
  };

  if (pageLoading) {
    return (
      <div className="space-y-8">
        <PageHeaderSkeleton />
        <CardSkeleton lines={2} />
        <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-3">
          {Array.from({ length: 6 }).map((_, i) => (
            <CardSkeleton key={i} lines={1} />
          ))}
        </div>
        <ChartSkeleton />
      </div>
    );
  }

  return (
    <div className="space-y-8">
      <PageHeader
        title={`Welcome back, ${user?.full_name?.split(" ")[0] || "User"}`}
        description="Monitor security posture, run scans, and review reports from your command center."
      />
      {loadError && (
        <p role="alert" className="rounded-md bg-destructive/10 px-3 py-2 text-sm text-destructive">
          {loadError}
        </p>
      )}

      <Card className="saas-card border-primary/20">
        <CardHeader>
          <CardTitle className="flex items-center gap-2 text-xl">
            <ScanSearch className="h-5 w-5 text-primary" />
            Security scan
          </CardTitle>
          <CardDescription>
            Analyze SSL certificates, TLS versions, and security headers in seconds
          </CardDescription>
        </CardHeader>
        <CardContent>
          <form onSubmit={handleScan} className="flex flex-col gap-4 sm:flex-row">
            <input
              type="url"
              value={url}
              onChange={(e) => setUrl(e.target.value)}
              placeholder="https://example.com"
              className="saas-input flex-1"
              required
              aria-label="Website URL to scan"
            />
            <Button type="submit" disabled={loading}>
              {loading ? (
                <>
                  <Loader2 className="h-4 w-4 animate-spin" />
                  Scanning...
                </>
              ) : (
                "Analyze Website"
              )}
            </Button>
          </form>
          {error && <p className="mt-3 text-sm text-destructive">{error}</p>}
        </CardContent>
      </Card>

      <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-3 xl:grid-cols-6">
        <StatCard label="Total scans" value={stats.totalScans} icon={ScanSearch} />
        <StatCard label="Avg. security score" value={stats.avgScore} icon={ShieldCheck} />
        <StatCard label="Reports" value={stats.totalReports} icon={FileText} />
        <StatCard label="Monitored domains" value={monitoring.total_monitored} icon={Globe} />
        <StatCard
          label="High risk domains"
          value={monitoring.high_risk_domains}
          icon={ShieldAlert}
        />
        <StatCard
          label="SSL expiring soon"
          value={monitoring.ssl_expiring_soon}
          icon={AlertTriangle}
        />
      </div>

      {stats.trendData.length > 1 && (
        <Card>
          <CardHeader>
            <CardTitle>Security trend</CardTitle>
            <CardDescription>
              Monitoring history and recent scan scores
            </CardDescription>
          </CardHeader>
          <CardContent className="h-56">
            <ResponsiveContainer width="100%" height="100%">
              <LineChart data={stats.trendData}>
                <XAxis dataKey="name" stroke="hsl(var(--muted-foreground))" />
                <YAxis domain={[0, 100]} stroke="hsl(var(--muted-foreground))" />
                <Tooltip
                  contentStyle={{
                    background: "hsl(var(--card))",
                    border: "1px solid hsl(var(--border))",
                  }}
                />
                <Line
                  type="monotone"
                  dataKey="score"
                  stroke="hsl(var(--primary))"
                  strokeWidth={2}
                  dot
                />
              </LineChart>
            </ResponsiveContainer>
          </CardContent>
        </Card>
      )}

      <div className="grid gap-6 lg:grid-cols-3">
        <Card>
          <CardHeader>
            <CardTitle>Recent alerts</CardTitle>
            <CardDescription>Latest monitoring notifications</CardDescription>
          </CardHeader>
          <CardContent>
            {recentAlerts.length === 0 ? (
              <EmptyState
                icon={AlertTriangle}
                title="No alerts yet"
                description="Monitoring notifications will appear here when thresholds are crossed."
                actionLabel="Set up monitoring"
                onAction={() => navigate("/monitoring")}
                className="py-10 border-none bg-transparent"
              />
            ) : (
              <ul className="divide-y divide-border">
                {recentAlerts.map((alert) => (
                  <li key={alert.id} className="py-3 text-sm">
                    <p className="font-medium">{alert.title}</p>
                    <p className="text-muted-foreground line-clamp-2">{alert.message}</p>
                    <p className="mt-1 text-xs capitalize text-primary">
                      {alert.severity} · {alert.domain}
                    </p>
                  </li>
                ))}
              </ul>
            )}
            <Button
              variant="link"
              className="mt-2 h-auto p-0"
              onClick={() => navigate("/monitoring")}
            >
              Manage monitoring
            </Button>
          </CardContent>
        </Card>

        <Card>
          <CardHeader>
            <CardTitle>Recent scans</CardTitle>
          </CardHeader>
          <CardContent>
            {recentScans.length === 0 ? (
              <EmptyState
                icon={ScanSearch}
                title="No scans available"
                description="Run your first security scan using the form above."
                className="py-10 border-none bg-transparent"
              />
            ) : (
              <ul className="divide-y divide-border">
                {recentScans.map((scan) => (
                  <li
                    key={scan.id}
                    className="flex items-center justify-between py-3 text-sm"
                  >
                    <span className="truncate pr-4">{scan.url}</span>
                    <Button
                      variant="ghost"
                      size="sm"
                      onClick={() => navigate(`/scan/${scan.id}`)}
                    >
                      {scan.security_score}/100
                    </Button>
                  </li>
                ))}
              </ul>
            )}
          </CardContent>
        </Card>

        <Card>
          <CardHeader>
            <CardTitle>Recent reports</CardTitle>
          </CardHeader>
          <CardContent>
            {recentReports.length === 0 ? (
              <EmptyState
                icon={FileText}
                title="No reports generated"
                description="Generate a PDF from any completed scan."
                actionLabel="View scan history"
                onAction={() => navigate("/scans")}
                className="py-10 border-none bg-transparent"
              />
            ) : (
              <ul className="divide-y divide-border">
                {recentReports.map((report) => (
                  <li
                    key={report.id}
                    className="flex items-center justify-between py-3 text-sm"
                  >
                    <span className="truncate pr-4">{report.domain || report.report_name}</span>
                    <Button
                      variant="ghost"
                      size="sm"
                      onClick={() => navigate(`/scan/${report.scan_id}`)}
                    >
                      View
                    </Button>
                  </li>
                ))}
              </ul>
            )}
          </CardContent>
        </Card>
      </div>
    </div>
  );
}
