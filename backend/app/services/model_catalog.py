# 预置模型目录（名称 + API 地址），只需填 Key
MODEL_CATALOG = [
    {"name": "DeepSeek V3", "model": "deepseek-chat", "base_url": "https://api.deepseek.com/v1", "provider_type": "openai"},
    {"name": "DeepSeek V4 Pro", "model": "deepseek-v4-pro", "base_url": "https://api.deepseek.com/v1", "provider_type": "openai"},
    {"name": "DeepSeek R1", "model": "deepseek-reasoner", "base_url": "https://api.deepseek.com/v1", "provider_type": "openai"},
    {"name": "OpenAI GPT-4o", "model": "gpt-4o", "base_url": "https://api.openai.com/v1", "provider_type": "openai"},
    {"name": "OpenAI GPT-4o-mini", "model": "gpt-4o-mini", "base_url": "https://api.openai.com/v1", "provider_type": "openai"},
    {"name": "OpenAI o3-mini", "model": "o3-mini", "base_url": "https://api.openai.com/v1", "provider_type": "openai"},
    {"name": "Claude 3.5 Sonnet", "model": "claude-3-5-sonnet-20241022", "base_url": "https://api.anthropic.com/v1", "provider_type": "openai"},
    {"name": "Claude 3 Opus", "model": "claude-3-opus-20240229", "base_url": "https://api.anthropic.com/v1", "provider_type": "openai"},
    {"name": "硅基流动 DeepSeek V3", "model": "deepseek-ai/DeepSeek-V3", "base_url": "https://api.siliconflow.cn/v1", "provider_type": "openai"},
    {"name": "硅基流动 DeepSeek R1", "model": "deepseek-ai/DeepSeek-R1", "base_url": "https://api.siliconflow.cn/v1", "provider_type": "openai"},
    {"name": "硅基流动 Qwen 72B", "model": "Qwen/Qwen2.5-72B-Instruct", "base_url": "https://api.siliconflow.cn/v1", "provider_type": "openai"},
    {"name": "通义千问 Plus", "model": "qwen-plus", "base_url": "https://dashscope.aliyuncs.com/compatible-mode/v1", "provider_type": "openai"},
    {"name": "智谱 GLM-4", "model": "glm-4", "base_url": "https://open.bigmodel.cn/api/paas/v4", "provider_type": "openai"},
    {"name": "月之暗面 Moonshot", "model": "moonshot-v1-8k", "base_url": "https://api.moonshot.cn/v1", "provider_type": "openai"},
    {"name": "百川 Baichuan4", "model": "Baichuan4", "base_url": "https://api.baichuan-ai.com/v1", "provider_type": "openai"},
    {"name": "MiniMax abab6.5", "model": "abab6.5s-chat", "base_url": "https://api.minimax.chat/v1", "provider_type": "openai"},
    {"name": "零一万物 yi-large", "model": "yi-large", "base_url": "https://api.lingyiwanwu.com/v1", "provider_type": "openai"},
    {"name": "豆包 Doubao Pro", "model": "doubao-pro-32k", "base_url": "https://ark.cn-beijing.volces.com/api/v3", "provider_type": "openai"},
    {"name": "Gemini 2.0 Flash", "model": "gemini-2.0-flash", "base_url": "https://generativelanguage.googleapis.com/v1beta/openai", "provider_type": "openai"},
    {"name": "Gemini 1.5 Pro", "model": "gemini-1.5-pro", "base_url": "https://generativelanguage.googleapis.com/v1beta/openai", "provider_type": "openai"},
    {"name": "Mistral Large", "model": "mistral-large-latest", "base_url": "https://api.mistral.ai/v1", "provider_type": "openai"},
    {"name": "Grok (xAI)", "model": "grok-beta", "base_url": "https://api.x.ai/v1", "provider_type": "openai"},
    {"name": "Cohere Command R+", "model": "command-r-plus", "base_url": "https://api.cohere.ai/v1", "provider_type": "openai"},
    {"name": "讯飞星火 4.0", "model": "spark-v4.0", "base_url": "https://spark-api-open.xf-yun.com/v1", "provider_type": "openai"},
    {"name": "腾讯混元", "model": "hunyuan-pro", "base_url": "https://api.hunyuan.cloud.tencent.com/v1", "provider_type": "openai"},
    {"name": "DeepSeek V2", "model": "deepseek-chat-v2", "base_url": "https://api.deepseek.com/v1", "provider_type": "openai"},
]

def get_catalog():
    return MODEL_CATALOG
