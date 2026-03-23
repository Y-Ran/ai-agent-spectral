# AI Agent Spectral

Claude Code 人格配置与自动化对话测试工具。

## 目录结构

```
personas/           # 人格配置文件
  ams-persona-prompt.md           # 爱弥斯（鸣潮）
  catgirl-persona-prompt.md       # 猫娘
  old-beijing-persona-prompt.md   # 老北京
  persona-extraction-guide.md     # 人格提取指南

testing/            # 自动对话测试
  persona_test.py                 # 测试脚本
  reports/                        # 测试报告输出目录
```

## 使用人格配置

在 `~/.claude/CLAUDE.md` 中通过 `@` 引用人格文件：

```markdown
@personas/ams-persona-prompt.md
```

人格文件通过符号链接从本项目映射到 `~/.claude/personas/`。

## 自动对话测试

测试工具通过两个独立的 Claude CLI 会话模拟用户与 AI 的多轮对话，用于评估人格配置的输出质量。

```bash
# 从项目根目录运行
python testing/persona_test.py --persona personas/ams-persona-prompt.md --rounds 10
```

参数：

| 参数 | 默认值 | 说明 |
|------|--------|------|
| `--persona` | (必填) | 人格文件路径（相对于项目根目录） |
| `--rounds` | 10 | 对话轮数 |
| `--output` | `testing/reports/` | 报告输出目录 |
| `--model` | `sonnet` | 模型名称 |

测试报告包含完整对话记录和 7 个评估维度的覆盖情况表。

## 依赖

- Python 3.10+
- Claude Code CLI（已认证，使用包月订阅额度）
