import React, { useState, useRef, useEffect } from "react";
import { uploadFile, ragQuery, processYoutube } from "../services/api";

export default function ChatArea({ current, onProcess, onSaved }) {
  const [messages, setMessages] = useState([]);
  const [input, setInput] = useState("");
  const containerRef = useRef();
  const fileInputRef = useRef();

  useEffect(() => {
    if (current) {
      const key = `conv_${current.id}`;
      try {
        const saved = JSON.parse(localStorage.getItem(key) || "null");
        setMessages(saved || [{ role: "ai", text: "This is a new conversation. Paste a YouTube link or upload a file to summarize." }]);
      } catch (e) {
        setMessages([{ role: "ai", text: "Start by processing a YouTube link or uploading a document." }]);
      }
    } else {
      setMessages([{ role: "ai", text: "Start by processing a YouTube link or uploading a document." }]);
    }
  }, [current]);

  useEffect(() => {
    containerRef.current?.scrollTo({ top: containerRef.current.scrollHeight, behavior: "smooth" });
  }, [messages]);

  async function processFile(file) {
    if (!file) return;
    setMessages(m => [...m, { role: "user", text: `Uploaded: ${file.name}` }]);
    setMessages(m => [...m, { role: "ai", text: `Processing ${file.name} ...` }]);
    try {
      const data = await uploadFile(file);
      const fileId = data.file_id || data.id || (Math.random().toString(36).slice(2,9));
      const aiMsg = `File processed! ID: ${fileId}. You can ask questions about this document now.`;
      setMessages(m => [...m.slice(0, -1), { role: "ai", text: aiMsg }]);
      const item = { id: fileId, url: file.name, title: file.name, createdAt: new Date().toISOString() };
      try { localStorage.setItem(`conv_${fileId}`, JSON.stringify([{ role: "ai", text: aiMsg }])); } catch (e) {}
      onSaved && onSaved(item);
    } catch (err) {
      setMessages(m => [...m.slice(0, -1), { role: "ai", text: `Error: ${err.message}` }]);
    }
  }

  async function handleSummarize() {
    if (!input.trim()) return;
    const url = input.trim();
    setMessages(m => [...m, { role: "user", text: url }]);
    setInput("");
    try {
      setMessages(m => [...m, { role: "ai", text: "Processing video... please wait." }]);
      const data = await processYoutube(url);
      const videoId = data.video_id || data.videoId || (Math.random().toString(36).slice(2,9));
      const aiMsg = `Done: video processed with id ${videoId}. Ask questions about this video now.`;
      setMessages(m => [...m.slice(0, -1), { role: "ai", text: aiMsg }]);
      const item = { id: videoId, url, title: url, createdAt: new Date().toISOString() };
      try { localStorage.setItem(`conv_${videoId}`, JSON.stringify([{ role: "ai", text: aiMsg }])); } catch (e) {}
      onSaved && onSaved(item);
    } catch (err) {
      setMessages(m => [...m.slice(0, -1), { role: "ai", text: `Error: ${err.message}` }]);
    }
  }

  async function handleAskQuestion() {
    if (!input.trim()) return;
    const question = input.trim();
    setInput("");
    setMessages(m => [...m, { role: "user", text: question }]);
    setMessages(m => [...m, { role: "ai", text: "Thinking..." }]);
    try {
      const id = current?.id;
      if (!id) throw new Error("No document or video selected.");
      const data = await ragQuery(id, question);
      const answer = data?.answer || "No answer returned.";
      setMessages(m => [...m.slice(0, -1), { role: "ai", text: answer }]);
      const key = `conv_${id}`;
      const prev = JSON.parse(localStorage.getItem(key) || "[]");
      localStorage.setItem(key, JSON.stringify([...prev, { role: "user", text: question }, { role: "ai", text: answer }]));
      onSaved && onSaved({ id, url: current?.url, createdAt: current?.createdAt || new Date().toISOString() });
    } catch (err) {
      setMessages(m => [...m.slice(0, -1), { role: "ai", text: `Failed to retrieve answer: ${err.message}` }]);
    }
  }

  function exportConversation() {
    if (!current) return;
    const key = `conv_${current.id}`;
    const conv = JSON.parse(localStorage.getItem(key) || "[]");
    const txt = conv.map((c) => `${c.role.toUpperCase()}: ${c.text}`).join("\n\n");
    const blob = new Blob([txt], { type: "text/plain" });
    const url = URL.createObjectURL(blob);
    const a = document.createElement("a");
    a.href = url;
    a.download = `${current.title || current.id}_chat.txt`;
    a.click();
    URL.revokeObjectURL(url);
  }

  function onFileChange(e) {
    const f = e.target.files?.[0];
    if (f) processFile(f);
  }

  return (
    <section style={{ display: "flex", flexDirection: "column", minHeight: "85vh", borderRadius: 8 }}>
      <div style={{ display: "flex", justifyContent: "space-between", padding: 12, borderBottom: "1px solid #eee" }}>
        <div>
          <button onClick={() => { const id = "conv_" + Date.now().toString(36); onSaved && onSaved({ id, url: null, title: "New Chat", createdAt: new Date().toISOString() }); setMessages([{ role: "ai", text: "New chat started." }]); }} style={{ marginRight: 8 }}>New Chat</button>
          <button onClick={exportConversation}>Export</button>
        </div>

        <div>
          <input ref={fileInputRef} type="file" accept=".pdf,.docx,.txt,.csv" onChange={onFileChange} />
        </div>
      </div>

      <div ref={containerRef} style={{ padding: 12, overflowY: "auto", maxHeight: "58vh", flex: 1 }}>
        {messages.map((m, i) => (
          <div key={i} style={{ display: "flex", justifyContent: m.role === "ai" ? "flex-start" : "flex-end", marginBottom: 8 }}>
            <div style={{ padding: 10, borderRadius: 8, maxWidth: "80%", background: m.role === "ai" ? "#fff" : "#e5e7eb" }}>
              {m.text}
            </div>
          </div>
        ))}
      </div>

      <div style={{ padding: 12, borderTop: "1px solid #eee" }}>
        <div style={{ display: "flex", gap: 8 }}>
          <input
            value={input}
            onChange={(e) => setInput(e.target.value)}
            onKeyDown={(e) => { if (e.key === "Enter") { if (!current && /youtube\.com|youtu\.be/.test(input)) handleSummarize(); else handleAskQuestion(); } }}
            placeholder={current ? "Ask a question about the video/document..." : "Paste YouTube link or upload a file..."}
            style={{ flex: 1, padding: 8, borderRadius: 20, border: "1px solid #ddd" }}
          />
          <button onClick={() => { if (!current && /youtube\.com|youtu\.be/.test(input)) handleSummarize(); else handleAskQuestion(); }} style={{ padding: "8px 16px", borderRadius: 20, background: "#111", color: "#fff" }}>Send</button>
        </div>
      </div>
    </section>
  );
}
