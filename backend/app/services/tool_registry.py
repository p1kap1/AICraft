"""工具注册表 + 执行引擎"""
import json, math, re, requests
from datetime import datetime
from sqlalchemy.orm import Session


# ===== 内置工具 =====
BUILTIN_TOOLS = {
    "get_time": {
        "exec": lambda args: datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "desc": "获取当前时间",
        "params": {},
    },
    "calculator": {
        "exec": lambda args: str(eval(args.get("expression", "0"), {"__builtins__": {}}, {"math": math})),
        "desc": "计算数学表达式，如 123*456",
        "params": {"expression": "数学表达式"},
    },
    "search": {
        "exec": lambda args: f"[搜索功能: {args.get('query', '')}]",
        "desc": "搜索信息",
        "params": {"query": "搜索关键词"},
    },
}


def get_tool_definitions(db: Session = None) -> list[dict]:
    """获取所有可用工具定义（内置 + 用户自定义）"""
    tools = []
    # 内置工具
    for name, info in BUILTIN_TOOLS.items():
        tools.append({
            "type": "function",
            "function": {
                "name": name,
                "description": info["desc"],
                "parameters": {
                    "type": "object",
                    "properties": {k: {"type": "string", "description": v} for k, v in info["params"].items()},
                    "required": list(info["params"].keys()),
                } if info["params"] else {"type": "object", "properties": {}},
            },
        })

    # 用户自定义工具（从数据库加载）
    if db:
        try:
            from app.models.others import Tool
            user_tools = db.query(Tool).filter(Tool.enabled == True).all()
            for t in user_tools:
                config = t.config or {}
                tools.append({
                    "type": "function",
                    "function": {
                        "name": t.name or f"tool_{t.id[:8]}",
                        "description": t.description or "自定义工具",
                        "parameters": {
                            "type": "object",
                            "properties": config.get("params", {}),
                            "required": config.get("required", []),
                        } if config.get("params") else {"type": "object", "properties": {}},
                    },
                })
        except:
            pass

    return tools


def execute_tool(name: str, args: dict, db: Session = None) -> str:
    """执行工具"""
    # 内置工具
    if name in BUILTIN_TOOLS:
        try: return str(BUILTIN_TOOLS[name]["exec"](args))
        except Exception as e: return f"工具执行错误: {e}"

    # 用户自定义工具
    if db:
        try:
            from app.models.others import Tool
            tool = db.query(Tool).filter(Tool.name == name).first()
            if tool and tool.tool_type == "api":
                config = tool.config or {}
                url = config.get("url", "")
                method = config.get("method", "GET").upper()
                # 替换 URL 中的参数
                for k, v in args.items():
                    url = url.replace(f"{{{k}}}", str(v))
                resp = requests.request(method, url,
                    params=args if method == "GET" else None,
                    json=args if method != "GET" else None,
                    timeout=10)
                return resp.text[:500]
            elif tool:
                return f"[工具 {name} 已注册，类型: {tool.tool_type}]"
        except Exception as e:
            return f"自定义工具错误: {e}"

    return f"未知工具: {name}"
