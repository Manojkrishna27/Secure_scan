import { motion } from "framer-motion";
import { Download, FileSearch, Globe, LineChart } from "lucide-react";

const steps = [
  {
    icon: Globe,
    title: "Enter Website URL",
    description: "Paste any HTTPS URL — production, staging, or public-facing apps.",
  },
  {
    icon: FileSearch,
    title: "Analyze Security",
    description: "We inspect SSL certificates, TLS versions, headers, and known misconfigurations.",
  },
  {
    icon: LineChart,
    title: "Review Findings",
    description: "Explore scores, risk levels, AI recommendations, and prioritized fixes.",
  },
  {
    icon: Download,
    title: "Download Report",
    description: "Export a professional PDF audit for compliance, clients, or internal review.",
  },
];

export function HowItWorksSection() {
  return (
    <section className="py-20 sm:py-28" id="how-it-works">
      <div className="container">
        <div className="mx-auto max-w-2xl text-center">
          <p className="text-sm font-semibold uppercase tracking-widest text-primary">
            How it works
          </p>
          <h2 className="mt-3 text-3xl font-bold tracking-tight sm:text-4xl">
            From URL to audit in four steps
          </h2>
        </div>

        <div className="relative mx-auto mt-16 max-w-3xl">
          <div
            className="absolute left-6 top-0 hidden h-full w-px bg-gradient-to-b from-primary/60 via-primary/20 to-transparent md:block"
            aria-hidden
          />
          <ol className="space-y-10">
            {steps.map(({ icon: Icon, title, description }, i) => (
              <motion.li
                key={title}
                className="relative flex gap-6 md:pl-4"
                initial={{ opacity: 0, x: -20 }}
                whileInView={{ opacity: 1, x: 0 }}
                viewport={{ once: true }}
                transition={{ delay: i * 0.1 }}
              >
                <div className="relative z-10 flex h-12 w-12 shrink-0 items-center justify-center rounded-full border-2 border-primary bg-background text-sm font-bold text-primary shadow-[0_0_20px_hsl(var(--primary)/0.25)]">
                  {i + 1}
                </div>
                <div className="flex-1 rounded-xl border border-border/60 bg-card/30 p-5 pt-4">
                  <div className="flex items-center gap-2">
                    <Icon className="h-4 w-4 text-primary" aria-hidden />
                    <h3 className="font-semibold">{title}</h3>
                  </div>
                  <p className="mt-2 text-sm text-muted-foreground">{description}</p>
                </div>
              </motion.li>
            ))}
          </ol>
        </div>
      </div>
    </section>
  );
}
