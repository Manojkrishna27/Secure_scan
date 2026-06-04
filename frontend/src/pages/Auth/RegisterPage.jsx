import { useState } from "react";
import { Link, useNavigate } from "react-router-dom";
import { Loader2, Mail, User } from "lucide-react";

import { AuthAlert } from "@/components/auth/AuthAlert";
import { AuthField } from "@/components/auth/AuthField";
import { AuthLayout } from "@/components/auth/AuthLayout";
import { PasswordField } from "@/components/auth/PasswordField";
import { Button } from "@/components/ui/button";
import { useAuth } from "@/context/AuthContext";
import { getApiMessage } from "@/services/api";

export default function RegisterPage() {
  const { register } = useAuth();
  const navigate = useNavigate();

  const [fullName, setFullName] = useState("");
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [confirmPassword, setConfirmPassword] = useState("");
  const [error, setError] = useState("");
  const [success, setSuccess] = useState("");
  const [loading, setLoading] = useState(false);

  const handleSubmit = async (e) => {
    e.preventDefault();
    setError("");
    setSuccess("");

    if (!fullName.trim()) {
      setError("Full name is required.");
      return;
    }
    if (!email.trim()) {
      setError("Email is required.");
      return;
    }
    if (password.length < 8) {
      setError("Password must be at least 8 characters.");
      return;
    }
    if (password !== confirmPassword) {
      setError("Passwords do not match.");
      return;
    }

    setLoading(true);
    try {
      await register(fullName.trim(), email.trim().toLowerCase(), password);
      setSuccess("Account created successfully. Redirecting you to sign in…");
      setTimeout(() => navigate("/login", { state: { registered: true } }), 1800);
    } catch (err) {
      setError(getApiMessage(err, "Registration failed. Please try again."));
    } finally {
      setLoading(false);
    }
  };

  return (
    <AuthLayout
      title="Create your account"
      subtitle="Start scanning websites for SSL, TLS, and security header issues in minutes."
      footer={
        <span>
          By registering, you agree to use SecureScan AI for authorized security assessments only.
        </span>
      }
    >
      <div className="saas-card rounded-xl border border-border/80 bg-card/50 p-6 shadow-sm sm:p-8">
        <form onSubmit={handleSubmit} className="space-y-5" noValidate>
          {error && <AuthAlert variant="error">{error}</AuthAlert>}
          {success && <AuthAlert variant="success">{success}</AuthAlert>}

          <AuthField
            id="fullName"
            label="Full name"
            type="text"
            value={fullName}
            onChange={(e) => setFullName(e.target.value)}
            placeholder="Alex Morgan"
            autoComplete="name"
            icon={User}
            disabled={loading}
          />

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

          <PasswordField
            id="password"
            label="Password"
            value={password}
            onChange={(e) => setPassword(e.target.value)}
            placeholder="Min. 8 characters"
            autoComplete="new-password"
            disabled={loading}
            showStrength
          />

          <PasswordField
            id="confirmPassword"
            label="Confirm password"
            value={confirmPassword}
            onChange={(e) => setConfirmPassword(e.target.value)}
            autoComplete="new-password"
            disabled={loading}
            error={
              confirmPassword && password !== confirmPassword
                ? "Passwords do not match"
                : undefined
            }
          />

          <Button type="submit" className="h-11 w-full text-sm font-semibold" disabled={loading}>
            {loading ? (
              <>
                <Loader2 className="h-4 w-4 animate-spin" aria-hidden />
                Creating account...
              </>
            ) : (
              "Create account"
            )}
          </Button>
        </form>

        <div className="relative my-6">
          <div className="absolute inset-0 flex items-center">
            <span className="w-full border-t border-border/80" />
          </div>
          <div className="relative flex justify-center text-xs uppercase">
            <span className="bg-card/50 px-2 text-muted-foreground">Already registered?</span>
          </div>
        </div>

        <p className="text-center text-sm text-muted-foreground">
          <Link
            to="/login"
            className="font-medium text-primary underline-offset-4 hover:underline"
          >
            Sign in to your account
          </Link>
        </p>
      </div>
    </AuthLayout>
  );
}
