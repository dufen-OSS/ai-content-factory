#!/usr/bin/env bash
# 把最新代码同步进 HF Space 部署目录（改代码后重新部署前跑一次）
set -e
cd "$(dirname "$0")/.."

rm -rf deploy/space/app deploy/space/frontend
cp -r app deploy/space/app
cp -r frontend deploy/space/frontend
cp requirements.txt deploy/space/requirements.txt

# 清理缓存产物
find deploy/space -name __pycache__ -type d -exec rm -rf {} + 2>/dev/null || true
rm -rf deploy/space/app/.pytest_cache 2>/dev/null || true

echo "✅ 已同步 app/ frontend/ requirements.txt -> deploy/space/"
echo "下一步：cd deploy/space && git add . && git commit && git push"
