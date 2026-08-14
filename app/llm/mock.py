"""Mock 规则引擎：无 API Key 时离线演示完整链路。

依据 user 消息 JSON 中的 task 字段分发到对应的确定性生成器，
产出与真实 LLM 相同结构的结果，保证 Demo 现场断网也能跑。
"""
import json
import re

from ..terms import find_banned, sanitize
from .client import LLMClient

# 平台 -> 默认内容类型
_PLATFORM_DEFAULT_TYPE = {
    "小红书": "种草图文",
    "抖音": "短视频脚本",
    "快手": "短视频脚本",
    "视频号": "短视频脚本",
    "B站": "短视频脚本",
}


def _pick(v, fallback):
    return v if isinstance(v, str) and v and v != "auto" else fallback


def _first(arr, default=""):
    if isinstance(arr, list) and arr:
        return str(arr[0])
    return default


class MockClient(LLMClient):
    name = "mock"

    def chat(self, system: str, user: str, temperature: float = 0.7) -> str:
        return f"[mock] {user}"

    def chat_json(self, system: str, user: str, temperature: float = 0.3) -> dict:
        try:
            payload = json.loads(user)
        except json.JSONDecodeError:
            payload = {"task": "script", "text": user}
        task = payload.get("task", "script")
        handler = getattr(self, f"task_{task}", self.task_generic)
        return handler(payload)

    # ---------------- 任务实现 ----------------

    def task_generic(self, payload: dict) -> dict:
        return {"ok": True, "note": "mock 通用输出", "task": payload.get("task")}

    def task_supervise(self, payload: dict) -> dict:
        product = payload.get("product", {}) or {}
        cat = str(product.get("category", "") or product.get("name", ""))
        platform = _pick(payload.get("requested_platform"), "auto")
        content_type = _pick(payload.get("requested_content_type"), "auto")

        # 按品类启发式推断平台
        if platform == "auto":
            if any(k in cat for k in ["护肤", "美妆", "彩妆", "穿搭", "时尚"]):
                platform = "小红书"
            elif any(k in cat for k in ["数码", "3C", "手机", "家电"]):
                platform = "抖音"
            else:
                platform = "抖音"
        if content_type == "auto":
            content_type = _PLATFORM_DEFAULT_TYPE.get(platform, "种草图文")
        return {
            "intent": {"platform": platform, "content_type": content_type},
            "reason": f"品类「{cat}」匹配 {platform} 内容生态，{content_type}转化最优",
        }

    def task_topics(self, payload: dict) -> dict:
        product = payload.get("product", {}) or {}
        name = str(product.get("name", "产品"))
        cat = str(product.get("category", "好物"))
        audience = str(product.get("target_audience", "目标用户"))
        topics = [
            f"{name}实测：{audience}的第一手体验",
            f"{cat}测评：{name}到底值不值",
            f"{name}这样用，效果直接翻倍",
            f"避坑指南：买{cat}前必看的{name}真相",
            f"{name}开箱：从拆封到上手全记录",
        ]
        return {"topics": topics[:4]}

    def task_deconstruct(self, payload: dict) -> dict:
        text = str(payload.get("text", ""))
        framework = _pick(payload.get("content_type"), "种草图文")
        sentences = [s.strip() for s in re.split(r"[。！？!?\n]", text) if s.strip()]
        hook = sentences[0] if sentences else "开头抛出痛点/结果，3 秒抓住用户"
        return {
            "template": {
                "framework": framework,
                "source_text": text[:200],
                "title_formula": "场景痛点 + 数字承诺 + 身份代入",
                "hook": hook,
                "skeleton": [
                    "痛点引入：一句话戳中用户烦恼",
                    "产品呈现：交代这是什么、给谁用",
                    "效果实证：使用过程 + 可感知结果",
                    "技巧加分：1-2 个使用小技巧",
                    "真实感受：像朋友一样收尾",
                ],
                "cta": "关注 + 收藏，评论区留下你的问题，领取专属优惠",
                "data_estimate": "收藏率高于平均，长尾搜索流量稳定",
            }
        }

    def task_select_template(self, payload: dict) -> dict:
        # 库内模板选择在 Python 侧已完成，这里回显
        template = payload.get("candidate", {}) or {}
        return {"template": template, "source": "library"}

    def task_script(self, payload: dict) -> dict:
        product = payload.get("product", {}) or {}
        intent = payload.get("intent", {}) or {}
        template = payload.get("template", {}) or {}
        platform = str(intent.get("platform", "抖音"))
        content_type = str(intent.get("content_type", "短视频脚本"))
        name = str(product.get("name", "这款产品"))
        cat = str(product.get("category", "好物"))
        points = product.get("selling_points") or ["品质可靠", "体验出色"]
        points = [str(p) for p in points]
        price = str(product.get("price", ""))
        audience = str(product.get("target_audience", "目标用户"))

        # 返修：存在审核反馈时替换违禁词
        feedback = payload.get("review_feedback") or []
        if feedback:
            points = [sanitize(p) for p in points]
            name = sanitize(name)

        base = {
            "title": f"{name}｜{cat}必入清单",
            "image_prompts": [
                f"产品实拍：{name}自然光近景，突出质感",
                f"场景图：{audience}使用{name}的日常画面",
                f"对比图：{name}与其他{cat}的规格对比",
            ],
            "hashtags": [f"#{name}", f"#{cat}", "#好物推荐", "#种草日记", f"#{platform}好物"],
        }

        if content_type == "种草图文":
            body = [
                f"先说说我的真实情况，{audience}应该都懂——{hook_point(template)}",
                f"这次入的{name}，整体是「{cat}」赛道里体验很扎实的一款。{points[0]}；"
                + ("；".join(points[1:]) if len(points) > 1 else "细节也很到位。"),
                f"用了几天最明显的变化是：{points[0]}确实有感知。分享两个小技巧：搭配使用效果更好，建议先试用再回购。",
                f"最后说句大实话：{name}不一定适合所有人，但如果你也属于{audience}，可以放心入。",
                cta_line(template),
            ]
            base["body"] = body
            return base

        if content_type == "短视频脚本":
            base["storyboard"] = [
                {"scene": 1, "duration": "3s", "visual": "痛点开场特写", "narration": hook_point(template)},
                {"scene": 2, "duration": "5s", "visual": "产品快速亮相 + 价格露出", "narration": f"今天必须安利这个{name}，{points[0]}！"},
                {"scene": 3, "duration": "8s", "visual": "卖点逐条演示", "narration": "；".join(points[:3])},
                {"scene": 4, "duration": "4s", "visual": "使用场景 + 用户反应", "narration": f"{audience}试完直接回购，反馈是真的好。"},
                {"scene": 5, "duration": "3s", "visual": "CTA 页 + 小黄车", "narration": "左下角小黄车，限时安排，冲！"},
            ]
            return base

        # 直播话术
        base["stages"] = [
            {"name": "开场留人", "script": f"刚进来的家人们先别划走，今天这个{name}，全网都在问。", "note": "前 30 秒留存"},
            {"name": "痛点共鸣", "script": f"{audience}的烦恼我太懂了——{hook_point(template)}", "note": "放大焦虑"},
            {"name": "产品种草", "script": f"{name}，{cat}赛道口碑款。{'；'.join(points[:3])}", "note": "卖点透传"},
            {"name": "信任背书", "script": "我自己用了两周，体验稳定，售后无忧。", "note": "增强信任"},
            {"name": "逼单催付", "script": "库存就这么多，拍下的家人记得领优惠券，3 2 1 上链接！", "note": "限时紧迫感"},
            {"name": "下播预告", "script": "没抢到的别急，明天同一时间还有一轮，先点关注不错过。", "note": "沉淀关注"},
        ]
        return base

    def task_review(self, payload: dict) -> dict:
        content = str(payload.get("content", ""))
        title = str(payload.get("title", ""))
        product = payload.get("product", {}) or {}
        cat = str(product.get("category", ""))
        issues = []
        hits = find_banned(title + "\n" + content)
        if hits:
            issues.append(f"命中广告法极限词：{'、'.join(hits)}，需替换为合规表达")
        if not content or len(content) < 20:
            issues.append("正文过短，信息量不足，需补充卖点与场景")
        if not title:
            issues.append("缺少标题")
        if len(issues) == 0:
            return {"passed": True, "feedback": ["内容合规，无广告法风险，可以发布"]}
        return {"passed": False, "feedback": issues}


def hook_point(template: dict) -> str:
    hook = template.get("hook")
    if isinstance(hook, str) and hook:
        return hook
    return "换季/换新这个痛点，谁碰谁懂"


def cta_line(template: dict) -> str:
    cta = template.get("cta")
    if isinstance(cta, str) and cta:
        return cta
    return "关注我，更多真实测评持续更新～"
