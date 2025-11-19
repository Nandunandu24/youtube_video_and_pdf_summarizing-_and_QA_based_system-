import React, { useState, useEffect } from "react";
import Auth from "./components/Auth";
import Dashboard from "./components/Dashboard";

export default function App() {
  const [user, setUser] = useState(null);

  useEffect(() => {
    try {
      const saved = localStorage.getItem("summarai_user");
      if (saved) setUser(JSON.parse(saved));
    } catch (e) {
      console.error("Failed to read saved user", e);
    }
  }, []);

  function handleLoginSuccess(userObj) {
    setUser(userObj);
    try { localStorage.setItem("summarai_user", JSON.stringify(userObj)); } catch (e) {}
  }

  function handleLogout() {
    setUser(null);
    try { localStorage.removeItem("summarai_user"); } catch (e) {}
  }

  return (
    <div className="min-h-screen bg-neutral-50 text-[#333]">
      {user ? (
        <Dashboard user={user} onLogout={handleLogout} />
      ) : (
        <Auth onLoginSuccess={handleLoginSuccess} />
      )}
    </div>
  );
}
