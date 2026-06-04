import { useEffect, useId, useRef } from "react";
import { createPortal } from "react-dom";
import { AnimatePresence, motion } from "framer-motion";
import { Loader2 } from "lucide-react";

import { Button } from "@/components/ui/button";
import { cn } from "@/utils/cn";

export function ConfirmDialog({
  open,
  onOpenChange,
  title,
  message,
  confirmLabel = "Confirm",
  cancelLabel = "Cancel",
  onConfirm,
  confirmVariant = "default",
  loading = false,
}) {
  const titleId = useId();
  const descId = useId();
  const cancelRef = useRef(null);

  useEffect(() => {
    if (!open) return undefined;
    const prev = document.body.style.overflow;
    document.body.style.overflow = "hidden";
    const t = requestAnimationFrame(() => cancelRef.current?.focus());
    return () => {
      document.body.style.overflow = prev;
      cancelAnimationFrame(t);
    };
  }, [open]);

  useEffect(() => {
    if (!open) return undefined;
    const onKey = (e) => {
      if (e.key === "Escape") onOpenChange(false);
    };
    window.addEventListener("keydown", onKey);
    return () => window.removeEventListener("keydown", onKey);
  }, [open, onOpenChange]);

  if (typeof document === "undefined") return null;

  return createPortal(
    <AnimatePresence>
      {open && (
        <>
          <motion.button
            type="button"
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            exit={{ opacity: 0 }}
            transition={{ duration: 0.15 }}
            className="fixed inset-0 z-[100] cursor-default bg-background/75 backdrop-blur-sm"
            onClick={() => onOpenChange(false)}
            aria-label="Close dialog"
          />
          <div className="fixed inset-0 z-[101] flex items-center justify-center p-4 pointer-events-none">
            <motion.div
              role="dialog"
              aria-modal="true"
              aria-labelledby={titleId}
              aria-describedby={descId}
              initial={{ opacity: 0, scale: 0.96, y: 10 }}
              animate={{ opacity: 1, scale: 1, y: 0 }}
              exit={{ opacity: 0, scale: 0.96, y: 10 }}
              transition={{ type: "spring", stiffness: 400, damping: 30 }}
              className={cn(
                "pointer-events-auto w-full max-w-md rounded-lg border border-border bg-card p-6 shadow-2xl"
              )}
              onClick={(e) => e.stopPropagation()}
            >
              <h2 id={titleId} className="text-lg font-semibold tracking-tight">
                {title}
              </h2>
              <p id={descId} className="mt-2 text-sm text-muted-foreground leading-relaxed">
                {message}
              </p>
              <div className="mt-6 flex flex-col-reverse gap-2 sm:flex-row sm:justify-end">
                <Button
                  ref={cancelRef}
                  type="button"
                  variant="outline"
                  disabled={loading}
                  onClick={() => onOpenChange(false)}
                >
                  {cancelLabel}
                </Button>
                <Button
                  type="button"
                  variant={confirmVariant === "destructive" ? "default" : "default"}
                  className={cn(
                    confirmVariant === "destructive" &&
                      "bg-destructive text-destructive-foreground hover:bg-destructive/90"
                  )}
                  disabled={loading}
                  onClick={onConfirm}
                >
                  {loading && <Loader2 className="h-4 w-4 animate-spin" />}
                  {confirmLabel}
                </Button>
              </div>
            </motion.div>
          </div>
        </>
      )}
    </AnimatePresence>,
    document.body
  );
}
