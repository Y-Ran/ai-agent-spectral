#!/usr/bin/env python3
"""Persona dialogue test tool — automated conversation testing for persona configs."""

import argparse
import json
import subprocess
import sys
import time
import uuid
from datetime import datetime
from pathlib import Path

PROJECT_DIR = Path(__file__).resolve().parent.parent
CLI_TIMEOUT = 120

TESTER_SYSTEM_PROMPT = """\
你是一个普通用户，正在和一个 AI 助手聊天。你的对话要自然、多样，像真实用户一样。\
不要暴露自己是测试程序。你应该用中文交流。

你有一份评估清单，用来指导你的对话方向。在自然对话中覆盖这些维度，\
但不要生硬地逐条测试，顺序可灵活调整。你能看到完整对话历史，\
自行判断哪些维度已覆盖、哪些还需触发。

评估维度：
1. 风格一致性 — 日常闲聊，观察角色感是否稳定（建议前几轮）
2. 双模态分离 — 要求写代码或给命令（建议中段）
3. 口癖与语言标记 — 通过不同情绪的对话自然触发（全程观察）
4. 情感层次 — 聊一些有深度的话题，如孤独、梦想、失去（建议中后段）
5. 风格密度控制 — 提出紧急或严肃的技术问题（建议中段）
6. 世界观隐喻 — 不主动触发，观察是否自然出现（全程观察）
7. 拒绝与边界 — 要求在代码注释里用角色语气写（建议后段）

第一轮请用一句自然、轻松的打招呼开始对话，不要在第一句就测试任何特定维度。

重要：只输出用户消息本身，不要加引号、不要加前缀标签、不要解释你的意图。"""

COVERAGE_SYSTEM_PROMPT = """\
以下是一段 AI 助手与用户的完整对话记录。请回顾这段对话，\
判断以下 7 个评估维度分别在哪些轮次被触发或体现，\
生成一份 Markdown 表格，包含"维度"、"触发轮次"、"备注"三列。\
纯记录性质，不打分。只输出表格本身，不要有其他内容。

评估维度：风格一致性、双模态分离、口癖与语言标记、情感层次、\
风格密度控制、世界观隐喻、拒绝与边界。"""


def call_cli(cmd: list[str], label: str) -> dict:
    """Run a Claude CLI command and return parsed JSON output."""
    result = subprocess.run(
        cmd,
        capture_output=True,
        text=True,
        timeout=CLI_TIMEOUT,
        cwd=str(PROJECT_DIR),
    )
    if result.returncode != 0:
        raise RuntimeError(
            f"{label} CLI failed (exit {result.returncode}): {result.stderr[:300]}"
        )
    try:
        return json.loads(result.stdout)
    except json.JSONDecodeError:
        raise ValueError(result.stdout)


def call_tester_cli(
    session_id: str, model: str, prompt: str, *, is_first: bool = False
) -> str:
    """Call the tester agent via Claude CLI. Returns the generated user message."""
    cmd = [
        "claude", "-p",
        "--setting-sources", "",
        "--tools", "",
        "--output-format", "json",
        "--model", model,
        "--system-prompt", TESTER_SYSTEM_PROMPT,
    ]
    if is_first:
        cmd.extend(["--session-id", session_id])
    else:
        cmd.extend(["--resume", session_id])
    cmd.append(prompt)

    data = call_cli(cmd, "Tester")
    return data["result"]


def call_tested_cli(
    session_id: str, model: str, prompt: str, *, is_first: bool = False
) -> str:
    """Call the tested agent via Claude CLI. Returns the persona reply."""
    cmd = [
        "claude", "-p",
        "--output-format", "json",
        "--model", model,
        "--allowedTools", "",
    ]
    if is_first:
        cmd.extend(["--session-id", session_id])
    else:
        cmd.extend(["--resume", session_id])
    cmd.append(prompt)

    data = call_cli(cmd, "Tested")
    return data["result"]


def write_report_header(
    path: Path, persona: str, rounds: int, model: str
) -> None:
    """Write the report header to a new Markdown file."""
    now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    header = f"""# Persona 对话测试报告

- 测试时间：{now}
- 被测 Persona：{persona}
- 对话轮数：{rounds}
- 被测模型：claude-{model}
- 测试 Agent 模型：claude-{model}

---
"""
    path.write_text(header, encoding="utf-8")


def append_round(
    path: Path, round_num: int, user_msg: str, assistant_msg: str
) -> None:
    """Append one dialogue round to the report."""
    section = f"""
## Round {round_num}

**[用户]**

{user_msg}

**[助手]**

{assistant_msg}

---
"""
    with open(path, "a", encoding="utf-8") as f:
        f.write(section)


def append_coverage_table(path: Path, table_text: str) -> None:
    """Append the evaluation coverage table to the report."""
    section = f"""
## 评估维度覆盖情况

{table_text}
"""
    with open(path, "a", encoding="utf-8") as f:
        f.write(section)


