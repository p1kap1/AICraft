"use client";
import { Card, CardHeader, CardTitle, CardContent } from "@/components/ui/card";
import { Code, ExternalLink } from "lucide-react";

export default function WidgetPage() {
  return (
    <div className="max-w-3xl mx-auto space-y-8">
      <div><h1 className="text-2xl font-bold tracking-tight">嵌入组件</h1><p className="text-sm text-slate-400 mt-1">将 Agent 嵌入到你的网站</p></div>
      <Card><CardHeader><CardTitle className="flex items-center gap-2"><Code className="w-4 h-4" />复制这段代码</CardTitle></CardHeader>
        <CardContent>
          <div className="bg-slate-700 rounded-lg p-4 text-sm font-mono text-slate-400">
            {'<iframe src="http://localhost:8000/widget/{agent_id}" width="400" height="600" style="border:none;border-radius:12px;position:fixed;bottom:20px;right:20px;z-index:9999"></iframe>'}
          </div>
          <p className="text-xs text-slate-500 mt-3">Agent 发布后，在 Discover 复制 Agent ID，替换 {'{agent_id}'}，贴到你网站的 HTML 里即可</p>
        </CardContent>
      </Card>
    </div>
  );
}
