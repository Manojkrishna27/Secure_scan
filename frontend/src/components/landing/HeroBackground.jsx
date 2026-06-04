import { motion } from "framer-motion";

const nodes = [
  { x: "12%", y: "18%", delay: 0 },
  { x: "78%", y: "22%", delay: 0.4 },
  { x: "88%", y: "68%", delay: 0.8 },
  { x: "22%", y: "72%", delay: 1.2 },
  { x: "55%", y: "45%", delay: 0.6 },
  { x: "35%", y: "38%", delay: 1 },
];

export function HeroBackground() {
  return (
    <div
      className="pointer-events-none absolute inset-0 overflow-hidden"
      aria-hidden
    >
      {/* Grid */}
      <div
        className="absolute inset-0 opacity-[0.35]"
        style={{
          backgroundImage: `
            linear-gradient(to right, hsl(var(--primary) / 0.08) 1px, transparent 1px),
            linear-gradient(to bottom, hsl(var(--primary) / 0.08) 1px, transparent 1px)
          `,
          backgroundSize: "48px 48px",
          maskImage: "radial-gradient(ellipse 80% 60% at 50% 40%, black, transparent)",
        }}
      />
      {/* Glow orbs */}
      <div className="absolute -left-32 top-20 h-96 w-96 rounded-full bg-primary/10 blur-3xl" />
      <div className="absolute -right-24 bottom-10 h-80 w-80 rounded-full bg-cyan-500/10 blur-3xl" />

      {/* Floating nodes + lines */}
      <svg className="absolute inset-0 h-full w-full" xmlns="http://www.w3.org/2000/svg">
        <line
          x1="12%"
          y1="18%"
          x2="55%"
          y2="45%"
          stroke="hsl(var(--primary) / 0.2)"
          strokeWidth="1"
        />
        <line
          x1="55%"
          y1="45%"
          x2="78%"
          y2="22%"
          stroke="hsl(var(--primary) / 0.15)"
          strokeWidth="1"
        />
        <line
          x1="55%"
          y1="45%"
          x2="35%"
          y2="38%"
          stroke="hsl(var(--primary) / 0.15)"
          strokeWidth="1"
        />
        <line
          x1="35%"
          y1="38%"
          x2="22%"
          y2="72%"
          stroke="hsl(var(--primary) / 0.12)"
          strokeWidth="1"
        />
        <line
          x1="78%"
          y1="22%"
          x2="88%"
          y2="68%"
          stroke="hsl(var(--primary) / 0.12)"
          strokeWidth="1"
        />
      </svg>

      {nodes.map((node, i) => (
        <motion.div
          key={i}
          className="absolute h-2 w-2 rounded-full bg-primary shadow-[0_0_12px_hsl(var(--primary)/0.6)]"
          style={{ left: node.x, top: node.y }}
          animate={{ y: [0, -8, 0], opacity: [0.5, 1, 0.5] }}
          transition={{
            duration: 4 + i * 0.3,
            repeat: Infinity,
            delay: node.delay,
            ease: "easeInOut",
          }}
        />
      ))}
    </div>
  );
}
