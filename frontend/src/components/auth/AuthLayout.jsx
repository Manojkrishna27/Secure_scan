import { Link } from "react-router-dom";
import { FileText, ScanSearch, Shield } from "lucide-react";

const highlights = [
  { icon: ScanSearch, text: "SSL, TLS, and security header analysis" },
  { icon: FileText, text: "Professional PDF audit reports" },
  { icon: Shield, text: "Domain monitoring and real-time alerts" },
];

export function AuthLayout({ title, subtitle, children, footer }) {
  return (
    <div className="flex min-h-screen flex-col bg-background lg:flex-row">
      {/* Brand panel — desktop */}
      <aside
        className="relative hidden w-full flex-col justify-between overflow-hidden bg-gradient-to-br from-slate-950 via-slate-900 to-slate-950 p-10 text-white lg:flex lg:w-[46%] xl:w-[42%]"
        aria-hidden={false}
      >
        <div
          className="pointer-events-none absolute inset-0 opacity-30"
          style={{
            backgroundImage:
              "radial-gradient(circle at 20% 20%, rgba(8,145,178,0.35) 0%, transparent 50%), radial-gradient(circle at 80% 80%, rgba(6,182,212,0.2) 0%, transparent 45%)",
          }}
        />
        <div className="relative z-10">
          <Link to="/" className="inline-flex items-center gap-3 transition-opacity hover:opacity-90">
            <span className="flex h-11 w-11 items-center justify-center rounded-lg bg-primary/20 ring-1 ring-primary/40">
              <Shield className="h-6 w-6 text-primary" aria-hidden />
            </span>
            <span className="text-xl font-semibold tracking-tight">SecureScan AI</span>
          </Link>
        </div>

        <div className="relative z-10 space-y-8 py-12">
          <div>
            <p className="text-sm font-medium uppercase tracking-widest text-primary/90">
              Cybersecurity platform
            </p>
            <h1 className="mt-3 text-3xl font-bold leading-tight tracking-tight xl:text-4xl">
              Assess. Score.
              <br />
              Improve.
            </h1>
            <p className="mt-4 max-w-md text-sm leading-relaxed text-slate-400">
              Enterprise-grade website security assessments with actionable insights,
              AI recommendations, and compliance-ready reporting.
            </p>
          </div>
          <ul className="space-y-4">
            {highlights.map(({ icon: Icon, text }) => (
              <li key={text} className="flex items-start gap-3 text-sm text-slate-300">
                <span className="flex h-8 w-8 shrink-0 items-center justify-center rounded-md bg-primary/15">
                  <Icon className="h-4 w-4 text-primary" aria-hidden />
                </span>
                <span className="pt-1">{text}</span>
              </li>
            ))}
          </ul>
        </div>

        <p className="relative z-10 text-xs text-slate-500">
          Trusted by security teams for continuous posture monitoring.
        </p>
      </aside>

      {/* Form panel */}
      <div className="flex flex-1 flex-col">
        <header className="flex items-center justify-between border-b border-border/60 px-6 py-4 lg:border-none lg:px-10 lg:pt-10">
          <Link
            to="/"
            className="inline-flex items-center gap-2.5 font-semibold tracking-tight lg:hidden"
          >
            <span className="flex h-9 w-9 items-center justify-center rounded-md bg-primary/15">
              <Shield className="h-5 w-5 text-primary" aria-hidden />
            </span>
            SecureScan AI
          </Link>
          <Link
            to="/"
            className="text-sm text-muted-foreground transition-colors hover:text-foreground"
          >
            ← Back to home
          </Link>
        </header>

        <main className="flex flex-1 flex-col items-center justify-center px-6 py-8 sm:px-10">
          <div className="w-full max-w-[420px]">
            <div className="mb-8 lg:mb-10">
              <h2 className="text-2xl font-bold tracking-tight sm:text-3xl">{title}</h2>
              {subtitle && (
                <p className="mt-2 text-sm leading-relaxed text-muted-foreground">{subtitle}</p>
              )}
            </div>
            {children}
          </div>
        </main>

        {footer && (
          <footer className="border-t border-border/60 px-6 py-4 text-center text-xs text-muted-foreground">
            {footer}
          </footer>
        )}
      </div>
    </div>
  );
}
