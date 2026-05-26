"use client";
import { useEffect, useState } from "react";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Card, CardHeader, CardTitle, CardDescription, CardContent } from "@/components/ui/card";
import { Key, User, BarChart3, Copy, Check, Trash2, Star } from "lucide-react";

const API = "/api";

export default function SettingsPage() {
  const [profile, setProfile] = useState<any>({});
  const [nickname, setNickname] = useState("");
  const [apiKeys, setApiKeys] = useState<any[]>([]);
  const [providers, setProviders] = useState<any[]>([]);
  const [defaultProvider, setDefaultProvider] = useState("");
  const [usage, setUsage] = useState<any>({});
  const [copied, setCopied] = useState("");
  const token = typeof window !== "undefined" ? localStorage.getItem("token") : "";
  const auth = () => token ? { Authorization: "Bearer " + token } : {};

  const load = () => {
    fetch(API + "/profile", { headers: auth() }).then(r => r.json()).then(d => { setProfile(d); setNickname(d.nickname); setDefaultProvider(d.default_provider_id || ""); });
    fetch(API + "/keys/user", { headers: auth() }).then(r => r.json()).then(setApiKeys);
    fetch(API + "/providers/user", { headers: auth() }).then(r => r.json()).then(setProviders);
    fetch(API + "/usage/stats", { headers: auth() }).then(r => r.json()).then(setUsage);
  };
  useEffect(() => { load(); }, []);

  const saveProfile = async () => {
    await fetch(API + "/profile?nickname=" + encodeURIComponent(nickname) + "&default_provider_id=" + defaultProvider, { method: "PUT", headers: auth() });
    load();
  };

  const createKey = async () => { await fetch(API + "/keys?name=APIKey", { method: "POST", headers: auth() }); load(); };
  const delKey = async (id: string) => { await fetch(API + "/keys/" + id, { method: "DELETE", headers: auth() }); load(); };
  const copy = (key: string) => { navigator.clipboard.writeText(key); setCopied(key); setTimeout(() => setCopied(""), 2000); };

  return (
    <div className="max-w-3xl mx-auto space-y-8">
      <div><h1 className="text-2xl font-bold tracking-tight">设置</h1><p className="text-sm text-slate-400 mt-1">管理你的账号和应用配置</p></div>

      <Card>
        <CardHeader><CardTitle className="flex items-center gap-2"><User className="w-4 h-4 text-cyan-400" />个人资料</CardTitle></CardHeader>
        <CardContent className="space-y-4">
          <div className="grid grid-cols-2 gap-4 text-sm"><div><span className="text-slate-400">邮箱:</span> {profile.email || "—"}</div><div><span className="text-slate-400">手机:</span> {profile.phone || "—"}</div></div>
          <div className="flex gap-2 items-end">
            <div className="flex-1">
              <label className="text-sm font-medium block mb-1">昵称</label>
              <Input value={nickname} onChange={e => setNickname(e.target.value)} />
            </div>
            <Button size="sm" onClick={saveProfile}>保存</Button>
          </div>

          <div className="space-y-2">
            <label className="text-sm font-medium flex items-center gap-1"><Star className="w-3 h-3 text-cyan-400"/>默认模型</label>
            <select className="w-full bg-slate-700 border border-slate-600 text-white p-2 rounded-lg text-sm" value={defaultProvider} onChange={e => setDefaultProvider(e.target.value)}>
              <option value="">未设置</option>
              {providers.map((p: any) => <option key={p.id} value={p.id}>{p.name}</option>)}
            </select>
            <p className="text-xs text-slate-500">对话时自动使用此模型，无需手动选择</p>
          </div>
        </CardContent>
      </Card>

      <Card>
        <CardHeader><CardTitle className="flex items-center gap-2"><Key className="w-4 h-4 text-cyan-400" />API Keys</CardTitle></CardHeader>
        <CardContent className="space-y-3">
          <Button size="sm" onClick={createKey}>+ 生成 Key</Button>
          {apiKeys.map((k: any) => (
            <div key={k.id} className="flex items-center justify-between bg-slate-700/50 rounded-lg p-3">
              <code className="text-sm font-mono text-cyan-400">{k.key}</code>
              <div className="flex items-center gap-1">
                <Button size="sm" variant="ghost" onClick={() => copy(k.key)}>{copied === k.key ? <Check className="w-4 h-4 text-green-400" /> : <Copy className="w-4 h-4" />}</Button>
                <Button size="sm" variant="ghost" onClick={() => delKey(k.id)}><Trash2 className="w-4 h-4 text-red-400" /></Button>
              </div>
            </div>
          ))}
        </CardContent>
      </Card>

      <Card>
        <CardHeader><CardTitle className="flex items-center gap-2"><BarChart3 className="w-4 h-4 text-cyan-400" />使用统计</CardTitle></CardHeader>
        <CardContent>
          <div className="grid grid-cols-3 gap-4">
            {[{ label: "总调用", val: usage.total_calls || 0 }, { label: "总 Token", val: (usage.total_tokens || 0).toLocaleString() }, { label: "用户", val: profile.nickname || "—" }].map(s => (
              <div key={s.label} className="bg-slate-700/50 rounded-xl p-4 text-center"><div className="text-2xl font-bold text-cyan-400">{s.val}</div><div className="text-xs text-slate-400 mt-1">{s.label}</div></div>
            ))}
          </div>
        </CardContent>
      </Card>
    </div>
  );
}
