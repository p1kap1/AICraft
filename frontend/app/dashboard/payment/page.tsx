"use client";
import { useEffect, useState } from "react";
import { Button } from "@/components/ui/button";
import { Card, CardHeader, CardTitle, CardContent } from "@/components/ui/card";
import { CreditCard, Wallet } from "lucide-react";
const API = "/api";

export default function PaymentPage() {
  const [history, setHistory] = useState<any[]>([]);
  const token = typeof window !== "undefined" ? localStorage.getItem("token") : "";
  const auth = () => token ? {Authorization:"Bearer "+token} : {};
  useEffect(()=>{fetch(API+"/payment/history",{headers:auth()}).then(r=>r.json()).then(setHistory).catch(()=>{});},[]);

  const pay = async (method: string) => {
    const amount = parseFloat(prompt("充值金额:")||"10");
    if(!amount)return;
    await fetch(API+"/payment/create?amount="+amount+"&method="+method,{method:"POST",headers:auth()});
    window.location.reload();
  };

  return (
    <div className="max-w-2xl mx-auto space-y-8">
      <div><h1 className="text-2xl font-bold tracking-tight">支付</h1><p className="text-sm text-slate-400 mt-1">充值余额</p></div>
      <div className="grid grid-cols-3 gap-4">
        {[{icon:"💳",name:"支付宝",method:"alipay"},{icon:"💚",name:"微信支付",method:"wechat"},{icon:"💳",name:"银行卡",method:"stripe"}].map(p=>(
          <Card key={p.method} className="cursor-pointer hover:border-cyan-500/30 text-center" onClick={()=>pay(p.method)}>
            <CardContent className="py-6"><div className="text-3xl mb-2">{p.icon}</div><div className="font-medium text-sm">{p.name}</div></CardContent>
          </Card>
        ))}
      </div>
      <Card><CardHeader><CardTitle className="flex items-center gap-2"><Wallet className="w-4 h-4"/>充值记录</CardTitle></CardHeader>
        <CardContent>{history.length===0?<p className="text-sm text-slate-500 py-4">暂无记录</p>:history.map((h:any,i:number)=>(<div key={i} className="flex justify-between py-2 border-b border-slate-700/50"><span>{h.method} ${h.amount}</span><span className="text-xs text-slate-400">{h.time}</span></div>))}</CardContent>
      </Card>
    </div>
  );
}
