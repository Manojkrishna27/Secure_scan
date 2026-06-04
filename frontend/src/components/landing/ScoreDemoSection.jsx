import { motion } from "framer-motion";
import {
  Bar,
  BarChart,
  Cell,
  ResponsiveContainer,
  Tooltip,
  XAxis,
  YAxis,
} from "recharts";

const breakdown = [
  { name: "SSL", score: 95, fill: "hsl(187, 78%, 48%)" },
  { name: "TLS", score: 88, fill: "hsl(187, 65%, 42%)" },
  { name: "Headers", score: 72, fill: "hsl(38, 92%, 50%)" },
  { name: "Findings", score: 85, fill: "hsl(142, 71%, 45%)" },
];

export function ScoreDemoSection() {
  return (
    <section className="border-y border-border/60 bg-muted/10 py-20 sm:py-28" id="demo">
      <div className="container">
        <div className="grid items-center gap-12 lg:grid-cols-2 lg:gap-16">
          <div>
            <p className="text-sm font-semibold uppercase tracking-widest text-primary">
              Interactive preview
            </p>
            <h2 className="mt-3 text-3xl font-bold tracking-tight sm:text-4xl">
              How secure is your website?
            </h2>
            <p className="mt-4 text-muted-foreground">
              SecureScan AI aggregates SSL, TLS, headers, and findings into a single
              security score — with clear breakdowns for every control area.
            </p>

            <motion.div
              className="mt-10 flex items-center gap-8"
              initial={{ opacity: 0, scale: 0.9 }}
              whileInView={{ opacity: 1, scale: 1 }}
              viewport={{ once: true }}
              transition={{ duration: 0.5 }}
            >
              <div className="relative flex h-36 w-36 items-center justify-center">
                <svg className="absolute inset-0 -rotate-90" viewBox="0 0 100 100" aria-hidden>
                  <circle cx="50" cy="50" r="42" fill="none" stroke="hsl(var(--muted))" strokeWidth="8" />
                  <circle
                    cx="50"
                    cy="50"
                    r="42"
                    fill="none"
                    stroke="hsl(var(--primary))"
                    strokeWidth="8"
                    strokeLinecap="round"
                    strokeDasharray={`${85 * 2.64} ${264 - 85 * 2.64}`}
                  />
                </svg>
                <div className="text-center">
                  <p className="text-3xl font-bold text-primary">85</p>
                  <p className="text-xs text-muted-foreground">/ 100</p>
                </div>
              </div>
              <div className="space-y-2 text-sm">
                <p>
                  <span className="font-semibold text-green-500">Low Risk</span>
                  <span className="text-muted-foreground"> · Grade B+</span>
                </p>
                <p className="text-muted-foreground">
                  Example scan result for a production web application with minor header gaps.
                </p>
              </div>
            </motion.div>
          </div>

          <motion.div
            className="rounded-2xl border border-border/60 bg-card/50 p-6 backdrop-blur-sm"
            initial={{ opacity: 0, x: 24 }}
            whileInView={{ opacity: 1, x: 0 }}
            viewport={{ once: true }}
            transition={{ duration: 0.5 }}
          >
            <p className="mb-4 text-sm font-semibold">Score breakdown by category</p>
            <div className="h-64">
              <ResponsiveContainer width="100%" height="100%">
                <BarChart data={breakdown} layout="vertical" margin={{ left: 8, right: 16 }}>
                  <XAxis type="number" domain={[0, 100]} hide />
                  <YAxis
                    type="category"
                    dataKey="name"
                    width={70}
                    tick={{ fill: "hsl(var(--muted-foreground))", fontSize: 12 }}
                    axisLine={false}
                    tickLine={false}
                  />
                  <Tooltip
                    cursor={{ fill: "hsl(var(--muted) / 0.3)" }}
                    contentStyle={{
                      background: "hsl(var(--card))",
                      border: "1px solid hsl(var(--border))",
                      borderRadius: 8,
                      fontSize: 12,
                    }}
                    formatter={(v) => [`${v}/100`, "Score"]}
                  />
                  <Bar dataKey="score" radius={[0, 6, 6, 0]} barSize={22}>
                    {breakdown.map((entry) => (
                      <Cell key={entry.name} fill={entry.fill} />
                    ))}
                  </Bar>
                </BarChart>
              </ResponsiveContainer>
            </div>
          </motion.div>
        </div>
      </div>
    </section>
  );
}
