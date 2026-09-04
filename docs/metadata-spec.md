# 五术古籍元数据规范（Metadata Specification）v1.0

> 本规范定义 Aether-Cycle 五术古籍图书馆的条目元数据格式、检索字段、分类体系与扩展原则。
> 所有入库条目必须遵循本规范；`scripts/validate_library.py` 据此做交付前质量门校验。

---

## 1. 条目物理结构

每个条目是一个 Markdown 文件，结构为：

```
---
<YAML Frontmatter>
---
### <section_title>

**【原文】**
<原文，锁死不可修改>

**【古注/评注/阐微】**（可选，版本相关）
<后世注文>

**【白话提要】**
<文义串讲，严禁现代断命与编造>
```

- 文件名 = `<book-prefix>_<locator>.md`，全 ASCII 小写，全局唯一
- `id` = 文件名（去扩展名），与文件名严格一致
- 正文强制三层：【原文】 > 【古注】 > 【白话提要】；原文层锁死

---

## 2. Frontmatter 字段规范

### 2.1 必填字段

| 字段 | 类型 | 说明 | 示例 |
|---|---|---|---|
| `id` | string | 全局唯一编号，= 文件名 stem | `qtbj_jia_yin` |
| `book` | string | 典籍名称（中文） | `穷通宝鉴` |
| `chapter` | string | 卷/章名 | `卷一·三春甲木` |
| `section_title` | string | 本条目标题 | `正月甲木` |
| `source_version` | string | 底本/版本出处 | `余春台辑·徐乐吾评注` |
| `author` | string | 作者/编者（托名标注） | `余春台` |
| `dynasty` | string | 朝代（托名标注） | `清` |
| `type` | string | 条目体裁枚举（见 §3） | `monthly` |
| `conditions` | object | 检索条件八键（见 §4） | |
| `weight` | int | 检索权重 0-10（见 §5） | `10` |
| `tags` | array | 主题标签（开放） | `["调候用神","春季甲木"]` |

### 2.2 可选字段

| 字段 | 类型 | 说明 |
|---|---|---|
| `chapter_num` | int | 章号（子平真诠等有连续章号的典籍） |

---

## 3. `type` 枚举（条目体裁）

| type | 说明 | 典型典籍 |
|---|---|---|
| `monthly` | 按月令/日干精确锚定的调候条目 | 穷通宝鉴 |
| `seasonal` | 按季节/季度的泛论条目 | 穷通宝鉴季度论 |
| `reference` | 总述/序/泛论条目 | 各书总论、称骨总述 |
| `chapter` | 按章切分的论述条目 | 子平真诠、滴天髓、神峰通考 |
| `shensha` | 神煞专论条目 | 三命通会神煞卷 |
| `rishi` | 日柱+时柱精确配断条目 | 三命通会日时断 |
| `nayin` | 六十甲子纳音论命条目（日柱精确锚定） | 李虚中命书六十甲子 |
| `fuwen` | 歌赋/韵文条目 | 渊海子平赋文 |
| `koujue` | 口诀/短偈条目 | 玉照定真经口诀 |
| `chenggu` | 称骨歌诀档 | 袁天罡称骨歌 |
| `chenggu-table` | 称骨重量表 | 袁天罡称骨年/月/日/时表 |

> 新增体裁须先在本规范登记，再更新 `frontmatter.schema.json` 的 type 枚举与 `validate_library.py`。

---

## 4. `conditions` 检索条件八键

所有条目统一包含以下八字段，空值为 `[]`：

| 字段 | 类型 | 说明 | 受控 |
|---|---|---|---|
| `day_master` | array | 日干（英文枚举：Jia..Gui） | 固定枚举 |
| `month_branch` | array | 月令（英文枚举：Yin..Chou） | 固定枚举 |
| `day_pillar` | array | 日柱（中文六十甲子） | 固定枚举 |
| `hour_pillar` | array | 时柱（中文六十甲子） | 固定枚举 |
| `ten_god` | array | 十神（正官/七杀/...） | **受控词表** |
| `pattern` | array | 格局（正官格/七杀格/...） | **受控词表** |
| `shensha` | array | 神煞（天乙贵人/驿马/...） | **受控词表** |
| `keywords` | array | 开放主题词（不参与硬匹配，只做包含式召回） | 开放 |

### 4.1 匹配语义
- **复合键组内 AND**：调候组 `[day_master, month_branch]`、日时组 `[day_pillar, hour_pillar]`，组内已声明字段须全部与命盘相交
- **检索维度组间 OR**：`ten_god / pattern / shensha` 三个单维组互为并列召回理由，任一命中即召回
- **无锚点通论条**：未声明任何硬字段的条目（序、泛论、纯歌赋）默认不参与结构化命盘召回，只通过关键词或书目浏览获取
- **排序**：命中精确度（声明的非空硬字段数）↓ → weight ↓ → path ↑

