# Oh My OpenCode 配置说明

本目录包含 LLMQuantNews 项目的 Oh My OpenCode 配置文件。

## 文件结构

```
.opencode/
├── oh-my-opencode.json    # 项目级配置
└── README.md              # 本说明文件
```

## 配置说明

### oh-my-opencode.json

```json
{
  "agents": {
    "planner-sisyphus": {
      "enabled": true,      // 启用默认规划 Agent
      "replace_plan": true  // 替换 OpenCode 默认 plan agent
    },
    "explore": {
      "enabled": true       // 启用代码探索 Agent
    },
    "oracle": {
      "enabled": true       // 启用问答 Agent
    }
  },
  "disabled_mcps": [],      // 禁用的 MCPs（空=全部启用）
  "experimental": {
    "preemptive_compaction_threshold": 0.85,  // 上下文压缩阈值
    "context_window_monitor_enabled": true    // 启用上下文监控
  },
  "hooks": {
    "todo-continuation-enforcer": { "enabled": true },  // 任务完成强制
    "context-window-monitor": { "enabled": true },      // 上下文监控
    "preemptive-compaction": { "enabled": true },       // 主动压缩
    "agent-usage-reminder": { "enabled": true }         // Agent 使用提醒
  },
  "skills": {
    "enabled": true,
    "paths": ["./skills"]   // 自定义 skills 路径
  },
  "project": {
    "name": "LLMQuantNews",
    "description": "AI 新闻量化分析平台",
    "language": "zh-CN",    // 代码注释语言
    "code_style": {
      "python": {
        "formatter": "black",
        "line_length": 88,
        "comments": "chinese"
      },
      "typescript": {
        "component_naming": "PascalCase",
        "styling": "MUI sx prop"
      }
    }
  }
}
```

## 可用 Skills

项目提供 5 个自定义 skills，位于项目根目录的 `skills/` 文件夹：

| Skill | 说明 | 使用场景 |
|-------|------|----------|
| `cleanup-project` | 清理 Python 缓存、测试废物、日志 | 开发完成后 |
| `crawler-testing` | 测试所有爬虫和信息源 | 添加新信息源后 |
| `doc-update` | 根据代码变更更新文档 | 功能开发完成后 |
| `news-analysis` | 测试 AI 评分和分析功能 | AI 功能修改后 |
| `api-testing` | 测试 API 端点完整性 | API 开发完成后 |

### 运行 Skills

```bash
# 在项目根目录运行
skill cleanup-project
skill crawler-testing
skill news-analysis
skill api-testing
skill doc-update
```

## Category 委派系统

Oh My OpenCode 支持根据任务类型自动委派到最优模型：

### visual-engineering
用于前端、UI/UX、设计、动画任务
```typescript
task(
  category="visual-engineering",
  load_skills=["playwright", "frontend-ui-ux"],
  prompt="..."
)
```

### quick
用于简单任务、单文件修改、typo 修复
```typescript
task(
  category="quick",
  load_skills=["git-master"],
  prompt="..."
)
```

### deep
用于复杂问题、需要深度推理的任务
```typescript
task(
  category="deep",
  load_skills=[],
  prompt="..."
)
```

### ultrabrain
用于高难度逻辑任务（谨慎使用）
```typescript
task(
  category="ultrabrain",
  load_skills=[],
  prompt="..."
)
```

## MCP 集成

### grep.app
在数百万 GitHub 仓库中搜索代码示例：
- 查找 FastAPI 最佳实践
- 搜索 React 组件模式
- 发现 Celery 配置示例

### Context7
获取最新的官方文档：
- LiteLLM API 文档
- FastAPI 官方指南
- React/MUI 文档

## 工作流示例

### 新功能开发
1. 使用 `explore` agent 研究现有代码模式
2. 使用 `librarian` agent 查询相关文档
3. 实现功能（遵循 AGENTS.md 规范）
4. 运行 `skill api-testing` 验证
5. 运行 `skill doc-update` 更新文档
6. 运行 `skill cleanup-project` 清理

### 爬虫开发
1. 继承 `BaseNewsCrawler` 基类
2. 实现 `fetch()` 和 `parse()` 方法
3. 注册到 `crawler/manager.py`
4. 配置信息源
5. 运行 `skill crawler-testing` 验证

### AI 模型调试
1. 修改 `backend/.env` 中的模型配置
2. 运行 `python backend/test_ai_config.py`
3. 运行 `skill news-analysis` 全面测试
4. 检查成本报告并优化

## 最佳实践

### 代码质量
- ✅ 所有新函数添加类型提示
- ✅ 业务逻辑注释使用中文
- ✅ 生产环境使用 logging 不用 print
- ✅ 遵循 Black 格式化（88 字符）

### 测试覆盖
- ✅ 新增 API 端点必须添加测试
- ✅ 修改爬虫必须运行连通性测试
- ✅ AI 功能修改必须测试多模型

### 文档同步
- ✅ 功能开发后运行 `skill doc-update`
- ✅ README 能指导新用户部署
- ✅ 所有公共 API 有文档说明

## 参考资料

- [Oh My OpenCode GitHub](https://github.com/code-yeongyu/oh-my-opencode)
- [AGENTS.md](../AGENTS.md) - 项目编码规范
- [README.md](../README.md) - 项目主文档

## 故障排除

### Skills 不工作
1. 确认 `.opencode/oh-my-opencode.json` 中 `skills.paths` 配置正确
2. 确认 skills 目录包含有效的 `SKILL.md` 文件
3. 检查 skill 名称与目录名一致

### MCPs 不工作
1. 检查 `.opencode/oh-my-opencode.json` 中 `disabled_mcps` 配置
2. 确认网络连接正常
3. 查看 OpenCode 日志获取详细错误

### 上下文压缩问题
1. 调整 `preemptive_compaction_threshold`（默认 0.85）
2. 降低阈值会更早压缩，但可能丢失上下文
3. 提高阈值保留更多上下文，但可能超出限制
