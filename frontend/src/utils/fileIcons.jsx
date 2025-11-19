// src/utils/fileIcons.jsx
import React from "react";
import { FiYoutube, FiFileText, FiFile } from "react-icons/fi";

export default function getIconForItem(item) {
  if (!item) return <FiFile />;

  const title = item.title?.toLowerCase() || "";
  const url = item.url?.toLowerCase() || "";

  if (url.includes("youtube.com") || url.includes("youtu.be")) {
    return <FiYoutube className="text-red-500" />;
  }

  // file detection
  if (title.endsWith(".pdf")) return <FiFileText className="text-blue-600" />;
  if (title.endsWith(".doc") || title.endsWith(".docx")) return <FiFileText className="text-indigo-600" />;
  if (title.endsWith(".txt")) return <FiFileText className="text-gray-600" />;
  if (title.endsWith(".csv")) return <FiFileText className="text-green-600" />;

  return <FiFile />;
}
