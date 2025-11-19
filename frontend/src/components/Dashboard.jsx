import React, { useState, useEffect } from "react";
import Sidebar from "./Sidebar";
import ChatArea from "./ChatArea";
import { processYoutube } from "../services/api";

export default function Dashboard({ user, onLogout }) {
  const [history, setHistory] = useState([]);
  const [current, setCurrent] = useState(null);
  const [darkMode, setDarkMode] = useState(false);

  useEffect(() => {
    try {
      const saved = JSON.parse(localStorage.getItem("summarai_history") || "[]");
      setHistory(saved);
    } catch (e) {
      setHistory([]);
    }
    const dark = localStorage.getItem("dark_mode") === "true";
    setDarkMode(dark);
    applyTheme(dark);
  }, []);

  function applyTheme(dark) {
    if (dark) document.documentElement.setAttribute("data-theme", "dark");
    else document.documentElement.removeAttribute("data-theme");
  }

  function saveHistory(updated) {
    setHistory(updated);
    try { localStorage.setItem("summarai_history", JSON.stringify(updated)); } catch (e) {}
  }

  function addToHistory(item) {
    if (!item?.id) return;
    const filtered = history.filter((h) => h.id !== item.id);
    const updated = [item, ...filtered];
    saveHistory(updated);
  }

  async function handleProcessYoutube(url) {
    try {
      const data = await processYoutube(url);
      const videoId = data.video_id || data.videoId || (Math.random().toString(36).slice(2,9));
      const item = { id: videoId, url, title: url, createdAt: new Date().toISOString() };
      addToHistory(item);
      setCurrent(item);
      return { id: videoId };
    } catch (e) {
      throw e;
    }
  }

  function handleDeleteChat(id) {
    const updated = history.filter((h) => h.id !== id);
    saveHistory(updated);
    try { localStorage.removeItem(`conv_${id}`); } catch (e) {}
    if (current?.id === id) setCurrent(null);
  }

  function handleClearAll() {
    saveHistory([]);
    Object.keys(localStorage).forEach((k) => { if (k.startsWith("conv_")) localStorage.removeItem(k); });
    setCurrent(null);
  }

  function handleRename(id, newTitle) {
    const updated = history.map((h) => (h.id === id ? { ...h, title: newTitle } : h));
    saveHistory(updated);
  }

  function handlePin(id) {
    const updated = history.map((h) => (h.id === id ? { ...h, pinned: !h.pinned } : h));
    saveHistory(updated);
  }

  function toggleDark() {
    const newVal = !darkMode;
    setDarkMode(newVal);
    try { localStorage.setItem("dark_mode", newVal.toString()); } catch (e) {}
    applyTheme(newVal);
  }

  function exportSelected(arr) {
    const output = arr.map((h) => {
      const conv = JSON.parse(localStorage.getItem(`conv_${h.id}`) || "[]");
      return { meta: h, conv };
    });
    const blob = new Blob([JSON.stringify(output, null, 2)], { type: "application/json" });
    const url = URL.createObjectURL(blob);
    const a = document.createElement("a");
    a.href = url;
    a.download = `chats_export_${Date.now()}.json`;
    a.click();
    URL.revokeObjectURL(url);
  }

  return (
    <div className="min-h-screen flex">
      <div style={{ width: "240px", position: "fixed", left: 0, top: 0, bottom: 0, overflowY: "auto", padding: 16 }} className={darkMode ? "bg-gray-900 text-white" : "bg-white text-black"}>
        <Sidebar
          history={history}
          current={current}
          onSelect={setCurrent}
          onDelete={handleDeleteChat}
          onRename={handleRename}
          onPin={handlePin}
          onClearAll={handleClearAll}
          darkMode={darkMode}
          toggleDark={toggleDark}
          user={user}
          onLogout={onLogout}
          onExportSelected={exportSelected}
        />
      </div>

      <div style={{ marginLeft: 240, flex: 1, padding: 16 }} className={darkMode ? "bg-gray-800 min-h-screen" : "bg-[#FFECB3] min-h-screen"}>
        <ChatArea current={current} onProcess={handleProcessYoutube} onSaved={(item) => { addToHistory(item); setCurrent(item); }} />
      </div>
    </div>
  );
}
