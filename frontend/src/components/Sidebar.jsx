import { NavLink } from "react-router-dom";
import {
  Activity,
  FileText,
  LayoutDashboard,
  ScanSearch,
  Settings,
  Shield,
  X,
} from "lucide-react";

import { Button } from "@/components/ui/button";
import { useAuth } from "@/context/AuthContext";
import { cn } from "@/utils/cn";

const baseLinks = [
  { to: "/dashboard", label: "Dashboard", icon: LayoutDashboard },
  { to: "/monitoring", label: "Monitoring", icon: Activity },
  { to: "/scans", label: "Scan history", icon: ScanSearch },
  { to: "/reports", label: "Reports", icon: FileText },
  { to: "/settings", label: "Settings", icon: Settings },
];

const adminLink = { to: "/admin", label: "Administration", icon: Shield };

export function Sidebar({ mobileOpen = false, onClose }) {
  const { user } = useAuth();
  const links =
    user?.role === "admin" ? [...baseLinks, adminLink] : baseLinks;

  return (
    <>
      {mobileOpen && (
        <button
          type="button"
          className="fixed inset-0 z-40 bg-background/80 backdrop-blur-sm md:hidden"
          onClick={onClose}
          aria-label="Close navigation menu"
        />
      )}
      <aside
        className={cn(
          "fixed inset-y-0 left-0 z-50 flex w-64 flex-col border-r border-border/80 bg-card pt-14 transition-transform duration-200 ease-out md:static md:z-auto md:translate-x-0 md:pt-0 md:shrink-0",
          mobileOpen ? "translate-x-0" : "-translate-x-full md:translate-x-0"
        )}
        aria-label="Main navigation"
      >
        <div className="flex items-center justify-between border-b border-border/60 px-4 py-3 md:hidden">
          <span className="text-sm font-semibold">Navigation</span>
          <Button
            type="button"
            variant="ghost"
            size="sm"
            onClick={onClose}
            aria-label="Close menu"
          >
            <X className="h-4 w-4" />
          </Button>
        </div>
        <nav className="flex flex-1 flex-col gap-0.5 p-3">
          {links.map(({ to, label, icon: Icon }) => (
            <NavLink
              key={to}
              to={to}
              onClick={onClose}
              className={({ isActive }) =>
                cn(
                  "flex items-center gap-3 rounded-md px-3 py-2.5 text-sm font-medium transition-colors",
                  isActive
                    ? "saas-nav-active pl-[10px]"
                    : "border-l-2 border-transparent text-muted-foreground hover:bg-accent/50 hover:text-foreground"
                )
              }
            >
              <Icon className="h-4 w-4 shrink-0" aria-hidden />
              {label}
            </NavLink>
          ))}
        </nav>
        <div className="mt-auto border-t border-border/60 p-4 text-xs text-muted-foreground">
          <p className="font-medium text-foreground/80 truncate">
            {user?.full_name}
          </p>
          <p className="truncate">{user?.email}</p>
        </div>
      </aside>
    </>
  );
}
