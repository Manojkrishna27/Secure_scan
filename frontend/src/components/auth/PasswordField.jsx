import { useState } from "react";
import { Eye, EyeOff, Lock } from "lucide-react";

import { AuthField } from "@/components/auth/AuthField";
import { cn } from "@/utils/cn";

export function PasswordField({
  id,
  label,
  value,
  onChange,
  placeholder = "••••••••",
  autoComplete = "current-password",
  error,
  disabled,
  showStrength = false,
}) {
  const [visible, setVisible] = useState(false);
  const strength = showStrength ? getPasswordStrength(value) : null;

  return (
    <div className="space-y-1.5">
      <AuthField
        id={id}
        label={label}
        error={error}
        disabled={disabled}
        icon={Lock}
      >
        <input
          id={id}
          type={visible ? "text" : "password"}
          value={value}
          onChange={onChange}
          placeholder={placeholder}
          autoComplete={autoComplete}
          disabled={disabled}
          required
          aria-invalid={error ? "true" : undefined}
          className={cn(
            "saas-input h-11 w-full pr-10 pl-10 disabled:cursor-not-allowed disabled:opacity-60",
            error && "border-destructive/60 focus-visible:ring-destructive/40"
          )}
        />
        <button
          type="button"
          onClick={() => setVisible((v) => !v)}
          className="absolute right-3 top-1/2 -translate-y-1/2 text-muted-foreground transition-colors hover:text-foreground"
          aria-label={visible ? "Hide password" : "Show password"}
          tabIndex={-1}
        >
          {visible ? <EyeOff className="h-4 w-4" /> : <Eye className="h-4 w-4" />}
        </button>
      </AuthField>
      {strength && value.length > 0 && (
        <div className="space-y-1 pl-0.5">
          <div className="flex h-1 overflow-hidden rounded-full bg-muted">
            <div
              className={cn("h-full transition-all duration-300", strength.barClass)}
              style={{ width: `${strength.percent}%` }}
            />
          </div>
          <p className="text-xs text-muted-foreground">{strength.label}</p>
        </div>
      )}
    </div>
  );
}

function getPasswordStrength(password) {
  let score = 0;
  if (password.length >= 8) score += 1;
  if (password.length >= 12) score += 1;
  if (/[A-Z]/.test(password) && /[a-z]/.test(password)) score += 1;
  if (/\d/.test(password)) score += 1;
  if (/[^A-Za-z0-9]/.test(password)) score += 1;

  if (score <= 2) {
    return { percent: 33, label: "Weak — add length and mixed characters", barClass: "bg-destructive" };
  }
  if (score <= 3) {
    return { percent: 66, label: "Fair — almost there", barClass: "bg-amber-500" };
  }
  return { percent: 100, label: "Strong password", barClass: "bg-green-500" };
}
