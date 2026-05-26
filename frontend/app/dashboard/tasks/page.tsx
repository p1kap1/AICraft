"use client";
import { useEffect, useState } from "react";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Card, CardHeader, CardTitle, CardContent } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Clock, Play, Trash2, Plus } from "lucide-react";
const API = "/api";

export default function TasksPage() {
  const [tasks, setTasks] = useState<any[]>([]);
  const [name, setName] = useState("");
  const [cron, setCron] = useState("0 9 * * *");
  const [prompt, setPrompt] = useState("");
  const [agents, setAgents] = useState<any[]>([]);
  const [agentId, setAgentId] = useState("");
  const token = typeof window !== "undefined" ? localStorage.getItem("token") : "";
  const auth = (ct?:string) => token ? {"Content-Type":ct||"application/json", Authorization:"Bearer "+token} : {};

  const load = () => {
    fetch(API+"/agents/user",{headers:auth()}).then(r=>r.json()).then(setAgents).catch(()=>{});
    fetch(API+"/tasks/user",{headers:auth()}).then(r=>r.json()).then(setTasks).catch(()=>{});
  };
  useEffect(()=>{load();},[]);

  const add = async () => {
    if(!name)return;
    await fetch(API+"/tasks?name="+encodeURIComponent(name)+"&cron_expr="+encodeURIComponent(cron)+"&prompt="+encodeURIComponent(prompt)+"&agent_id="+agentId,{method:"POST",headers:auth()});
    setName("");setPrompt("");load();
  };
  const run = async (id:string) => {await fetch(API+"/tasks/"+id+"/run",{method:"POST",headers:auth()});load();};
  const del = async (id:string) => {await fetch(API+"/tasks/"+id,{method:"DELETE",headers:auth()});load();};

  return (
    <div className="max-w-4xl mx-auto space-y-8">
      <div className="flex items-center justify-between"><div><h1 className="text-2xl font-bold tracking-tight">定时任务</h1><p className="text-sm text-slate-400 mt-1">Agent 定时自动执行</p></div></div>
      <Card><CardHeader><CardTitle>新建任务</CardTitle></CardHeader>
        <CardContent className="space-y-3">
          <div className="grid grid-cols-2 gap-3">
            <Input placeholder="任务名称" value={name} onChange={e=>setName(e.target.value)}/>
            <Input placeholder="Cron (0 9 * * *)" value={cron} onChange={e=>setCron(e.target.value)}/>
          </div>
          <Input placeholder="执行指令" value={prompt} onChange={e=>setPrompt(e.target.value)}/>
          <select className="w-full bg-slate-700 border border-slate-600 text-white p-2 rounded-lg text-sm" value={agentId} onChange={e=>setAgentId(e.target.value)}>
            <option value="">选择 Agent（可选）</option>
            {agents.map((a:any)=><option key={a.id} value={a.id}>{a.name}</option>)}
          </select>
          <Button onClick={add} size="sm"><Plus className="w-3 h-3 mr-1"/>创建</Button>
        </CardContent>
      </Card>
      <div className="space-y-3">
        {tasks.map((t:any)=>(
          <Card key={t.id}><CardHeader className="flex flex-row items-center justify-between pb-3">
            <div className="flex items-center gap-3"><Clock className="w-5 h-5 text-cyan-400"/><CardTitle className="text-base">{t.name}</CardTitle><Badge>{t.cron}</Badge></div>
            <div className="flex gap-2">
              <Button size="sm" variant="outline" onClick={()=>run(t.id)}><Play className="w-3 h-3 mr-1"/>执行</Button>
              <Button size="sm" variant="ghost" onClick={()=>del(t.id)}><Trash2 className="w-3 h-3 text-red-400"/></Button>
            </div>
          </CardHeader></Card>
        ))}
        {tasks.length===0 && <p className="text-center py-10 text-slate-500">暂无定时任务</p>}
      </div>
    </div>
  );
}
