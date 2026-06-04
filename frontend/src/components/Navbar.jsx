import { useState } from "react";
import { Link, NavLink, useNavigate } from "react-router-dom";
import { LogOut, Menu, Shield, User } from "lucide-react";

import { NotificationBell } from "@/components/NotificationBell";
import { Button } from "@/components/ui/button";
import { ConfirmDialog } from "@/components/ui/ConfirmDialog";
import { useAuth } from "@/context/AuthContext";
import { cn } from "@/utils/cn";

const mobileNavLinks = [
  { to: "/dashboard", label: "Dashboard" },
  { to: "/monitoring", label: "Monitoring" },
  { to: "/scans", label: "Scan history" },
  { to: "/reports", label: "Reports" },
  { to: "/settings", label: "Settings" },
];

const landingNavLinks = [
  { href: "/#features", label: "Features" },
  { href: "/#how-it-works", label: "How it works" },
  { href: "/#sample-report", label: "Sample report" },
];

export function Navbar({ onMenuToggle, showMenuButton = false }) {
  const { isAuthenticated, user, logout } = useAuth();
  const navigate = useNavigate();
  const [logoutOpen, setLogoutOpen] = useState(false);
  const [logoutLoading, setLogoutLoading] = useState(false);

  const handleLogoutConfirm = async () => {
    setLogoutLoading(true);
    try {
      await logout();
      setLogoutOpen(false);
      navigate("/login", { replace: true });
    } finally {
      setLogoutLoading(false);
    }
  };

  return (
    <>
      <header className="sticky top-0 z-50 border-b border-border/80 bg-card/90 backdrop-blur-md">
        <div className="container flex h-14 items-center justify-between gap-4">
          <div className="flex items-center gap-3 min-w-0">
            {showMenuButton && isAuthenticated && (
              <Button
                type="button"
                variant="ghost"
                size="sm"
                className="md:hidden shrink-0"
                onClick={onMenuToggle}
                aria-label="Open navigation menu"
              >
                <Menu className="h-5 w-5" />
              </Button>
            )}
            <Link
              to={isAuthenticated ? "/dashboard" : "/"}
              className="flex items-center gap-2.5 font-semibold tracking-tight min-w-0"
            >
              <span className="flex h-8 w-8 shrink-0 items-center justify-center rounded-md bg-primary/15">
                <Shield className="h-4 w-4 text-primary" aria-hidden />
              </span>
              <span className="truncate hidden sm:inline">SecureScan AI</span>
            </Link>
          </div>

          <nav className="flex items-center gap-1 sm:gap-2" aria-label="Account navigation">
            {isAuthenticated ? (
              <>
                <NotificationBell />
                <div className="hidden lg:flex items-center gap-1 text-sm text-muted-foreground px-2 max-w-[200px] truncate">
                  <User className="h-4 w-4 shrink-0" aria-hidden />
                  <span className="truncate" title={user?.email}>
                    {user?.full_name || user?.email}
                  </span>
                </div>
                {user?.role === "admin" && (
                  <Button variant="ghost" size="sm" className="hidden md:inline-flex" asChild>
                    <NavLink
                      to="/admin"
                      className={({ isActive }) =>
                        cn(isActive && "text-primary bg-primary/10")
                      }
                    >
                      Admin
                    </NavLink>
                  </Button>
                )}
                <Button
                  variant="outline"
                  size="sm"
                  onClick={() => setLogoutOpen(true)}
                  className="gap-1.5"
                >
                  <LogOut className="h-4 w-4" aria-hidden />
                  <span className="hidden sm:inline">Logout</span>
                </Button>
              </>
            ) : (
              <>
                <nav className="hidden md:flex items-center gap-1 mr-2" aria-label="Landing sections">
                  {landingNavLinks.map(({ href, label }) => (
                    <a
                      key={href}
                      href={href}
                      className="rounded-md px-3 py-1.5 text-sm text-muted-foreground transition-colors hover:text-foreground"
                    >
                      {label}
                    </a>
                  ))}
                </nav>
                <Button variant="ghost" size="sm" asChild>
                  <Link to="/login">Login</Link>
                </Button>
                <Button size="sm" asChild>
                  <Link to="/register">Register</Link>
                </Button>
              </>
            )}
          </nav>
        </div>

        {showMenuButton && isAuthenticated && (
          <nav
            className="md:hidden border-t border-border/60 px-4 py-2 flex gap-1 overflow-x-auto"
            aria-label="Quick navigation"
          >
            {mobileNavLinks.map(({ to, label }) => (
              <NavLink
                key={to}
                to={to}
                className={({ isActive }) =>
                  cn(
                    "shrink-0 rounded-md px-3 py-1.5 text-xs font-medium transition-colors",
                    isActive
                      ? "bg-primary/15 text-primary"
                      : "text-muted-foreground hover:text-foreground"
                  )
                }
              >
                {label}
              </NavLink>
            ))}
            {user?.role === "admin" && (
              <NavLink
                to="/admin"
                className={({ isActive }) =>
                  cn(
                    "shrink-0 rounded-md px-3 py-1.5 text-xs font-medium",
                    isActive ? "bg-primary/15 text-primary" : "text-muted-foreground"
                  )
                }
              >
                Admin
              </NavLink>
            )}
          </nav>
        )}
      </header>

      <ConfirmDialog
        open={logoutOpen}
        onOpenChange={setLogoutOpen}
        title="Confirm Logout"
        message="Are you sure you want to logout from SecureScan AI?"
        confirmLabel="Yes, Logout"
        cancelLabel="Cancel"
        confirmVariant="destructive"
        loading={logoutLoading}
        onConfirm={handleLogoutConfirm}
      />
    </>
  );
}
