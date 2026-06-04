import { NavLink, Outlet } from "react-router-dom";
import { BarChart3, FileText, LayoutDashboard, Users } from "lucide-react";

import { PageHeader } from "@/components/PageHeader";
import { cn } from "@/utils/cn";

const adminLinks = [
  { to: "/admin", label: "Overview", icon: LayoutDashboard, end: true },
  { to: "/admin/analytics", label: "Analytics", icon: BarChart3 },
  { to: "/admin/users", label: "Users", icon: Users },
  { to: "/admin/logs", label: "Audit logs", icon: FileText },
];

export default function AdminLayout() {
  return (
    <div className="space-y-6">
      <PageHeader
        title="Administration"
        description="Platform management, analytics, and compliance audit trails"
      />
      <nav
        className="flex gap-1 overflow-x-auto border-b border-border pb-px"
        aria-label="Admin sections"
      >
        {adminLinks.map(({ to, label, icon: Icon, end }) => (
          <NavLink
            key={to}
            to={to}
            end={end}
            className={({ isActive }) =>
              cn(
                "flex shrink-0 items-center gap-2 border-b-2 px-4 py-2.5 text-sm font-medium transition-colors -mb-px",
                isActive
                  ? "border-primary text-primary"
                  : "border-transparent text-muted-foreground hover:text-foreground hover:border-border"
              )
            }
          >
            <Icon className="h-4 w-4" aria-hidden />
            {label}
          </NavLink>
        ))}
      </nav>
      <Outlet />
    </div>
  );
}
