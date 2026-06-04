import { useCountUp } from "@/hooks/useCountUp";

function MetricCard({ target, suffix, label, sub, decimals = 0, format }) {
  const { ref, value } = useCountUp(target, { duration: 2000, decimals });

  let display = format ? format(value) : `${value}${suffix}`;

  return (
    <div
      ref={ref}
      className="rounded-xl border border-border/60 bg-card/50 p-6 text-center backdrop-blur-sm transition-colors hover:border-primary/30"
    >
      <p className="text-3xl font-bold tracking-tight text-primary sm:text-4xl">{display}</p>
      <p className="mt-2 font-semibold">{label}</p>
      <p className="mt-1 text-xs text-muted-foreground">{sub}</p>
    </div>
  );
}

const metrics = [
  {
    target: 1000,
    suffix: "+",
    label: "Security Scans",
    sub: "Websites assessed",
    format: (v) => (v >= 1000 ? "1000+" : `${v}+`),
  },
  {
    target: 500,
    suffix: "+",
    label: "Reports Generated",
    sub: "PDF audit exports",
    format: (v) => (v >= 500 ? "500+" : `${v}+`),
  },
  {
    target: 99.9,
    suffix: "%",
    label: "Scan Accuracy",
    sub: "Engine reliability",
    decimals: 1,
    format: (v) => `${v.toFixed(1)}%`,
  },
  {
    target: 24,
    suffix: "/7",
    label: "Monitoring",
    sub: "Continuous coverage",
    format: (v) => `${v}/7`,
  },
];

export function MetricsSection() {
  return (
    <section className="border-y border-border/60 bg-muted/20 py-16 sm:py-20" aria-label="Platform metrics">
      <div className="container">
        <div className="grid gap-6 sm:grid-cols-2 lg:grid-cols-4">
          {metrics.map((m) => (
            <MetricCard key={m.label} {...m} />
          ))}
        </div>
      </div>
    </section>
  );
}
