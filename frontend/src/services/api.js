const BASE = "http://127.0.0.1:8000";

async function safeFetch(url, opts = {}) {
  try {
    const res = await fetch(url, opts);
    const json = await res.json().catch(() => ({}));
    if (!res.ok) {
      const err = json.detail || json.error || json.message || `HTTP ${res.status}`;
      throw new Error(err);
    }
    return json;
  } catch (e) {
    // rethrow so callers can handle, but keep helpful message
    throw new Error(e.message || "Network error");
  }
}

export async function processYoutube(url) {
  // Try real backend, fallback to a mock so UI still works
  const endpoint = `${BASE}/youtube/process?youtube_url=${encodeURIComponent(url)}`;
  try {
    return await safeFetch(endpoint, { method: "POST" });
  } catch (e) {
    console.warn("processYoutube backend failed, returning mock:", e.message);
    return { video_id: "mock_" + Math.random().toString(36).slice(2,9) };
  }
}

export async function uploadFile(file) {
  const form = new FormData();
  form.append("file", file);
  try {
    const res = await fetch(`${BASE}/files/upload`, { method: "POST", body: form });
    if (!res.ok) {
      const json = await res.json().catch(() => ({}));
      throw new Error(json.detail || json.message || "Upload failed");
    }
    return res.json();
  } catch (e) {
    console.warn("uploadFile backend failed, returning mock:", e.message);
    return { file_id: "mockfile_" + Math.random().toString(36).slice(2,9) };
  }
}

export async function ragQuery(video_id, question) {
  try {
    const res = await safeFetch(`${BASE}/rag/query`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ video_id, question })
    });
    return res;
  } catch (e) {
    console.warn("ragQuery backend failed, returning mock:", e.message);
    return { answer: "Mock answer: backend unavailable.", sources: [] };
  }
}

export async function login(email, password) {
  try {
    return await safeFetch(`${BASE}/login`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ email, password })
    });
  } catch (e) {
    console.warn("login backend failed, returning mock user:", e.message);
    return { access_token: "mock_token", user: { email, username: email.split("@")[0] } };
  }
}

export async function signup(email, password, confirm) {
  try {
    return await safeFetch(`${BASE}/signup`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ email, password })
    });
  } catch (e) {
    console.warn("signup backend failed, returning mock:", e.message);
    return { id: Date.now(), email };
  }
}
