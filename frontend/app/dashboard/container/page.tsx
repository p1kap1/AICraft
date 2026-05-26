"use client";
import { useEffect, useState } from "react";
import { Button } from "@/components/ui/button";
import { Card, CardHeader, CardTitle, CardContent } from "@/components/ui/card";
import { Container, Play } from "lucide-react";
const API = "/api";

export default function ContainerPage() {
  const [containers, setContainers] = useState<any[]>([]);
  const token = typeof window !== "undefined" ? localStorage.getItem("token") : "";
  const auth = () => token ? {Authorization:"Bearer "+token} : {};

  const load = () => fetch(API+"/container/status",{headers:auth()}).then(r=>r.json()).then(d=>setContainers(d.containers||[]));
  useEffect(()=>{load();},[]);

  return (
    <div className="max-w-4xl mx-auto space-y-8">
      <div><h1 className="text-2xl font-bold tracking-tight">容器管理</h1><p className="text-sm text-slate-400 mt-1">Docker 工具容器状态</p></div>
      <Card><CardHeader><CardTitle className="flex items-center gap-2"><Container className="w-4 h-4"/>运行中容器</CardTitle></CardHeader>
        <CardContent>
          {containers.length===0 ? <p className="text-sm text-slate-500 py-4">暂无容器</p> :
            containers.map((c:any,i:number)=>(
              <div key={i} className="flex justify-between py-2 border-b border-slate-700/50"><span className="font-mono text-sm">{c.id}</span><span className="text-xs text-slate-400">{c.image} {c.status}</span></div>
            ))
          }
        </CardContent>
      </Card>
    </div>
  );
}
