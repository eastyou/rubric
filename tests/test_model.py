"""model 模块单元测试。"""

from __future__ import annotations

import tempfile
import unittest
from pathlib import Path

from rubric.model import (
    MAX_DESC,
    MAX_DIM_NAME,
    MAX_LEVELS,
    Rubric,
    RubricError,
    format_rubric,
    load_rubric,
    parse_csv,
)

SAMPLE = """维度,优秀,良好,合格
内容,主题鲜明，材料充实,主题明确，材料较充实,主题基本明确
结构,层次清晰，过渡自然,层次较清晰,结构基本完整
语言,准确生动，富有表现力,通顺连贯,语句基本通顺
"""


class ParseCsvTest(unittest.TestCase):
    def test_sample(self) -> None:
        rubric = parse_csv(SAMPLE)
        self.assertEqual(rubric.levels, ("优秀", "良好", "合格"))
        self.assertEqual(len(rubric.dimensions), 3)
        self.assertEqual(rubric.dimensions[0][0], "内容")

    def test_header_variants(self) -> None:
        for header in ("评价维度,优,良", "评价项目,优,良", "项目,优,良"):
            rubric = parse_csv(header + "\n内容,甲,乙\n")
            self.assertEqual(len(rubric.dimensions), 1, header)

    def test_missing_header(self) -> None:
        with self.assertRaises(RubricError) as ctx:
            parse_csv("内容,甲,乙\n")
        self.assertIn("维度", str(ctx.exception))

    def test_too_few_levels(self) -> None:
        with self.assertRaises(RubricError):
            parse_csv("维度,优秀\n内容,甲\n")

    def test_too_many_levels(self) -> None:
        header = "维度," + ",".join("等级%d" % index for index in range(MAX_LEVELS + 1))
        with self.assertRaises(RubricError):
            parse_csv(header + "\n内容," + ",".join("甲" for _ in range(MAX_LEVELS + 1)) + "\n")

    def test_wrong_column_count(self) -> None:
        with self.assertRaises(RubricError) as ctx:
            parse_csv("维度,优秀,良好\n内容,甲\n")
        self.assertIn("第 2 行", str(ctx.exception))

    def test_duplicate_dimension(self) -> None:
        with self.assertRaises(RubricError):
            parse_csv("维度,优秀,良好\n内容,甲,乙\n内容,丙,丁\n")

    def test_empty_dimension(self) -> None:
        with self.assertRaises(RubricError):
            parse_csv("维度,优秀,良好\n,甲,乙\n")

    def test_empty_description(self) -> None:
        with self.assertRaises(RubricError):
            parse_csv("维度,优秀,良好\n内容,甲,\n")

    def test_description_too_long(self) -> None:
        with self.assertRaises(RubricError):
            parse_csv("维度,优秀,良好\n内容,%s,乙\n" % ("字" * (MAX_DESC + 1)))

    def test_dimension_too_long(self) -> None:
        with self.assertRaises(RubricError):
            parse_csv("维度,优秀,良好\n%s,甲,乙\n" % ("字" * (MAX_DIM_NAME + 1)))

    def test_empty_text(self) -> None:
        with self.assertRaises(RubricError):
            parse_csv("\n\n")

    def test_only_header(self) -> None:
        with self.assertRaises(RubricError):
            parse_csv("维度,优秀,良好\n")

    def test_non_text(self) -> None:
        with self.assertRaises(RubricError):
            parse_csv(123)  # type: ignore[arg-type]

    def test_bom(self) -> None:
        rubric = parse_csv("\ufeff" + SAMPLE)
        self.assertEqual(len(rubric.dimensions), 3)

    def test_load_utf8(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "rubric.csv"
            path.write_text(SAMPLE, encoding="utf-8")
            self.assertEqual(load_rubric(path).levels, ("优秀", "良好", "合格"))

    def test_load_gbk(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "rubric.csv"
            path.write_bytes(SAMPLE.encode("gbk"))
            self.assertEqual(load_rubric(path).dimensions[0][0], "内容")

    def test_unknown_encoding(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "rubric.csv"
            path.write_bytes(b"\xff\xff\xff")
            with self.assertRaises(RubricError):
                load_rubric(path)

    def test_missing_file(self) -> None:
        with self.assertRaises(FileNotFoundError):
            load_rubric("/tmp/definitely-missing-rubric.csv")


class RubricTest(unittest.TestCase):
    def setUp(self) -> None:
        self.rubric = parse_csv(SAMPLE)

    def test_description(self) -> None:
        self.assertEqual(self.rubric.description("内容", 0), "主题鲜明，材料充实")

    def test_bad_index(self) -> None:
        for index in (-1, 3, True, "0"):
            with self.assertRaises(RubricError):
                self.rubric.description("内容", index)  # type: ignore[arg-type]

    def test_unknown_dimension(self) -> None:
        with self.assertRaises(RubricError):
            self.rubric.description("不存在", 0)

    def test_duplicate_level(self) -> None:
        with self.assertRaises(RubricError):
            Rubric(levels=("优", "优"), dimensions=(("内容", ("甲", "乙")),))

    def test_too_few_dimensions(self) -> None:
        with self.assertRaises(RubricError):
            Rubric(levels=("优", "良"), dimensions=())

    def test_bad_dimension_shape(self) -> None:
        with self.assertRaises(RubricError):
            Rubric(levels=("优", "良"), dimensions=(("内容",),))  # type: ignore[arg-type]

    def test_format_roundtrip(self) -> None:
        again = parse_csv(format_rubric(self.rubric))
        self.assertEqual(again.levels, self.rubric.levels)
        self.assertEqual(again.dimensions, self.rubric.dimensions)

    def test_format_non_rubric(self) -> None:
        with self.assertRaises(RubricError):
            format_rubric("rubric")  # type: ignore[arg-type]


if __name__ == "__main__":
    unittest.main()
