#!/bin/bash

# LLMQuant News 停止脚本
# 停止所有前后端服务

set -e

# 颜色定义
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# 项目根目录
PROJECT_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
PID_FILE="$PROJECT_ROOT/.pids"

echo -e "${GREEN}========================================${NC}"
echo -e "${GREEN}  停止 LLMQuant News 服务${NC}"
echo -e "${GREEN}========================================${NC}"

# 检查 PID 文件
if [ ! -f "$PID_FILE" ]; then
    echo -e "${YELLOW}未找到 PID 文件，可能服务未在运行${NC}"
    exit 0
fi

# 读取并停止所有进程
echo -e "\n${YELLOW}正在停止服务...${NC}"
while IFS= read -r pid; do
    if [ -n "$pid" ]; then
        if kill -0 "$pid" 2>/dev/null; then
            echo -e "停止进程 PID: $pid"
            kill "$pid" 2>/dev/null || true
            # 等待进程结束
            for i in {1..10}; do
                if ! kill -0 "$pid" 2>/dev/null; then
                    break
                fi
                sleep 0.5
            done
            # 强制终止如果还在运行
            if kill -0 "$pid" 2>/dev/null; then
                echo -e "${YELLOW}强制终止 PID: $pid${NC}"
                kill -9 "$pid" 2>/dev/null || true
            fi
        fi
    fi
done < "$PID_FILE"

# 删除 PID 文件
rm -f "$PID_FILE"

# 清理日志文件（可选，默认保留）
# rm -f "$PROJECT_ROOT/backend.log" "$PROJECT_ROOT/frontend.log"

echo -e "\n${GREEN}========================================${NC}"
echo -e "${GREEN}  所有服务已停止！${NC}"
echo -e "${GREEN}========================================${NC}"
