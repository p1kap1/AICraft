from fastapi import APIRouter, Depends, HTTPException, Request
from fastapi.responses import HTMLResponse
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.models.agent import Agent
from app.services.tool_registry import get_tool_definitions, execute_tool
from openai import OpenAI
from app.core.config import settings
import json

router = APIRouter(prefix="/widget", tags=["widget"])

WIDGET_HTML = '''<!DOCTYPE html><html><head><meta charset="UTF-8"><style>
#aicraft-widget{position:fixed;bottom:20px;right:20px;z-index:9999;font-family:sans-serif}
#aicraft-btn{width:56px;height:56px;border-radius:50%;background:#38bdf8;border:none;cursor:pointer;font-size:24px;box-shadow:0 4px 12px rgba(0,0,0,.3)}
#aicraft-panel{display:none;position:fixed;bottom:90px;right:20px;width:360px;height:500px;background:#1e293b;border-radius:12px;box-shadow:0 8px 32px rgba(0,0,0,.4);flex-direction:column;overflow:hidden;border:1px solid #334155}
#aicraft-msgs{flex:1;overflow-y:auto;padding:16px;color:#e2e8f0;font-size:14px}
#aicraft-msgs div{margin-bottom:8px;padding:8px 12px;border-radius:8px;max-width:85%}
#aicraft-msgs .user{background:#38bdf8;color:#0f172a;margin-left:auto}
#aicraft-msgs .bot{background:#334155}
#aicraft-input{display:flex;padding:12px;border-top:1px solid #334155}
#aicraft-input input{flex:1;background:#0f172a;border:1px solid #334155;color:#e2e8f0;padding:8px 12px;border-radius:8px;outline:none;font-size:14px}
#aicraft-input button{background:#38bdf8;color:#0f172a;border:none;padding:8px 16px;border-radius:8px;margin-left:8px;cursor:pointer;font-weight:600}
</style></head><body><div id="aicraft-widget"><button id="aicraft-btn" onclick="document.getElementById('aicraft-panel').style.display='flex';this.style.display='none'">💬</button><div id="aicraft-panel"><div id="aicraft-msgs"></div><div id="aicraft-input"><input id="aicraft-msg" placeholder="Ask me anything..." onkeydown="if(event.key==='Enter')send()"><button onclick="send()">Send</button></div></div></div><script>
async function send(){var m=document.getElementById("aicraft-msg").value;if(!m)return;var d=document.getElementById("aicraft-msgs");d.innerHTML+='<div class="user">'+m+"</div>";document.getElementById("aicraft-msg").value="";var b=document.createElement("div");b.className="bot";d.appendChild(b);var r=await fetch("/widget/'''+'{agent_id}'+'''/chat",{method:"POST",headers:{"Content-Type":"application/json"},body:JSON.stringify({message:m})});var t=await r.text();b.textContent=t;d.scrollTop=d.scrollHeight}
</script></body></html>'''

@router.get("/{agent_id}", response_class=HTMLResponse)
def widget_html(agent_id: str):
    return WIDGET_HTML.replace('{agent_id}', agent_id)

@router.post("/{agent_id}/chat")
def widget_chat(agent_id: str, request: Request, db: Session = Depends(get_db)):
    agent = db.query(Agent).filter(Agent.id == agent_id).first()
    if not agent: raise HTTPException(404, "Agent not found")
    body = request.json() if hasattr(request, 'json') else {}
    msg = body.get("message", "")
    client = OpenAI(api_key=settings.OPENAI_API_KEY, base_url=settings.OPENAI_BASE_URL)
    messages = [{"role":"system","content": agent.system_prompt or "You are a helpful assistant"},{"role":"user","content":msg}]
    resp = client.chat.completions.create(model=settings.DEFAULT_MODEL, messages=messages)
    return resp.choices[0].message.content
