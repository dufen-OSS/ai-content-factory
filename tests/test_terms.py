"""违禁词检测与返修替换测试。"""
from app.terms import find_banned, sanitize


def test_find_banned_hits():
    text = "全网最低价，销量第一，绝对好，纯天然无副作用"
    hits = find_banned(text)
    assert "全网最低" in hits
    assert "销量第一" in hits
    assert "绝对" in hits


def test_find_banned_clean():
    assert find_banned("高性价比，口碑很好，值得回购") == []


def test_sanitize_replaces_banned():
    out = sanitize("这是全网最低价，第一品牌")
    assert "全网最低" not in out
    assert "第一品牌" not in out
    assert find_banned(out) == []


def test_sanitize_idempotent():
    text = "高性价比之选"
    assert sanitize(text) == text
