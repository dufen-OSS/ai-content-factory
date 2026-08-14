"""内置爆款模板库（七维表结构）。

每个模板包含：标题公式 / 开头钩子 / 内容骨架 / 收尾CTA / 数据预估 / 可抄骨架。
「模板拆解 Agent」从库中按 平台+内容类型 检索最匹配模板；用户也可粘贴竞品爆款文案，
由 LLM 现场拆解出相同结构。
"""
from typing import Optional

_TEMPLATES: list[dict] = [
    {
        "id": "xhs-grass-01",
        "platform": "小红书",
        "content_type": "种草图文",
        "name": "实测型种草",
        "title_formula": "场景痛点 + 数字承诺 + 身份代入（例：干皮救星！这个面霜我用了7天真的会谢）",
        "hook": "开头 3 行内抛结果/痛点，建立「我也是普通人」的信任感",
        "skeleton": [
            "真实情况引入（谁适合看）",
            "产品第一印象（颜值/质地/气味）",
            "使用过程记录（时间线/步骤）",
            "效果实证（照片/数据/体感）",
            "避雷点 + 适用人群边界",
        ],
        "cta": "关注 + 收藏，评论区留肤质，帮你判断适不适合",
        "data_estimate": "收藏率显著高于平均，长尾搜索流量稳定",
        "framework": "真实体验 + 步骤还原 + 边界说明，避免「无脑吹」人设崩塌",
        "tags": ["护肤", "美妆", "日用", "测评"],
    },
    {
        "id": "xhs-grass-02",
        "platform": "小红书",
        "content_type": "种草图文",
        "name": "避坑清单型",
        "title_formula": "反向制造焦虑 + 清单体（例：买前必看！这5个坑我替你踩过了）",
        "hook": "上来就说「你大概率会踩坑」，抓住收藏动机",
        "skeleton": [
            "抛出行业常见坑",
            "逐个拆解（坑 -> 原因 -> 怎么避）",
            "给出推荐清单（含本品）",
            "成本/性价比对比",
        ],
        "cta": "先收藏再逛，买的时候回来对一下清单",
        "data_estimate": "收藏/点赞比高，转发率好，适合长期 SEO",
        "framework": "以「帮你省钱避坑」为名，用清单体降低决策成本",
        "tags": ["测评", "数码", "家电", "3C", "省钱"],
    },
    {
        "id": "dy-short-01",
        "platform": "抖音",
        "content_type": "短视频脚本",
        "name": "痛点-演示-促单型",
        "title_formula": "反常识开头 + 结果前置（例：用了它，同事以为我换了个人）",
        "hook": "前 3 秒：最惨痛点特写，画面+台词双重冲击",
        "skeleton": [
            "黄金3秒：痛点/反常识开场",
            "产品亮相：快速露价格",
            "卖点演示：逐条可视化",
            "场景还原：用户真实使用",
            "促单 CTA：小黄车 + 限时",
        ],
        "cta": "左下角小黄车，限时活动，错过等一年",
        "data_estimate": "完播率看钩子，转化率看第三幕卖点演示",
        "framework": "3 秒钩子 -> 卖点可视化 -> 场景代入 -> 紧迫促单，节奏紧凑",
        "tags": ["带货", "日用", "食品", "美妆"],
    },
    {
        "id": "dy-short-02",
        "platform": "抖音",
        "content_type": "短视频脚本",
        "name": "开箱种草型",
        "title_formula": "期待感 + 惊喜点（例：这箱我拆了，结果被圈粉了）",
        "hook": "第一镜头：快递箱特写 + 「你们要的开箱来了」",
        "skeleton": [
            "开箱仪式（拆封特写）",
            "配件/颜值逐一亮相",
            "上手实测（关键功能）",
            "惊喜点/反差（最加分）",
            "购买建议 + CTA",
        ],
        "cta": "想要同款的，点下方链接带走",
        "data_estimate": "开箱类完播率中等，但评论互动率高",
        "framework": "以「探宝」心理驱动，每个环节都埋一个惊喜点",
        "tags": ["开箱", "数码", "3C", "新奇"],
    },
    {
        "id": "dy-live-01",
        "platform": "抖音",
        "content_type": "直播话术",
        "name": "憋单逼单型",
        "title_formula": "福利前置 + 限量制造稀缺（例：今天只放 50 单，拍完就下）",
        "hook": "开场 30 秒：福利预告 + 留人",
        "skeleton": [
            "开场留人（福利预告）",
            "痛点共鸣（用户场景代入）",
            "产品种草（卖点透传）",
            "信任背书（自用/售后/资质）",
            "逼单催付（库存/倒计时）",
            "下播预告（沉淀关注）",
        ],
        "cta": "3 2 1 上链接！没抢到的先关注，明天还有",
        "data_estimate": "憋单时长与转化率强相关，前 5 分钟留存是生死线",
        "framework": "福利钩子 -> 信任递进 -> 稀缺逼单，话术要有节奏感",
        "tags": ["直播", "带货", "食品", "日用"],
    },
    {
        "id": "ks-live-01",
        "platform": "快手",
        "content_type": "直播话术",
        "name": "老铁信任型",
        "title_formula": "家人称谓 + 实在人设（例：家人们，今天这批货是我自己蹲仓库挑的）",
        "hook": "以「老铁」「家人」开场，拉近关系",
        "skeleton": [
            "老铁开场（拉家常）",
            "实话说实话（价格透明）",
            "产品实讲（产地/用料）",
            "现场试（当众验货）",
            "给足赠品（人情味）",
            "约定下次（沉淀关注）",
        ],
        "cta": "拍到的老铁记得回来点关注，下回还给你们留",
        "data_estimate": "快手信任型转化更依赖主播真诚感而非套路",
        "framework": "人情味 > 套路，把「实在」演到细节里",
        "tags": ["直播", "农产品", "日用", "服饰"],
    },
]


def list_templates() -> list[dict]:
    return [dict(t) for t in _TEMPLATES]


def select_template(
    platform: str = "", content_type: str = "", product_category: str = ""
) -> Optional[dict]:
    """按 平台 + 内容类型 + 品类标签 打分，返回最匹配模板。"""
    best, best_score = None, -1
    for t in _TEMPLATES:
        score = 0
        if platform and t["platform"] == platform:
            score += 3
        if content_type and t["content_type"] == content_type:
            score += 3
        if product_category:
            for tag in t["tags"]:
                if tag and tag in product_category:
                    score += 1
        if score > best_score:
            best, best_score = t, score
    return dict(best) if best else None
