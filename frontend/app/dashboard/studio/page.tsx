"use client";
import { useEffect, useState } from "react";
import { Bot, Plus, Rocket, Trash2, RotateCcw, Pencil } from "lucide-react";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Textarea } from "@/components/ui/textarea";
import { Badge } from "@/components/ui/badge";
import { Card, CardHeader, CardTitle, CardDescription, CardContent } from "@/components/ui/card";

const API = "/api";

export default function StudioPage() {
  const [agents, setAgents] = useState<any[]>([]);
  const [open, setOpen] = useState(false);
  const [editingId, setEditingId] = useState("");
  const [name, setName] = useState("");
  const [desc, setDesc] = useState("");
  const [sysPrompt, setSysPrompt] = useState("");
  const [providerSource, setProviderSource] = useState("personal");
  const [providerId, setProviderId] = useState("");
  const [platforms, setPlatforms] = useState<any[]>([]);
  const [allTools, setAllTools] = useState<any[]>([]);
  const [selectedTools, setSelectedTools] = useState<string[]>([]);
  const [allKbs, setAllKbs] = useState<any[]>([]);
  const [selectedKbs, setSelectedKbs] = useState<string[]>([]);

  const builtinTools = [
    { id: "get_time", name: "get_time — 获取当前时间" },
    { id: "calculator", name: "calculator — 计算数学表达式" },
    { id: "search", name: "search — 搜索互联网信息" },
  ];
  const token = typeof window !== "undefined" ? localStorage.getItem("token") : "";
  const auth = (ct?: string) => ({ "Content-Type": ct || "application/json", Authorization: "Bearer " + token });

  const load = () => {
    fetch(API + "/agents/user", { headers: auth() }).then(r => r.json()).then(setAgents);
    fetch(API + "/tools/user", { headers: auth() }).then(r => r.json()).then(setAllTools);
    fetch(API + "/knowledge/user", { headers: auth() }).then(r => r.json()).then(setAllKbs);
    fetch(API + "/admin/providers", { headers: auth() }).then(r => r.json()).then((d) => {
      // 同模型去重
      const seen = new Set();
      setPlatforms((Array.isArray(d) ? d : []).filter((p: any) => {
        if (seen.has(p.model)) return false;
        seen.add(p.model);
        return true;
      }));
    }).catch(() => {});
  };
  useEffect(() => { load(); }, []);

  const create = async () => {
    if (!name) return;
    try {
      const r = await fetch(API + "/agents", { method: "POST", headers: auth(), body: JSON.stringify({ name, description: desc, system_prompt: sysPrompt, provider_source: providerSource, provider_id: providerSource === "platform" ? providerId : null, tool_ids: selectedTools, knowledge_base_ids: selectedKbs }) });
      if (r.ok) { setOpen(false); setName(""); setDesc(""); setSysPrompt(""); load(); }
      else alert("创建失败: " + (await r.json()).message);
    } catch (e: any) { alert("网络错误: " + e.message); }
  };

  const del = async (id: string) => { await fetch(API + "/agents/" + id, { method: "DELETE", headers: auth() }); load(); };
  const publish = async (id: string) => {
    const ver = prompt("版本号:") || "1.0.0";
    await fetch(API + "/agents/" + id + "/publish", { method: "POST", headers: auth(), body: JSON.stringify({ version_number: ver, change_log: "" }) });
    load();
  };

  const startEdit = (a: any) => {
    setEditingId(a.id); setName(a.name); setDesc(a.description || ""); setSysPrompt(a.system_prompt || "");
    setProviderSource(a.provider_source || "personal"); setProviderId(a.provider_id || "");
    setSelectedTools(a.tool_ids || []); setSelectedKbs(a.knowledge_base_ids || []);
    setOpen(true);
  };

  const saveEdit = async () => {
    if (!name) return;
    try {
      const r = await fetch(API + "/agents/" + editingId, { method: "PUT", headers: auth(), body: JSON.stringify({ name, description: desc, system_prompt: sysPrompt, tool_ids: selectedTools, knowledge_base_ids: selectedKbs }) });
      if (r.ok) { setOpen(false); setEditingId(""); setName(""); setDesc(""); setSysPrompt(""); load(); }
      else alert("更新失败");
    } catch (e: any) { alert("网络错误: " + e.message); }
  };

  return (
    <div className="max-w-4xl mx-auto space-y-8">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold tracking-tight">Agent 工作室</h1>
          <p className="text-sm text-slate-400 mt-1">创建和管理你的 AI Agent</p>
        </div>
        <Button onClick={() => setOpen(true)} className="gap-2">
          <Plus className="w-4 h-4" /> 创建 Agent
        </Button>
      </div>

      {open && (
        <Card className="mb-6 border-cyan-500/20 bg-slate-800/50">
          <CardHeader>
              <CardTitle className="text-lg">{editingId ? "编辑 Agent" : "新建 Agent"}</CardTitle>
            <CardDescription>配置 Agent 的角色、能力和行为</CardDescription>
          </CardHeader>
          <CardContent className="space-y-4">
            <div className="space-y-2">
              <label className="text-sm font-medium">名称</label>
              <Input placeholder="例如：客服助手" value={name} onChange={e => setName(e.target.value)} />
            </div>
            <div className="space-y-2">
              <label className="text-sm font-medium">描述</label>
              <Input placeholder="简要描述" value={desc} onChange={e => setDesc(e.target.value)} />
            </div>
            <div className="space-y-2">
              <label className="text-sm font-medium">系统提示词</label>
              <Textarea placeholder="定义 Agent 的行为规则..." value={sysPrompt} onChange={e => setSysPrompt(e.target.value)} rows={4} />
            </div>
            <div className="space-y-2">
              <label className="text-sm font-medium">模型来源</label>
              <select className="w-full bg-slate-700 border border-slate-600 text-white p-2 rounded-lg text-sm" value={providerSource} onChange={e => setProviderSource(e.target.value)}>
                <option value="personal">个人 API Key</option>
                <option value="platform">平台余额</option>
              </select>
            </div>
            {providerSource === "platform" && (
              <div className="space-y-2">
                <label className="text-sm font-medium">选择平台模型</label>
                <select className="w-full bg-slate-700 border border-slate-600 text-white p-2 rounded-lg text-sm" value={providerId} onChange={e => setProviderId(e.target.value)}>
                  <option value="">选择...</option>
                  {platforms.map((p: any) => <option key={p.id} value={p.id}>{p.name} ({p.model}) - ${p.price}/千token</option>)}
                </select>
              </div>
            )}
            <div className="space-y-2">
              <label className="text-sm font-medium">绑定工具</label>
              <p className="text-xs text-slate-500">系统内置</p>
              <div className="max-h-20 overflow-y-auto space-y-1">
                {builtinTools.map((t) => (
                  <label key={t.id} className="flex items-center gap-2 text-sm cursor-pointer">
                    <input type="checkbox" checked={selectedTools.includes(t.id)} onChange={e => { if (e.target.checked) setSelectedTools([...selectedTools, t.id]); else setSelectedTools(selectedTools.filter(id => id !== t.id)); }} />
                    {t.name}
                  </label>
                ))}
              </div>
              {allTools.length > 0 && (
                <>
                  <p className="text-xs text-slate-500 mt-2">自定义工具</p>
                  <div className="max-h-20 overflow-y-auto space-y-1">
                    {allTools.map((t: any) => (
                      <label key={t.id} className="flex items-center gap-2 text-sm cursor-pointer">
                        <input type="checkbox" checked={selectedTools.includes(t.id)} onChange={e => { if (e.target.checked) setSelectedTools([...selectedTools, t.id]); else setSelectedTools(selectedTools.filter(id => id !== t.id)); }} />
                        {t.name}
                      </label>
                    ))}
                  </div>
                </>
              )}
            </div>
            <div className="space-y-2">
              <label className="text-sm font-medium">绑定知识库</label>
              {allKbs.length > 0 ? (
                <div className="max-h-24 overflow-y-auto space-y-1">
                  {allKbs.map((k: any) => (
                    <label key={k.id} className="flex items-center gap-2 text-sm cursor-pointer">
                      <input type="checkbox" checked={selectedKbs.includes(k.id)} onChange={e => { if (e.target.checked) setSelectedKbs([...selectedKbs, k.id]); else setSelectedKbs(selectedKbs.filter(id => id !== k.id)); }} />
                      {k.name}
                    </label>
                  ))}
                </div>
              ) : <p className="text-xs text-slate-500">暂无知识库，先去「知识库」页创建</p>}
            </div>
            <div className="flex gap-2">
              <Button variant="outline" onClick={() => setOpen(false)}>取消</Button>
              <Button onClick={editingId ? saveEdit : create}>{editingId ? "保存" : "创建"}</Button>
            </div>
          </CardContent>
        </Card>
      )}

      <div className="space-y-3">
        {agents.length === 0 ? (
          <div className="text-center py-20 border border-dashed border-slate-700 rounded-xl">
            <Bot className="w-10 h-10 mx-auto mb-3 text-slate-600" />
            <h3 className="text-sm font-medium text-slate-400 mb-1">还没有 Agent</h3>
            <p className="text-xs text-slate-500">点击上方按钮创建第一个</p>
          </div>
        ) : (
          agents.map((a: any) => (
            <Card key={a.id} className="hover:border-slate-600/80 transition-all group">
              <CardHeader className="pb-3">
                <div className="flex items-start justify-between">
                  <div className="flex items-center gap-3">
                    <div className="w-10 h-10 rounded-lg bg-gradient-to-br from-cyan-500/20 to-blue-500/10 flex items-center justify-center">
                      <Bot className="w-5 h-5 text-cyan-400" />
                    </div>
                    <div>
                      <CardTitle className="text-base">{a.name}</CardTitle>
                      <CardDescription className="text-xs mt-0.5">{a.description || "暂无描述"}</CardDescription>
                    </div>
                  </div>
                  <div className="flex items-center gap-1 opacity-0 group-hover:opacity-100 transition">
                    {a.published_version && <Badge variant="success" className="text-[10px] h-5">v{a.published_version}</Badge>}
                    <Button size="sm" variant="ghost" onClick={() => startEdit(a)} className="h-7 w-7 p-0"><Pencil className="w-3.5 h-3.5" /></Button>
                    <Button size="sm" variant="ghost" onClick={() => publish(a.id)} className="h-7 w-7 p-0"><Rocket className="w-3.5 h-3.5" /></Button>
                    <Button size="sm" variant="ghost" onClick={() => del(a.id)} className="h-7 w-7 p-0 hover:text-red-400"><Trash2 className="w-3.5 h-3.5" /></Button>
                  </div>
                </div>
              </CardHeader>
              {a.system_sysPrompt && (
                <CardContent className="pt-0">
                  <p className="text-xs text-slate-500 line-clamp-2">{a.system_sysPrompt}</p>
                </CardContent>
              )}
            </Card>
          ))
        )}
      </div>
    </div>
  );
}
