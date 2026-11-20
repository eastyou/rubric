"""render 模块单元测试。"""

from __future__ import annotations

import unittest

from rubric.model import RubricError, parse_csv
from rubric.render import render_html, row_height_mm

SAMPLE = """维度,优秀,良好,合格
内容,主题鲜明,主题明确,基本明确
结构,层次清晰,层次较清晰,基本完整
"""


class RenderHtmlTest(unittest.TestCase):
    def setUp(self) -> None:
        self.rubric = parse_csv(SAMPLE)

    def test_basic_document(self) -> None:
        page = render_html(self.rubric)
        self.assertTrue(page.startswith("<!doctype html>"))
        self.assertIn("A4 landscape", page)
        self.assertIn("评分量规", page)

    def test_level_headers(self) -> None:
        page = render_html(self.rubric)
        for level in ("优秀", "良好", "合格"):
            self.assertIn("<th>%s</th>" % level, page)
        self.assertIn('<th class="dim">维度</th>', page)

    def test_dimension_rows(self) -> None:
        page = render_html(self.rubric)
        self.assertIn('<td class="dim">内容</td>', page)
        self.assertIn('<td class="dim">结构</td>', page)
        self.assertIn("主题鲜明", page)
        self.assertEqual(page.count("<tr>"), 3)

    def test_task(self) -> None:
        page = render_html(self.rubric, task="作文评价")
        self.assertIn("评价任务：作文评价", page)

    def test_no_task(self) -> None:
        page = render_html(self.rubric, task="  ")
        self.assertNotIn("评价任务：", page)

    def test_title_escaped(self) -> None:
        page = render_html(self.rubric, title="<量规>")
        self.assertIn("&lt;量规&gt;", page)

    def test_non_rubric(self) -> None:
        with self.assertRaises(RubricError):
            render_html("rubric")  # type: ignore[arg-type]

    def test_empty_title(self) -> None:
        with self.assertRaises(RubricError):
            render_html(self.rubric, title=" ")

    def test_non_text_task(self) -> None:
        with self.assertRaises(RubricError):
            render_html(self.rubric, task=1)  # type: ignore[arg-type]

    def test_long_task(self) -> None:
        with self.assertRaises(RubricError):
            render_html(self.rubric, task="字" * 41)

    def test_row_height(self) -> None:
        self.assertAlmostEqual(row_height_mm(2), 30.0)
        self.assertAlmostEqual(row_height_mm(10), 14.8)
        with self.assertRaises(RubricError):
            row_height_mm(0)


if __name__ == "__main__":
    unittest.main()
