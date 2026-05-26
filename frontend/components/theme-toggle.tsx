"use client";
import { useEffect, useState } from "react";

export default function ThemeToggle() {
  const [dark, setDark] = useState(true);

  useEffect(() => {
    const saved = localStorage.getItem("theme");
    if (saved === "light") { setDark(false); document.documentElement.classList.remove("dark"); }
  }, []);

  const toggle = () => {
    const next = !dark;
    setDark(next);
    localStorage.setItem("theme", next ? "dark" : "light");
    if (next) document.documentElement.classList.add("dark");
    else document.documentElement.classList.remove("dark");
  };

  return (
    <button onClick={toggle} className="flex items-center gap-2 text-xs text-slate-400 hover:text-white transition">
      {dark ? "☀️ 浅色" : "🌙 深色"}
    </button>
  );
}
