"""命令行入口单元测试。"""

from __future__ import annotations

import contextlib
import io
import tempfile
import unittest
from pathlib import Path
from typing import List

from rubric.cli import main

SAMPLE = """维度,优秀,良好,合格
内容,主题鲜明,主题明确,基本明确
"""


class CliTest(unittest.TestCase):
    def setUp(self) -> None:
        self.tmp = tempfile.TemporaryDirectory()
        self.root = Path(self.tmp.name)
        self.rubric = self.root / "rubric.csv"
        self.rubric.write_text(SAMPLE, encoding="utf-8")
        self.target = self.root / "rubric.html"

    def tearDown(self) -> None:
        self.tmp.cleanup()

    def run_cli(self, argv: List[str]) -> int:
        out, err = io.StringIO(), io.StringIO()
        with contextlib.redirect_stdout(out), contextlib.redirect_stderr(err):
            return main(argv)

    def test_generate(self) -> None:
        code = self.run_cli(["-i", str(self.rubric), "-o", str(self.target)])
        self.assertEqual(code, 0)
        page = self.target.read_text(encoding="utf-8")
        self.assertIn("评分量规", page)
        self.assertIn("主题鲜明", page)

    def test_title_and_task(self) -> None:
        code = self.run_cli(
            [
                "-i", str(self.rubric), "-o", str(self.target),
                "--title", "作文量规", "--task", "写人作文",
            ]
        )
        self.assertEqual(code, 0)
        page = self.target.read_text(encoding="utf-8")
        self.assertIn("作文量规", page)
        self.assertIn("写人作文", page)

    def test_invalid_csv(self) -> None:
        bad = self.root / "bad.csv"
        bad.write_text("内容,甲,乙\n", encoding="utf-8")
        code = self.run_cli(["-i", str(bad), "-o", str(self.target)])
        self.assertEqual(code, 2)
        self.assertFalse(self.target.exists())

    def test_missing_file(self) -> None:
        code = self.run_cli(
            ["-i", str(self.root / "missing.csv"), "-o", str(self.target)]
        )
        self.assertEqual(code, 1)

    def test_missing_input_argument(self) -> None:
        with self.assertRaises(SystemExit) as ctx:
            with contextlib.redirect_stderr(io.StringIO()):
                main(["-o", str(self.target)])
        self.assertEqual(ctx.exception.code, 2)

    def test_help(self) -> None:
        with self.assertRaises(SystemExit) as ctx:
            with contextlib.redirect_stdout(io.StringIO()):
                main(["--help"])
        self.assertEqual(ctx.exception.code, 0)


if __name__ == "__main__":
    unittest.main()
