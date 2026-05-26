"use client";
import { Card, CardHeader, CardTitle, CardDescription, CardContent } from "@/components/ui/card";
import { Code, ExternalLink } from "lucide-react";

export default function ApiDocsPage() {
  return (
    <div className="max-w-4xl mx-auto space-y-8">
      <div><h1 className="text-2xl font-bold tracking-tight">API 文档</h1><p className="text-sm text-slate-400 mt-1">Agent OpenAPI 和 Widget 嵌入说明</p></div>
      <Card><CardHeader><CardTitle className="flex items-center gap-2"><Code className="w-4 h-4" />调用 Agent API</CardTitle><CardDescription>将 Agent 发布为 REST API，外部系统可直接调用</CardDescription></CardHeader>
        <CardContent className="space-y-4">
          <div className="bg-slate-700 rounded-lg p-4 text-sm font-mono space-y-2">
            <div className="text-cyan-400"># 获取 Agent 信息</div>
            <div>GET /api/v1/agent/{"{agent_id}"}/info</div>
            <div className="text-cyan-400 mt-3"># 调用 Agent</div>
            <div>POST /api/v1/agent/{"{agent_id}"}/chat</div>
            <div>Content-Type: application/json</div>
            <div className="text-slate-400">{"{ \"message\": \"你好\" }"}</div>
          </div>
          <a href="http://localhost:8000/api/docs" target="_blank" className="text-cyan-400 text-sm flex items-center gap-1 hover:underline">
            <ExternalLink className="w-3 h-3"/> Swagger API 文档
          </a>
        </CardContent>
      </Card>
      <Card><CardHeader><CardTitle>Widget 嵌入</CardTitle><CardDescription>将 Agent 嵌入到网站</CardDescription></CardHeader>
        <CardContent>
          <div className="bg-slate-700 rounded-lg p-4 text-sm font-mono text-slate-400">
            {"<iframe src=\"http://localhost:8000/widget/{agent_id}\"></iframe>"}
          </div>
        </CardContent>
      </Card>
    </div>
  );
}
