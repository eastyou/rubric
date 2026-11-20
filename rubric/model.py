"""评分量规数据模型：CSV 解析、维度与等级校验。"""

from __future__ import annotations

import csv
import io
from dataclasses import dataclass
from pathlib import Path
from typing import Dict, List, Tuple, Union

MIN_DIMENSIONS = 1
MAX_DIMENSIONS = 12
MIN_LEVELS = 2
MAX_LEVELS = 6
MAX_DIM_NAME = 12
MAX_LEVEL_NAME = 8
MAX_DESC = 40

HEADER_NAMES = {"维度", "评价维度", "评价项目", "项目"}


class RubricError(ValueError):
    """量规数据或参数不合法。"""


@dataclass(frozen=True)
class Rubric:
    """一份评分量规：等级名称与「维度 -> 各等级描述」。"""

    levels: Tuple[str, ...]
    dimensions: Tuple[Tuple[str, Tuple[str, ...]], ...]

    def __post_init__(self) -> None:
        try:
            levels = tuple(self.levels)
        except TypeError as exc:
            raise RubricError("等级必须是序列") from exc
        if not MIN_LEVELS <= len(levels) <= MAX_LEVELS:
            raise RubricError(
                "等级数量必须在 %d~%d 之间，当前是 %d"
                % (MIN_LEVELS, MAX_LEVELS, len(levels))
            )
        for name in levels:
            if not isinstance(name, str) or not name.strip():
                raise RubricError("等级名称不能为空")
            if len(name.strip()) > MAX_LEVEL_NAME:
                raise RubricError("等级名称最多 %d 个字符" % MAX_LEVEL_NAME)
        if len({name.strip() for name in levels}) != len(levels):
            raise RubricError("等级名称不能重复")

        try:
            dimensions = tuple(self.dimensions)
        except TypeError as exc:
            raise RubricError("维度必须是序列") from exc
        if not MIN_DIMENSIONS <= len(dimensions) <= MAX_DIMENSIONS:
            raise RubricError(
                "维度数量必须在 %d~%d 之间，当前是 %d"
                % (MIN_DIMENSIONS, MAX_DIMENSIONS, len(dimensions))
            )
        cleaned: List[Tuple[str, Tuple[str, ...]]] = []
        seen: Dict[str, None] = {}
        for item in dimensions:
            if not isinstance(item, (list, tuple)) or len(item) != 2:
                raise RubricError("每个维度必须包含名称与描述列表")
            name, descriptions = item
            if not isinstance(name, str):
                raise RubricError("维度名称必须是文本")
            name = name.strip()
            if not name:
                raise RubricError("维度名称不能为空")
            if len(name) > MAX_DIM_NAME:
                raise RubricError(
                    "维度名称最多 %d 个字符：%s" % (MAX_DIM_NAME, name)
                )
            if name in seen:
                raise RubricError("维度名称重复：%s" % name)
            seen[name] = None
            try:
                cells = tuple(descriptions)
            except TypeError as exc:
                raise RubricError("维度「%s」的描述必须是序列" % name) from exc
            if len(cells) != len(levels):
                raise RubricError(
                    "维度「%s」有 %d 个描述，等级有 %d 个"
                    % (name, len(cells), len(levels))
                )
            for value in cells:
                if not isinstance(value, str) or not value.strip():
                    raise RubricError("维度「%s」的等级描述不能为空" % name)
                if len(value.strip()) > MAX_DESC:
                    raise RubricError(
                        "维度「%s」的描述最多 %d 个字符" % (name, MAX_DESC)
                    )
            cleaned.append((name, tuple(value.strip() for value in cells)))
        object.__setattr__(self, "levels", tuple(name.strip() for name in levels))
        object.__setattr__(self, "dimensions", tuple(cleaned))

    def description(self, dimension: str, level_index: int) -> str:
        """取某维度某等级的描述，索引从 0 开始。"""
        if isinstance(level_index, bool) or not isinstance(level_index, int):
            raise RubricError("等级索引必须是整数")
        if not 0 <= level_index < len(self.levels):
            raise RubricError("等级索引超出范围：%d" % level_index)
        for name, cells in self.dimensions:
            if name == dimension:
                return cells[level_index]
        raise RubricError("找不到维度：%s" % dimension)


def _decode(data: bytes) -> str:
    if not isinstance(data, (bytes, bytearray)):
        raise RubricError("文件内容必须是字节")
    for encoding in ("utf-8-sig", "gbk"):
        try:
            return bytes(data).decode(encoding)
        except UnicodeDecodeError:
            continue
    raise RubricError("无法识别文件编码，请另存为 UTF-8 或 GBK 后重试")


def parse_csv(text: str, source: str = "输入内容") -> Rubric:
    """解析量规 CSV：首行是「维度,等级1,等级2,...」。"""
    if not isinstance(text, str):
        raise RubricError("CSV 内容必须是文本")
    text = text.lstrip("\ufeff")
    reader = csv.reader(io.StringIO(text))
    rows: List[Tuple[int, List[str]]] = []
    for line_no, row in enumerate(reader, start=1):
        cells = [cell.strip() for cell in row]
        if not any(cells):
            continue
        rows.append((line_no, cells))
    if not rows:
        raise RubricError("%s 中没有内容" % source)

    header_line, header = rows[0]
    if header[0] not in HEADER_NAMES:
        raise RubricError(
            "%s 第 %d 行必须以「维度」开头，例如：维度,优秀,良好,合格"
            % (source, header_line)
        )
    if len(header) < MIN_LEVELS + 1:
        raise RubricError("%s 至少需要 %d 个等级" % (source, MIN_LEVELS))
    levels = header[1:]
    if len(levels) > MAX_LEVELS:
        raise RubricError("%s 最多支持 %d 个等级" % (source, MAX_LEVELS))

    dimensions: List[Tuple[str, List[str]]] = []
    for line_no, cells in rows[1:]:
        if len(cells) != len(levels) + 1:
            raise RubricError(
                "%s 第 %d 行有 %d 列，应为 %d 列（维度 + %d 个等级）"
                % (source, line_no, len(cells), len(levels) + 1, len(levels))
            )
        dimensions.append((cells[0], cells[1:]))
    if not dimensions:
        raise RubricError("%s 中只有表头，没有维度" % source)

    try:
        return Rubric(
            levels=tuple(levels),
            dimensions=tuple((name, tuple(cells)) for name, cells in dimensions),
        )
    except RubricError as exc:
        raise RubricError("%s：%s" % (source, exc)) from exc


def load_rubric(path: Union[str, Path]) -> Rubric:
    """读取量规 CSV 文件。"""
    target = Path(path)
    return parse_csv(_decode(target.read_bytes()), source=str(target))


def format_rubric(rubric: Rubric) -> str:
    """把量规写回 CSV 文本。"""
    if not isinstance(rubric, Rubric):
        raise RubricError("rubric 必须是 Rubric 对象")
    buffer = io.StringIO()
    writer = csv.writer(buffer, lineterminator="\n")
    writer.writerow(["维度"] + list(rubric.levels))
    for name, cells in rubric.dimensions:
        writer.writerow([name] + list(cells))
    return buffer.getvalue()
