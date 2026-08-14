# Hugging Face Spaces 免费部署指南（让 HR 点开链接即可见）

> 方案：**单个 Space**（一个容器同时跑 FastAPI + Streamlit），一条公开 URL，无需信用卡。
> 成本：免费。LLM 默认 Mock 兜底，可一键切 DeepSeek。

---

## 0. 前置准备（2 分钟）

- 注册 Hugging Face 账号：https://huggingface.co/join
- 创建 **Access Token**（带 write 权限）：https://huggingface.co/settings/tokens
- 确认本机 git 可用（已确认 ✅ 2.54.0）

## 1. 本地：把代码同步进 Space 目录（30 秒）

```bash
cd "E:/第287期-仿百度文库的在线文库管理系统/ai-content-factory"
bash deploy/sync.sh        # 自动复制 app/ frontend/ requirements.txt 到 deploy/space/
```

> 之后每次改代码，重新部署前只需再跑一次 `bash deploy/sync.sh`。

## 2. 创建 Space（网页操作，2 分钟）

1. 打开 https://huggingface.co/new-space
2. **Space name**：`ai-content-factory`（或自定义）
3. **License**：MIT
4. **SDK**：选择 **Docker**
5. 点 **Create Space**

## 3. 推送代码（命令行，2 分钟）

```bash
cd "E:/第287期-仿百度文库的在线文库管理系统/ai-content-factory/deploy/space"
git init
git add .
git commit -m "deploy: AI content factory"
git remote add origin https://huggingface.co/spaces/<你的HF用户名>/ai-content-factory
git push -u origin main
```

> 推送时会提示输入账号密码：用户名填你的 HF 用户名，密码填**第 0 步的 Access Token**。

## 4. 等待构建并测试（5-10 分钟）

1. 回到 Space 页面，看 **Runtime** 或 **Logs** Tab，等待构建完成（首次要装依赖，约 3-8 分钟）
2. 构建成功后，访问：
   `https://<你的HF用户名>-ai-content-factory.hf.space`
3. 按顺序点一遍：内容生成 → 模板拆解 → Agent 日志

## 5. 切换 DeepSeek 真模型（可选，30 秒）

Space 页 → **Settings** → **Variables and secrets** 添加：

| Key | Value |
|---|---|
| `LLM_PROVIDER` | `deepseek` |
| `DEEPSEEK_API_KEY` | `sk-你的key` |

保存后点 **Restart**。切回 Mock：删掉这两个变量或把 `LLM_PROVIDER` 改回 `mock` 再重启。

---

## 常见问题

**Q：首次打开很慢？**
A：Space 首次构建/冷启动要几分钟；构建好后就常驻了。给 HR 前先自己点一次"预热"。

**Q：Space 会休眠吗？**
A：免费 Space 一般常驻，比 Render 免费层（15 分钟无访问就休眠）稳得多。

**Q：想用别的域名/平台？**
A：Render/Railway 免费层会休眠，第一次点开要等 ~50s，体验差；HF 更适合纯展示。

**Q：容器里能联网调 DeepSeek 吗？**
A：能，HF Space 有公网访问。
