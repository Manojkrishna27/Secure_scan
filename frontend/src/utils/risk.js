export function riskClass(risk) {
  if (!risk) return "text-muted-foreground";
  const r = String(risk).toLowerCase();
  if (r.includes("low")) return "text-green-500";
  if (r.includes("medium")) return "text-yellow-500";
  return "text-destructive";
}
