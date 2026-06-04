import { Shield } from "lucide-react";

import { cn } from "@/utils/cn";
import { riskClass } from "@/utils/risk";

export function SecurityScoreDisplay({ score, grade, riskLevel, size = "lg" }) {
  const pct = Math.min(100, Math.max(0, score ?? 0));
  const radius = size === "lg" ? 52 : 40;
  const stroke = size === "lg" ? 8 : 6;
  const circumference = 2 * Math.PI * radius;
  const offset = circumference - (pct / 100) * circumference;
  const dim = size === "lg" ? 128 : 96;

  return (
    <div className="flex flex-wrap items-center gap-8">
      <div className="relative" style={{ width: dim, height: dim }}>
        <svg
          width={dim}
          height={dim}
          className="-rotate-90"
          aria-hidden
        >
          <circle
            cx={dim / 2}
            cy={dim / 2}
            r={radius}
            fill="none"
            stroke="hsl(var(--secondary))"
            strokeWidth={stroke}
          />
          <circle
            cx={dim / 2}
            cy={dim / 2}
            r={radius}
            fill="none"
            stroke="hsl(var(--primary))"
            strokeWidth={stroke}
            strokeLinecap="round"
            strokeDasharray={circumference}
            strokeDashoffset={offset}
            className="transition-all duration-700"
          />
        </svg>
        <div className="absolute inset-0 flex flex-col items-center justify-center">
          <span className={cn("font-bold text-primary", size === "lg" ? "text-3xl" : "text-xl")}>
            {score ?? "—"}
          </span>
          <span className="text-xs text-muted-foreground">/ 100</span>
        </div>
      </div>
      <div className="space-y-2">
        <div className="flex items-center gap-2">
          <Shield className="h-5 w-5 text-primary" aria-hidden />
          <span className="text-sm font-medium text-muted-foreground">Security grade</span>
        </div>
        <p className="text-3xl font-bold tracking-tight">{grade || "—"}</p>
        <p className={cn("text-lg font-medium", riskClass(riskLevel))}>
          {riskLevel || "Unknown risk"}
        </p>
      </div>
    </div>
  );
}
