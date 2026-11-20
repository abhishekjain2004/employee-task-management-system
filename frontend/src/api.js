const API_BASE = import.meta.env.VITE_API_BASE_URL || "http://127.0.0.1:8000";

export function getToken() {
  return localStorage.getItem("ets_token");
}

export function saveSession(token, user) {
  localStorage.setItem("ets_token", token);
  localStorage.setItem("ets_user", JSON.stringify(user));
}

export function clearSession() {
  localStorage.removeItem("ets_token");
  localStorage.removeItem("ets_user");
}

export function getSavedUser() {
  try {
    return JSON.parse(localStorage.getItem("ets_user") || "null");
  } catch {
    return null;
  }
}

export async function api(path, options = {}) {
  const headers = { ...(options.headers || {}) };
  if (!(options.body instanceof FormData)) headers["Content-Type"] = "application/json";
  const token = getToken();
  if (token) headers.Authorization = `Bearer ${token}`;

  const response = await fetch(`${API_BASE}${path}`, {
    ...options,
    headers,
    body: options.body && typeof options.body !== "string" && !(options.body instanceof FormData)
      ? JSON.stringify(options.body)
      : options.body,
  });

  const raw = await response.text();
  let data;
  try { data = raw ? JSON.parse(raw) : null; } catch { data = raw; }

  if (!response.ok) {
    if (response.status === 401) clearSession();
    const message = data?.detail
      ? (Array.isArray(data.detail) ? data.detail.map(x => x.msg).join(", ") : data.detail)
      : `Request failed (${response.status})`;
    throw new Error(message);
  }
  return data;
}
