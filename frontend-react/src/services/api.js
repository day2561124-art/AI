export const API_BASE = import.meta.env.VITE_API_BASE || "http://127.0.0.1:8000";

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
    body: JSON.stringify({ question }),
  });
}

export function sendFeedback(payload) {
  return request("/api/feedback", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(payload),
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
