import { useEffect, useState } from "react";
import { motion } from "framer-motion";
import { Link } from "react-router-dom";
import { ArrowRight, FileText } from "lucide-react";

import { CTASection } from "@/components/landing/CTASection";
import { CoverageSection } from "@/components/landing/CoverageSection";
import { FeaturesSection } from "@/components/landing/FeaturesSection";
import { HeroBackground } from "@/components/landing/HeroBackground";
import { HeroPreview } from "@/components/landing/HeroPreview";
import { HowItWorksSection } from "@/components/landing/HowItWorksSection";
import { MetricsSection } from "@/components/landing/MetricsSection";
import { ReportPreviewSection } from "@/components/landing/ReportPreviewSection";
import { ScoreDemoSection } from "@/components/landing/ScoreDemoSection";
import { TestimonialsSection } from "@/components/landing/TestimonialsSection";
import { Button } from "@/components/ui/button";
import { getHealth } from "@/services/api";

export default function LandingPage() {
  const [apiStatus, setApiStatus] = useState(null);

  useEffect(() => {
    getHealth()
      .then(setApiStatus)
      .catch(() => setApiStatus({ status: "unreachable" }));
  }, []);

  return (
    <div className="overflow-x-hidden">
      {/* ── Hero ── */}
      <section className="relative min-h-[90vh] flex items-center py-16 sm:py-20 lg:py-24">
        <HeroBackground />
        <div className="container relative z-10">
          <div className="grid items-center gap-12 lg:grid-cols-2 lg:gap-16">
            <motion.div
              initial={{ opacity: 0, y: 28 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ duration: 0.6 }}
            >
              <span className="inline-flex items-center rounded-full border border-primary/30 bg-primary/10 px-3 py-1 text-xs font-semibold uppercase tracking-wider text-primary">
                Trusted Website Security Scanner
              </span>

              <h1 className="mt-6 text-4xl font-bold leading-[1.1] tracking-tight sm:text-5xl lg:text-[3.25rem] xl:text-6xl">
                Analyze Your Website Security in Seconds
              </h1>

              <p className="mt-6 max-w-xl text-lg leading-relaxed text-muted-foreground">
                Get SSL certificate insights, TLS analysis, security header audits,
                AI-powered recommendations, PDF reports, and continuous monitoring.
              </p>

              <div className="mt-10 flex flex-wrap gap-4">
                <Button size="lg" className="h-12 gap-2 px-8 text-base font-semibold" asChild>
                  <Link to="/register">
                    Start Security Scan
                    <ArrowRight className="h-4 w-4" aria-hidden />
                  </Link>
                </Button>
                <Button
                  size="lg"
                  variant="outline"
                  className="h-12 gap-2 border-border/80 bg-background/50 px-8 text-base backdrop-blur-sm"
                  asChild
                >
                  <a href="#sample-report">
                    <FileText className="h-4 w-4" aria-hidden />
                    View Demo Report
                  </a>
                </Button>
              </div>

              {apiStatus && (
                <p className="mt-6 flex items-center gap-2 text-sm text-muted-foreground">
                  <span
                    className={`inline-block h-2 w-2 rounded-full ${
                      apiStatus.status === "healthy" ? "bg-green-500" : "bg-destructive"
                    }`}
                    aria-hidden
                  />
                  {apiStatus.status === "healthy"
                    ? `${apiStatus.service || "API"} is online`
                    : "API offline — start backend to enable live scans"}
                </p>
              )}
            </motion.div>

            <HeroPreview />
          </div>
        </div>
      </section>

      <MetricsSection />
      <FeaturesSection />
      <ScoreDemoSection />
      <HowItWorksSection />
      <ReportPreviewSection />
      <TestimonialsSection />
      <CoverageSection />
      <CTASection />
    </div>
  );
}
