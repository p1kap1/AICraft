"use client";
import { useEffect, useState } from "react";
import { Button } from "@/components/ui/button";
import { Card, CardHeader, CardTitle, CardDescription, CardContent } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Shield, Check, Plus, Trash2, Server } from "lucide-react";

const API = "/api";

export default function AdminPage() {
  const [tools, setTools] = useState<any[]>([]);
  const [rags, setRags] = useState<any[]>([]);
  const [platforms, setPlatforms] = useState<any[]>([]);
  const [catalog, setCatalog] = useState<any[]>([]);
  const [selectedModel, setSelectedModel] = useState("");
  const [pKey, setPKey] = useState("");
  const [pPrice, setPPrice] = useState("0.01");
  const token = typeof window !== "undefined" ? localStorage.getItem("token") : "";
  const auth = () => token ? { Authorization: "Bearer " + token } : {};

  const load = () => {
    fetch(API + "/admin/tools/pending", { headers: auth() }).then(r => r.json()).then(d => setTools(Array.isArray(d)?d:d.data||[]));
    fetch(API + "/admin/rag/pending", { headers: auth() }).then(r => r.json()).then(d => setRags(Array.isArray(d)?d:d.data||[]));
    fetch(API + "/admin/providers", { headers: auth() }).then(r => r.json()).then(setPlatforms);
    fetch(API + "/models/catalog", { headers: auth() }).then(r => r.json()).then(setCatalog);
  };
  useEffect(() => { load(); }, []);

  const approve = async (id: string) => { await fetch(API + "/admin/tools/" + id + "/approve", { method: "POST", headers: auth() }); load(); };
  const approveRag = async (id: string) => { await fetch(API + "/admin/rag/" + id + "/approve", { method: "POST", headers: auth() }); load(); };

  const addPlatform = async () => {
    const m = catalog.find((c: any) => c.model === selectedModel);
    if (!m || !pKey) return;
    await fetch(API + "/admin/providers?name=" + encodeURIComponent(m.name) + "&base_url=" + encodeURIComponent(m.base_url) + "&api_key=" + encodeURIComponent(pKey) + "&model=" + encodeURIComponent(m.model) + "&price=" + parseFloat(pPrice), { method: "POST", headers: auth() });
    setSelectedModel(""); setPKey(""); load();
  };
  const delPlatform = async (id: string) => { await fetch(API + "/admin/providers/" + id, { method: "DELETE", headers: auth() }); load(); };

  return (
    <div className="max-w-4xl mx-auto space-y-8">
      <div><h1 className="text-2xl font-bold tracking-tight">管理后台</h1><p className="text-sm text-slate-400 mt-1">审核工具、管理平台模型</p></div>

      <Card>
        <CardHeader><CardTitle className="flex items-center gap-2"><Shield className="w-4 h-4 text-cyan-400" /> 工具审核</CardTitle></CardHeader>
        <CardContent>
          {tools.length === 0 ? <p className="text-sm text-slate-500 py-4">暂无待审核</p> : tools.map((i: any) => (
            <div key={i.id} className="flex items-center justify-between py-2 border-b border-slate-700/50"><span>{i.name}</span><Button size="sm" variant="outline" onClick={() => approve(i.id)}><Check className="w-3 h-3 mr-1"/>通过</Button></div>
          ))}
        </CardContent>
      </Card>

      <Card>
        <CardHeader><CardTitle className="flex items-center gap-2"><Server className="w-4 h-4 text-cyan-400" /> 平台模型管理</CardTitle><CardDescription>只需选择模型并填入 API Key</CardDescription></CardHeader>
        <CardContent className="space-y-3">
          <div className="grid grid-cols-2 gap-3">
            <select className="bg-slate-700 border border-slate-600 text-white p-2 rounded-lg text-sm" value={selectedModel} onChange={e => setSelectedModel(e.target.value)}>
              <option value="">选择模型...</option>
              {catalog.map((m: any) => <option key={m.model} value={m.model}>{m.name} ({m.model})</option>)}
            </select>
            <input className="bg-slate-700 border border-slate-600 text-white p-2 rounded text-sm" placeholder="价格/千token" value={pPrice} onChange={e => setPPrice(e.target.value)} />
          </div>
          {selectedModel && (
            <div className="text-xs text-slate-400 bg-slate-700/50 p-2 rounded">API 地址: {catalog.find((m:any)=>m.model===selectedModel)?.base_url}</div>
          )}
          <input className="w-full bg-slate-700 border border-slate-600 text-white p-2 rounded text-sm" placeholder="API Key" type="password" value={pKey} onChange={e => setPKey(e.target.value)} />
          <Button size="sm" onClick={addPlatform} disabled={!selectedModel||!pKey}><Plus className="w-3 h-3 mr-1"/>添加</Button>
          <div className="mt-4 space-y-2">
            {platforms.map((p:any) => (
              <div key={p.id} className="flex items-center justify-between py-2 border-b border-slate-700/50">
                <div><span className="font-medium">{p.name}</span> <Badge variant="secondary" className="ml-2 text-[10px]">{p.model}</Badge></div>
                <Button size="sm" variant="ghost" onClick={() => delPlatform(p.id)}><Trash2 className="w-3 h-3 text-red-400"/></Button>
              </div>
            ))}
          </div>
        </CardContent>
      </Card>
    </div>
  );
}
