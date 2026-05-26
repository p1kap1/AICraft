"""FastAPI 入口"""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.core.config import settings
from app.core.database import engine, Base
from app.api.v1 import auth, agents, chat, tools, providers, knowledge, workspace, openapi, tasks, keys, usage, profile, billing, market, widget, binding, admin, sso, payment, container, rag_admin, admin_providers, models

# 导入所有模型确保建表
import app.models.user  # noqa
import app.models.agent  # noqa
import app.models.others  # noqa
import app.models.knowledge  # noqa
import app.models.memory  # noqa
import app.models.task  # noqa
import app.models.apikey  # noqa
import app.models.usage  # noqa
import app.models.billing  # noqa
import app.models.market  # noqa
import app.models.sso  # noqa
import app.models.payment  # noqa
import app.models.rag_review  # noqa
import app.models.platform_provider  # noqa

# 创建所有表
Base.metadata.create_all(bind=engine)

app = FastAPI(title=settings.APP_NAME, docs_url="/api/docs", openapi_url="/api/openapi.json")

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 注册路由
app.include_router(auth.router)
app.include_router(agents.router)
app.include_router(chat.router)
app.include_router(tools.router)
app.include_router(providers.router)
app.include_router(knowledge.router)
app.include_router(workspace.router)
app.include_router(openapi.router)
app.include_router(tasks.router)
app.include_router(keys.router)
app.include_router(usage.router)
app.include_router(profile.router)
app.include_router(billing.router)
app.include_router(market.router)
app.include_router(widget.router)
app.include_router(binding.router)
app.include_router(admin.router)
app.include_router(sso.router)
app.include_router(payment.router)
app.include_router(container.router)
app.include_router(rag_admin.router)
app.include_router(admin_providers.router)
app.include_router(models.router)


@app.get("/api/health")
def health():
    return {"code": 200, "message": "ok"}


@app.get("/api")
def root():
    return {"name": "AICraft", "version": "0.1.0", "docs": "/api/docs"}
