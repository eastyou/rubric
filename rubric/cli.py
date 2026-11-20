"""命令行入口：生成可打印的评分量规。"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path
from typing import Optional, Sequence

from .model import Rubric, RubricError, load_rubric
from .render import render_html


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="rubric",
        description="评分量规：维度,等级 CSV 一键生成 A4 可打印评价表",
    )
    parser.add_argument("--version", action="version", version="rubric 0.1.0")
    parser.add_argument(
        "-i", "--input", required=True, help="量规 CSV（维度,优秀,良好,合格...）"
    )
    parser.add_argument(
        "-o", "--output", default="评分量规.html", help="输出 HTML 路径"
    )
    parser.add_argument("--title", default="评分量规", help="页面标题")
    parser.add_argument("--task", default="", help="评价任务名称")
    return parser


def main(argv: Optional[Sequence[str]] = None) -> int:
    args = build_parser().parse_args(argv)

    try:
        rubric: Rubric = load_rubric(args.input)
        page = render_html(rubric, title=args.title, task=args.task)
    except RubricError as exc:
        print("错误: %s" % exc, file=sys.stderr)
        return 2
    except OSError as exc:
        print("错误: 读取量规失败: %s" % exc, file=sys.stderr)
        return 1

    try:
        Path(args.output).write_text(page, encoding="utf-8")
    except OSError as exc:
        print("错误: 写入文件失败: %s" % exc, file=sys.stderr)
        return 1

    print(
        "已生成 %s：%d 个维度，%d 个等级"
        % (args.output, len(rubric.dimensions), len(rubric.levels))
    )
    print("用浏览器打开后按 Ctrl/Cmd + P，纸张选 A4 横向即可打印")
    return 0


if __name__ == "__main__":  # pragma: no cover
    raise SystemExit(main())
