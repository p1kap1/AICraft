"use client";
import { useEffect, useState } from "react";
import { Card, CardHeader, CardTitle, CardContent } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Brain, Trash2 } from "lucide-react";
const API = "/api";

export default function MemoryPage() {
  const [memories, setMemories] = useState<any[]>([]);
  const token = typeof window !== "undefined" ? localStorage.getItem("token") : "";
  useEffect(() => {
    const t = localStorage.getItem("token"); if(!t)return;
    fetch(API+"/chat/sessions",{headers:{Authorization:"Bearer "+t}}).then(r=>r.json()).then(setMemories).catch(()=>{});
  }, []);

  return (
    <div className="max-w-4xl mx-auto space-y-8">
      <div><h1 className="text-2xl font-bold tracking-tight">长期记忆</h1><p className="text-sm text-slate-400 mt-1">Agent 自动提取的用户信息</p></div>
      <div className="space-y-3">
        {memories.length===0 ? (
          <div className="text-center py-16 border border-dashed border-slate-700 rounded-xl">
            <Brain className="w-10 h-10 mx-auto mb-3 text-slate-600"/>
            <p className="text-sm text-slate-400">暂无记忆数据</p><p className="text-xs text-slate-500 mt-1">Agent 对话后会自动提取</p>
          </div>
        ) : memories.map((m:any,i:number)=>(
          <Card key={i}><CardHeader className="flex flex-row items-center justify-between pb-3">
            <div className="flex items-center gap-3"><Brain className="w-5 h-5 text-purple-400"/><CardTitle className="text-sm">{m.title||"会话 "+i}</CardTitle></div>
            <Badge variant="secondary">{m.agent_id?"Agent":"直接对话"}</Badge>
          </CardHeader></Card>
        ))}
      </div>
    </div>
  );
}
