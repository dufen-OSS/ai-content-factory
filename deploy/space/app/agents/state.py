"""LangGraph 共享状态：ContentState。

所有节点接收 ContentState、返回部分字段的 dict 做增量更新。
"""
from typing import Any, Dict, List

from pydantic import BaseModel, Field


class ProductInfo(BaseModel):
    name: str = ""
    category: str = ""
    selling_points: List[str] = Field(default_factory=list)
    target_audience: str = ""
    price: str = ""
    link: str = ""


class ContentState(BaseModel):
    # ---- 输入 ----
    product: ProductInfo = Field(default_factory=ProductInfo)
    platform: str = "auto"
    content_type: str = "auto"
    # 用户粘贴的竞品爆款文案（可选，触发 LLM 模板拆解）
    deconstruct_text: str = ""

    # ---- 中间产物 ----
    intent: Dict[str, Any] = Field(default_factory=dict)
    topics: List[str] = Field(default_factory=list)
    template: Dict[str, Any] = Field(default_factory=dict)
    template_source: str = ""

    # ---- 产出 ----
    title: str = ""
    body: List[str] = Field(default_factory=list)
    storyboard: List[Dict[str, Any]] = Field(default_factory=list)
    stages: List[Dict[str, Any]] = Field(default_factory=list)
    script: str = ""
    image_prompts: List[str] = Field(default_factory=list)
    hashtags: List[str] = Field(default_factory=list)

    # ---- 审核 ----
    review_passed: bool = False
    review_feedback: List[str] = Field(default_factory=list)
    retry_count: int = 0

    # ---- 可观测性：每个 Agent 的执行日志 ----
    agent_trace: List[Dict[str, Any]] = Field(default_factory=list)

    def trace(self, agent: str, action: str, result: Any) -> "ContentState":
        """追加一条 Agent 执行日志（节点内调用后返回新的 state 部分更新）。"""
        self.agent_trace = self.agent_trace + [
            {
                "agent": agent,
                "action": action,
                "result": result,
            }
        ]
        return self

    def to_output(self) -> dict:
        return {
            "product": self.product.model_dump(),
            "intent": self.intent,
            "topics": self.topics,
            "template": self.template,
            "template_source": self.template_source,
            "title": self.title,
            "script": self.script,
            "body": self.body,
            "storyboard": self.storyboard,
            "stages": self.stages,
            "image_prompts": self.image_prompts,
            "hashtags": self.hashtags,
            "review": {
                "passed": self.review_passed,
                "feedback": self.review_feedback,
                "retry_count": self.retry_count,
            },
            "agent_trace": self.agent_trace,
        }
