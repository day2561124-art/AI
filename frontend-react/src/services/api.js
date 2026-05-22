export const API_BASE = import.meta.env.VITE_API_BASE || "http://127.0.0.1:8000";
const VISITOR_KEY = "ai_customer_service_visitor_id";

export function getVisitorId() {
  let visitorId = localStorage.getItem(VISITOR_KEY);
  if (!visitorId) {
    visitorId = globalThis.crypto?.randomUUID
      ? globalThis.crypto.randomUUID()
      : `${Date.now()}-${Math.random()}`;
    localStorage.setItem(VISITOR_KEY, visitorId);
  }
  return visitorId;
}

async function request(path, options = {}) {
  const response = await fetch(`${API_BASE}${path}`, options);
  if (!response.ok) {
    throw new Error(`API request failed: ${response.status}`);
  }
  return response.json();
}

export function askQuestion(question) {
  return request("/api/chat", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ question, visitor_id: getVisitorId() }),
  });
}

export function getPublicChatHistory(limit = 30) {
  return request(`/api/chat-history?limit=${limit}`);
}

export function sendFeedback(payload) {
  return request("/api/feedback", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ ...payload, visitor_id: getVisitorId() }),
  });
}

export function trackVisit(page) {
  return request("/api/analytics/visit", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({
      visitor_id: getVisitorId(),
      page,
      path: location.href,
      referrer: document.referrer || null,
    }),
  });
}

function adminHeaders(token) {
  return token ? { "X-Admin-Token": token } : {};
}

export function getAdminStats(token) {
  return request("/api/admin/stats", { headers: adminHeaders(token) });
}

export function getChatLogs(token) {
  return request("/api/admin/chat-logs", { headers: adminHeaders(token) });
}

export function getFeedback(token) {
  return request("/api/admin/feedback", { headers: adminHeaders(token) });
}

export function getUnanswered(token) {
  return request("/api/admin/unanswered", { headers: adminHeaders(token) });
}

export function getVisits(token) {
  return request("/api/admin/visits", { headers: adminHeaders(token) });
}

export function reloadKnowledge(token) {
  return request("/api/admin/knowledge/reload", {
    method: "POST",
    headers: adminHeaders(token),
  });
}

export function uploadKnowledge(token, file) {
  const formData = new FormData();
  formData.append("file", file);
  return request("/api/admin/knowledge/upload", {
    method: "POST",
    headers: adminHeaders(token),
    body: formData,
  });
}
