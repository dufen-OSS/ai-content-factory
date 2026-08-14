# AI 电商内容工厂（MVP Demo）

输入商品信息 → 多 Agent 协作 → 输出可发布的带货脚本 / 种草图文 / 直播话术。

**核心卖点**：热门内容模板拆解（七维表）+ LangGraph 多 Agent 编排 + 审核自动返修。

## 技术栈

| 层 | 选型 |
|---|---|
| Agent 编排 | LangGraph（有状态多 Agent 工作流、条件路由、返修循环） |
| 后端 | FastAPI |
| 前端 | Streamlit |
| LLM | 可插拔：DeepSeek / OpenAI 兼容 / **Ollama 本地** / Mock（离线规则引擎） |
| 部署 | Docker / docker-compose |

## 5-Agent 工作流

```
Supervisor(意图/路由) → 选题 Agent → 模板拆解 Agent → 脚本生成 Agent → 审核 Agent
                                                              │
                                      不通过(≤2次) → 返修回脚本生成（携带 feedback）
                                                              ▼
                                                         交付成稿
```

- **Supervisor**：判断目标平台（抖音/小红书/快手…）与内容类型（种草图文/短视频脚本/直播话术）
- **选题 Agent**：生成 4 个差异化选题
- **模板拆解 Agent**：库内检索，或对用户粘贴的竞品爆款文案做 LLM 现场拆解（七维表：标题公式/开头钩子/内容骨架/收尾CTA/数据预估/可抄骨架）
- **脚本生成 Agent**：模板骨架 × 商品卖点 → 成稿
- **审核 Agent**：广告法违禁极限词 + 完整性检查，不通过自动返修

## 快速开始（本地）

```bash
# 1. 创建并激活虚拟环境
py -m venv .venv
.venv/Scripts/activate        # Windows；macOS/Linux 用 source .venv/bin/activate

# 2. 安装依赖
pip install -r requirements.txt

# 3. 配置 LLM（可选。不填自动用 Mock 引擎，离线也能演示）
cp .env.example .env
# 编辑 .env：
#   LLM_PROVIDER=deepseek + DEEPSEEK_API_KEY   -> 云端 DeepSeek
#   LLM_PROVIDER=ollama                         -> 本地 Ollama（qwen2.5:7b 已验证，无需 Key）
#   LLM_PROVIDER=openai + OPENAI_API_KEY        -> 任意 OpenAI 兼容
#   LLM_PROVIDER=mock                           -> 离线规则引擎

# 4. 启动后端
uvicorn app.main:app --port 8000          # 或 python -m app.main

# 5. 启动前端（另开终端）
streamlit run frontend/app.py             # 浏览器打开 http://localhost:8501
```

## 快速开始（Docker）

```bash
export DEEPSEEK_API_KEY=sk-xxx            # 不填则用 Mock 引擎
docker compose up --build
# 前端 http://localhost:8501   后端 http://localhost:8000/api/health
```

## 测试

```bash
python -m pytest tests/ -v                          # 默认 Mock 引擎，离线可跑
LLM_PROVIDER=ollama python -m pytest tests/ -v      # 本地真模型（qwen2.5:7b，已实测 12/12 通过）
```

真模型端到端验证（含耗时/产出）：

```bash
LLM_PROVIDER=ollama python scripts/verify_ollama.py
```

## 接口

| 方法 | 路径 | 说明 |
|---|---|---|
| POST | `/api/generate` | 商品信息 → 完整生成链路（含 Agent 执行日志） |
| POST | `/api/deconstruct` | 粘贴爆款文案 → 七维表模板拆解 |
| GET | `/api/templates` | 内置模板库 |
| GET | `/api/health` | 健康检查 + 当前 LLM 供应商 |

## 项目结构

```
ai-content-factory/
├── app/
│   ├── main.py / api.py      # FastAPI 入口与路由
│   ├── graph.py              # LangGraph 工作流（条件路由/返修）
│   ├── templates.py          # 内置爆款模板库（七维表）
│   ├── terms.py              # 广告法违禁词库
│   ├── config.py             # 环境变量配置
│   ├── agents/               # Supervisor/选题/模板拆解/脚本/审核
│   └── llm/                  # DeepSeek/OpenAI兼容/Mock 可插拔客户端
├── frontend/app.py           # Streamlit 演示界面
├── tests/                    # 单元 + 端到端测试
├── Dockerfile / docker-compose.yml
└── requirements.txt
```
