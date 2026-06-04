import { useEffect, useState } from "react";
import {
  Bar,
  BarChart,
  Cell,
  Line,
  LineChart,
  Pie,
  PieChart,
  ResponsiveContainer,
  Tooltip,
  XAxis,
  YAxis,
} from "recharts";
import { Download, Search } from "lucide-react";

import { StatCard } from "@/components/StatCard";
import { Button } from "@/components/ui/button";
import {
  Card,
  CardContent,
  CardHeader,
  CardTitle,
} from "@/components/ui/card";
import { CardSkeleton, ChartSkeleton } from "@/components/ui/skeleton";
import {
  adminSearch,
  exportAuditLogsCsv,
  exportScansCsv,
  exportUsersCsv,
  getAdminAnalytics,
  getAdminHealth,
  getAdminRecent,
  getAdminStats,
} from "@/services/adminService";

const PIE_COLORS = ["#22c55e", "#eab308", "#ef4444", "#6366f1"];

export default function AdminDashboard() {
  const [stats, setStats] = useState(null);
  const [analytics, setAnalytics] = useState(null);
  const [recent, setRecent] = useState(null);
  const [health, setHealth] = useState(null);
  const [loading, setLoading] = useState(true);
  const [searchQ, setSearchQ] = useState("");
  const [searchResults, setSearchResults] = useState(null);

  useEffect(() => {
    Promise.all([
      getAdminStats(),
      getAdminAnalytics("daily"),
      getAdminRecent(),
      getAdminHealth(),
    ])
      .then(([s, a, r, h]) => {
        setStats(s);
        setAnalytics(a);
        setRecent(r);
        setHealth(h);
      })
      .finally(() => setLoading(false));
  }, []);

  const handleSearch = async (e) => {
    e.preventDefault();
    if (searchQ.trim().length < 2) return;
    const data = await adminSearch(searchQ.trim());
    setSearchResults(data);
  };

  if (loading) {
    return (
      <div className="space-y-8">
        <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-3">
          {Array.from({ length: 6 }).map((_, i) => (
            <CardSkeleton key={i} lines={1} />
          ))}
        </div>
        <div className="grid gap-6 lg:grid-cols-2">
          <ChartSkeleton />
          <ChartSkeleton />
        </div>
      </div>
    );
  }

  const kpis = [
    { label: "Total users", value: stats?.total_users ?? 0 },
    { label: "Total scans", value: stats?.total_scans ?? 0 },
    { label: "Total reports", value: stats?.total_reports ?? 0 },
    { label: "Monitored domains", value: stats?.total_domains ?? 0 },
    { label: "Notifications", value: stats?.total_notifications ?? 0 },
    { label: "High risk domains", value: stats?.high_risk_domains ?? 0 },
  ];

  return (
    <div className="space-y-8">
      <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-3">
        {kpis.map((k) => (
          <StatCard key={k.label} label={k.label} value={k.value} />
        ))}
      </div>

      <Card>
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <Search className="h-5 w-5" />
            Global search
          </CardTitle>
        </CardHeader>
        <CardContent>
          <form onSubmit={handleSearch} className="flex gap-2">
            <input
              value={searchQ}
              onChange={(e) => setSearchQ(e.target.value)}
              placeholder="Users, domains, scans, reports..."
              className="saas-input h-10 flex-1"
            />
            <Button type="submit">Search</Button>
          </form>
          {searchResults && (
            <div className="mt-4 grid gap-4 text-sm md:grid-cols-2">
              {["users", "scans", "reports", "domains"].map((key) =>
                searchResults[key]?.length > 0 ? (
                  <div key={key}>
                    <p className="mb-1 font-medium capitalize">{key}</p>
                    <ul className="text-muted-foreground">
                      {searchResults[key].slice(0, 5).map((item) => (
                        <li key={item.id} className="truncate">
                          {item.full_name || item.email || item.domain || item.url || item.report_name}
                        </li>
                      ))}
                    </ul>
                  </div>
                ) : null
              )}
            </div>
          )}
        </CardContent>
      </Card>

      <div className="grid gap-6 lg:grid-cols-2">
        <Card>
          <CardHeader>
            <CardTitle>User growth</CardTitle>
          </CardHeader>
          <CardContent className="h-56">
            <ResponsiveContainer width="100%" height="100%">
              <LineChart data={analytics?.user_growth || []}>
                <XAxis dataKey="label" stroke="hsl(var(--muted-foreground))" />
                <YAxis stroke="hsl(var(--muted-foreground))" />
                <Tooltip />
                <Line type="monotone" dataKey="count" stroke="hsl(var(--primary))" />
              </LineChart>
            </ResponsiveContainer>
          </CardContent>
        </Card>
        <Card>
          <CardHeader>
            <CardTitle>Scan activity</CardTitle>
          </CardHeader>
          <CardContent className="h-56">
            <ResponsiveContainer width="100%" height="100%">
              <BarChart data={analytics?.scan_activity || []}>
                <XAxis dataKey="label" stroke="hsl(var(--muted-foreground))" />
                <YAxis stroke="hsl(var(--muted-foreground))" />
                <Tooltip />
                <Bar dataKey="count" fill="hsl(var(--primary))" />
              </BarChart>
            </ResponsiveContainer>
          </CardContent>
        </Card>
      </div>

      <div className="grid gap-6 lg:grid-cols-2">
        <Card>
          <CardHeader>
            <CardTitle>Risk distribution</CardTitle>
          </CardHeader>
          <CardContent className="h-56">
            <ResponsiveContainer width="100%" height="100%">
              <PieChart>
                <Pie
                  data={analytics?.risk_distribution || []}
                  dataKey="value"
                  nameKey="name"
                  cx="50%"
                  cy="50%"
                  outerRadius={80}
                  label
                >
                  {(analytics?.risk_distribution || []).map((_, i) => (
                    <Cell key={i} fill={PIE_COLORS[i % PIE_COLORS.length]} />
                  ))}
                </Pie>
                <Tooltip />
              </PieChart>
            </ResponsiveContainer>
          </CardContent>
        </Card>
        <Card>
          <CardHeader>
            <CardTitle>Score distribution</CardTitle>
          </CardHeader>
          <CardContent className="h-56">
            <ResponsiveContainer width="100%" height="100%">
              <BarChart data={analytics?.score_distribution || []}>
                <XAxis dataKey="range" stroke="hsl(var(--muted-foreground))" />
                <YAxis stroke="hsl(var(--muted-foreground))" />
                <Tooltip />
                <Bar dataKey="count" fill="hsl(var(--primary))" />
              </BarChart>
            </ResponsiveContainer>
          </CardContent>
        </Card>
      </div>

      <Card>
        <CardHeader>
          <CardTitle>System health</CardTitle>
        </CardHeader>
        <CardContent className="flex flex-wrap gap-6 text-sm">
          <span>Database: <strong>{health?.database}</strong></span>
          <span>API: <strong>{health?.api}</strong></span>
          <span>Monitoring: <strong>{health?.monitoring_service}</strong></span>
        </CardContent>
      </Card>

      <div className="flex flex-wrap gap-2">
        <Button variant="outline" onClick={exportUsersCsv}>
          <Download className="mr-2 h-4 w-4" />
          Export users
        </Button>
        <Button variant="outline" onClick={exportScansCsv}>
          <Download className="mr-2 h-4 w-4" />
          Export scans
        </Button>
        <Button variant="outline" onClick={exportAuditLogsCsv}>
          <Download className="mr-2 h-4 w-4" />
          Export audit logs
        </Button>
      </div>

      <div className="grid gap-6 lg:grid-cols-2">
        <Card>
          <CardHeader>
            <CardTitle>Recent users</CardTitle>
          </CardHeader>
          <CardContent>
            <ul className="divide-y divide-border text-sm">
              {(recent?.users || []).map((u) => (
                <li key={u.id} className="py-2">
                  {u.full_name} — {u.email}
                </li>
              ))}
            </ul>
          </CardContent>
        </Card>
        <Card>
          <CardHeader>
            <CardTitle>Recent alerts</CardTitle>
          </CardHeader>
          <CardContent>
            <ul className="divide-y divide-border text-sm">
              {(recent?.alerts || []).map((a) => (
                <li key={a.id} className="py-2">
                  {a.title} — {a.domain}
                </li>
              ))}
            </ul>
          </CardContent>
        </Card>
      </div>
    </div>
  );
}
