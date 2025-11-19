import React, { useState } from "react";

export default function Sidebar({
  history = [],
  current,
  onSelect,
  onDelete,
  onRename,
  onPin,
  onClearAll,
  darkMode,
  toggleDark,
  user = { username: "User", email: "" },
  onLogout,
  onExportSelected,
}) {
  const [editingId, setEditingId] = useState(null);
  const [renameVal, setRenameVal] = useState("");
  const [selected, setSelected] = useState(new Set());

  function toggleSelect(id) {
    const s = new Set(selected);
    if (s.has(id)) s.delete(id);
    else s.add(id);
    setSelected(s);
  }

  function exportSelected() {
    if (selected.size === 0) return;
    const arr = history.filter((h) => selected.has(h.id));
    onExportSelected && onExportSelected(arr);
  }

  return (
    <aside style={{ height: "100%", display: "flex", flexDirection: "column", justifyContent: "space-between" }}>
      <div>
        <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center", marginBottom: 12 }}>
          <div style={{ fontWeight: 700 }}>History</div>
          <div style={{ display: "flex", gap: 8 }}>
            <button onClick={toggleDark} style={{ padding: 6 }}>{darkMode ? "Light" : "Dark"}</button>
            <button onClick={exportSelected} style={{ padding: 6 }}>Export</button>
          </div>
        </div>

        <div style={{ overflowY: "auto", maxHeight: "60vh" }}>
          {history.length === 0 && <div style={{ color: "#666" }}>No chats yet. Start by uploading or pasting a link.</div>}

          {history
            .slice()
            .sort((a, b) => (a.pinned === b.pinned ? 0 : a.pinned ? -1 : 1) || new Date(b.createdAt) - new Date(a.createdAt))
            .map((h) => {
              const active = current && current.id === h.id;
              return (
                <div key={h.id} style={{ display: "flex", justifyContent: "space-between", alignItems: "center", padding: 8, borderRadius: 6, background: active ? "#FFF8E7" : "transparent", marginBottom: 6 }}>
                  <div style={{ display: "flex", alignItems: "center", gap: 8, cursor: "pointer", flex: 1 }} onClick={() => onSelect(h)}>
                    <input type="checkbox" checked={selected.has(h.id)} onChange={() => toggleSelect(h.id)} onClick={(e)=>e.stopPropagation()} />
                    <div style={{ overflow: "hidden", textOverflow: "ellipsis", whiteSpace: "nowrap" }}>
                      <div style={{ fontWeight: 600 }}>{h.title || h.url || h.id}</div>
                      <div style={{ fontSize: 12, color: "#666" }}>{new Date(h.createdAt).toLocaleString()}</div>
                    </div>
                  </div>

                  <div style={{ display: "flex", gap: 6, marginLeft: 8 }}>
                    <button onClick={() => onPin(h.id)}>{h.pinned ? "Unpin" : "Pin"}</button>
                    <button onClick={(e)=>{ e.stopPropagation(); setEditingId(h.id); setRenameVal(h.title || h.url || h.id); }}>Rename</button>
                    <button onClick={() => onDelete(h.id)}>Delete</button>
                  </div>
                </div>
              );
            })}
        </div>

        <div style={{ marginTop: 12 }}>
          <button onClick={onClearAll} style={{ width: "100%", padding: 8, background: "#fee2e2", borderRadius: 6 }}>Clear All Chats</button>
        </div>
      </div>

      <div style={{ marginTop: 12, borderTop: "1px solid #eee", paddingTop: 12 }}>
        <div style={{ fontWeight: 600 }}>{user?.username || "User"}</div>
        <div style={{ fontSize: 12, color: "#666" }}>{user?.email || ""}</div>
        <div style={{ marginTop: 8 }}>
          <button onClick={onLogout} style={{ padding: 6 }}>Logout</button>
        </div>
      </div>
    </aside>
  );
}
