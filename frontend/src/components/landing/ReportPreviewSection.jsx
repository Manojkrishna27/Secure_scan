import { Link } from "react-router-dom";
import { motion } from "framer-motion";
import { AlertTriangle, CheckCircle2, Download, Shield } from "lucide-react";

import { Button } from "@/components/ui/button";

const findings = [
  { sev: "Medium", title: "Missing Content-Security-Policy", color: "text-amber-500" },
  { sev: "Low", title: "Referrer-Policy not configured", color: "text-blue-400" },
];

const recommendations = [
  "Enable HSTS with max-age ≥ 31536000",
  "Deploy strict CSP default-src directive",
  "Disable TLS 1.0 and 1.1 if detected",
];

export function ReportPreviewSection() {
  return (
    <section
      className="border-y border-border/60 bg-muted/10 py-20 sm:py-28"
      id="sample-report"
    >
      <div className="container">
        <div className="grid items-start gap-12 lg:grid-cols-2 lg:gap-16">
          <div>
            <p className="text-sm font-semibold uppercase tracking-widest text-primary">
              Sample report
            </p>
            <h2 className="mt-3 text-3xl font-bold tracking-tight sm:text-4xl">
              Professional audit exports
            </h2>
            <p className="mt-4 text-muted-foreground">
              Every scan generates a multi-section PDF with executive dashboard, certificate
              analysis, findings, and AI-powered remediation guidance.
            </p>
            <Button className="mt-8 gap-2" size="lg" asChild>
              <Link to="/register">
                <Download className="h-4 w-4" aria-hidden />
                Download Sample Report
              </Link>
            </Button>
            <p className="mt-3 text-xs text-muted-foreground">
              Create a free account to generate reports from your own scans.
            </p>
          </div>

          <motion.div
            className="overflow-hidden rounded-2xl border border-border/80 bg-card shadow-2xl"
            initial={{ opacity: 0, y: 24 }}
            whileInView={{ opacity: 1, y: 0 }}
            viewport={{ once: true }}
          >
            {/* Report mock header */}
            <div className="bg-gradient-to-r from-slate-900 to-slate-800 px-6 py-5 text-white">
              <div className="flex items-center gap-2">
                <Shield className="h-5 w-5 text-primary" aria-hidden />
                <span className="text-sm font-semibold">SecureScan AI</span>
              </div>
              <p className="mt-3 text-lg font-bold">Security Assessment Report</p>
              <p className="text-xs text-slate-400">example.com · Generated today</p>
            </div>

            <div className="space-y-4 p-6">
              <div className="flex items-center justify-between rounded-lg border border-primary/20 bg-primary/5 p-4">
                <div>
                  <p className="text-xs text-muted-foreground">Security Score</p>
                  <p className="text-2xl font-bold text-primary">85/100</p>
                </div>
                <div className="text-right">
                  <p className="text-xs text-muted-foreground">SSL Status</p>
                  <p className="flex items-center gap-1 text-sm font-semibold text-green-500">
                    <CheckCircle2 className="h-4 w-4" /> Valid
                  </p>
                </div>
              </div>

              <div>
                <p className="mb-2 text-xs font-semibold uppercase tracking-wide text-muted-foreground">
                  Findings
                </p>
                <ul className="space-y-2">
                  {findings.map((f) => (
                    <li
                      key={f.title}
                      className="flex items-start gap-2 rounded-md border border-border/60 bg-muted/20 px-3 py-2 text-sm"
                    >
                      <AlertTriangle className={`mt-0.5 h-4 w-4 shrink-0 ${f.color}`} aria-hidden />
                      <span>
                        <span className={`text-xs font-bold ${f.color}`}>{f.sev}</span>
                        {" · "}
                        {f.title}
                      </span>
                    </li>
                  ))}
                </ul>
              </div>

              <div>
                <p className="mb-2 text-xs font-semibold uppercase tracking-wide text-muted-foreground">
                  Recommendations
                </p>
                <ul className="space-y-1.5 text-sm text-muted-foreground">
                  {recommendations.map((r) => (
                    <li key={r} className="flex gap-2">
                      <span className="text-primary">→</span>
                      {r}
                    </li>
                  ))}
                </ul>
              </div>
            </div>
          </motion.div>
        </div>
      </div>
    </section>
  );
}
