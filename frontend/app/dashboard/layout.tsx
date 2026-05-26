"use client";
import { useEffect, useState } from "react";
import { useRouter, usePathname } from "next/navigation";
import { Bot, MessageSquare, Search, Settings, Key, Wrench, BookOpen, ShoppingBag, CreditCard, Shield, History, Clock, DollarSign, Code, Container } from "lucide-react";
import { cn } from "@/lib/utils";
import { Button } from "@/components/ui/button";

const allNav = [
  { key: "discover", label: "发现", icon: Search, adminOnly: false },
  { key: "chat", label: "对话", icon: MessageSquare, adminOnly: false },
  { key: "studio", label: "Agent 工作室", icon: Bot, adminOnly: false },
  { key: "versions", label: "版本管理", icon: History, adminOnly: false },
  { key: "tools", label: "工具", icon: Wrench, adminOnly: false },
  { key: "market", label: "工具市场", icon: ShoppingBag, adminOnly: false },
  { key: "providers", label: "服务商", icon: Key, adminOnly: false },
  { key: "knowledge", label: "知识库", icon: BookOpen, adminOnly: false },
  { key: "tasks", label: "定时任务", icon: Clock, adminOnly: false },
  { key: "billing", label: "计费", icon: CreditCard, adminOnly: false },
  { key: "payment", label: "支付", icon: DollarSign, adminOnly: false },
  { key: "api-docs", label: "API 文档", icon: Code, adminOnly: false },
  { key: "settings", label: "设置", icon: Settings, adminOnly: false },
  { key: "admin", label: "管理", icon: Shield, adminOnly: true },
  { key: "container", label: "容器", icon: Container, adminOnly: true },
];

export default function DashboardLayout({ children }: { children: React.ReactNode }) {
  const [user, setUser] = useState<any>(null);
  const [isDark, setIsDark] = useState(true);
  const router = useRouter();
  const pathname = usePathname();

  useEffect(() => {
    const u = localStorage.getItem("user");
    const t = localStorage.getItem("token");
    if (!u || !t) { router.push("/login"); return; }
    fetch("/api/profile", {
      headers: { Authorization: "Bearer " + t }
    }).then(r => r.json()).then(setUser);
  }, []);

  return (
    <div className="flex h-screen bg-slate-900">
      <aside className="w-60 bg-slate-800/80 border-r border-slate-700/50 flex flex-col">
        <div className="p-4 border-b border-slate-700/50">
          <h1 className="text-lg font-bold text-cyan-400 flex items-center gap-2">
            <Bot className="w-5 h-5" /> AICraft
          </h1>
        </div>
        <nav className="flex-1 p-3 space-y-1 overflow-auto">
          {allNav.filter(n => !n.adminOnly || user?.is_admin).map((n) => {
            const Icon = n.icon;
            const active = pathname.includes("/dashboard/" + n.key);
            return (
              <button
                key={n.key}
                onClick={() => router.push("/dashboard/" + n.key)}
                className={cn(
                  "w-full flex items-center gap-3 px-3 py-2 rounded-lg text-sm transition-colors",
                  active
                    ? "bg-cyan-500/10 text-cyan-400 font-medium"
                    : "text-slate-400 hover:text-white hover:bg-slate-700/50"
                )}
              >
                <Icon className="w-4 h-4" />
                {n.label}
              </button>
            );
          })}
        </nav>
        <div className="p-4 border-t border-slate-700/50">
          <div className="flex items-center justify-between">
            <div>
              <div className="text-sm text-slate-300">{user?.nickname || "用户"}</div>
              <div className="text-[10px] text-slate-500">{user?.is_admin ? "管理员" : "普通用户"}</div>
            </div>
            <button
              onClick={() => { localStorage.clear(); router.push("/login"); }}
              className="text-xs text-slate-400 hover:text-red-400 transition"
            >退出</button>
          </div>
        </div>
      </aside>
      <main className="flex-1 overflow-auto">{children}</main>
    </div>
  );
}
