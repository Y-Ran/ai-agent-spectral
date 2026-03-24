# AI Agent Spectral

让你的 AI Agent 拥有灵魂。

AI Agent Spectral 是一套为 Claude Code 设计的**人格配置框架**——从角色素材中提取人格特征，生成结构化的 persona prompt，并通过自动化对话测试验证效果。

## 特色

**双模态架构** — 对话中保持鲜明的角色感（语气词、口癖、情感层次），代码和文档等交付物自动切换为中性专业输出，不会在你的 commit message 里冒出"哈哈~"。

**完整的提取方法论** — 从原始台词到可用的 persona prompt，覆盖世界观集成、语言模式分析、情感行为建模、风格密度控制等维度，附带[完整实例](persona-extraction-demo-wuthering-waves.md)作为参考。

**自动化对话测试** — 一个 vanilla agent 扮演用户，被测 agent 加载 persona 回复，自动跑 N 轮对话并生成评估报告。不用自己一句句试，跑一次就能看到人格在闲聊、技术问答、情感深度、边界拒绝等场景下的表现。

**即插即用** — persona 文件就是一个 Markdown，放到 `~/.claude/CLAUDE.md` 里用 `@` 引用即可生效，无需额外依赖。

## 目录结构

```
persona-extraction-guide.md                  # 通用人格提取指南（Phase 0-4）
persona-extraction-demo-wuthering-waves.md   # 提取实例：爱弥斯（完整五阶段）
persona-extraction-demo-iuno.md              # 提取实例：尤诺（含台词统计分析）

personas/                                    # 人格配置文件（最终产物）
  ams-persona-prompt.md                      #   爱弥斯 — 明朗温暖的电子幽灵
  iuno-persona-prompt.md                     #   尤诺 — 高傲率真的天才谕女
  catgirl-persona-prompt.md                  #   猫娘 — 傲娇可爱
  old-beijing-persona-prompt.md              #   老北京 — 京腔京韵

testing/                                     # 自动对话测试
  persona_test.py                            #   测试脚本
  reports/                                   #   测试报告输出（git 排除）
```

## 从素材到人格：完整工作流

从一堆角色台词文本生成一份可用的人格配置文件，分为以下阶段：

```
原始素材 (.docx/文本)
    │
    ▼
[Phase 0] 世界观集成 ─── 采集世界观五层信息，建立知识边界
    │
    ▼
[Phase 1] 特征提取 ───── 台词逐行标注，统计语气词/口癖/称呼/笑声频率
    │
    ▼
[Phase 2] 结构化建模 ─── 角色卡片 + 语言规则表 + 情感行为矩阵
    │
    ▼
[Phase 3] 配置文件生成 ─ 填入双模态架构模板，输出 persona prompt
    │
    ▼
[Phase 4] 验证调优 ───── 自动对话测试 → 标注问题 → 回到 Phase 2 修正 → 重新生成
```

### Phase 0-1：素材准备与特征提取

准备角色台词文本（支持 .docx 或纯文本），然后让 Claude Code 提取并统计：

```
请根据以下素材文件，按照 persona-extraction-guide.md 的流程，
生成一份 [角色名] 的角色提取文档，输出到 persona-extraction-demo-[角色名].md。

角色素材：[文件路径，如 ~/downloads/角色台词.docx 或目录路径]

提取要求：
- Phase 0：从台词中提取角色所在区域的世界观设定（地理、组织、术语、人物关系）
- Phase 1：逐行统计语气词频率、口癖出现次数、称呼体系、笑声频率
- 从行为选择（非自述）推断性格底色
- 识别表层/底层情感及转换条件
```

提取文档是中间产物，包含量化统计和结构化建模结果。参考实例：
- [爱弥斯提取文档](persona-extraction-demo-wuthering-waves.md)
- [尤诺提取文档](persona-extraction-demo-iuno.md)（含 404 条台词的频率统计）

### Phase 2-3：建模与配置生成

基于提取文档生成人格配置文件：

```
请根据 persona-extraction-demo-[角色名].md 的提取结果，
参考 personas/ 目录下已有配置的双模态架构，
生成一份 [角色名] 的人格配置文件，输出到 personas/[角色名]-persona-prompt.md。
```

也可以跳过提取文档，直接一步生成（适合简单角色或快速原型）：

```
请根据以下素材，参考 personas/ 目录下已有配置的双模态架构，
生成一份 [角色名] 的人格配置文件，输出到 personas/[角色名]-persona-prompt.md。

角色素材：[文件路径，如 ~/downloads/角色台词.docx 或目录路径]
```

### Phase 4：测试与迭代

```bash
python testing/persona_test.py --persona personas/[角色名]-persona-prompt.md --rounds 10
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

根据测试结果迭代：

1. 标注"出戏"或"不自然"的位置
2. 回到提取文档补充或修正相应规则
3. 重新生成配置文件的对应段落
4. 重跑测试直到满意

常见调优方向见 [persona-extraction-guide.md](persona-extraction-guide.md) 的 Phase 4.2 节。

## 使用人格

在 `~/.claude/CLAUDE.md` 中引用人格文件：

```markdown
@personas/ams-persona-prompt.md
```

人格文件通过符号链接从本项目映射到 `~/.claude/personas/`。

## 依赖

- Python 3.10+（仅测试脚本需要）
- python-docx（仅素材为 .docx 格式时需要：`pip install python-docx`）
- [Claude Code CLI](https://docs.anthropic.com/en/docs/claude-code)（已认证，使用包月订阅额度）
