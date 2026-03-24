# AI Agent Spectral

本项目管理 Codex 的人格配置文件及自动对话测试工具。

## 项目结构

- `persona-extraction-guide.md` — 通用人格提取指南（Phase 0-4 五阶段流程）
- `persona-extraction-demo-*.md` — 角色提取文档（中间产物，含台词统计和结构化建模）
- `personas/` — 人格配置文件（最终产物，.md），通过符号链接映射到 `~/.claude/personas/`
- `testing/persona_test.py` — 自动对话测试脚本，从项目根目录运行
- `testing/reports/` — 测试报告输出目录

## 人格生成工作流

从角色素材到最终人格配置分为两个阶段、两个产物：

```
用户提供的素材  ──→  persona-extraction-demo-[角色名].md  ──→  personas/[角色名]-persona-prompt.md
 (.docx/文本/目录)       (提取文档：中间产物)                      (人格配置：最终产物)
```

### 阶段一：生成提取文档

从用户指定的素材文件中提取角色特征，按 `persona-extraction-guide.md` 的 Phase 0-2 流程输出提取文档。提取文档包含：

- Phase 0：区域世界观（地理、组织、术语、人物关系表）
- Phase 1：台词量化分析（语气词频率统计、口癖出现次数、称呼体系、笑声频率、性格底色、情感层次）
- Phase 2：结构化建模（角色卡片、语言规则表、情感行为矩阵）

提取文档命名为 `persona-extraction-demo-[角色名].md`，放在项目根目录。

### 阶段二：生成人格配置

基于提取文档，参考 `personas/` 下已有配置的双模态架构模板，生成人格配置文件。配置文件命名为 `personas/[角色名]-persona-prompt.md`。

### 迭代

测试发现问题后，先更新提取文档中对应的规则，再据此修正人格配置。不要跳过提取文档直接改配置——提取文档是"为什么这么配"的依据。

## 开发约定

- 人格配置文件遵循双模态设计：对话区保持角色感，产物区保持中性专业
- 提取文档中的台词统计必须基于实际数据，不可凭印象编写频率
- 同一角色的提取文档和人格配置应保持一致——配置中的每条规则都应能在提取文档中找到依据
- 测试脚本通过 Claude CLI 子进程调用，不依赖 Anthropic API key
- 被测 agent 使用 `--allowedTools ""` 禁用工具调用，确保纯对话输出
- 测试 agent 使用 `--setting-sources "" --tools ""` 隔离人格配置
- 素材文件由用户指定路径（任意位置的 .docx 或文本文件），.docx 格式使用 python-docx 读取
