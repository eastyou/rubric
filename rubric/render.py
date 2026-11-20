"""把评分量规渲染成可打印的 A4 横向表格。"""

from __future__ import annotations

import html
from typing import List

from .model import MAX_DESC, Rubric, RubricError

PAGE_WIDTH_MM = 297.0
PAGE_HEIGHT_MM = 210.0
MARGIN_X_MM = 12.0
USABLE_WIDTH_MM = PAGE_WIDTH_MM - MARGIN_X_MM * 2
TABLE_WIDTH_MM = USABLE_WIDTH_MM - 1.0
DIM_WIDTH_MM = 34.0


def _num(value: float) -> str:
    text = "%.1f" % value
    return text.rstrip("0").rstrip(".") if "." in text else text


def row_height_mm(dimensions: int) -> float:
    """按维度数量计算行高。"""
    if isinstance(dimensions, bool) or not isinstance(dimensions, int):
        raise RubricError("维度数量必须是整数")
    if dimensions < 1:
        raise RubricError("维度数量必须大于 0")
    return min(30.0, 148.0 / dimensions)


def _table_markup(rubric: Rubric) -> str:
    levels = rubric.levels
    level_width = (TABLE_WIDTH_MM - DIM_WIDTH_MM) / len(levels)
    cols = ['<col style="width:%smm">' % _num(DIM_WIDTH_MM)]
    cols.extend(['<col style="width:%smm">' % _num(level_width)] * len(levels))
    heads = "".join("<th>%s</th>" % html.escape(name) for name in levels)
    head = (
        '<thead><tr><th class="dim">维度</th>%s</tr></thead>' % heads
    )
    body: List[str] = []
    for name, cells in rubric.dimensions:
        tds = "".join("<td>%s</td>" % html.escape(cell) for cell in cells)
        body.append('<tr><td class="dim">%s</td>%s</tr>' % (html.escape(name), tds))
    return (
        '<table class="rubric"><colgroup>%s</colgroup>%s<tbody>%s</tbody></table>'
        % ("".join(cols), head, "".join(body))
    )


def render_html(
    rubric: Rubric,
    title: str = "评分量规",
    task: str = "",
) -> str:
    """生成完整 HTML：维度为行、等级为列的横向评价表。"""
    if not isinstance(rubric, Rubric):
        raise RubricError("rubric 必须是 Rubric 对象")
    if not isinstance(title, str) or not title.strip():
        raise RubricError("标题不能为空")
    if not isinstance(task, str):
        raise RubricError("评价任务必须是文本")
    task = task.strip()
    if len(task) > MAX_DESC:
        raise RubricError("评价任务最多 %d 个字符" % MAX_DESC)

    height = row_height_mm(len(rubric.dimensions))
    meta = (
        '<p class="meta">评价任务：%s</p>' % html.escape(task) if task else ""
    )
    head = (
        '<header class="head"><h1>%s</h1>%s'
        '<p class="hint">在每个维度对应的等级格中打「✓」，可在最后一列写下得分。</p>'
        "</header>" % (html.escape(title.strip()), meta)
    )
    foot = (
        '<footer class="foot"><span>共 %d 个维度 · %d 个等级</span>'
        "<span>rubric · A4 横向</span></footer>"
        % (len(rubric.dimensions), len(rubric.levels))
    )
    toolbar = (
        '<div class="toolbar"><strong>%s</strong>'
        "<span>%d 个维度 · %d 个等级%s</span></div>"
        % (
            html.escape(title.strip()),
            len(rubric.dimensions),
            len(rubric.levels),
            " · " + html.escape(task) if task else "",
        )
    )

    return (
        "<!doctype html>\n"
        '<html lang="zh-CN">\n<head>\n<meta charset="utf-8">\n'
        '<meta name="viewport" content="width=device-width, initial-scale=1">\n'
        "<title>%s</title>\n<style>%s</style>\n</head>\n<body>\n"
        '%s\n<section class="sheet">%s%s%s</section>\n</body>\n</html>\n'
        % (
            html.escape(title.strip()),
            _style(height),
            toolbar,
            head,
            _table_markup(rubric),
            foot,
        )
    )


def _style(height: float) -> str:
    template = """
  :root { color-scheme: light; }
  * { box-sizing: border-box; }
  body {
    margin: 0;
    padding: 7mm 0 10mm;
    background: #e2e8f0;
    color: #0f172a;
    font-family: "PingFang SC", "Microsoft YaHei", "Noto Sans CJK SC", sans-serif;
  }
  .toolbar {
    width: 297mm;
    margin: 0 auto 5mm;
    display: flex;
    align-items: baseline;
    justify-content: space-between;
    gap: 12px;
    color: #334155;
    font-size: 13px;
  }
  .toolbar strong { font-size: 15px; letter-spacing: 1px; }
  .toolbar span { color: #64748b; font-size: 12px; }
  .sheet {
    width: 297mm;
    height: 210mm;
    margin: 0 auto 7mm;
    padding: 10mm 12mm 8mm;
    background: #fff;
    box-shadow: 0 6px 22px rgba(15, 23, 42, 0.14);
    display: flex;
    flex-direction: column;
    page-break-after: always;
    break-after: page;
    overflow: hidden;
  }
  .sheet:last-child { page-break-after: auto; break-after: auto; }
  .head { text-align: center; margin-bottom: 3mm; }
  .head h1 {
    margin: 0;
    font-size: 19pt;
    font-weight: 600;
    letter-spacing: 5pt;
  }
  .head .meta { margin: 1.5mm 0 0; font-size: 10pt; color: #334155; }
  .head .hint { margin: 1.5mm 0 0; font-size: 8.5pt; color: #64748b; }
  table.rubric {
    width: 272mm;
    border-collapse: collapse;
    table-layout: fixed;
  }
  table.rubric th,
  table.rubric td {
    border: 0.25mm solid #94a3b8;
    padding: 1.5mm 2mm;
    text-align: center;
    vertical-align: middle;
    font-size: 9pt;
    line-height: 1.45;
    overflow-wrap: anywhere;
  }
  table.rubric th {
    height: 10mm;
    background: #f1f5f9;
    font-size: 10pt;
    font-weight: 600;
  }
  table.rubric th.dim,
  table.rubric td.dim {
    background: #f8fafc;
    font-weight: 600;
    font-size: 10pt;
    letter-spacing: 0.5pt;
  }
  table.rubric td { height: __ROW_HEIGHT__mm; }
  .foot {
    margin-top: auto;
    padding-top: 2mm;
    display: flex;
    justify-content: space-between;
    font-size: 8pt;
    color: #64748b;
    border-top: 0.2mm solid #e2e8f0;
  }
  @page { size: A4 landscape; margin: 0; }
  @media print {
    body { background: #fff; padding: 0; }
    .toolbar { display: none; }
    .sheet { margin: 0; box-shadow: none; }
    * { -webkit-print-color-adjust: exact; print-color-adjust: exact; }
  }
"""
    return template.replace("__ROW_HEIGHT__", _num(height))
