"use client";
import { useEffect, useState } from "react";
import { Button } from "@/components/ui/button";
import { Card, CardHeader, CardTitle, CardContent } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { RotateCcw, History } from "lucide-react";
import { useSearchParams } from "next/navigation";
const API = "/api";

export default function VersionsPage() {
  const [agents, setAgents] = useState<any[]>([]);
  const [selectedAgent, setSelectedAgent] = useState("");
  const [versions, setVersions] = useState<any[]>([]);
  const token = typeof window !== "undefined" ? localStorage.getItem("token") : "";
  const auth = () => token ? { Authorization: "Bearer "+token } : {};

  useEffect(() => {
    const t = localStorage.getItem("token"); if(!t)return;
    fetch(API+"/agents/user",{headers:{Authorization:"Bearer "+t}}).then(r=>r.json()).then(setAgents).catch(()=>{});
  }, []);

  const loadVersions = (id: string) => {
    setSelectedAgent(id);
    fetch(API+"/agents/"+id+"/versions",{headers:auth()}).then(r=>r.json()).then(setVersions).catch(()=>{});
  };

  const rollback = async (agentId: string, versionId: string) => {
    await fetch(API+"/agents/"+agentId+"/versions/"+versionId+"/rollback",{method:"POST",headers:auth()});
    loadVersions(agentId);
  };

  return (
    <div className="max-w-4xl mx-auto space-y-8">
      <div><h1 className="text-2xl font-bold tracking-tight">版本管理</h1><p className="text-sm text-slate-400 mt-1">查看和回滚 Agent 版本</p></div>
      <select className="w-full bg-slate-800 border border-slate-700 text-white p-2 rounded-lg" value={selectedAgent} onChange={e=>loadVersions(e.target.value)}>
        <option value="">选择 Agent...</option>
        {agents.map((a:any)=><option key={a.id} value={a.id}>{a.name}</option>)}
      </select>
      <div className="space-y-3">
        {versions.map((v:any)=>(
          <Card key={v.id}>
            <CardHeader className="flex flex-row items-center justify-between pb-3">
              <div className="flex items-center gap-3">
                <History className="w-5 h-5 text-cyan-400"/>
                <div><CardTitle className="text-base">v{v.version_number}</CardTitle><p className="text-xs text-slate-400">{v.change_log||"无更新日志"}</p></div>
              </div>
              <Badge variant={v.publish_status===2?"success":"secondary"}>{v.publish_status===2?"已发布":"私有"}</Badge>
            </CardHeader>
            <CardContent className="flex justify-end"><Button size="sm" variant="outline" onClick={()=>rollback(v.agent_id,v.id)}><RotateCcw className="w-3 h-3 mr-1"/>回滚</Button></CardContent>
          </Card>
        ))}
      </div>
    </div>
  );
}
