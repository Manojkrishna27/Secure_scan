import { motion } from "framer-motion";
import {
  Activity,
  Bell,
  Bot,
  FileText,
  LayoutDashboard,
  Lock,
  ScanSearch,
} from "lucide-react";

const features = [
  {
    icon: Lock,
    title: "SSL & TLS Analysis",
    description: "Deep certificate validation, protocol support, and chain-of-trust verification.",
  },
  {
    icon: ScanSearch,
    title: "Security Header Scanner",
    description: "Audit HSTS, CSP, X-Frame-Options, and modern browser protections.",
  },
  {
    icon: Bot,
    title: "AI Security Auditor",
    description: "Prioritized remediation guidance powered by rule-based security analysis.",
  },
  {
    icon: FileText,
    title: "PDF Security Reports",
    description: "Enterprise-grade audit exports for compliance and stakeholder review.",
  },
  {
    icon: Activity,
    title: "Domain Monitoring",
    description: "Scheduled scans with alerts when SSL, TLS, or headers regress.",
  },
  {
    icon: LayoutDashboard,
    title: "Admin Dashboard",
    description: "Platform analytics, user management, audit logs, and CSV exports.",
  },
  {
    icon: Bell,
    title: "Notifications & Alerts",
    description: "Real-time monitoring notifications for critical security changes.",
  },
];

const container = {
  hidden: { opacity: 0 },
  show: { opacity: 1, transition: { staggerChildren: 0.08 } },
};

const item = {
  hidden: { opacity: 0, y: 16 },
  show: { opacity: 1, y: 0, transition: { duration: 0.4 } },
};

export function FeaturesSection() {
  return (
    <section className="py-20 sm:py-28" id="features">
      <div className="container">
        <div className="mx-auto max-w-2xl text-center">
          <p className="text-sm font-semibold uppercase tracking-widest text-primary">
            Platform capabilities
          </p>
          <h2 className="mt-3 text-3xl font-bold tracking-tight sm:text-4xl">
            Everything you need to secure the web
          </h2>
          <p className="mt-4 text-muted-foreground">
            From instant scans to continuous monitoring — built for security engineers,
            DevOps teams, and compliance workflows.
          </p>
        </div>

        <motion.div
          className="mt-14 grid gap-5 sm:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4"
          variants={container}
          initial="hidden"
          whileInView="show"
          viewport={{ once: true, margin: "-80px" }}
        >
          {features.map(({ icon: Icon, title, description }) => (
            <motion.div
              key={title}
              variants={item}
              className="group rounded-xl border border-border/60 bg-card/40 p-6 transition-all duration-300 hover:-translate-y-1 hover:border-primary/40 hover:shadow-lg hover:shadow-primary/5"
            >
              <div className="mb-4 flex h-11 w-11 items-center justify-center rounded-lg bg-primary/10 transition-colors group-hover:bg-primary/20">
                <Icon className="h-5 w-5 text-primary" aria-hidden />
              </div>
              <h3 className="font-semibold tracking-tight">{title}</h3>
              <p className="mt-2 text-sm leading-relaxed text-muted-foreground">{description}</p>
            </motion.div>
          ))}
        </motion.div>
      </div>
    </section>
  );
}
