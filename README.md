# AICraft — AI Agent 构建平台

[![Python](https://img.shields.io/badge/Python-3.11-blue)](https://python.org)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.115-green)](https://fastapi.tiangolo.com)
[![Next.js](https://img.shields.io/badge/Next.js-14-black)](https://nextjs.org)
[![License](https://img.shields.io/badge/License-MIT-yellow)](LICENSE)

参考主流 Agent 平台架构，用 Python 全栈实现的 AI Agent 构建平台。用户通过可视化界面配置 Agent 的角色、模型和工具，对话时自动规划任务、调用工具、检索知识库，Agent 可一键发布为 REST API。

## 功能

| 模块 | 说明 |
| ------ | ------ |
| Agent 多步规划 | 意图分析 → 子任务拆分 → 工具调度 → 结果汇总 |
| 工具动态调用 | Function Calling + 工具注册表，支持内置工具和 API 工具 |
| 上下文窗口管理 | 滑动窗口 + 摘要策略双模式自动切换 |
| RAG 知识库 | 文档上传 → 向量化 → pgvector 检索 → 回答带来源 |
| 多模型接入 | 统一 Provider 层，支持 DeepSeek/OpenAI/Claude/硅基流动等 26 个模型 |
| 长期记忆 | Agent 对话后自动提取关键信息，跨会话注入 |
| Agent OpenAPI | 一键发布为 REST API，供外部系统调用 |
| 高可用故障转移 | 多 Key 负载均衡 + 自动故障切换 |
| 计费系统 | 余额体系 + 平台模型托管 |
| 工具市场 | 发布/浏览/安装社区工具 |
| 定时任务 | Agent 定时自动执行 |
| 多会话管理 | ChatGPT 式会话列表 + 切换 + 删除 |

## 技术栈

```
后端：Python / FastAPI / PostgreSQL + pgvector / OpenAI SDK / Redis / Docker
前端：Next.js 14 + TypeScript + Tailwind CSS + shadcn/ui
AI：   DeepSeek Function Calling / 自研 Agent 引擎
```

## 快速启动

```bash
# 1. 数据库
docker run -d --name aicraft-db -e POSTGRES_PASSWORD=postgres -p 5432:5432 pgvector/pgvector:pg15

# 2. 后端
cd backend
cp .env.example .env   # 填入 API Key
pip install -r requirements.txt
uvicorn app.main:app --port 8000

# 3. 前端
cd frontend
npm install
npm run dev
```

打开 http://localhost:3000

## 项目结构

```
AICraft/
├── backend/              # FastAPI 后端
│   ├── app/
│   │   ├── api/v1/       # 21 个 API 模块
│   │   ├── models/       # 数据模型
│   │   ├── services/     # 业务服务（Agent引擎、工具、记忆、缓存等）
│   │   ├── core/         # 配置、安全、数据库
│   │   └── schemas/      # Pydantic 请求/响应模型
│   └── requirements.txt
├── frontend/             # Next.js 14 前端
│   ├── app/dashboard/    # 15 个页面
│   ├── components/ui/    # shadcn/ui 组件
│   └── package.json
└── docker-compose.yml    # 一键部署
```

## 设计理念

- **Agent 即模板**：Agent 提供系统提示词 + 工具绑定 + 知识库绑定，API Key 由调用者提供，创建者的 Key 绝不泄露
- **工具与模型解耦**：`get_tool_definitions()` 是抽象层，换模型只需改描述格式，工具实现不依赖模型协议
- **四步流水线**：所有 Agent 对话强制走意图分析 → 任务拆分 → 工具调度 → 结果汇总，不依赖单次 LLM 调用

## License

MIT
