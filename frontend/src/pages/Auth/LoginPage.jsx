import { useState } from "react";
import { Link, useNavigate, useLocation } from "react-router-dom";
import { Loader2, Mail } from "lucide-react";

import { AuthAlert } from "@/components/auth/AuthAlert";
import { AuthField } from "@/components/auth/AuthField";
import { AuthLayout } from "@/components/auth/AuthLayout";
import { PasswordField } from "@/components/auth/PasswordField";
import { Button } from "@/components/ui/button";
import { useAuth } from "@/context/AuthContext";
import { getApiMessage } from "@/services/api";

export default function LoginPage() {
  const { login } = useAuth();
  const navigate = useNavigate();
  const location = useLocation();
  const from = location.state?.from?.pathname || "/dashboard";
  const justRegistered = location.state?.registered;

  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [error, setError] = useState("");
  const [loading, setLoading] = useState(false);

  const handleSubmit = async (e) => {
    e.preventDefault();
    setError("");

    if (!email.trim()) {
      setError("Email is required.");
      return;
    }
    if (!password) {
      setError("Password is required.");
      return;
    }

    setLoading(true);
    try {
      await login(email.trim().toLowerCase(), password);
      navigate(from, { replace: true });
    } catch (err) {
      setError(getApiMessage(err, "Login failed. Please check your credentials."));
    } finally {
      setLoading(false);
    }
  };

  return (
    <AuthLayout
      title="Welcome back"
      subtitle="Sign in to access your security dashboard, scans, and reports."
      footer={
        <span>
          © {new Date().getFullYear()} SecureScan AI · Confidential security platform
        </span>
      }
    >
      <div className="saas-card rounded-xl border border-border/80 bg-card/50 p-6 shadow-sm sm:p-8">
        <form onSubmit={handleSubmit} className="space-y-5" noValidate>
          {justRegistered && (
            <AuthAlert variant="success">
              Your account is ready. Sign in with your email and password.
            </AuthAlert>
          )}
          {error && <AuthAlert variant="error">{error}</AuthAlert>}

          <AuthField
            id="email"
            label="Work email"
            type="email"
            value={email}
            onChange={(e) => setEmail(e.target.value)}
            placeholder="you@company.com"
            autoComplete="email"
            icon={Mail}
            disabled={loading}
          />

          <div className="space-y-1">
            <PasswordField
              id="password"
              label="Password"
              value={password}
              onChange={(e) => setPassword(e.target.value)}
              autoComplete="current-password"
              disabled={loading}
            />
          </div>

          <Button type="submit" className="h-11 w-full text-sm font-semibold" disabled={loading}>
            {loading ? (
              <>
                <Loader2 className="h-4 w-4 animate-spin" aria-hidden />
                Signing in...
              </>
            ) : (
              "Sign in"
            )}
          </Button>
        </form>

        <div className="relative my-6">
          <div className="absolute inset-0 flex items-center">
            <span className="w-full border-t border-border/80" />
          </div>
          <div className="relative flex justify-center text-xs uppercase">
            <span className="bg-card/50 px-2 text-muted-foreground">New to SecureScan?</span>
          </div>
        </div>

        <p className="text-center text-sm text-muted-foreground">
          Create a free account to run security scans and generate audit reports.{" "}
          <Link
            to="/register"
            className="font-medium text-primary underline-offset-4 hover:underline"
          >
            Sign up
          </Link>
        </p>
      </div>
    </AuthLayout>
  );
}
