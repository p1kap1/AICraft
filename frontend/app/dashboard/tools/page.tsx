"use client";
import { useEffect, useState } from "react";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Card, CardHeader, CardTitle, CardDescription, CardContent } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Wrench, Plus, Trash2, Globe, Calculator, Clock, Search } from "lucide-react";

const API = "/api";
const toolIcons: any = { search: Search, calculator: Calculator, time: Clock, function: Wrench, api: Globe };

export default function ToolsPage() {
  const [tools, setTools] = useState<any[]>([]);
  const [name, setName] = useState("");
  const [desc, setDesc] = useState("");
  const [toolType, setToolType] = useState("function");
  const [apiUrl, setApiUrl] = useState("");
  const [showForm, setShowForm] = useState(false);
  const token = typeof window !== "undefined" ? localStorage.getItem("token") : "";
  const auth = () => token ? { Authorization: "Bearer " + token } : {};

  const load = () => fetch(API + "/tools/user", { headers: auth() }).then(r => r.json()).then(setTools);
  useEffect(() => { load(); }, []);

  const add = async () => {
    if (!name) return;
    await fetch(API + "/tools?name=" + encodeURIComponent(name) + "&description=" + encodeURIComponent(desc) + "&tool_type=api", { method: "POST", headers: auth() });
    setName(""); setDesc(""); setApiUrl(""); setShowForm(false); load();
  };
  const del = async (id: string) => { await fetch(API + "/tools/" + id, { method: "DELETE", headers: auth() }); load(); };

  return (
    <div className="max-w-4xl mx-auto space-y-8">
      <div className="flex items-center justify-between">
        <div><h1 className="text-2xl font-bold tracking-tight">工具管理</h1><p className="text-sm text-slate-400 mt-1">Agent 可调用的工具，创建后绑定到 Agent 即可在对话中自动调用</p></div>
        <Button onClick={() => setShowForm(!showForm)} className="gap-2"><Plus className="w-4 h-4" /> {showForm ? "取消" : "添加"}</Button>
      </div>

      {showForm && (
        <Card className="border-cyan-500/20 bg-slate-800/50">
          <CardHeader><CardTitle className="text-lg">添加工具</CardTitle></CardHeader>
          <CardContent className="space-y-3">
            <Input placeholder="工具名称" value={name} onChange={e => setName(e.target.value)} />
            <Input placeholder="描述（告诉 Agent 什么时候调用这个工具）" value={desc} onChange={e => setDesc(e.target.value)} />
            <Input placeholder="API 地址 (支持 {参数} 替换，如 https://api.weather.com?city={city})" value={apiUrl} onChange={e => setApiUrl(e.target.value)} />
            <p className="text-xs text-slate-500">Agent 调用时自动发 HTTP 请求，URL 中的 {'{参数}'} 会替换为实际值</p>
            <Button onClick={add}>保存</Button>
          </CardContent>
        </Card>
      )}

      {/* 内置工具 */}
      <div>
        <h3 className="text-sm font-medium text-slate-400 mb-3">系统内置工具（始终可用）</h3>
        <div className="grid gap-3 md:grid-cols-3">
          {[["get_time", "获取当前日期时间", Clock], ["calculator", "计算数学表达式", Calculator], ["search", "搜索互联网信息", Search]].map(([name, desc, Icon]) => (
            <Card key={name} className="border-slate-700/50">
              <CardContent className="p-4 flex items-center gap-3">
                <div className="w-8 h-8 rounded-lg bg-cyan-500/10 flex items-center justify-center"><Icon className="w-4 h-4 text-cyan-400" /></div>
                <div><div className="font-medium text-sm">{name}</div><div className="text-xs text-slate-400">{desc}</div></div>
              </CardContent>
            </Card>
          ))}
        </div>
      </div>

      {/* 自定义工具 */}
      <div className="space-y-3">
        <h3 className="text-sm font-medium text-slate-400">自定义工具</h3>
        {tools.length === 0 ? (
          <div className="text-center py-12 border border-dashed border-slate-700 rounded-xl">
            <Wrench className="w-8 h-8 mx-auto mb-2 text-slate-600" /><p className="text-sm text-slate-400">暂无自定义工具</p>
          </div>
        ) : tools.map((t: any) => {
          const Icon = toolIcons[t.tool_type] || Wrench;
          return (
            <Card key={t.id} className="group">
              <CardHeader className="flex flex-row items-center justify-between pb-3">
                <div className="flex items-center gap-3">
                  <div className="w-10 h-10 rounded-lg bg-cyan-500/10 flex items-center justify-center"><Icon className="w-5 h-5 text-cyan-400" /></div>
                  <div><CardTitle className="text-base">{t.name}</CardTitle><CardDescription className="text-xs">{t.description || ""}</CardDescription></div>
                </div>
                <div className="flex items-center gap-2">
                  <Badge className="text-[10px]">{t.tool_type}</Badge>
                  <Button variant="ghost" size="icon" onClick={() => del(t.id)} className="opacity-0 group-hover:opacity-100"><Trash2 className="w-4 h-4 text-red-400" /></Button>
                </div>
              </CardHeader>
            </Card>
          );
        })}
      </div>
    </div>
  );
}
