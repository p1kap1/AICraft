"use client";
import { useEffect, useState } from "react";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Card, CardHeader, CardTitle, CardDescription, CardContent } from "@/components/ui/card";
import { BookOpen, Plus, Upload, Trash2, Search } from "lucide-react";

const API = "/api";

export default function KnowledgePage() {
  const [kbs, setKbs] = useState<any[]>([]);
  const [name, setName] = useState("");
  const [desc, setDesc] = useState("");
  const [showForm, setShowForm] = useState(false);
  const [expandedId, setExpandedId] = useState("");
  const [chunks, setChunks] = useState<any[]>([]);
  const token = typeof window !== "undefined" ? localStorage.getItem("token") : "";
  const auth = (ct?: string) => ({ "Content-Type": ct||"application/json", Authorization: "Bearer "+token });

  const load = () => fetch(API + "/knowledge/user", { headers: auth() }).then(r => r.json()).then(setKbs);
  useEffect(() => { load(); }, []);

  const add = async () => { if(!name)return; await fetch(API + "/knowledge?name="+encodeURIComponent(name)+"&description="+encodeURIComponent(desc), { method:"POST", headers:auth() }); setName(""); setDesc(""); setShowForm(false); load(); };
  const del = async (id: string) => { await fetch(API + "/knowledge/"+id, { method:"DELETE", headers:auth() }); load(); };
  const upload = async (kbId: string) => {
    const input = document.createElement("input"); input.type="file";
    input.onchange = async (e: any) => {
      const f = e.target.files?.[0]; if(!f)return;
      const form = new FormData(); form.append("file", f);
      await fetch(API + "/knowledge/"+kbId+"/upload", { method:"POST", headers:{Authorization:"Bearer "+token}, body:form });
      load();
    }; input.click();
  };

  const toggleChunks = async (id: string) => {
    if (expandedId === id) { setExpandedId(""); return; }
    setExpandedId(id);
    const r = await fetch(API + "/knowledge/" + id + "/chunks", { headers: auth() });
    setChunks(await r.json());
  };

  return (
    <div className="max-w-4xl mx-auto space-y-8">
      <div className="flex items-center justify-between">
        <div><h1 className="text-2xl font-bold tracking-tight">知识库</h1><p className="text-sm text-slate-400 mt-1">上传文档构建 RAG 检索，绑定 Agent 后对话自动调用</p></div>
        <Button onClick={() => setShowForm(!showForm)} className="gap-2"><Plus className="w-4 h-4" /> {showForm ? "取消" : "创建"}</Button>
      </div>

      {showForm && (
        <Card className="border-cyan-500/20 bg-slate-800/50">
          <CardHeader><CardTitle className="text-lg">创建知识库</CardTitle></CardHeader>
          <CardContent className="space-y-3">
            <Input placeholder="知识库名称" value={name} onChange={e=>setName(e.target.value)} />
            <Input placeholder="描述（可选）" value={desc} onChange={e=>setDesc(e.target.value)} />
            <Button onClick={add}>保存</Button>
          </CardContent>
        </Card>
      )}

      <div className="space-y-3">
        {kbs.length===0 ? (
          <div className="text-center py-16 border border-dashed border-slate-700 rounded-xl">
            <BookOpen className="w-10 h-10 mx-auto mb-3 text-slate-600"/>
            <p className="text-sm text-slate-400 mb-1">暂无知识库</p>
            <p className="text-xs text-slate-500">创建知识库 → 上传文档 → 绑定到 Agent → 对话自动检索</p>
          </div>
        ) : kbs.map((k:any) => (
          <Card key={k.id} className="group">
            <CardHeader className="flex flex-row items-center justify-between pb-3">
              <div className="flex items-center gap-3">
                <div className="w-10 h-10 rounded-lg bg-cyan-500/10 flex items-center justify-center"><BookOpen className="w-5 h-5 text-cyan-400"/></div>
                <div>
                  <CardTitle className="text-base">{k.name}</CardTitle>
                  <CardDescription className="text-xs">{k.description||"暂无描述"}</CardDescription>
                </div>
              </div>
              <div className="flex items-center gap-1 opacity-0 group-hover:opacity-100 transition">
                <Button size="sm" variant="outline" onClick={()=>upload(k.id)} className="h-7 text-xs"><Upload className="w-3 h-3 mr-1"/>上传</Button>
                <Button size="sm" variant="ghost" onClick={()=>del(k.id)} className="h-7 w-7 p-0"><Trash2 className="w-4 h-4 text-red-400"/></Button>
              </div>
            </CardHeader>
            <CardContent className="pt-0">
              <p className="text-xs text-slate-500">绑定到 Agent 后，对话时会自动检索知识库内容，Agent 基于检索结果回答</p>
              <button onClick={() => toggleChunks(k.id)} className="text-xs text-cyan-400 mt-2 hover:underline">
                {expandedId === k.id ? "收起内容" : "查看内容"}
              </button>
              {expandedId === k.id && chunks.length > 0 && (
                <div className="mt-3 space-y-2 max-h-48 overflow-y-auto">
                  {chunks.map((c: any, i: number) => (
                    <div key={i} className="bg-slate-700/50 p-2 rounded text-xs text-slate-400">{c.content}</div>
                  ))}
                </div>
              )}
            </CardContent>
          </Card>
        ))}
      </div>
    </div>
  );
}
