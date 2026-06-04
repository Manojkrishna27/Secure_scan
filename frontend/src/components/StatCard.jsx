import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { cn } from "@/utils/cn";

export function StatCard({ label, value, icon: Icon, hint, className }) {
  return (
    <Card className={cn("saas-stat-card", className)}>
      <CardHeader className="flex flex-row items-start justify-between space-y-0 pb-2">
        <CardDescription className="text-xs font-medium uppercase tracking-wide">
          {label}
        </CardDescription>
        {Icon && (
          <Icon className="h-4 w-4 text-primary/80" aria-hidden />
        )}
      </CardHeader>
      <CardContent>
        <CardTitle className="text-2xl font-bold tabular-nums">{value}</CardTitle>
        {hint && (
          <p className="mt-1 text-xs text-muted-foreground">{hint}</p>
        )}
      </CardContent>
    </Card>
  );
}
