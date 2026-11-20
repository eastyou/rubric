# rubric

[![CI](https://github.com/eastyou/rubric/actions/workflows/ci.yml/badge.svg)](https://github.com/eastyou/rubric/actions/workflows/ci.yml)
[![License: MIT](https://img.shields.io/badge/license-MIT-blue.svg)](LICENSE)
[![Python](https://img.shields.io/badge/python-3.9%2B-brightgreen.svg)](pyproject.toml)

给老师用的评分量规生成器：把「维度,等级描述…」整理成 CSV，一条命令生成 A4 横向可打印评价表。**零依赖，不联网，打印即用。**

维度做行、等级做列，每格写清该等级的表现描述；学生自评、互评、教师评分都能直接在上面打勾，评分标准一目了然。

## 特性

- **维度 × 等级**：1~12 个维度、2~6 个等级，按 CSV 表头自动扩展列
- **A4 横向**：宽表格排版，描述文字自动换行不溢出
- **等级表头**：`优秀/良好/合格/待改进` 或自定义等级名，表头浅色底
- **维度列强调**：第一列加粗浅底，快速定位评价项目
- **评价任务**：`--task 写人作文` 显示在标题下方
- **逐行校验**：列数不匹配、维度重复、描述为空或超长都会指出具体行号
- **编码兼容**：UTF-8（含 BOM）与 GBK 自动识别
- **44 个单元测试**：覆盖 CSV 解析、维度校验、渲染与命令行

## 安装

```bash
pip install rubric
```

也可以直接下载源码，在项目目录里运行：

```bash
python -m rubric --help
```

## 用法

准备 `作文量规.csv`：

```csv
维度,优秀,良好,合格,待改进
内容,主题鲜明，材料充实,主题明确，材料较充实,主题基本明确,主题不清
结构,层次清晰，过渡自然,层次较清晰,结构基本完整,结构混乱
语言,准确生动，富有表现力,通顺连贯,语句基本通顺,语病较多
```

生成评分量规：

```bash
python -m rubric -i 作文量规.csv --task 写人作文 --title 作文评分量规 -o 评分量规.html
```

### 参数

| 参数 | 说明 | 默认 |
| --- | --- | --- |
| `-i, --input` | 量规 CSV | 必填 |
| `-o, --output` | 输出 HTML 路径 | `评分量规.html` |
| `--title` | 页面标题 | `评分量规` |
| `--task` | 评价任务名称 | 空 |

### CSV 格式

- 第一行是表头：`维度,等级1,等级2,...`，必须以「维度」开头
- 表头支持 `维度`、`评价维度`、`评价项目`、`项目`
- 每行数据列数必须与表头一致
- 维度名称最多 12 个字符，等级名称最多 8 个字符
- 每条等级描述最多 40 个字符
- 维度名称不能重复
- 编码支持 UTF-8（含 BOM）与 GBK

## 打印

用浏览器打开生成的 HTML，按 `Ctrl/Cmd + P`：

- 纸张：A4 横向
- 边距：无 / 默认
- 勾选「背景图形」，表头与维度列底色才会打印

## 项目结构

```text
rubric/
├── rubric/
│   ├── model.py    # CSV 解析、维度与等级校验
│   ├── render.py   # A4 横向量规排版
│   └── cli.py      # 命令行入口
├── tests/          # 44 个单元测试
└── examples/       # 示例量规
```

## 开发

```bash
python -m unittest discover -s tests
```

## 许可证

[MIT](LICENSE) © 2026 eastyou
