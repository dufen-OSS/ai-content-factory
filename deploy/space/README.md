---
title: AI 电商内容工厂
emoji: 🏭
colorFrom: blue
colorTo: indigo
sdk: docker
pinned: false
license: mit
app_port: 7860
---

# AI 电商内容工厂 · 在线 Demo

输入商品信息 → 5-Agent 协作 → 输出可发布的带货脚本 / 种草图文 / 直播话术。

技术栈：LangGraph + FastAPI + Streamlit。LLM 可插拔（默认 Mock 离线引擎，可切换 DeepSeek）。

## 使用

- **内容生成** Tab：填商品名称/品类/卖点 → 生成
- **模板拆解** Tab：粘贴竞品爆款文案 → 拆出七维表
- **Agent 架构** Tab：5-Agent 工作流与条件路由说明

## 切换 DeepSeek 真模型

在 Space 的 Settings → Variables and secrets 中添加：

| Key | Value |
|---|---|
| `LLM_PROVIDER` | `deepseek` |
| `DEEPSEEK_API_KEY` | `sk-...` |

然后 Restart。
