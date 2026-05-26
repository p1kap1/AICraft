"use client";
import { useEffect, useState } from "react";
import { Button } from "@/components/ui/button";
import { Card, CardHeader, CardTitle, CardDescription, CardContent } from "@/components/ui/card";
import { ShoppingBag, Upload, Download } from "lucide-react";
const API = "/api";

export default function MarketPage() {
  const [items, setItems] = useState<any[]>([]);
  const [myTools, setMyTools] = useState<any[]>([]);
  const [publishId, setPublishId] = useState("");
  const token = typeof window !== "undefined" ? localStorage.getItem("token") : "";
  const auth = () => ({ Authorization: "Bearer "+token });

  const load = () => {
    fetch(API + "/market/browse", { headers: auth() }).then(r=>r.json()).then(d=>setItems(Array.isArray(d)?d:d.data||[]));
    fetch(API + "/tools/user", { headers: auth() }).then(r=>r.json()).then(setMyTools);
  };
  useEffect(()=>{load();},[]);

  const publish = async () => { if(!publishId)return; await fetch(API+"/market/publish?tool_id="+publishId,{method:"POST",headers:auth()}); setPublishId(""); load(); };
  const install = async (id:string) => { await fetch(API+"/market/install/"+id,{method:"POST",headers:auth()}); load(); };

  return (
    <div className="max-w-4xl mx-auto space-y-8">
      <div><h1 className="text-2xl font-bold tracking-tight">工具市场</h1><p className="text-sm text-slate-400 mt-1">发布和发现 Agent 工具</p></div>
      <Card>
        <CardHeader><CardTitle className="text-lg">发布我的工具</CardTitle><CardDescription>将本地工具分享到市场</CardDescription></CardHeader>
        <CardContent className="flex gap-2">
          <select className="bg-slate-700 border border-slate-600 text-white p-2 rounded-lg flex-1 text-sm" value={publishId} onChange={e=>setPublishId(e.target.value)}>
            <option value="">选择工具...</option>
            {myTools.map(t=><option key={t.id} value={t.id}>{t.name}</option>)}
          </select>
          <Button onClick={publish} disabled={!publishId} className="gap-1"><Upload className="w-4 h-4"/> 发布</Button>
        </CardContent>
      </Card>
      <div className="grid gap-4 md:grid-cols-2">
        {items.length===0 ? (
          <div className="col-span-2 text-center py-16 border border-dashed border-slate-700 rounded-xl">
            <ShoppingBag className="w-10 h-10 mx-auto mb-3 text-slate-600"/>
            <p className="text-sm text-slate-400">暂无工具</p>
          </div>
        ) : items.map((i:any)=>(
          <Card key={i.id}>
            <CardHeader><CardTitle className="text-base">{i.name}</CardTitle><CardDescription className="text-xs">{i.description||""}</CardDescription></CardHeader>
            <CardContent className="flex justify-between items-center">
              <span className="text-xs text-slate-500">下载 {i.downloads||0} 次</span>
              <Button size="sm" variant="outline" onClick={()=>install(i.id)} className="gap-1"><Download className="w-3 h-3"/> 安装</Button>
            </CardContent>
          </Card>
        ))}
      </div>
    </div>
  );
}