### 4.2 五术扩展原则
- **命·八字**：使用上述八键（已落地）
- **命·紫微/七政**：暂用 `keywords` 标主星/宫位/星曜，未来扩展专属 conditions（如 `ziwei_star` / `ziwei_palace`）
- **医**：暂用 `keywords` 标方剂/证候/经络/药物/脏腑，未来扩展专属 conditions（如 `yi_formula` / `yi_syndrome` / `yi_meridian` / `yi_herb`）
- **相**：暂用 `keywords` 标部位/格局/龙穴砂水，未来扩展专属 conditions
- **卜**：暂用 `keywords` 标卦象/六亲/宫位/星门神，未来扩展专属 conditions
- **山**：暂用 `keywords` 标丹道阶段/功法/导引/符咒，未来扩展专属 conditions

> 原则：**先用 keywords 轻量索引，某术规模达到 3 部以上再设计专属 conditions**，避免过早设计复杂 schema。

---

## 5. `weight` 检索权重（0-10）

| 权重 | 适用 | 示例 |
|---|---|---|
| 10 | 核心精确锚定条 | 穷通宝鉴月度、子平真诠格局章 |
| 9 | 核心论述条 | 滴天髓天干地支篇 |
| 8 | 季度/泛论核心条 | 穷通宝鉴季度论 |
| 6 | 第二梯队条 | 三命通会、渊海子平 |
| 5 | 参考类条 | 穷通总论参考 |
| 3 | 第三梯队实战条 | 神峰通考 |
| 2 | 补遗/民俗条 | 玉照、千里、五行精纪、命理约言、称骨 |

---

## 6. 分类体系（category / subcategory）

`category` / `subcategory` 是 **manifest 层的推断字段**（由 `build_manifest.py` 根据路径自动推断），不写进 frontmatter。

| category | 说明 | subcategory 示例 |
|---|---|---|
| `ming` | 命·命理 | `bazi`（八字）、`ziwei`（紫微）、`qizheng`（七政四余） |
| `yi` | 医·中医 | `jingdian`（经典）、`fangshu`（方书）、`bencao`（本草）、`zhenjiu`（针灸）、`wenbing`（温病） |
| `xiang` | 相·相术 | `renxiang`（人相）、`dixiang`（地相/风水）、`xingxiang`（星相） |
| `bu` | 卜·卜筮 | `yijing`（易经）、`liuyao`（六爻）、`meihua`（梅花）、`qimen`（奇门）、`liuren`（六壬）、`taiyi`（太乙） |
| `shan` | 山·仙学养生 | `dandao`（丹道）、`yangsheng`（养生）、`wushu`（武术）、`fuzhou`（符咒） |

> 现有八字库（core/ origin-shensha/ extended）统一推断为 `category=ming, subcategory=bazi`。
> 未来新增书放到对应 `category/subcategory/` 目录下，自动推断。

---

## 7. 受控词表

`ten_god / pattern / shensha` 为受控字段，取值必须在 `schema/controlled_vocabulary.json` 中登记。

- 词表由 `scripts/export_vocab.py` 从全库扫描确定性生成（含频次、已登记别名）
- 新增取值须先更新数据并重跑 `export_vocab.py`，再通过 `validate_library.py` 校验
- 同义异形（如 `三奇`/`三奇贵人`）在词表中登记为 alias，内容增强时物理归一到规范词
- `keywords` 为开放字段，不做受控校验

---

## 8. 质量门校验（validate_library.py）

交付前必须通过：
1. Frontmatter 可被 YAML 解析
2. `id` 全局唯一且与文件名一致
3. 必填字段齐全，conditions 八字段为列表
4. `day_master` / `month_branch` 为英文枚举；`day_pillar` / `hour_pillar` 为合法六十甲子
5. `ten_god` / `pattern` / `shensha` 取值在受控词表内
6. 穷通宝鉴 monthly 必有 day_master+month_branch；三命通会 rishi 必有 day_pillar+hour_pillar；shensha 必有 shensha
7. 子平真诠章号 1..48 唯一连续
8. 正文分层标记齐全（【原文】/【经文】/【原文·口诀】之一 + 【白话提要】）

---

## 9. 版本与变更

- 本规范 v1.0 于 2026-09 制定，随五术扩展持续更新
- 新增 `type` / 受控词 / 专属 conditions 须先更新本规范，再落地数据与代码
- `manifest.json` 的 `schema_version` 在不兼容变更时递增（当前 v2）

---

*本规范是五术古籍图书馆的元数据宪法，所有入库与检索行为以此为准。*
