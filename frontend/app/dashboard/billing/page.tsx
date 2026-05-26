"use client";
import { useEffect, useState } from "react";
import { Button } from "@/components/ui/button";
import { Card, CardHeader, CardTitle, CardDescription, CardContent } from "@/components/ui/card";
import { CreditCard, DollarSign } from "lucide-react";
const API = "/api";

export default function BillingPage() {
  const [balance, setBalance] = useState<any>({});
  const token = typeof window !== "undefined" ? localStorage.getItem("token") : "";
  const auth = () => token ? { Authorization: "Bearer " + token } : {};

  const load = () => fetch(API + "/billing/balance", { headers: auth() }).then(r => r.json()).then(setBalance);
  useEffect(() => { load(); }, []);

  const topup = async () => { await fetch(API + "/billing/topup?amount=10", { method: "POST", headers: auth() }); load(); };

  return (
    <div className="max-w-lg mx-auto space-y-8">
      <div>
        <h1 className="text-2xl font-bold tracking-tight">计费</h1>
        <p className="text-sm text-slate-400 mt-1">管理账户余额和订单</p>
      </div>
      <Card className="text-center">
        <CardHeader>
          <CardTitle className="flex items-center justify-center gap-2"><DollarSign className="w-5 h-5 text-cyan-400" /> 账户余额</CardTitle>
        </CardHeader>
        <CardContent>
          <div className="text-5xl font-bold text-cyan-400 my-4">${(balance.balance || 0).toFixed(2)}</div>
          <p className="text-sm text-slate-400 mb-6">累计使用: ${(balance.total_used || 0).toFixed(2)}</p>
          <Button onClick={topup} size="lg" className="gap-2"><CreditCard className="w-4 h-4" /> 充值 $10</Button>
        </CardContent>
      </Card>
    </div>
  );
}
