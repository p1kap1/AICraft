"use client";
import { useEffect, useState } from "react";
import { Button } from "@/components/ui/button";
import { Card, CardHeader, CardTitle, CardDescription, CardContent } from "@/components/ui/card";
import { Key, Trash2 } from "lucide-react";

const API = "/api";

export default function ProvidersPage() {
  const [providers, setProviders] = useState<any[]>([]);
  const [catalog, setCatalog] = useState<any[]>([]);
  const [selectedModel, setSelectedModel] = useState("");
  const [key, setKey] = useState("");
  const [showForm, setShowForm] = useState(false);
  const token = typeof window !== "undefined" ? localStorage.getItem("token") : "";
  const auth = () => ({ Authorization: "Bearer " + token });

  const load = () => {
    fetch(API + "/providers/user", { headers: auth() }).then(r => r.json()).then(setProviders);
    fetch(API + "/models/catalog", { headers: auth() }).then(r => r.json()).then(setCatalog);
  };
  useEffect(() => { load(); }, []);

  const add = async () => {
    const m = catalog.find((c: any) => c.model === selectedModel);
    if (!m || !key) return;
    await fetch(API + "/providers?name=" + encodeURIComponent(m.name) + "&base_url=" + encodeURIComponent(m.base_url) + "&api_key=" + encodeURIComponent(key) + "&provider_type=openai", { method: "POST", headers: auth() });
    setSelectedModel(""); setKey(""); setShowForm(false); load();
  };

  const del = async (id: string) => { await fetch(API + "/providers/" + id, { method: "DELETE", headers: auth() }); load(); };

  return (
    <div className="max-w-3xl mx-auto space-y-8">
      <div className="flex items-center justify-between">
        <div><h1 className="text-2xl font-bold tracking-tight">模型服务商</h1><p className="text-sm text-slate-400 mt-1">配置你的 API Key</p></div>
        <Button onClick={() => setShowForm(!showForm)}>{showForm ? "取消" : "+ 添加"}</Button>
      </div>

      {showForm && (
        <Card className="border-cyan-500/20 bg-slate-800/50">
          <CardHeader><CardTitle className="text-lg">添加服务商</CardTitle><CardDescription>只需选择模型 + 填入 API Key</CardDescription></CardHeader>
          <CardContent className="space-y-3">
            <select className="w-full bg-slate-700 border border-slate-600 text-white p-2 rounded-lg text-sm" value={selectedModel} onChange={e => setSelectedModel(e.target.value)}>
              <option value="">选择模型...</option>
              {catalog.map((m: any) => <option key={m.model} value={m.model}>{m.name} ({m.model})</option>)}
            </select>
            {selectedModel && <div className="text-xs text-slate-400 bg-slate-700/50 p-2 rounded">{catalog.find((m:any)=>m.model===selectedModel)?.base_url}</div>}
            <input className="w-full bg-slate-700 border border-slate-600 text-white p-2 rounded-lg text-sm" placeholder="API Key" type="password" value={key} onChange={e => setKey(e.target.value)} />
            <Button onClick={add} disabled={!selectedModel||!key}>保存</Button>
          </CardContent>
        </Card>
      )}

      <div className="space-y-3">
        {providers.length === 0 ? (
          <div className="text-center py-16 border border-dashed border-slate-700 rounded-xl">
            <Key className="w-10 h-10 mx-auto mb-3 text-slate-600"/><p className="text-sm text-slate-400">暂无服务商</p>
          </div>
        ) : providers.map((p: any) => (
          <Card key={p.id} className="group">
            <CardHeader className="flex flex-row items-center justify-between pb-3">
              <div className="flex items-center gap-3">
                <Key className="w-5 h-5 text-cyan-400"/><div><CardTitle className="text-base">{p.name}</CardTitle></div>
              </div>
              <Button variant="ghost" size="icon" onClick={() => del(p.id)} className="opacity-0 group-hover:opacity-100"><Trash2 className="w-4 h-4 text-red-400"/></Button>
            </CardHeader>
          </Card>
        ))}
      </div>
    </div>
  );
}
