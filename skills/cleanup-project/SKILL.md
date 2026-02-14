---
name: cleanup-project
description: 项目收尾时清理无用文件，包括Python缓存、测试废物文件、日志等，保持项目整洁
---

## 清理范围

### 1. Python缓存文件
- `__pycache__/` 目录（所有层级）
- `*.pyc` 文件
- `*.pyo` 文件
- `*.pyd` 文件（Windows）

### 2. 测试相关文件
- `.pytest_cache/` 目录
- `htmlcov/` 覆盖率报告目录
- `.coverage` 覆盖率数据文件
- `test-results/` 测试结果目录

### 3. 开发环境文件
- `.mypy_cache/` 类型检查缓存
- `node_modules/.cache/`（如有）

### 4. 日志文件（可选）
- `*.log` 文件（超过7天的）
- `logs/` 目录中的旧日志

### 5. 构建产物（可选）
- `dist/` 目录（构建输出）
- `build/` 目录（构建中间文件）
- `frontend/dist/`（前端构建产物）

## 清理步骤

1. **扫描阶段**
   - 递归查找所有 `__pycache__` 目录
   - 查找所有 `.pyc`、`.pyo` 文件
   - 识别测试缓存和日志文件

2. **确认阶段**
   - 列出将要清理的文件/目录清单
   - 显示预计释放的空间大小
   - 等待用户确认

3. **执行阶段**
   - 安全删除（使用 `rm -rf` 或 `os.remove`）
   - 记录已清理的项目

4. **验证阶段**
   - 检查是否还有残留
   - 生成清理报告

## 使用方法

```bash
# 项目根目录下执行
python scripts/cleanup.py

# 或手动清理
cd backend && find . -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null
find . -type f -name "*.pyc" -delete
```

## 注意事项

- 生产环境不要运行此脚本（避免删除运行中的缓存）
- 清理前确保所有测试已通过（`.pytest_cache` 可以安全删除）
- 不要删除 `.env` 文件或配置目录
- 清理日志文件前确认是否需要保留历史记录

## 安全白名单

以下文件/目录**禁止**清理：
- `.env`、`.env.local` 等环境配置文件
- `data/` 数据目录
- `uploads/` 上传文件目录
- `config/` 配置目录
- Git仓库相关：`.git/`
