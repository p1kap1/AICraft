"use client";
import { useEffect, useState } from "react";
import { Button } from "@/components/ui/button";
import { Card, CardHeader, CardTitle, CardContent } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { useRouter } from "next/navigation";
import { Bot, ArrowRight } from "lucide-react";

const API = "/api";

export default function DiscoverPage() {
  const [agents, setAgents] = useState<any[]>([]);
  const router = useRouter();
  const token = typeof window !== "undefined" ? localStorage.getItem("token") : "";

  useEffect(() => {
    if (!token) return;
    fetch(API + "/agents/published", { headers: { Authorization: "Bearer " + token } })
      .then(r => r.json()).then(d => setAgents(Array.isArray(d) ? d : d.data || []));
  }, []);

  return (
    <div className="max-w-4xl">
      <h2 className="text-2xl font-bold mb-6">发现 Agent</h2>
      <p className="text-sm text-slate-400 mb-6">浏览社区发布的 Agent，使用你自己的 API Key 对话</p>

      <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-3">
        {agents.map((a: any) => (
          <Card key={a.id} className="hover:border-cyan-500/30 transition cursor-pointer" onClick={() => router.push("/dashboard/chat?agent=" + a.agent_id)}>
            <CardHeader>
              <CardTitle className="flex items-center gap-2"><Bot className="w-4 h-4 text-cyan-400" /> {a.name}</CardTitle>
              <div className="text-xs text-slate-400">版本: {a.version_number || "1.0.0"}</div>
            </CardHeader>
            <CardContent>
              <p className="text-xs text-slate-400 line-clamp-3 mb-3">{(a.system_prompt || "暂无系统提示词").slice(0, 150)}</p>
              <div className="flex gap-1 mb-3">
                {a.tool_ids && a.tool_ids.length > 0 && <Badge variant="default" className="text-[10px]">🔧 {a.tool_ids.length} 工具</Badge>}
                {a.knowledge_base_ids && a.knowledge_base_ids.length > 0 && <Badge variant="secondary" className="text-[10px]">📚 知识库</Badge>}
              </div>
              <div className="flex justify-end">
                <Button size="sm" variant="ghost"><ArrowRight className="w-4 h-4" /></Button>
              </div>
            </CardContent>
          </Card>
        ))}
        {agents.length === 0 && <p className="text-slate-500 col-span-full text-center py-16">暂无可发现的 Agent，快去 Studio 创建并发布</p>}
      </div>
    </div>
  );
}
