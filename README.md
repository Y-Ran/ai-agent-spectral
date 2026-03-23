# AI Agent Spectral

让你的 AI Agent 拥有灵魂。

AI Agent Spectral 是一套为 Claude Code 设计的**人格配置框架**——从角色素材中提取人格特征，生成结构化的 persona prompt，并通过自动化对话测试验证效果。

## 特色

**双模态架构** — 对话中保持鲜明的角色感（语气词、口癖、情感层次），代码和文档等交付物自动切换为中性专业输出，不会在你的 commit message 里冒出"哈哈~"。

**完整的提取方法论** — 从原始台词到可用的 persona prompt，覆盖世界观集成、语言模式分析、情感行为建模、风格密度控制等维度，附带[鸣潮角色实例](persona-extraction-demo-wuthering-waves.md)作为参考。

**自动化对话测试** — 一个 vanilla agent 扮演用户，被测 agent 加载 persona 回复，自动跑 N 轮对话并生成评估报告。不用自己一句句试，跑一次就能看到人格在闲聊、技术问答、情感深度、边界拒绝等场景下的表现。

**即插即用** — persona 文件就是一个 Markdown，放到 `~/.claude/CLAUDE.md` 里用 `@` 引用即可生效，无需额外依赖。

## 目录结构

```
persona-extraction-guide.md                  # 通用人格提取指南
persona-extraction-demo-wuthering-waves.md   # 提取实例（鸣潮·爱弥斯）

personas/                                    # 人格配置文件
  ams-persona-prompt.md                      #   爱弥斯 — 明朗温暖的电子幽灵
  catgirl-persona-prompt.md                  #   猫娘 — 傲娇可爱
  old-beijing-persona-prompt.md              #   老北京 — 京腔京韵

testing/                                     # 自动对话测试
  persona_test.py                            #   测试脚本
  reports/                                   #   测试报告输出（git 排除）
```

## 快速开始

### 使用现有人格

在 `~/.claude/CLAUDE.md` 中引用人格文件：

```markdown
@personas/ams-persona-prompt.md
```

人格文件通过符号链接从本项目映射到 `~/.claude/personas/`。

### 创建新人格

参考 [persona-extraction-guide.md](persona-extraction-guide.md) 中的五阶段流程，从角色素材生成配置文件。也可以直接让 Claude Code 帮你提取：

```
请根据以下角色素材，参考 personas/ 目录下已有配置的双模态架构，
生成一份 [角色名] 的人格配置文件，输出到 personas/[角色名]-persona-prompt.md。
```

### 测试人格效果

```bash
python testing/persona_test.py --persona personas/ams-persona-prompt.md --rounds 10
```

| 参数 | 默认值 | 说明 |
|------|--------|------|
| `--persona` | (必填) | 人格文件路径（相对于项目根目录） |
| `--rounds` | 10 | 对话轮数 |
| `--output` | `testing/reports/` | 报告输出目录 |
| `--model` | `sonnet` | 模型名称 |

测试报告包含完整对话记录和 7 个评估维度的覆盖情况：

| 评估维度 | 说明 |
|---------|------|
| 风格一致性 | 角色感在多轮对话中是否稳定 |
| 双模态分离 | 对话区 vs 产物区的切换是否正确 |
| 口癖与语言标记 | 标志性表达是否自然出现 |
| 情感层次 | 表层/底层情感的触发与转换 |
| 风格密度控制 | 不同场景下风格浓度是否合适 |
| 世界观隐喻 | 角色背景的隐喻是否自然融入 |
| 拒绝与边界 | 面对违规请求时的拒绝方式 |

## 依赖

- Python 3.10+
- [Claude Code CLI](https://docs.anthropic.com/en/docs/claude-code)（已认证，使用包月订阅额度）
