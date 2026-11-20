"""rubric：A4 可打印评分量规。"""

from __future__ import annotations

from .model import (
    HEADER_NAMES,
    MAX_DESC,
    MAX_DIMENSIONS,
    MAX_DIM_NAME,
    MAX_LEVELS,
    MAX_LEVEL_NAME,
    MIN_DIMENSIONS,
    MIN_LEVELS,
    Rubric,
    RubricError,
    format_rubric,
    load_rubric,
    parse_csv,
)
from .render import render_html, row_height_mm

__version__ = "0.1.0"

__all__ = [
    "HEADER_NAMES",
    "MAX_DESC",
    "MAX_DIMENSIONS",
    "MAX_DIM_NAME",
    "MAX_LEVELS",
    "MAX_LEVEL_NAME",
    "MIN_DIMENSIONS",
    "MIN_LEVELS",
    "Rubric",
    "RubricError",
    "format_rubric",
    "load_rubric",
    "parse_csv",
    "render_html",
    "row_height_mm",
    "__version__",
]
