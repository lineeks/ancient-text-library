# schema/ — 检索契约与受控词表

本目录是"带检索功能的古籍图书馆"的索引契约层，只描述结构与合法取值，不含正文。

| 文件 | 作用 | 如何产生 / 被谁使用 |
|---|---|---|
| `controlled_vocabulary.json` | `ten_god / pattern / shensha` 的**受控词表**（含频次、已登记别名）与天干地支固定枚举 | `scripts/export_vocab.py` 扫描全库确定性生成；`scripts/validate_library.py` 据此做白名单校验 |
| `manifest.schema.json` | 根 `manifest.json` 的 JSON Schema（2020-12），引擎消费契约 | 手写维护；可供编辑器 / 消费方校验清单结构 |
| `frontmatter.schema.json` | 每个条目 `.md` 的 YAML Frontmatter 结构契约 | 手写维护；受控字段取值另见 `controlled_vocabulary.json` |

## 规则

- **受控字段**：`ten_god / pattern / shensha` 只能用词表中的规范词或已登记别名；要引入新取值，
  先更新数据并运行 `python -X utf8 scripts/export_vocab.py` 刷新词表，再通过质量门。
- **开放字段**：`keywords` 是开放主题词，不做取值校验，只用于包含式召回。
- **别名归一**：`controlled_vocabulary.json` 中 `aliases` 登记存量异形（如 `三奇 → 三奇贵人`）；
  内容增强时把别名物理替换为规范词，随后重跑导出，别名即从词表消失。
- 天干 `day_master`、月令 `month_branch` 为固定英文枚举；`day_pillar/hour_pillar` 为中文六十甲子。
- 三个文件均为 UTF-8、无时间戳，重复生成字节稳定。
