import { useEffect, useState } from "react";
import { FileText, ScrollText } from "lucide-react";

import { EmptyState } from "@/components/EmptyState";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { TableSkeleton } from "@/components/ui/skeleton";
import { exportAuditLogsCsv, getAuditLogs } from "@/services/adminService";

export default function AdminAuditLogs() {
  const [data, setData] = useState({ logs: [], page: 1, pages: 1 });
  const [loading, setLoading] = useState(true);
  const [action, setAction] = useState("");
  const [page, setPage] = useState(1);

  const load = async () => {
    setLoading(true);
    try {
      const result = await getAuditLogs({ page, per_page: 15, action: action || undefined });
      setData(result);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    load();
  }, [page, action]);

  return (
    <Card className="saas-card">
      <CardHeader className="flex flex-col gap-4 sm:flex-row sm:items-center sm:justify-between">
        <CardTitle className="flex items-center gap-2">
          <ScrollText className="h-5 w-5 text-primary" />
          Audit logs
        </CardTitle>
        <Button variant="outline" size="sm" onClick={exportAuditLogsCsv}>
          Export CSV
        </Button>
      </CardHeader>
      <CardContent>
        <div className="mb-6 flex flex-col gap-2 sm:flex-row">
          <input
            value={action}
            onChange={(e) => setAction(e.target.value)}
            placeholder="Filter by action..."
            className="saas-input h-10 flex-1"
            aria-label="Filter audit logs by action"
          />
          <Button
            variant="outline"
            onClick={() => {
              setPage(1);
              load();
            }}
          >
            Apply filter
          </Button>
        </div>
        {loading ? (
          <TableSkeleton rows={8} cols={1} />
        ) : data.logs.length === 0 ? (
          <EmptyState
            icon={FileText}
            title="No audit entries"
            description="Administrative actions will be recorded here for compliance review."
          />
        ) : (
          <>
            <ul className="divide-y divide-border rounded-lg border border-border/60">
              {data.logs.map((log) => (
                <li
                  key={log.id}
                  className="px-4 py-4 text-sm transition-colors hover:bg-accent/30"
                >
                  <p className="font-medium">{log.description}</p>
                  <p className="mt-1 text-xs text-muted-foreground">
                    <span className="font-mono text-primary/80">{log.action}</span>
                    {" · "}
                    {log.target_type} #{log.target_id}
                    {" · "}
                    {log.admin_name || "system"}
                    {" · "}
                    {new Date(log.created_at).toLocaleString()}
                  </p>
                </li>
              ))}
            </ul>
            <div className="mt-6 flex flex-wrap items-center justify-between gap-4">
              <Button
                variant="outline"
                size="sm"
                disabled={page <= 1}
                onClick={() => setPage((p) => p - 1)}
              >
                Previous
              </Button>
              <span className="text-sm text-muted-foreground tabular-nums">
                Page {data.page} of {data.pages || 1}
              </span>
              <Button
                variant="outline"
                size="sm"
                disabled={page >= data.pages}
                onClick={() => setPage((p) => p + 1)}
              >
                Next
              </Button>
            </div>
          </>
        )}
      </CardContent>
    </Card>
  );
}