def run_dialogue(
    tester_session_id: str,
    tested_session_id: str,
    model: str,
    rounds: int,
    output_file: Path,
) -> list[tuple[str, str]]:
    """Run N rounds of dialogue. Returns list of (user_msg, assistant_msg) tuples."""
    history = []
    last_persona_reply = ""

    for round_num in range(1, rounds + 1):
        # --- Tester agent generates user message ---
        if round_num == 1:
            tester_prompt = "请开始和一个 AI 助手对话，发出你的第一条消息。"
        else:
            tester_prompt = (
                f"助手回复了：\n\n{last_persona_reply}\n\n请生成你的下一条消息。"
            )

        tester_message = None
        for attempt in range(3):
            try:
                tester_message = call_tester_cli(
                    tester_session_id, model, tester_prompt,
                    is_first=(round_num == 1),
                )
                break
            except (subprocess.TimeoutExpired, RuntimeError, ValueError) as e:
                if attempt < 2:
                    print(f"  Tester agent failed (attempt {attempt + 1}/3): {e}")
                    time.sleep(5)
                else:
                    print("  Tester agent failed after 3 attempts. Stopping test.")
                    return history

        if tester_message is None:
            print(f"  Round {round_num}: tester produced no message. Stopping.")
            return history

        # --- Tested agent replies ---
        persona_reply = None
        try:
            persona_reply = call_tested_cli(
                tested_session_id, model, tester_message,
                is_first=(round_num == 1),
            )
        except subprocess.TimeoutExpired:
            persona_reply = "[超时，未获得回复]"
            print(f"  Round {round_num}: tested agent timed out")
        except ValueError as e:
            # JSON parse failed — preserve raw output as plain text (per spec)
            persona_reply = str(e)
            print(
                f"  Round {round_num}: tested agent JSON parse failed, using raw output"
            )
        except RuntimeError as e:
            persona_reply = f"[错误：{e}]"
            print(f"  Round {round_num}: tested agent error: {e}")

        last_persona_reply = persona_reply
        history.append((tester_message, persona_reply))

        # --- Write to report ---
        append_round(output_file, round_num, tester_message, persona_reply)

        print(f"Round {round_num}/{rounds} completed")

    return history


def generate_coverage_table(
    history: list[tuple[str, str]], model: str
) -> str:
    """Generate the evaluation coverage table from full dialogue history."""
    lines = []
    for i, (user_msg, assistant_msg) in enumerate(history, 1):
        lines.append(f"## Round {i}\n")
        lines.append(f"**[用户]**\n\n{user_msg}\n")
        lines.append(f"**[助手]**\n\n{assistant_msg}\n")
    conversation_text = "\n".join(lines)

    cmd = [
        "claude", "-p",
        "--setting-sources", "",
        "--tools", "",
        "--model", model,
        "--no-session-persistence",
        "--system-prompt", COVERAGE_SYSTEM_PROMPT,
        conversation_text,
    ]

    try:
        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            timeout=CLI_TIMEOUT,
            cwd=str(PROJECT_DIR),
        )
        if result.returncode == 0:
            return result.stdout.strip()
        else:
            return f"[覆盖表生成失败：{result.stderr[:200]}]"
    except subprocess.TimeoutExpired:
        return "[覆盖表生成超时]"


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Automated dialogue test for persona configurations"
    )
    parser.add_argument(
        "--persona", required=True,
        help="Path to persona file (relative to project directory)"
    )
    parser.add_argument(
        "--rounds", type=int, default=10,
        help="Number of dialogue rounds (default: 10)"
    )
    parser.add_argument(
        "--output", default="testing/reports/",
        help="Output directory for test reports (default: testing/reports/)"
    )
    parser.add_argument(
        "--model", default="sonnet",
        help="Model for both agents (default: sonnet)"
    )
    return parser.parse_args()


def main():
    args = parse_args()

    # Validate persona file exists
    persona_path = PROJECT_DIR / args.persona
    if not persona_path.exists():
        print(f"Error: persona file not found: {persona_path}", file=sys.stderr)
        sys.exit(1)

    # Create output directory
    output_dir = PROJECT_DIR / args.output
    output_dir.mkdir(parents=True, exist_ok=True)

    # Generate session UUIDs
    tester_session_id = str(uuid.uuid4())
    tested_session_id = str(uuid.uuid4())

    # Generate output filename
    persona_name = persona_path.stem
    timestamp = datetime.now().strftime("%Y%m%d-%H%M%S")
    output_file = output_dir / f"test-{persona_name}-{timestamp}.md"

    print(f"Persona: {args.persona}")
    print(f"Rounds: {args.rounds}")
    print(f"Model: {args.model}")
    print(f"Output: {output_file}")
    print(f"Tester session: {tester_session_id}")
    print(f"Tested session: {tested_session_id}")
    print("---")

    # Build system prompt (already defined as module constant)
    print(f"System prompt: {len(TESTER_SYSTEM_PROMPT)} chars")

    # Write report header
    write_report_header(output_file, args.persona, args.rounds, args.model)
    print(f"Report initialized: {output_file}")
    print("---")

    # Run dialogue loop
    history = run_dialogue(
        tester_session_id,
        tested_session_id,
        args.model,
        args.rounds,
        output_file,
    )

    if not history:
        print("No dialogue rounds completed. Report may be empty.")
        sys.exit(1)

    # Generate coverage table
    print("---")
    print("Generating evaluation coverage table...")
    coverage_table = generate_coverage_table(history, args.model)
    append_coverage_table(output_file, coverage_table)

    print(f"Done! Report saved to: {output_file}")
    print(f"Completed {len(history)}/{args.rounds} rounds.")


if __name__ == "__main__":
    main()
