"use client";
import { createContext, useContext, useEffect, useState } from "react";

type Theme = "dark" | "light";

const ThemeContext = createContext<{ theme: Theme; toggle: () => void }>({ theme: "dark", toggle: () => {} });

export function ThemeProvider({ children }: { children: React.ReactNode }) {
  const [theme, setTheme] = useState<Theme>("dark");
  useEffect(() => {
    const saved = localStorage.getItem("theme") as Theme;
    if (saved) setTheme(saved);
  }, []);
  const toggle = () => {
    const next = theme === "dark" ? "light" : "dark";
    setTheme(next);
    localStorage.setItem("theme", next);
    document.documentElement.classList.toggle("dark", next === "dark");
  };

  useEffect(() => {
    document.documentElement.classList.toggle("dark", theme === "dark");
  }, [theme]);
  return (
    <ThemeContext.Provider value={{ theme, toggle }}>
      <div className={theme}>{children}</div>
    </ThemeContext.Provider>
  );
}

export function useTheme() { return useContext(ThemeContext); }
