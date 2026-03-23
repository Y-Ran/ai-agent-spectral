# AI Agent Spectral

本项目管理 Claude Code 的人格配置文件及自动对话测试工具。

## 项目结构

- `personas/` — 人格配置文件（.md），通过符号链接映射到 `~/.claude/personas/`
- `testing/persona_test.py` — 自动对话测试脚本，从项目根目录运行
- `testing/reports/` — 测试报告输出目录

## 开发约定

- 人格配置文件遵循双模态设计：对话区保持角色感，产物区保持中性专业
- 测试脚本通过 Claude CLI 子进程调用，不依赖 Anthropic API key
- 被测 agent 使用 `--allowedTools ""` 禁用工具调用，确保纯对话输出
- 测试 agent 使用 `--setting-sources "" --tools ""` 隔离人格配置
