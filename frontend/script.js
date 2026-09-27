/* ============================================================
   script.js  –  Medicine Reminder System – Shared Utilities
   All pages have their own inline <script> for page-specific
   logic. This file holds shared helpers that can be loaded via:
     <script src="script.js"></script>
   ============================================================ */

/* ── Config ──────────────────────────────────────────────── */
const API = (window.location.protocol === "file:" || ((window.location.hostname === "localhost" || window.location.hostname === "127.0.0.1") && window.location.port !== "8000"))
  ? "http://127.0.0.1:8000"
  : window.location.origin;

/* ── Auth helpers ────────────────────────────────────────── */

/** Get the stored auth token. Returns null if not logged in. */
function getToken() {
  return localStorage.getItem("token");
}

/** Redirect to login if not authenticated. Call on every protected page. */
function requireAuth() {
  if (!getToken()) window.location.href = "index.html";
}

/** Clear session and redirect to login. */
function logout() {
  localStorage.clear();
  window.location.href = "index.html";
}

/* ── Authenticated fetch wrapper ─────────────────────────── */

/**
 * Fetch helper that automatically attaches the Authorization header.
 * @param {string} path    - e.g. "/medicines"
 * @param {object} options - standard fetch options
 * @returns {Promise<any>} - parsed JSON
 * @throws {Error} if response is not ok
 */
async function apiFetch(path, options = {}) {
  const token = getToken();
  const headers = {
    "Content-Type": "application/json",
    ...(token ? { Authorization: token } : {}),
    ...(options.headers || {}),
  };
  const res  = await fetch(`${API}${path}`, { ...options, headers });
  const data = await res.json();
  if (!res.ok) throw new Error(data.detail || `Request failed (${res.status})`);
  return data;
}

/* ── Toast notification ──────────────────────────────────── */

/**
 * Show a toast notification (#toast and #toast-msg must exist in the page).
 * @param {string}  msg        - Text to display
 * @param {boolean} isReminder - Apply reminder styling if true
 * @param {number}  duration   - Auto-hide delay in ms (default 3500)
 */
function showToast(msg, isReminder = false, duration = 3500) {
  const toast = document.getElementById("toast");
  const msgEl = document.getElementById("toast-msg");
  if (!toast || !msgEl) return;
  msgEl.textContent = msg;
  toast.classList.toggle("reminder-toast", isReminder);
  toast.classList.add("show");
  clearTimeout(toast._hideTimer);
  toast._hideTimer = setTimeout(() => toast.classList.remove("show"), duration);
}

function closeToast() {
  const toast = document.getElementById("toast");
  if (toast) toast.classList.remove("show");
}

/* ── Date / Time helpers ─────────────────────────────────── */

/**
 * Format "HH:MM" or "HH:MM:SS"  →  "hh:MM AM/PM"
 * @param {string} t
 * @returns {string}
 */
function formatTime(t) {
  if (!t) return "–";
  const [h, m] = t.split(":").map(Number);
  return `${String(h % 12 || 12).padStart(2, "0")}:${String(m).padStart(2, "0")} ${h >= 12 ? "PM" : "AM"}`;
}

/** Return today's date as "YYYY-MM-DD" */
function todayISO() {
  return new Date().toISOString().split("T")[0];
}

/**
 * Format "YYYY-MM-DD"  →  "27 Sep 2026"
 * @param {string} dateStr
 * @returns {string}
 */
function formatDateDisplay(dateStr) {
  if (!dateStr) return "–";
  return new Date(dateStr).toLocaleDateString("en-IN", {
    day: "2-digit", month: "short", year: "numeric",
  });
}

/* ── Status badge HTML ───────────────────────────────────── */

/**
 * Return a coloured badge <span> for a status string.
 * @param {string} status - "taken" | "skipped" | "pending"
 * @returns {string} HTML
 */
function statusBadge(status) {
  switch (status) {
    case "taken":   return '<span class="badge badge-success">✅ Taken</span>';
    case "skipped": return '<span class="badge badge-danger">⏭️ Skipped</span>';
    default:        return '<span class="badge badge-warning">⏳ Pending</span>';
  }
}

/* ── Sidebar user info ───────────────────────────────────── */

/**
 * Populate #user-name and #user-avatar from localStorage.
 * Call once on page load for any page with a sidebar.
 */
function initSidebarUser() {
  const username = localStorage.getItem("username") || "User";
  const nameEl   = document.getElementById("user-name");
  const avatarEl = document.getElementById("user-avatar");
  if (nameEl)   nameEl.textContent   = username;
  if (avatarEl) avatarEl.textContent = username.charAt(0).toUpperCase();
}

/* ── Reminder alert checker ──────────────────────────────── */

/**
 * Scan today's reminders and fire a toast for any pending dose
 * whose scheduled_time matches the current HH:MM.
 * @param {Array} reminders - data from GET /reminders/today
 */
function checkReminderAlerts(reminders) {
  const hhmm = new Date().toTimeString().slice(0, 5);
  (reminders || []).forEach((r) => {
    const schedTime = (r.scheduled_time || "").slice(0, 5);
    if (r.status === "pending" && schedTime === hhmm) {
      showToast(`⏰ Time to take: ${r.medicines?.name || "your medicine"}`, true, 7000);
    }
  });
}
