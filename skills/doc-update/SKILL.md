---
name: doc-update
description: 项目收尾时更新文档和README，根据代码变更检查并同步更新相关文档
---

## 更新范围

### 1. README.md 检查项
- [ ] 功能特性列表是否完整
- [ ] 技术栈版本是否最新
- [ ] 部署步骤是否准确
- [ ] API端点文档是否更新
- [ ] 环境变量说明是否完整

### 2. API 文档
- [ ] 新增/修改的接口是否已记录
- [ ] 请求/响应参数是否准确
- [ ] 错误码说明是否完善

### 3. 配置文档
- [ ] 爬虫配置示例是否更新
- [ ] 推送渠道配置说明
- [ ] AI模型配置选项

### 4. 代码注释
- [ ] 复杂业务逻辑是否有中文注释
- [ ] 公共函数是否有docstring
- [ ] 配置项是否有说明

## 更新流程

### 步骤1: 扫描变更
```bash
# 查看最近的代码变更
git diff HEAD~10 --name-only

# 检查新增文件
git status --short
```

### 步骤2: 文档同步检查

1. **功能变更检查**
   ```
   新功能: 自动识别 → 检查README功能列表
   功能删除: 自动识别 → 从文档中移除
   功能修改: 自动识别 → 更新相关说明
   ```

2. **API变更检查**
   ```
   新增端点: routers/新增 → 更新API文档
   参数变更: schemas/修改 → 更新请求示例
   路由变更: main.py/注册 → 更新路由列表
   ```

3. **配置变更检查**
   ```
   config.py修改 → 更新环境变量说明
   models.py修改 → 更新数据模型文档
   ```

### 步骤3: 具体更新任务

#### README.md 更新模板

```markdown
## 更新检查清单

### 新增功能
- [ ] 在"功能特性"部分添加
- [ ] 在"快速开始"添加使用说明（如需要）

### API变更
- [ ] 更新API端点列表
- [ ] 添加/修改接口说明

### 配置变更
- [ ] 更新.env.example
- [ ] 在README添加配置说明
```

#### 爬虫配置文档更新

当修改 `backend/app/crawler/` 目录时：

1. 检查 `crawler_scripts/README.md` 是否需要更新
2. 更新爬虫配置示例
3. 添加新爬虫类型的说明

## 自动化更新建议

### 预提交检查

```bash
#!/bin/bash
# .git/hooks/pre-commit

# 检查文档是否过期
python scripts/check_doc_sync.py

# 检查README链接
markdown-link-check README.md
```

### 文档同步脚本

```python
# scripts/check_doc_sync.py

def check_doc_sync():
    """检查代码和文档是否同步"""
    
    # 1. 检查API路由和文档
    api_routes = extract_api_routes()
    doc_apis = extract_doc_apis()
    
    missing_in_doc = api_routes - doc_apis
    if missing_in_doc:
        print(f"警告: 以下API未在文档中说明: {missing_in_doc}")
    
    # 2. 检查配置项
    config_vars = extract_config_vars()
    doc_configs = extract_doc_configs()
    
    missing_configs = config_vars - doc_configs
    if missing_configs:
        print(f"警告: 以下配置项未在文档中说明: {missing_configs}")
    
    # 3. 检查功能列表
    features = extract_features_from_code()
    doc_features = extract_doc_features()
    
    if features != doc_features:
        print("建议: README功能列表可能需要更新")
```

## 文档更新规范

### 新增爬虫类型时

1. 更新 `README.md` - 功能特性部分
2. 更新 `AGENTS.md` - 爬虫规范部分
3. 更新 `crawler_scripts/README.md` - 添加示例
4. 添加配置示例到 `.env.example`

### 新增API端点时

1. 在代码中添加docstring（中文）
2. 更新API文档（如有独立文档）
3. 更新README中的API列表（如公开API）

### 修改数据模型时

1. 更新 `backend/app/schemas.py` 中的注释
2. 更新数据库迁移说明
3. 更新API文档中的响应示例

## 更新优先级

### P0 - 必须更新
- README中的部署步骤
- API重大变更
- 环境变量变更

### P1 - 建议更新
- 功能列表
- 配置示例
- 错误码说明

### P2 - 可选更新
- 代码注释完善
- 架构图更新
- 使用示例优化

## 验收标准

- [ ] README可以指导新用户完成部署
- [ ] 所有公共API都有文档说明
- [ ] 配置文件示例与实际代码一致
- [ ] 没有过时的文档内容
- [ ] 链接和引用都有效
