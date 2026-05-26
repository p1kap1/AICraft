"use client";
import { useEffect, useState, useRef } from "react";
import { useRouter, useSearchParams } from "next/navigation";
import { Send, Bot, User, Loader2, Plus, MessageSquare, Trash2 } from "lucide-react";
import { Input } from "@/components/ui/input";
import { Button } from "@/components/ui/button";

const API = "/api";

export default function ChatPage() {
  const [agents, setAgents] = useState<any[]>([]);
  const [agentId, setAgentId] = useState("");
  const searchParams = useSearchParams();

  useEffect(() => {
    // 从 URL 参数读取 agent
    const aid = searchParams.get("agent");
    if (aid) setAgentId(aid);
  }, [searchParams]);
  const [input, setInput] = useState("");
  const [msgs, setMsgs] = useState<{ role: string; content: string }[]>([]);
  const [loading, setLoading] = useState(false);
  const [sessions, setSessions] = useState<any[]>([]);
  const [sessionId, setSessionId] = useState("");
  const bottomRef = useRef<HTMLDivElement>(null);
  const token = typeof window !== "undefined" ? localStorage.getItem("token") : "";
  const auth = () => token ? { Authorization: "Bearer " + token } : {};

  const loadSessions = () => {
    fetch(API + "/chat/sessions", { headers: auth() }).then(r => r.json()).then(setSessions);
  };

  const loadMessages = (sid: string) => {
    setSessionId(sid);
    fetch(API + "/chat/sessions/" + sid + "/messages", { headers: auth() })
      .then(r => r.json()).then(setMsgs);
  };

  const newSession = () => {
    setMsgs([]);
    setSessionId("");
  };

  const delSession = async (sid: string) => {
    if (!confirm("确定删除这个会话？")) return;
    const r = await fetch(API + "/chat/sessions/" + sid, { method: "DELETE", headers: auth() });
    if (r.ok) {
      if (sessionId === sid) { setMsgs([]); setSessionId(""); }
      loadSessions();
    }
  };

  useEffect(() => {
    const t = localStorage.getItem("token"); if (!t) return;
    fetch(API + "/agents/user", { headers: { Authorization: "Bearer " + t } }).then(r => r.json()).then(setAgents).catch(e => console.error(e));
    loadSessions();
  }, []);

  useEffect(() => { bottomRef.current?.scrollIntoView({ behavior: "smooth" }); }, [msgs]);

  const send = async () => {
    if (!input || loading) return;
    const msg = input; setInput(""); setLoading(true);
    setMsgs(prev => [...prev, { role: "user", content: msg }, { role: "assistant", content: "" }]);
    const aiIdx = msgs.length + 1;

    const r = await fetch(API + "/chat/stream", {
      method: "POST", headers: { ...auth(), "Content-Type": "application/json" },
      body: JSON.stringify({ message: msg, agent_id: agentId || null, session_id: sessionId || null }),
    });
    if (!r.ok) {
      const d = await r.json();
      setMsgs(prev => [...prev, { role: "system", content: "错误: " + (d.detail || d.message || "未知错误") }]);
      setLoading(false); return;
    }
    const reader = r.body!.getReader(); const dec = new TextDecoder(); let ai = "";
    while (true) {
      const { done, value } = await reader.read();
      if (done) break;
      for (const line of dec.decode(value).split("\n")) {
        if (line.startsWith("data: ")) {
          try {
            const d = JSON.parse(line.slice(6));
            if (d.type === "text") ai += d.content;
            else if (d.type === "tool") ai += "\n🔧 " + d.name + ": " + (d.result || "").slice(0, 100);
            else if (d.type === "system") ai += "\n" + d.content;
            setMsgs(prev => { const n = [...prev]; n[aiIdx] = { role: "assistant", content: ai }; return n; });
          } catch {}
        }
      }
    }
    setLoading(false);
    loadSessions();
  };

  return (
    <div className="flex h-full">
      {/* 会话列表 */}
      <div className="w-56 border-r border-slate-700/50 flex flex-col">
        <div className="p-3 border-b border-slate-700/50">
          <Button className="w-full justify-start gap-2" size="sm" onClick={newSession}>
            <Plus className="w-4 h-4" /> 新对话
          </Button>
        </div>
        <div className="flex-1 overflow-y-auto">
          {sessions.map((s: any) => (
            <div key={s.id} onClick={() => loadMessages(s.id)}
              className={`w-full flex items-center gap-2 px-3 py-2 text-sm text-left hover:bg-slate-700/50 transition group cursor-pointer ${s.id === sessionId ? "bg-cyan-500/10 text-cyan-400" : "text-slate-400"}`}>
              <MessageSquare className="w-3.5 h-3.5 shrink-0" />
              <span className="truncate flex-1">{s.title || "新会话"}</span>
              <Trash2 className="w-3.5 h-3.5 opacity-0 group-hover:opacity-100 text-red-400 hover:text-red-300 shrink-0" onClick={(e) => { e.stopPropagation(); delSession(s.id); }} />
            </div>
          ))}
        </div>
      </div>

      {/* 聊天区 */}
      <div className="flex-1 flex flex-col max-w-3xl mx-auto w-full">
        <div className="p-3 border-b border-slate-700/50">
          <select className="w-full bg-slate-800 border border-slate-700 text-white p-2 rounded-lg text-sm" value={agentId} onChange={e => setAgentId(e.target.value)}>
            <option value="">直接对话</option>
            {agents.map((a: any) => <option key={a.id} value={a.id}>{a.name}</option>)}
          </select>
        </div>

        <div className="flex-1 overflow-y-auto p-4 space-y-4">
          {msgs.length === 0 && (
            <div className="text-center text-slate-500 mt-20">
              <Bot className="w-12 h-12 mx-auto mb-3 text-cyan-400/50" />
              <p className="text-lg">开始对话</p>
              <p className="text-sm">选择一个 Agent 并发送消息</p>
            </div>
          )}
          {msgs.map((m, i) => (
            <div key={i} className={"flex gap-3 " + (m.role === "user" ? "justify-end" : "")}>
              {m.role === "assistant" && <Bot className="w-6 h-6 text-cyan-400 mt-1 shrink-0" />}
              <div className={"rounded-xl px-4 py-2.5 text-sm max-w-[80%] whitespace-pre-wrap " + (m.role === "user" ? "bg-cyan-500 text-slate-900" : m.role === "system" ? "bg-yellow-500/10 border border-yellow-500/30 text-yellow-400 text-xs" : "bg-slate-800 border border-slate-700")}>
                {m.content || (i === msgs.length - 1 && loading ? <Loader2 className="w-4 h-4 animate-spin" /> : "")}
              </div>
              {m.role === "user" && <User className="w-6 h-6 text-slate-400 mt-1 shrink-0" />}
            </div>
          ))}
          <div ref={bottomRef} />
        </div>

        <div className="p-4 border-t border-slate-700/50">
          <div className="flex gap-2">
            <Input placeholder="输入消息..." value={input} onChange={e => setInput(e.target.value)} onKeyDown={e => e.key === "Enter" && send()} disabled={loading} className="bg-slate-800 border-slate-700" />
            <Button onClick={send} disabled={loading} size="icon" className="bg-cyan-500 hover:bg-cyan-400 text-slate-900"><Send className="w-4 h-4" /></Button>
          </div>
        </div>
      </div>
    </div>
  );
}
