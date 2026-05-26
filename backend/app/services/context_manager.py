"""Token 上下文管理 - 滑动窗口 + 摘要策略"""

from openai import OpenAI
from app.core.config import settings


# 粗略估算：中文约 1.5 字/token，英文约 0.75 字/token
def estimate_tokens(text: str) -> int:
    """估算 token 数量"""
    return len(text) // 2


MAX_TOKENS = 4000           # 上下文窗口上限
SUMMARY_THRESHOLD = 3000    # 超过此值触发摘要
WINDOW_SIZE = 10            # 滑动窗口保留的消息条数


class ContextManager:
    """管理对话上下文，防止 token 超限"""

    def __init__(self, strategy: str = "window"):
        """
        strategy: "window" 滑动窗口 / "summary" 摘要 / "none" 不限制
        """
        self.strategy = strategy
        self.summary = ""  # 累计摘要

    def process(
        self,
        messages: list[dict],
        system_prompts: list[str],
    ) -> list[dict]:
        """处理消息列表，返回裁剪后的结果"""
        if self.strategy == "none":
            return messages

        # 计算当前 token 用量
        total = sum(estimate_tokens(m["content"]) for m in messages)
        for sp in system_prompts:
            total += estimate_tokens(sp)

        if total <= MAX_TOKENS:
            return messages

        if self.strategy == "window":
            return self._apply_window(messages)
        elif self.strategy == "summary":
            return self._apply_summary(messages)
        return messages

    def _apply_window(self, messages: list[dict]) -> list[dict]:
        """滑动窗口：只保留最近 N 条消息"""
        return messages[-WINDOW_SIZE:]

    def _apply_summary(self, messages: list[dict]) -> list[dict]:
        """摘要策略：把早期消息压缩成摘要"""
        if len(messages) < WINDOW_SIZE:
            return messages

        recent = messages[-WINDOW_SIZE:]   # 保留最近的消息
        old = messages[:-WINDOW_SIZE]       # 需要摘要的早期消息

        if old:
            new_summary = self._generate_summary(old)
            if self.summary:
                self.summary = self._merge_summaries(self.summary, new_summary)
            else:
                self.summary = new_summary

        # 摘要作为 system 消息嵌入
        result = []
        if self.summary:
            result.append({"role": "system", "content": f"[对话历史摘要] {self.summary}"})
        result.extend(recent)
        return result

    def _generate_summary(self, messages: list[dict]) -> str:
        """调用 LLM 生成摘要"""
        try:
            client = OpenAI(
                api_key=settings.OPENAI_API_KEY,
                base_url=settings.OPENAI_BASE_URL,
            )
            text = "\n".join(
                f"{m['role']}: {m['content'][:300]}" for m in messages[:20]
            )
            resp = client.chat.completions.create(
                model=settings.DEFAULT_MODEL,
                messages=[
                    {"role": "system", "content": "把以下对话总结为一段简短摘要，保留关键信息和决策。"},
                    {"role": "user", "content": text},
                ],
                temperature=0.3,
                max_tokens=300,
            )
            return resp.choices[0].message.content.strip()
        except Exception:
            # LLM 不可用时简单拼接
            return "...（早期对话已省略）"

    def _merge_summaries(self, old_summary: str, new_summary: str) -> str:
        """合并摘要"""
        return f"{old_summary}\n{new_summary}"
