import { Link } from "react-router-dom";
import { motion } from "framer-motion";
import { ArrowRight, Shield } from "lucide-react";

import { Button } from "@/components/ui/button";

export function CTASection() {
  return (
    <section className="py-20 sm:py-28">
      <div className="container">
        <motion.div
          className="relative overflow-hidden rounded-2xl border border-primary/30 bg-gradient-to-br from-primary/10 via-card to-card px-8 py-16 text-center sm:px-16"
          initial={{ opacity: 0, y: 20 }}
          whileInView={{ opacity: 1, y: 0 }}
          viewport={{ once: true }}
        >
          <div
            className="pointer-events-none absolute inset-0 opacity-40"
            style={{
              backgroundImage:
                "radial-gradient(circle at 30% 50%, hsl(var(--primary) / 0.15), transparent 50%)",
            }}
            aria-hidden
          />
          <Shield className="mx-auto h-12 w-12 text-primary" aria-hidden />
          <h2 className="relative mt-6 text-3xl font-bold tracking-tight sm:text-4xl">
            Start protecting your website today
          </h2>
          <p className="relative mx-auto mt-4 max-w-xl text-muted-foreground">
            Join teams using SecureScan AI for continuous security posture management,
            compliance reporting, and proactive threat reduction.
          </p>
          <Button size="lg" className="relative mt-8 gap-2 text-base" asChild>
            <Link to="/register">
              Analyze My Website
              <ArrowRight className="h-4 w-4" aria-hidden />
            </Link>
          </Button>
        </motion.div>
      </div>
    </section>
  );
}
