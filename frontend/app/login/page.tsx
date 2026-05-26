"use client";
import { useState } from "react";
import { useRouter } from "next/navigation";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Card, CardHeader, CardTitle, CardDescription, CardContent } from "@/components/ui/card";

export default function Login() {
  const [account, setAccount] = useState("");
  const [pass, setPass] = useState("");
  const [msg, setMsg] = useState("");
  const router = useRouter();

  const login = async () => {
    const r = await fetch("http://localhost:8000/api/login", {
      method: "POST", headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ account, password: pass }),
    });
    const d = await r.json();
    if (d.token) { localStorage.setItem("token", d.token); localStorage.setItem("user", JSON.stringify(d)); router.push("/dashboard/chat"); }
    else setMsg(d.detail || "登录失败");
  };

  return (
    <div className="min-h-screen flex items-center justify-center bg-gradient-to-br from-slate-900 to-slate-800">
      <Card className="w-96 border-slate-700">
        <CardHeader className="text-center">
          <CardTitle className="text-2xl text-cyan-400">AICraft</CardTitle>
          <CardDescription>AI Agent 构建平台</CardDescription>
        </CardHeader>
        <CardContent className="space-y-4">
          <Input placeholder="邮箱或手机号" value={account} onChange={(e) => setAccount(e.target.value)} />
          <Input type="password" placeholder="密码" value={pass} onChange={(e) => setPass(e.target.value)} />
          <Button className="w-full" onClick={login}>登录</Button>
          {msg && <p className="text-red-400 text-sm text-center">{msg}</p>}
          <p className="text-center text-slate-500 text-sm">没有账号？<a href="/register" className="text-cyan-400 hover:underline">注册</a></p>
        </CardContent>
      </Card>
    </div>
  );
}
