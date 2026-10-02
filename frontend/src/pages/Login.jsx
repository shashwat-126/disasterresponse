import React from "react";
import { useState } from "react";
import { Navigate } from "react-router-dom";
import { useAuth } from "../context/AuthContext";

// Every role in EADRP signs in through the same form — what differs is the
// account, not the screen. Admin accounts see every incident and every
// department's queue; each DEPARTMENT_STAFF account is scoped to exactly one
// department (via department_id on the user record) and only ever sees that
// department's assignments; CITIZEN accounts only see incidents they reported.
// These are the seeded demo logins from scripts/seed_users.py — one per
// department — so the separation is something you can actually click through.
const DEMO_LOGINS = [
  { label: "Admin", email: "admin@eadrp.com", password: "Admin@1234" },
  //{ label: "Fire dept.", email: "fire1@eadrp.com", password: "FireStaff@123" },
  //{ label: "Medical dept.", email: "medical1@eadrp.com", password: "MedStaff@123" },
  //{ label: "Police dept.", email: "police1@eadrp.com", password: "PoliceStaff@123" },
  //{ label: "Disaster Mgmt Authority", email: "dma1@eadrp.com", password: "DmaStaff@123" },
  //{ label: "Citizen reporter", email: "citizen1@eadrp.com", password: "Citizen@123" },
];

export default function Login() {
  const { user, login } = useAuth();
  const [email, setEmail] = useState("admin@eadrp.com");
  const [password, setPassword] = useState("Admin@1234");
  const [error, setError] = useState("");
  const [submitting, setSubmitting] = useState(false);

  if (user) return <Navigate to="/" replace />;

  async function handleSubmit(event) {
    event.preventDefault();
    setSubmitting(true);
    setError("");
    try {
      await login(email, password);
    } catch (err) {
      setError(err?.response?.data?.detail || "Login failed");
    } finally {
      setSubmitting(false);
    }
  }

  function useDemo(demo) {
    setEmail(demo.email);
    setPassword(demo.password);
  }

  return (
    <div className="auth-shell">
      <div className="auth-grid">
        <div className="auth-panel">
          <div className="eyebrow" style={{ color: "var(--text-on-dark-muted)" }}>
            Operational console
          </div>
          <h1>Coordinate every department from one incident feed.</h1>
          <p>
            EADRP triages incoming reports with an AI severity model, auto-assigns the right
            departments, and tracks each one's response — acknowledgement, action taken, and
            proof of completion — through to resolution.
          </p>

          <div style={{ marginTop: "auto", paddingTop: 28 }}>
            <div className="eyebrow" style={{ color: "var(--text-on-dark-muted)", marginBottom: 10 }}>
              Demo logins — tap to fill
            </div>
            <div>
              {DEMO_LOGINS.map((demo) => (
                <button
                  key={demo.email}
                  type="button"
                  onClick={() => useDemo(demo)}
                  className="auth-credential-row"
                  style={{
                    width: "100%",
                    background: "transparent",
                    border: "none",
                    borderBottom: "1px solid var(--ink-700)",
                    color: "inherit",
                    cursor: "pointer",
                    textAlign: "left",
                  }}
                >
                  <span>{demo.label}</span>
                  <span className="mono" style={{ color: "var(--text-on-dark-muted)" }}>{demo.email}</span>
                </button>
              ))}
            </div>
          </div>
        </div>

        <div className="auth-form-side">
          <h2 style={{ fontSize: 22 }}>Sign in</h2>
          <p className="page-subtitle" style={{ marginBottom: 24 }}>
            Each department has its own scoped account — pick a demo login on the left, or use
            your own credentials.
          </p>
          <form onSubmit={handleSubmit} style={{ display: "grid", gap: 16 }}>
            <div style={{ display: "grid", gap: 8 }}>
              <label className="eyebrow">Email</label>
              <input type="email" value={email} onChange={(e) => setEmail(e.target.value)} placeholder="you@eadrp.com" />
            </div>
            <div style={{ display: "grid", gap: 8 }}>
              <label className="eyebrow">Password</label>
              <input type="password" value={password} onChange={(e) => setPassword(e.target.value)} placeholder="••••••••" />
            </div>
            {error ? <div className="banner banner-danger">{error}</div> : null}
            <button type="submit" disabled={submitting} className="btn btn-primary" style={{ padding: "13px 18px" }}>
              {submitting ? "Signing in..." : "Sign in"}
            </button>
          </form>
        </div>
      </div>
    </div>
  );
}
