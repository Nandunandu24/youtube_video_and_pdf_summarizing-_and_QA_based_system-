import React, { useState } from "react";
import { login, signup } from "../services/api";

export default function Auth({ onLoginSuccess }) {
  const [tab, setTab] = useState("login"); // 'login' or 'signup'
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [confirm, setConfirm] = useState("");
  const [loading, setLoading] = useState(false);

  async function handleSubmit(e) {
    e.preventDefault();
    setLoading(true);
    try {
      if (tab === "login") {
        const res = await login(email, password);
        // login may return { access_token, user } or mock user
        const user = res.user || { email };
        try { localStorage.setItem("summarai_token", res.access_token || ""); } catch (e) {}
        onLoginSuccess(user);
      } else {
        if (password !== confirm) throw new Error("Passwords do not match");
        await signup(email, password, confirm);
        const res = await login(email, password);
        const user = res.user || { email };
        try { localStorage.setItem("summarai_token", res.access_token || ""); } catch (e) {}
        onLoginSuccess(user);
      }
    } catch (err) {
      alert(err?.message || "Authentication failed");
      console.error(err);
    } finally {
      setLoading(false);
    }
  }

  return (
    <main className="min-h-screen flex items-center justify-center bg-[#FFF8E7] p-4">
      <div className="w-full max-w-md bg-white p-6 rounded-lg shadow">
        <h1 className="text-2xl font-bold text-center mb-4">SummarAI</h1>

        <div className="flex justify-center gap-2 mb-4">
          <button
            onClick={() => setTab("login")}
            className={tab === "login" ? "px-4 py-2 bg-gray-800 text-white rounded" : "px-4 py-2 bg-gray-200 rounded"}
          >
            Login
          </button>
          <button
            onClick={() => setTab("signup")}
            className={tab === "signup" ? "px-4 py-2 bg-gray-800 text-white rounded" : "px-4 py-2 bg-gray-200 rounded"}
          >
            Sign up
          </button>
        </div>

        <form onSubmit={handleSubmit} className="space-y-3">
          <input
            type="email"
            value={email}
            onChange={(e) => setEmail(e.target.value)}
            placeholder="Email"
            required
            className="w-full border p-2 rounded"
          />
          <input
            type="password"
            value={password}
            onChange={(e) => setPassword(e.target.value)}
            placeholder="Password"
            required
            className="w-full border p-2 rounded"
          />
          {tab === "signup" && (
            <input
              type="password"
              value={confirm}
              onChange={(e) => setConfirm(e.target.value)}
              placeholder="Confirm password"
              required
              className="w-full border p-2 rounded"
            />
          )}

          <button type="submit" disabled={loading} className="w-full bg-black text-white p-2 rounded">
            {loading ? "Please wait..." : tab === "login" ? "Login" : "Create account"}
          </button>
        </form>

        <div className="mt-3 text-center">
          <a href="#" onClick={(e)=>e.preventDefault()} className="text-sm text-blue-600">Forgot password?</a>
        </div>
      </div>
    </main>
  );
}
