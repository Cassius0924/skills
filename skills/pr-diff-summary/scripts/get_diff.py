#!/usr/bin/env python3
"""PR Diff 获取工具

获取当前分支相对于目标分支的差异内容，供 AI 生成改动总结使用。
先获取 --stat 概览，再逐文件获取详细 diff。

用法:
    python get_diff.py [--source SOURCE] [--target TARGET] [--max-lines N] [--output text|json]
"""

from __future__ import annotations

import argparse
import json
import subprocess
import sys
from typing import Dict, List, Optional, Tuple


def run_git(args: List[str]) -> Tuple[int, str, str]:
    """执行 git 命令，返回 (returncode, stdout, stderr)。"""
    result = subprocess.run(
        ["git"] + args,
        capture_output=True,
        text=True,
    )
    return result.returncode, result.stdout.strip(), result.stderr.strip()


def detect_target_branch() -> str:
    """自动检测目标分支：优先 main，其次 master，同时检查本地和远程。"""
    candidates = [
        ("refs/heads/main", "main"),
        ("refs/remotes/origin/main", "origin/main"),
        ("refs/heads/master", "master"),
        ("refs/remotes/origin/master", "origin/master"),
    ]
    for ref, name in candidates:
        code, _, _ = run_git(["rev-parse", "--verify", ref])
        if code == 0:
            return name
    print(
        "错误: 未找到 main 或 master 分支，请通过 --target 手动指定目标分支",
        file=sys.stderr,
    )
    sys.exit(1)


def get_current_branch() -> str:
    """获取当前分支名。"""
    code, branch, err = run_git(["rev-parse", "--abbrev-ref", "HEAD"])
    if code != 0:
        print(f"错误: 无法获取当前分支 — {err}", file=sys.stderr)
        sys.exit(1)
    return branch


def get_diff_stat(base: str, source: str) -> str:
    """获取 diff --stat 概览。"""
    code, stat, err = run_git(["diff", "--stat", f"{base}..{source}"])
    if code != 0:
        print(f"错误: 获取 diff stat 失败 — {err}", file=sys.stderr)
        sys.exit(1)
    return stat


def get_changed_files(base: str, source: str) -> List[str]:
    """获取变更文件列表。"""
    code, output, err = run_git(["diff", "--name-only", f"{base}..{source}"])
    if code != 0:
        print(f"错误: 获取变更文件列表失败 — {err}", file=sys.stderr)
        sys.exit(1)
    return [f for f in output.split("\n") if f]


def get_file_diff(base: str, source: str, filepath: str, max_lines: int) -> str:
    """获取单个文件的详细 diff，超过 max_lines 则截断。"""
    code, diff, err = run_git(["diff", f"{base}..{source}", "--", filepath])
    if code != 0:
        return f"[获取 {filepath} 的 diff 失败: {err}]"

    lines = diff.split("\n")
    if len(lines) > max_lines:
        truncated = "\n".join(lines[:max_lines])
        return (
            truncated
            + f"\n\n... [截断: 该文件 diff 共 {len(lines)} 行，仅展示前 {max_lines} 行]"
        )
    return diff


def resolve_merge_base(target: str, source: str) -> str:
    """获取 merge-base，失败时回退到 target 本身。"""
    code, base, _ = run_git(["merge-base", target, source])
    if code == 0:
        return base
    return target


def main() -> None:
    parser = argparse.ArgumentParser(
        description="获取分支间的 diff 内容，用于 PR 改动总结"
    )
    parser.add_argument("--source", default=None, help="源分支（默认: 当前分支）")
    parser.add_argument(
        "--target", default=None, help="目标分支（默认: 自动检测 main/master）"
    )
    parser.add_argument(
        "--max-lines",
        type=int,
        default=300,
        help="每个文件最大 diff 行数（默认: 300）",
    )
    parser.add_argument(
        "--output",
        choices=["json", "text"],
        default="text",
        help="输出格式（默认: text）",
    )
    args = parser.parse_args()

    source = args.source or get_current_branch()
    target = args.target or detect_target_branch()

    # 获取 merge-base 作为比较基准
    base = resolve_merge_base(target, source)

    # 1. stat 概览
    stat = get_diff_stat(base, source)

    # 2. 变更文件列表
    files = get_changed_files(base, source)

    # 3. 逐文件获取详细 diff
    file_diffs = {}  # type: Dict[str, str]
    for f in files:
        file_diffs[f] = get_file_diff(base, source, f, args.max_lines)

    # 输出
    if args.output == "json":
        result = {
            "source_branch": source,
            "target_branch": target,
            "merge_base": base[:12] if len(base) > 12 else base,
            "stat": stat,
            "changed_files": files,
            "file_count": len(files),
            "file_diffs": file_diffs,
        }
        print(json.dumps(result, ensure_ascii=False, indent=2))
    else:
        print(f"=== 分支对比: {source} -> {target} ===\n")
        print(f"--- STAT 概览 ---\n{stat}\n")
        print(f"--- 变更文件数: {len(files)} ---\n")
        for f in files:
            print("=" * 60)
            print(f"文件: {f}")
            print("=" * 60)
            print(file_diffs[f])
            print()


if __name__ == "__main__":
    main()
