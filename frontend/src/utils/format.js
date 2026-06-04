export function formatDate(iso) {
  if (!iso) return "—";
  return new Date(iso).toLocaleString();
}

export function formatDateShort(iso) {
  if (!iso) return "—";
  return new Date(iso).toLocaleDateString(undefined, {
    month: "short",
    day: "numeric",
    year: "numeric",
  });
}
