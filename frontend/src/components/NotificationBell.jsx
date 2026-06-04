import { useCallback, useEffect, useRef, useState } from "react";
import { Link } from "react-router-dom";
import { Bell, Check, Loader2, Trash2 } from "lucide-react";

import { Button } from "@/components/ui/button";
import {
  deleteNotification,
  getNotifications,
  getUnreadCount,
  markAsRead,
} from "@/services/notificationService";
import { cn } from "@/utils/cn";

const severityClass = {
  High: "text-destructive",
  Medium: "text-amber-400",
  Low: "text-muted-foreground",
};

export function NotificationBell() {
  const [open, setOpen] = useState(false);
  const [unread, setUnread] = useState(0);
  const [items, setItems] = useState([]);
  const [loading, setLoading] = useState(false);
  const ref = useRef(null);

  const refresh = useCallback(async () => {
    try {
      const [count, notes] = await Promise.all([
        getUnreadCount(),
        getNotifications(8),
      ]);
      setUnread(count);
      setItems(notes);
    } catch {
      /* ignore */
    }
  }, []);

  useEffect(() => {
    refresh();
    const interval = setInterval(refresh, 60000);
    return () => clearInterval(interval);
  }, [refresh]);

  useEffect(() => {
    const onClickOutside = (e) => {
      if (ref.current && !ref.current.contains(e.target)) {
        setOpen(false);
      }
    };
    const onEscape = (e) => {
      if (e.key === "Escape") setOpen(false);
    };
    document.addEventListener("mousedown", onClickOutside);
    document.addEventListener("keydown", onEscape);
    return () => {
      document.removeEventListener("mousedown", onClickOutside);
      document.removeEventListener("keydown", onEscape);
    };
  }, []);

  const toggle = async () => {
    const next = !open;
    setOpen(next);
    if (next) {
      setLoading(true);
      await refresh();
      setLoading(false);
    }
  };

  const handleMarkRead = async (id) => {
    await markAsRead(id);
    await refresh();
  };

  const handleDelete = async (id, e) => {
    e.stopPropagation();
    await deleteNotification(id);
    await refresh();
  };

  return (
    <div className="relative" ref={ref}>
      <Button
        variant="ghost"
        size="sm"
        onClick={toggle}
        aria-label={`Notifications${unread > 0 ? `, ${unread} unread` : ""}`}
        aria-expanded={open}
        aria-haspopup="true"
        className="relative"
      >
        <Bell className="h-4 w-4" />
        {unread > 0 && (
          <span className="absolute -right-0.5 -top-0.5 flex h-4 min-w-4 items-center justify-center rounded-full bg-destructive px-1 text-[10px] font-bold text-destructive-foreground">
            {unread > 99 ? "99+" : unread}
          </span>
        )}
      </Button>

      {open && (
        <div
          className="absolute right-0 top-full z-50 mt-2 w-[min(100vw-2rem,24rem)] overflow-hidden rounded-lg border border-border bg-card shadow-xl animate-in fade-in slide-in-from-top-1 duration-200"
          role="menu"
        >
          <div className="flex items-center justify-between border-b border-border bg-muted/30 px-4 py-3">
            <span className="text-sm font-semibold">Notifications</span>
            {unread > 0 && (
              <span className="rounded-full bg-primary/15 px-2 py-0.5 text-xs font-medium text-primary">
                {unread} unread
              </span>
            )}
          </div>
          <div className="max-h-80 overflow-y-auto">
            {loading ? (
              <div className="flex justify-center py-10">
                <Loader2 className="h-5 w-5 animate-spin text-muted-foreground" />
              </div>
            ) : items.length === 0 ? (
              <p className="px-4 py-10 text-center text-sm text-muted-foreground">
                No notifications yet.
              </p>
            ) : (
              <ul>
                {items.map((note) => (
                  <li
                    key={note.id}
                    className={cn(
                      "border-b border-border/60 px-4 py-3 text-sm last:border-0 transition-colors",
                      !note.is_read && "bg-primary/5 border-l-2 border-l-primary pl-[14px]"
                    )}
                  >
                    <div className="flex items-start justify-between gap-2">
                      <div className="min-w-0 flex-1">
                        <p
                          className={cn(
                            "font-medium truncate",
                            !note.is_read && "text-foreground"
                          )}
                        >
                          {note.title}
                        </p>
                        <p className="text-xs text-muted-foreground line-clamp-2 mt-0.5">
                          {note.message}
                        </p>
                        <p
                          className={cn(
                            "mt-1.5 text-xs font-medium",
                            severityClass[note.severity] || severityClass.Low
                          )}
                        >
                          {note.severity} · {note.domain}
                        </p>
                      </div>
                      <div className="flex shrink-0 gap-0.5">
                        {!note.is_read && (
                          <Button
                            variant="ghost"
                            size="sm"
                            className="h-8 w-8 p-0"
                            onClick={() => handleMarkRead(note.id)}
                            aria-label="Mark as read"
                          >
                            <Check className="h-3.5 w-3.5" />
                          </Button>
                        )}
                        <Button
                          variant="ghost"
                          size="sm"
                          className="h-8 w-8 p-0 text-destructive hover:text-destructive"
                          onClick={(e) => handleDelete(note.id, e)}
                          aria-label="Delete notification"
                        >
                          <Trash2 className="h-3.5 w-3.5" />
                        </Button>
                      </div>
                    </div>
                  </li>
                ))}
              </ul>
            )}
          </div>
          <div className="border-t border-border bg-muted/20 p-2">
            <Button variant="ghost" size="sm" className="w-full" asChild>
              <Link to="/monitoring" onClick={() => setOpen(false)}>
                View monitoring
              </Link>
            </Button>
          </div>
        </div>
      )}
    </div>
  );
}
