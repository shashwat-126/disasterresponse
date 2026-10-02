import React from "react";
import { useEffect, useRef, useState } from "react";
import { useNavigate } from "react-router-dom";
import { getNotifications, markAllNotificationsRead, markNotificationRead } from "../api/notifications";

export default function NotificationBell() {
  const [open, setOpen] = useState(false);
  const [notifications, setNotifications] = useState([]);
  const [unreadCount, setUnreadCount] = useState(0);
  const containerRef = useRef(null);
  const navigate = useNavigate();

  async function load() {
    try {
      const data = await getNotifications(20);
      setNotifications(data.notifications);
      setUnreadCount(data.unread_count);
    } catch {
      // Silently ignore; the bell just stays quiet if the endpoint isn't reachable.
    }
  }

  useEffect(() => {
    load();
    const interval = setInterval(load, 30000);
    return () => clearInterval(interval);
  }, []);

  useEffect(() => {
    function handleClickOutside(event) {
      if (containerRef.current && !containerRef.current.contains(event.target)) {
        setOpen(false);
      }
    }
    document.addEventListener("mousedown", handleClickOutside);
    return () => document.removeEventListener("mousedown", handleClickOutside);
  }, []);

  async function handleOpen() {
    setOpen((prev) => !prev);
  }

  async function handleNotificationClick(notification) {
    if (!notification.is_read) {
      try {
        await markNotificationRead(notification.id);
      } catch {
        // ignore
      }
    }
    setOpen(false);
    if (notification.incident_id) {
      navigate(`/incidents/${notification.incident_id}`);
    }
    load();
  }

  async function handleMarkAllRead() {
    try {
      await markAllNotificationsRead();
      load();
    } catch {
      // ignore
    }
  }

  return (
    <div ref={containerRef} style={{ position: "relative" }}>
      <button onClick={handleOpen} className="btn btn-sm" style={{ position: "relative" }}>
        🔔
        {unreadCount > 0 ? (
          <span
            className="mono"
            style={{
              position: "absolute", top: -6, right: -6, background: "var(--danger)", color: "#fff",
              borderRadius: 999, fontSize: 10, fontWeight: 700, minWidth: 17, height: 17,
              display: "grid", placeItems: "center", padding: "0 4px",
            }}
          >
            {unreadCount > 9 ? "9+" : unreadCount}
          </span>
        ) : null}
      </button>

      {open ? (
        <div
          className="card-sm"
          style={{
            position: "absolute", right: 0, top: "calc(100% + 8px)", width: 340, maxHeight: 420,
            overflowY: "auto", boxShadow: "var(--shadow-lg)", zIndex: 20, padding: 0,
          }}
        >
          <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center", padding: "12px 16px", borderBottom: "1px solid var(--border)" }}>
            <div style={{ fontWeight: 700, fontSize: 14 }}>Notifications</div>
            <button onClick={handleMarkAllRead} className="link" style={{ border: "none", background: "none", cursor: "pointer", fontSize: 12.5 }}>
              Mark all read
            </button>
          </div>
          {notifications.length === 0 ? (
            <div className="empty-state" style={{ border: "none" }}>No notifications yet.</div>
          ) : (
            notifications.map((n) => (
              <div
                key={n.id}
                onClick={() => handleNotificationClick(n)}
                style={{
                  padding: "12px 16px", borderBottom: "1px solid var(--border)",
                  background: n.is_read ? "var(--surface)" : "var(--accent-soft)", cursor: "pointer", fontSize: 13.5,
                }}
              >
                <div style={{ color: "var(--text-primary)" }}>{n.message}</div>
                <div className="mono" style={{ color: "var(--text-muted)", fontSize: 11.5, marginTop: 4 }}>
                  {new Date(n.created_at).toLocaleString()}
                </div>
              </div>
            ))
          )}
        </div>
      ) : null}
    </div>
  );
}
