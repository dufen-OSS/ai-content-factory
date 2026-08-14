# GitHub 部署指南（让 HR 看到）

> 方案：**公开 GitHub 仓库（代码证据）+ GitHub Pages 展示页（免费、中国可访问）+ 可选 Zeabur 活链接**。
> GitHub 本身只托管静态页面，跑不了 FastAPI/Streamlit 后端；活链接需借助 PaaS（推荐 Zeabur，国内可访问）。

---

## 一、公开 GitHub 仓库（代码证据）

### 1. 创建 GitHub 仓库（网页，2 分钟）
1. 登录 github.com → New repository
2. 名字：`ai-content-factory`；**Public**；不要勾选初始化文件（本地已有代码）

### 2. 推代码（命令行，2 分钟）
```bash
cd "E:/第287期-仿百度文库的在线文库管理系统/ai-content-factory"
git remote add origin https://github.com/dufen-OSS/ai-content-factory.git
git push -u origin main
```
> 若提示认证：Windows 一般已配 Git Credential Manager，会弹出浏览器登录；没有就用 Personal Access Token（Settings → Developer settings → Tokens → 勾选 repo 权限）当密码。

HR 看到 `github.com/dufen-OSS/ai-content-factory`，可浏览代码、README、测试。

---

## 二、GitHub Pages 展示页（HR 看的一页纸）

展示页已建好：`docs/index.html`（架构图 + 真实输出示例 + 5-Agent 职责 + 视频/活链接占位）+ `docs/report.html`（完整汇报）。

### 开启 Pages（2 分钟）
1. 仓库 → Settings → Pages
2. Source 选 **GitHub Actions**（工作流已建好，`.github/workflows/pages.yml`，push 到 main 自动发布）
3. 等 1-2 分钟，访问：
   **`https://dufen-OSS.github.io/ai-content-factory/`**

### 填占位内容（录好视频/部署活链接后）
编辑 `docs/index.html`，把两处 `（占位：...）` 换成你的 Loom 视频链接和活链接，再 push 一次即可。

---

## 三、活链接（可选，推荐 Zeabur，国内可访问）

Zeabur（zeabur.com）：从 GitHub 仓库一键部署容器，免费额度够演示用。

1. 注册 zeabur.com（国内手机号即可）
2. 新建项目 → 关联 GitHub 仓库 `ai-content-factory`
3. 部署配置选 **Docker**（项目根 `deploy/space/Dockerfile` 已备好，一个容器同时跑前后端）
   - 或直接部署根目录 Dockerfile 前先 `bash deploy/sync.sh` 生成 `deploy/space/` 并作为服务目录
4. 设环境变量：`LLM_PROVIDER=mock`（默认兜底）；要真模型加 `LLM_PROVIDER=deepseek` + `DEEPSEEK_API_KEY=sk-...`
5. 绑定端口 7860，得到公开 URL，贴进展示页

> 备选：Render.com 免费层（会休眠，首次打开 ~50s）；Railway（需绑卡，国内访问不稳定）。**国内可访问性首选 Zeabur。**

---

## 四、改代码后怎么更新

```bash
bash deploy/sync.sh      # 同步 app/ frontend/ 到 deploy/space/
git add -A && git commit -m "update" && git push   # 仓库 + Pages 自动更新
# Zeabur 会自动重新部署（若开了自动部署）
```

---

## 五、给 HR 的最终交付

| 渠道 | 链接 | 说明 |
|---|---|---|
| 代码 | github.com/dufen-OSS/ai-content-factory | 工程能力证据 |
| 展示页 | dufen-OSS.github.io/ai-content-factory/ | 架构 + 实测 + 视频/活链接 |
| 演示视频 | 占位（Loom/网盘） | 兜底，防活链接不稳定 |
| 活链接 | 占位（Zeabur） | 可交互 Demo |
