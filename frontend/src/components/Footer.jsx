import { Link } from "react-router-dom";
import { Github, Linkedin, Mail, Shield } from "lucide-react";

const productLinks = [
  { label: "Features", href: "/#features" },
  { label: "How it works", href: "/#how-it-works" },
  { label: "Sample report", href: "/#sample-report" },
  { label: "Pricing", href: "/register" },
];

const resourceLinks = [
  { label: "Documentation", href: "https://github.com" },
  { label: "GitHub", href: "https://github.com", icon: Github },
  { label: "Contact", href: "mailto:contact@securescan.ai", icon: Mail },
  { label: "LinkedIn", href: "https://linkedin.com", icon: Linkedin },
];

export function Footer() {
  return (
    <footer className="border-t border-border/60 bg-card/30">
      <div className="container py-14">
        <div className="grid gap-10 sm:grid-cols-2 lg:grid-cols-4">
          <div className="sm:col-span-2 lg:col-span-1">
            <Link to="/" className="inline-flex items-center gap-2.5 font-semibold">
              <span className="flex h-9 w-9 items-center justify-center rounded-md bg-primary/15">
                <Shield className="h-5 w-5 text-primary" aria-hidden />
              </span>
              SecureScan AI
            </Link>
            <p className="mt-4 max-w-xs text-sm leading-relaxed text-muted-foreground">
              Intelligent website security assessment — SSL, TLS, headers, monitoring,
              and enterprise PDF reports.
            </p>
          </div>

          <div>
            <h3 className="text-sm font-semibold uppercase tracking-wider">Product</h3>
            <ul className="mt-4 space-y-2.5">
              {productLinks.map(({ label, href }) => (
                <li key={label}>
                  <a
                    href={href}
                    className="text-sm text-muted-foreground transition-colors hover:text-primary"
                  >
                    {label}
                  </a>
                </li>
              ))}
            </ul>
          </div>

          <div>
            <h3 className="text-sm font-semibold uppercase tracking-wider">Resources</h3>
            <ul className="mt-4 space-y-2.5">
              {resourceLinks.map(({ label, href, icon: Icon }) => (
                <li key={label}>
                  <a
                    href={href}
                    target={href.startsWith("http") ? "_blank" : undefined}
                    rel={href.startsWith("http") ? "noopener noreferrer" : undefined}
                    className="inline-flex items-center gap-2 text-sm text-muted-foreground transition-colors hover:text-primary"
                  >
                    {Icon && <Icon className="h-3.5 w-3.5" aria-hidden />}
                    {label}
                  </a>
                </li>
              ))}
            </ul>
          </div>

          <div>
            <h3 className="text-sm font-semibold uppercase tracking-wider">Get started</h3>
            <p className="mt-4 text-sm text-muted-foreground">
              Run your first security scan in under a minute.
            </p>
            <Link
              to="/register"
              className="mt-4 inline-block text-sm font-medium text-primary hover:underline"
            >
              Create free account →
            </Link>
          </div>
        </div>

        <div className="mt-12 flex flex-col items-center justify-between gap-4 border-t border-border/60 pt-8 text-center text-xs text-muted-foreground sm:flex-row sm:text-left">
          <p>© {new Date().getFullYear()} SecureScan AI. All rights reserved.</p>
          <p>Confidential security assessments for authorized use only.</p>
        </div>
      </div>
    </footer>
  );
}
