import { motion } from "framer-motion";
import { CheckCircle2, Shield } from "lucide-react";

const stats = [
  { label: "Security Score", value: "92/100", highlight: true },
  { label: "SSL", value: "Valid", ok: true },
  { label: "TLS", value: "1.3", ok: true },
  { label: "Headers", value: "5/6", ok: true },
  { label: "Risk", value: "Low", ok: true },
];

export function HeroPreview() {
  return (
    <motion.div
      className="relative mx-auto w-full max-w-md lg:max-w-none"
      initial={{ opacity: 0, y: 40 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.7, delay: 0.2 }}
    >
      <motion.div
        className="absolute -inset-4 rounded-3xl bg-primary/20 blur-2xl"
        animate={{ opacity: [0.3, 0.5, 0.3] }}
        transition={{ duration: 4, repeat: Infinity }}
      />

      <motion.div
        className="relative overflow-hidden rounded-2xl border border-white/10 bg-card/40 p-5 shadow-2xl backdrop-blur-xl sm:p-6"
        animate={{ y: [0, -6, 0] }}
        transition={{ duration: 5, repeat: Infinity, ease: "easeInOut" }}
      >
        <div className="mb-4 flex items-center justify-between border-b border-border/60 pb-4">
          <div className="flex items-center gap-2">
            <Shield className="h-5 w-5 text-primary" aria-hidden />
            <span className="text-sm font-semibold">Live Scan Preview</span>
          </div>
          <span className="rounded-full bg-green-500/15 px-2.5 py-0.5 text-xs font-medium text-green-500">
            Scanning…
          </span>
        </div>

        <div className="mb-4 rounded-xl border border-primary/20 bg-primary/5 p-4 text-center">
          <p className="text-xs uppercase tracking-wider text-muted-foreground">Security Score</p>
          <p className="mt-1 text-4xl font-bold text-primary">92</p>
          <p className="text-xs text-muted-foreground">/ 100 · Grade A</p>
        </div>

        <div className="grid grid-cols-2 gap-3">
          {stats.slice(1).map((s, i) => (
            <motion.div
              key={s.label}
              className="rounded-lg border border-border/60 bg-background/60 px-3 py-2.5"
              initial={{ opacity: 0, scale: 0.95 }}
              animate={{ opacity: 1, scale: 1 }}
              transition={{ delay: 0.4 + i * 0.1 }}
            >
              <p className="text-[10px] uppercase tracking-wide text-muted-foreground">{s.label}</p>
              <p className="mt-0.5 flex items-center gap-1 text-sm font-semibold">
                {s.ok && <CheckCircle2 className="h-3.5 w-3.5 text-green-500" aria-hidden />}
                {s.value}
              </p>
            </motion.div>
          ))}
        </div>

        <div className="mt-4 space-y-2">
          <div className="flex justify-between text-xs text-muted-foreground">
            <span>Scan progress</span>
            <span>87%</span>
          </div>
          <div className="h-1.5 overflow-hidden rounded-full bg-muted">
            <motion.div
              className="h-full rounded-full bg-primary"
              initial={{ width: "0%" }}
              animate={{ width: "87%" }}
              transition={{ duration: 1.5, delay: 0.6 }}
            />
          </div>
        </div>
      </motion.div>

      {/* Floating mini card */}
      <motion.div
        className="absolute -right-2 top-8 hidden rounded-lg border border-border/80 bg-card/90 px-3 py-2 shadow-lg backdrop-blur-md sm:block lg:-right-6"
        animate={{ y: [0, 8, 0] }}
        transition={{ duration: 3.5, repeat: Infinity, delay: 0.5 }}
      >
        <p className="text-[10px] text-muted-foreground">TLS 1.3</p>
        <p className="text-xs font-semibold text-green-500">Enabled ✓</p>
      </motion.div>
    </motion.div>
  );
}
