#!/bin/bash

# LLMQuant News 启动脚本
# 同时启动前后端服务

set -e

# 颜色定义
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# 项目根目录
PROJECT_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
PID_FILE="$PROJECT_ROOT/.pids"

# 检查是否已经在运行
if [ -f "$PID_FILE" ]; then
    echo -e "${YELLOW}警告: 发现已存在的 PID 文件，可能服务已在运行${NC}"
    echo "如需重新启动，请先运行 ./stop.sh"
    exit 1
fi

echo -e "${GREEN}========================================${NC}"
echo -e "${GREEN}  启动 LLMQuant News 服务${NC}"
echo -e "${GREEN}========================================${NC}"

# 创建 PID 文件
touch "$PID_FILE"

# 启动后端
echo -e "\n${YELLOW}[1/2] 启动后端服务...${NC}"
cd "$PROJECT_ROOT/backend"

# 检查虚拟环境
if [ -d ".venv" ]; then
    source .venv/bin/activate
elif [ -d "venv" ]; then
    source venv/bin/activate
fi

# 后台启动 uvicorn
python -m uvicorn app.main:app --reload --host 0.0.0.0 --port 8000 > "$PROJECT_ROOT/backend.log" 2>&1 &
BACKEND_PID=$!
echo $BACKEND_PID >> "$PID_FILE"
echo -e "${GREEN}后端已启动 (PID: $BACKEND_PID)${NC}"
echo -e "${GREEN}后端日志: backend.log${NC}"

# 等待后端启动
sleep 2

# 启动前端
echo -e "\n${YELLOW}[2/2] 启动前端服务...${NC}"
cd "$PROJECT_ROOT/frontend"

# 检查 node_modules
if [ ! -d "node_modules" ]; then
    echo -e "${YELLOW}安装前端依赖...${NC}"
    npm install
fi

# 后台启动前端
npm run dev > "$PROJECT_ROOT/frontend.log" 2>&1 &
FRONTEND_PID=$!
echo $FRONTEND_PID >> "$PID_FILE"
echo -e "${GREEN}前端已启动 (PID: $FRONTEND_PID)${NC}"
echo -e "${GREEN}前端日志: frontend.log${NC}"

# 等待前端启动
sleep 2

echo -e "\n${GREEN}========================================${NC}"
echo -e "${GREEN}  所有服务已启动！${NC}"
echo -e "${GREEN}========================================${NC}"
echo ""
echo -e "${YELLOW}访问地址:${NC}"
echo -e "  前端: ${GREEN}http://localhost:3000${NC}"
echo -e "  后端 API: ${GREEN}http://localhost:8000${NC}"
echo -e "  API 文档: ${GREEN}http://localhost:8000/docs${NC}"
echo ""
echo -e "${YELLOW}管理命令:${NC}"
echo -e "  停止服务: ${GREEN}./scripts/stop.sh${NC}"
echo -e "  查看日志: ${GREEN}tail -f backend.log frontend.log${NC}"
echo ""
echo -e "PID 文件: $PID_FILE"
