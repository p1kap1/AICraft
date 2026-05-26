"use client";
import { useState } from "react";
import { useRouter } from "next/navigation";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Card, CardHeader, CardTitle, CardContent } from "@/components/ui/card";

export default function Register() {
  const [email, setEmail] = useState("");
  const [pass, setPass] = useState("");
  const [msg, setMsg] = useState("");
  const router = useRouter();

  const register = async () => {
    const r = await fetch("http://localhost:8000/api/register", {
      method: "POST", headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ email, password: pass, nickname: "用户" }),
    });
    const d = await r.json();
    if (d.code === 200) router.push("/login");
    else setMsg(d.message || "注册失败");
  };

  return (
    <div className="min-h-screen flex items-center justify-center bg-gradient-to-br from-slate-900 to-slate-800">
      <Card className="w-96 border-slate-700">
        <CardHeader className="text-center"><CardTitle className="text-2xl text-cyan-400">注册</CardTitle></CardHeader>
        <CardContent className="space-y-4">
          <Input placeholder="邮箱" value={email} onChange={(e) => setEmail(e.target.value)} />
          <Input type="password" placeholder="密码（至少6位）" value={pass} onChange={(e) => setPass(e.target.value)} />
          <Button className="w-full" onClick={register}>注册</Button>
          {msg && <p className="text-red-400 text-sm text-center">{msg}</p>}
          <p className="text-center text-slate-500 text-sm">已有账号？<a href="/login" className="text-cyan-400 hover:underline">登录</a></p>
        </CardContent>
      </Card>
    </div>
  );
}
