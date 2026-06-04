import { motion } from "framer-motion";
import {
  Activity,
  Bot,
  FileText,
  GitBranch,
  Globe,
  Lock,
  ScanSearch,
} from "lucide-react";

const coverage = [
  { icon: Lock, label: "SSL Certificate" },
  { icon: Globe, label: "TLS Versions" },
  { icon: GitBranch, label: "Certificate Chain" },
  { icon: ScanSearch, label: "Security Headers" },
  { icon: Activity, label: "Domain Monitoring" },
  { icon: Bot, label: "AI Recommendations" },
  { icon: FileText, label: "PDF Reports" },
];

export function CoverageSection() {
  return (
    <section className="border-y border-border/60 bg-muted/10 py-20 sm:py-28" id="coverage">
      <div className="container">
        <div className="mx-auto max-w-2xl text-center">
          <p className="text-sm font-semibold uppercase tracking-widest text-primary">
            Security coverage
          </p>
          <h2 className="mt-3 text-3xl font-bold tracking-tight sm:text-4xl">
            What SecureScan checks
          </h2>
          <p className="mt-4 text-muted-foreground">
            Comprehensive website security assessment across certificates, transport, headers, and ongoing monitoring.
          </p>
        </div>

        <motion.ul
          className="mt-14 grid grid-cols-2 gap-4 sm:grid-cols-3 lg:grid-cols-4 xl:grid-cols-7"
          initial="hidden"
          whileInView="show"
          viewport={{ once: true }}
          variants={{
            hidden: {},
            show: { transition: { staggerChildren: 0.06 } },
          }}
        >
          {coverage.map(({ icon: Icon, label }) => (
            <motion.li
              key={label}
              variants={{
                hidden: { opacity: 0, scale: 0.9 },
                show: { opacity: 1, scale: 1 },
              }}
              className="flex flex-col items-center rounded-xl border border-border/60 bg-card/40 p-5 text-center transition-colors hover:border-primary/40"
            >
              <motion.div
                whileHover={{ scale: 1.08 }}
                className="flex h-12 w-12 items-center justify-center rounded-full bg-primary/10"
              >
                <Icon className="h-6 w-6 text-primary" aria-hidden />
              </motion.div>
              <p className="mt-3 text-xs font-medium leading-tight sm:text-sm">{label}</p>
            </motion.li>
          ))}
        </motion.ul>
      </div>
    </section>
  );
}
