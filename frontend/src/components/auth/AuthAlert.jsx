import { AlertCircle, CheckCircle2 } from "lucide-react";

import { cn } from "@/utils/cn";

export function AuthAlert({ variant = "error", children }) {
  const isError = variant === "error";
  return (
    <div
      role="alert"
      className={cn(
        "flex items-start gap-3 rounded-lg border px-4 py-3 text-sm",
        isError
          ? "border-destructive/30 bg-destructive/10 text-destructive"
          : "border-primary/30 bg-primary/10 text-primary"
      )}
    >
      {isError ? (
        <AlertCircle className="mt-0.5 h-4 w-4 shrink-0" aria-hidden />
      ) : (
        <CheckCircle2 className="mt-0.5 h-4 w-4 shrink-0" aria-hidden />
      )}
      <span className="leading-relaxed">{children}</span>
    </div>
  );
}
