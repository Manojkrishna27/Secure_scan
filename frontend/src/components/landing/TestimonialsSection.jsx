import { motion } from "framer-motion";
import { Quote } from "lucide-react";

const testimonials = [
  {
    quote:
      "SecureScan AI helped us identify critical security header misconfigurations before our SOC 2 audit. The PDF reports are client-ready.",
    name: "Sarah Chen",
    role: "Security Engineer",
    org: "FinTech SaaS",
  },
  {
    quote:
      "We monitor 40+ domains with scheduled scans. The alerting alone saved us from an expired certificate incident.",
    name: "Marcus Webb",
    role: "DevOps Lead",
    org: "E-commerce Platform",
  },
  {
    quote:
      "The AI recommendations give our junior engineers a clear remediation path. It's like having a lightweight AppSec consultant on demand.",
    name: "Priya Nair",
    role: "Engineering Manager",
    org: "HealthTech Startup",
  },
];

export function TestimonialsSection() {
  return (
    <section className="py-20 sm:py-28" id="testimonials">
      <div className="container">
        <div className="mx-auto max-w-2xl text-center">
          <p className="text-sm font-semibold uppercase tracking-widest text-primary">
            Trusted by teams
          </p>
          <h2 className="mt-3 text-3xl font-bold tracking-tight sm:text-4xl">
            What security professionals say
          </h2>
        </div>

        <div className="mt-14 grid gap-6 md:grid-cols-3">
          {testimonials.map((t, i) => (
            <motion.blockquote
              key={t.name}
              className="flex flex-col rounded-xl border border-border/60 bg-card/40 p-6"
              initial={{ opacity: 0, y: 20 }}
              whileInView={{ opacity: 1, y: 0 }}
              viewport={{ once: true }}
              transition={{ delay: i * 0.1 }}
            >
              <Quote className="h-8 w-8 text-primary/40" aria-hidden />
              <p className="mt-4 flex-1 text-sm leading-relaxed text-muted-foreground">
                &ldquo;{t.quote}&rdquo;
              </p>
              <footer className="mt-6 border-t border-border/60 pt-4">
                <p className="font-semibold text-sm">{t.name}</p>
                <p className="text-xs text-muted-foreground">
                  {t.role} · {t.org}
                </p>
              </footer>
            </motion.blockquote>
          ))}
        </div>
      </div>
    </section>
  );
}
