# Aether-Cycle・子平命理古籍知识库

> 面向八字排盘引擎的结构化古籍文库：**即时检索・引经据典・原汁原味**。
>
> 每条古籍条文以 Markdown + YAML Frontmatter 标引，排盘内核输出
> `日干 / 月令 / 格局 / 十神 / 神煞 / 日柱 / 时柱` 后，对 `conditions`
> 字段做数组交集匹配，毫秒级返回 **原文（经文）/ 古注（阐微）/ 命例 / 白话提要** 分层内容。

截至当前，全库收录 **10 部典籍、1547 个结构化条目**，质量门全部通过；
除《千里命稿》本身为民国白话外，其余 1525 条【白话提要】已全部完成逐条文义校补（无「待补」占位）。

---

## 一、目录结构

```
ancient-text-library/
├── README.md                     # 本文件：命名规范 / Frontmatter 规范 / 检索方式
├── INDEX.md                      # 全库总索引（收录进度 + 分书导航 + 检索字段速查，build_index 生成）
├── manifest.json                 # 机器检索总清单（build_manifest 确定性生成，引擎一次性加载）
├── AGENTS.md                     # 协作者规范：小步频繁 commit / 内容不变量 / 构建命令 / 环境坑
├── engine/                       # Rust 检索骨架（框架无关，可被 Tauri 直接依赖；cargo test 自测）
│   ├── Cargo.toml / Cargo.lock
│   └── src/lib.rs                #   Library/Chart/Entry：加载 manifest、匹配、排序
├── tests/                        # 召回回归测试（Python，与 Rust 语义交叉对齐）
│   └── recall_regression.py
├── docs/                         # 交叉校勘等工程化笔记
│   └── cross-collation-tianyi-guiren.md  # 天乙贵人：三命 × 五行精纪 × 命理约言
├── raw/                          # 原始下载文本（统一 UTF-8，不做内容改动）
│   ├── qiongtongbaojian.txt      #   穷通宝鉴（余春台辑本）
│   ├── zipingzhenquan.txt        #   子平真诠评注（源为 UTF-16 LE，已转 UTF-8）
│   ├── ditiansuichanwei.txt      #   滴天髓阐微
│   ├── sanmingtonghui.txt        #   三命通会（四库本白文）
│   ├── yuanhaiziping.txt         #   渊海子平
│   ├── shenfengtongkao.txt       #   神峰通考
│   ├── yuzhaodingzhenjing.txt    #   玉照定真经（四库本）
│   ├── qianliminggao.txt         #   千里命稿
│   ├── wuxingjingji.txt          #   五行精纪（南宋禄命类书，同源古籍电子本）
│   └── mingliyaoyan.txt          #   命理约言（陈素庵原著、韦千里选辑标点本，六页合并）
├── scripts/                      # 可复现构建脚本（解析/索引纯标准库；校验用 PyYAML）
│   ├── download_sources.py / redownload_zpqz.py
│   ├── parse_qiongtong.py        #   穷通宝鉴 → 日干×月令条目
│   ├── parse_ziping.py           #   子平真诠 → 48 章
│   ├── parse_ditianchui.py       #   滴天髓阐微 → 通神论34 + 六亲论29
│   ├── parse_sanmingtonghui.py   #   三命通会 → 31 神煞 + 717 日时断
│   ├── parse_yuanhaiziping.py    #   渊海子平 → 赋论 30 篇
│   ├── parse_shenfengtongkao.py  #   神峰通考 → 65 节
│   ├── parse_yuzhaodingzhenjing.py # 玉照定真经 → 提要 + 255 口诀
│   ├── parse_qianliminggao.py    #   千里命稿 → 22 篇
│   ├── parse_wuxingjingji.py     #   五行精纪 → 序2 + 34卷72节 = 74 条
│   ├── fetch_mingliyaoyan.py     #   命理约言：抓取中华典藏六页并清洗合并
│   ├── parse_mingliyaoyan.py     #   命理约言 → 序/48法/20赋/48论/杂论/跋 = 119 条
│   ├── build_index.py            #   扫描 Frontmatter 生成各级 INDEX.md（人读导航）
│   ├── build_manifest.py         #   聚合为根 manifest.json（机读总清单，确定性、无时间戳）
│   ├── retrieve_reference.py     #   参考检索器（Python，Rust engine 的等价参照 + CLI）
│   ├── enrich_conditions.py      #   行级幂等增强 conditions 精准标签（--book/--dry，不碰正文）
│   ├── validate_library.py       #   交付前质量门：YAML/id/字段/枚举/分层
│   ├── export_for_baihua.py      #   白话管线：导出某书 id/标题/原文（含注解、命例）
│   ├── export_compact.py         #   白话管线：精简导出（仅 id/标题/原文层，剔除注解与命例代码块）
│   ├── fill_baihua.py            #   白话管线：按 id 幂等回填【白话提要】（--check 只统计）
│   └── baihua_data/              #   白话译文源数据：*.json（{id: 译文}，可分批、可合并）
├── library/                      # 五术典籍内容（山/医/命/相/卜）
│   └── ming/                     # 命·命理
│       └── bazi/                 # 子平八字（现有 11 部 1672 条）
│           ├── core/             #   第一梯队核心典籍（weight 8-10）
│           │   ├── qiongtongbj/  #   穷通宝鉴 122 + INDEX
│           │   ├── zipingzhenquan/ #  子平真诠评注 48 + INDEX
│           │   └── ditianchui/   #   滴天髓阐微 63 + INDEX
│           ├── origin-shensha/    #   第二梯队 渊源与神煞（weight 6）
│           │   ├── sanmingtonghui/ #  三命通会 748 + INDEX
│           │   └── yuanhaiziping/ #   渊海子平赋论 30 + INDEX
│           └── extended/          #   第三梯队 实战辨惑与补遗（weight 2-4）
│               ├── shenfengtongkao/ # 神峰通考 65
│               ├── yuzhaodingzhenjing/ # 玉照定真经 256
│               ├── qianliminggao/ #  千里命稿 22
│               ├── wuxingjingji/  #   五行精纪 74
│               ├── mingliyaoyan/  #   命理约言 119
│               ├── chenggu/       #   袁天罡称骨歌 57
│               ├── lxzmingshu/    #   李虚中命书 68
│               └── luoluozi/      #   珞琭子赋注 62
│           └── ziwei/             # 紫微斗数（subcategory=ziwei）
│               ├── quanshu/       #   紫微斗数全书 17
│               ├── quanji/        #   紫微斗数全集 29
│               └── gusuifu/       #   斗数骨髓赋 29
├── yi/ xiang/ bu/ shan/          # 其余四术（待建，见 library/ 下对应目录）
```

---

## 二、文件命名规范（为什么文件名是英文）

为保证跨平台、跨语言、Git 与代码 `import` / 路径匹配稳定，**所有 Markdown 文件名一律使用 ASCII 英文小写**，
中文标题只出现在文件内的 Frontmatter（`section_title` / `chapter`）与正文标题中。
文件名 = **典籍缩写_定位键**，全局唯一。

### 2.1 天干 / 地支英文对照表（命名与检索共用）

| 天干 | 英文     | 五行 |   | 地支 | 英文     | 节气月 |
| -- | ------ | -- | - | -- | ------ | --- |
| 甲  | `Jia`  | 木  |   | 寅  | `Yin`  | 正月  |
| 乙  | `Yi`   | 木  |   | 卯  | `Mao`  | 二月  |
| 丙  | `Bing` | 火  |   | 辰  | `Chen` | 三月  |
| 丁  | `Ding` | 火  |   | 巳  | `Si`   | 四月  |
| 戊  | `Wu`   | 土  |   | 午  | `Wu`   | 五月  |
| 己  | `Ji`   | 土  |   | 未  | `Wei`  | 六月  |
| 庚  | `Geng` | 金  |   | 申  | `Shen` | 七月  |
| 辛  | `Xin`  | 金  |   | 酉  | `You`  | 八月  |
| 壬  | `Ren`  | 水  |   | 戌  | `Xu`   | 九月  |
| 癸  | `Gui`  | 水  |   | 亥  | `Hai`  | 十月  |
|    |        |    |   | 子  | `Zi`   | 十一月 |
|    |        |    |   | 丑  | `Chou` | 十二月 |

> 时柱 / 日柱文件名用「天干 + 地支」小写连拼，如 甲子 = `jiazi`、丙寅 = `bingyin`、己亥 = `jihai`。

### 2.2 各典籍文件名规则

| 典籍（缩写）        | 规则                                                                        | 示例                                                                    |
| ------------- | ------------------------------------------------------------------------- | --------------------------------------------------------------------- |
| 穷通宝鉴 `qtbj`   | `qtbj_<日干>_<月令>`；合并月两支连写；季度用 spring/summer/autumn/winter；参考用 `qtbj_ref_*` | `qtbj_jia_yin.md`= 甲日寅月；`qtbj_ji_summer.md`= 己土三夏                     |
| 子平真诠 `zpzq`   | `zpzq_ch<两位章号>_<拼音>`                                                      | `zpzq_ch31_zhengguan.md`= 第 31 章论正官                                   |
| 滴天髓 `dtcs`    | `dtcs_<ts\|lq><两位篇号>_<拼音>`（ts = 通神论，lq = 六亲论）                             | `dtcs_ts29_hannuan.md`= 通神论 29 寒暖；`dtcs_lq12_congxiang.md`= 六亲论 12 从象 |
| 三命通会 `smth`   | 神煞 `smth_ss_<拼音>`；日时断 `smth_rs_<日柱拼音>_<时柱拼音>`（源文重出加 `_2`）                 | `smth_ss_tianyiguiren.md`= 天乙贵人；`smth_rs_gengzi_jimao.md`= 庚子日己卯时     |
| 渊海子平 `yhzp`   | `yhzp_<两位序号>_<拼音>`                                                        | `yhzp_25_wuyandubu.md`= 第 25 篇五言独步                                    |
| 神峰通考 `sftk`   | `sftk_<两位序号>_<拼音>`                                                        | `sftk_08_bingyao.md`= 第 8 节病药说类                                       |
| 玉照定真经 `yzzj`  | `yzzj_<三位序号>`（000 = 四库提要）                                                 | `yzzj_001.md`= 第 1 条口诀                                                |
| 千里命稿 `qlmg`   | `qlmg_<两位序号>_<拼音>`                                                        | `qlmg_06_liushen.md`= 第 6 篇六神篇                                        |
| 五行精纪 `wxjj`   | 序 `wxjj_xu1/xu2`；正文 `wxjj_v<两位卷号>_<两位节号>`                                 | `wxjj_v01_01.md`= 卷一第 1 节论六十甲子上；`wxjj_v14_01.md`= 卷十四论天乙贵神        |
| 命理约言 `mlyy`   | 序 `mlyy_xu01`、跋 `mlyy_ba01`；法 `mlyy_fa<NN>`、赋 `mlyy_fu<NN>`、论 `mlyy_lun<NN>`、杂论 `mlyy_za01` | `mlyy_fa01.md`= 卷一第 1 法；`mlyy_lun12.md`= 卷三第 12 论                     |

---

## 三、Frontmatter 字段规范

每个 `.md` 以 YAML Frontmatter 开头，字段即引擎检索索引：

```yaml
---
id: "qtbj_jia_yin"              # 全局唯一，与文件名一致（不含 .md）
book: "穷通宝鉴"                 # 典籍名
chapter: "甲木·寅月"             # 卷章节名
chapter_num: 1                  # 篇/章/条序号（可省略）
section_title: "正月甲木"         # 条目标题（中文）
source_version: "余春台辑本"      # 版本出处
author: "余春台"
dynasty: "清"
type: "monthly"                 # 见下方类型表
conditions:                     # —— 命理匹配规则（检索核心）——
  day_master: ["Jia"]           #   日干（英文枚举）
  month_branch: ["Yin"]         #   月令（英文枚举）
  day_pillar: []                #   日柱（中文六十甲子，三命日时断用）
  hour_pillar: []               #   时柱（中文六十甲子）
  ten_god: []                   #   十神：正官/七杀/正财/偏财/正印/偏印/伤官/食神/比肩/劫财
  pattern: []                   #   格局：正官格/七杀格/财格/印格/从格/化格…
  shensha: []                   #   神煞：天乙贵人/驿马/羊刃…
  keywords: ["调候", "寅月"]      #   关键词（主题召回）
weight: 10                      # 多书命中时的排序权重（见 3.2）
tags: ["穷通宝鉴", "甲木", "寅月"]
---
```

### 3.1 type 取值

| type                                 | 用于                          | 说明                                |
| ------------------------------------ | --------------------------- | --------------------------------- |
| `monthly` / `seasonal` / `reference` | 穷通宝鉴                        | 月度 / 季度合并 / 总论参考                  |
| `chapter`                            | 子平真诠、神峰通考、千里命稿、五行精纪、命理约言 | 按章节                               |
| （part+chapter_num）                  | 滴天髓                         | 通神论 / 六亲论分篇                       |
| `shensha`                            | 三命通会                        | 神煞 / 干支关系，必填 `shensha`            |
| `rishi`                              | 三命通会                        | 日时断，必填 `day_pillar`+`hour_pillar` |
| `fuwen`                              | 渊海子平                        | 歌赋                                |
| `koujue`                             | 玉照定真经                       | 逐条口诀                              |

### 3.2 weight 权重（多书命中时降序展示）

穷通宝鉴月度 **10** ＞ 滴天髓 / 子平格局 **9** ＞ 穷通宝鉴季度 **8** ＞
第二梯队（三命通会、渊海子平）**6** ＞ 穷通宝鉴总论参考 **5** ＞ 神峰通考 **3** ＞
玉照定真经 / 千里命稿 / 五行精纪 / 命理约言 **2**。

### 3.3 各典籍检索差异

- **穷通宝鉴（调候）**：只填 `day_master`+`month_branch`，日干月令 **100% 精确锚定**。
- **子平真诠（格局）**：填 `pattern`+`ten_god`，格局评定后召回。
- **滴天髓（气象理气）**：以 `pattern`/`ten_god`/`keywords` 主题召回，作理论依据层。
- **三命通会（神煞 + 日时断）**：神煞条填 `shensha`；日时断填 `day_pillar`+`hour_pillar`（717 条精确命中）。
- **渊海子平（古歌赋印证）**：以 `keywords` 主题召回，作排盘下方歌赋佐证。
- **神峰通考（病药实战）**：以 `keywords`（病药、雕枯旺弱、盖头、动静等）召回，weight=3。
- **玉照定真经 / 千里命稿（古法流变 / 现代参照）**：玉照以口诀条目供溯源；千里本身为民国白话，按 `ten_god`/`pattern`/`keywords` 召回，weight=2。
- **五行精纪（南宋禄命类书）**：体例为汇编体（每节集《烛神经》《珞琭子》《李虚中》等诸家），泛论以 `keywords` 主题召回纳音、干神支神、禄马官印、六亲运限等古法源流；贵人、合化、刑冲、德合等主题已由 `enrich_conditions.py` 补 `shensha`/`pattern`/`ten_god` 精确标签，weight=2。
- **命理约言（清·陈素庵，韦千里选辑）**：以法 / 赋 / 论分体裁；十神法与赋已补对应子平 `pattern`，诸神煞论只保留 `shensha`（已清除早期按"煞"字误标的 `ten_god=七杀 / pattern=七杀格`），weight=2。

---

## 四、正文分层结构（原文锁死，不可篡改）

通用三层：**【原文】→（古注 / 阐微 / 命例，视版本而定）→【白话提要】**。

铁律：

1. **【原文】一字不改**，异体字、通假字、OCR 俗字（如「夘」= 卯、「徳」= 德、「防」= 凶、「刼」= 劫）均保留原貌；检索字段（`day_pillar` 等）才用规范字，二者分离。
2. 古注 / 阐微与原文分层渲染，不得混排。
3. 【白话提要】只逐条文义串讲、**不新增任何现代断命、不编造**；《千里命稿》本身即白话，保留原讲解、不另译。当前全库白话层已全部补齐（1525 条译文 + 千里 22 条原白话 = 1547 条无占位）。
4. 原书所附四柱 / 大运 / 历代命例统一入代码块或专设层，不与断语混淆。

各书分层一览：

| 典籍           | 分层                                                |
| ------------ | ------------------------------------------------- |
| 穷通宝鉴 / 子平真诠 | 【原文】（+ 评注，若有）→【白话提要】                              |
| 滴天髓阐微       | 【经文】→【刘伯温原注】→【任铁樵阐微】→【附：命例】；另有 3 处现代【校勘按语・若思】单独成层 |
| 三命通会・神煞     | 【原文】（四库白文，夹注保留）→【白话提要】                            |
| 三命通会・日时断    | 【原文】断语 →【附：历代命例引证】（【…】内历代名造）→【白话提要】               |
| 渊海子平        | 【原文】歌赋 →【白话提要】                                    |
| 神峰通考        | 【原文】（现代标点）→【白话提要】                                 |
| 玉照定真经       | 【原文・口诀】→【张颙注】→【白话提要】；000 为【原文（四库提要）】              |
| 千里命稿        | 【原文】白话讲解（连贯，不拆命例）                                 |
| 五行精纪        | 【原文】（汇编诸家，书名出处保留）→【白话提要】                          |
| 命理约言        | 【原文】（韦千里选辑标点本）→【白话提要】                           |

### 4.1 白话回填管线（幂等、可复跑）

为保证「原文锁死、只改白话层」，白话校补走独立管线，不直接手改 md：

```
# 1) 导出某书 id/标题/原文（完整版，含注解、命例代码块）
python scripts/export_for_baihua.py <book_dir> [tag]
# 1') 或精简导出（仅 @@id|标题 + 【原文】层，剔除注解与命例代码块，适合汇编大体量书）
python scripts/export_compact.py <book_dir> [tag]
# 2) 在 scripts/baihua_data/ 下撰写 baihua_<书>_<批>.json，形如 {"条目id": "白话译文"}
#    （可分多批，fill 时自动 glob 合并）
# 3) 幂等回填：按 id 只替换该条白话层首个全角「（待补）」，已是译文则跳过
python scripts/fill_baihua.py            # 执行回填
python scripts/fill_baihua.py --check    # 只统计已补 / 待补，不写文件
```

---

## 五、排盘引擎如何检索（调用逻辑）

程序启动**一次性加载根 `manifest.json`**（无需遍历目录、运行时不依赖 YAML 解析），
将每条 `conditions` 载入内存索引；正文仍在 `path` 指向的 Markdown，命中后按需读取、分层渲染。

```
排盘内核输出八字
 ├─ 日干=Jia, 月令=Yin ──► 穷通宝鉴 day_master∩month_branch → qtbj_jia_yin.md（weight 10）
 ├─ 格局=正官格        ──► 子平真诠/滴天髓/千里命稿/命理约言 pattern 命中
 ├─ 十神=七杀          ──► ten_god 命中（子平 ch39、千里六神篇、命理约言诸论等）
 ├─ 旺衰/从化/调候     ──► 滴天髓 pattern/keywords；神峰病药 keywords
 ├─ 神煞=天乙贵人      ──► 三命通会 shensha；五行精纪卷十三/十四、命理约言贵人论（源流与辨正）
 ├─ 日柱=庚子,时柱=己卯 ──► 三命通会 day_pillar∩hour_pillar → smth_rs_gengzi_jimao.md
 ├─ 纳音/禄马/运限古法 ──► 五行精纪 keywords 主题召回
 └─ 古歌赋佐证         ──► 渊海子平 keywords 召回
```

### 5.1 匹配语义：复合键「组内 AND」、检索维度「组间 OR」

- **组内 AND（复合键必须同时满足）**：调候键 `day_master + month_branch`、
  日时键 `day_pillar + hour_pillar`，组内每个已声明字段都要与命盘相交，
  以保证"甲日寅月""庚子日己卯时"这类精确锚定不被放宽。
- **组间 OR（并列维度任一命中即可）**：`ten_god / pattern / shensha` 是三个独立召回
  理由，一条目同时标了格局与神煞时，命盘只满足格局也应召回，不被其附带的神煞条件误杀。
- 条目**未声明任何结构化硬字段**（序、通论）视为无约束通用条，恒可召回。
- `keywords` 不参与硬匹配，只做主题包含式召回（见参考实现 `keyword_query`）。

```python
# 与 scripts/retrieve_reference.py、engine/src/lib.rs 严格一致
GROUPS = [("day_master", "month_branch"), ("day_pillar", "hour_pillar"),
          ("ten_god",), ("pattern",), ("shensha",)]

def match(cond, chart) -> bool:
    declared_any = False
    for fields in GROUPS:                       # 遍历每个匹配键组
        declared = [f for f in fields if cond.get(f)]
        if not declared:
            continue                            # 该组未声明，不约束
        declared_any = True
        if all(set(cond[f]) & set(chart.get(f, [])) for f in declared):
            return True                         # 某一已声明组整体命中 → 召回（组间 OR）
    return not declared_any                     # 全未声明=通论条，恒召回
```

### 5.2 排序：精确度优先，其次典籍权重

命中结果按 **(命中精确度 ↓, weight ↓, path ↑)** 排序：精确度 = 条目声明的非空结构化
字段数（如穷通调候条同时锚定日干+月令，精确度 2；单维格局/神煞条为 1；无约束通论为 0）。
因此精准锚定条文永远排在无约束通论之前，同精确度内再按典籍梯队 weight 降序，
避免《论用神》这类通论以 weight 10 挤占精确条文。

### 5.3 两套等价参考实现（已交叉自测）

- **Rust（生产）**：`engine/`，纯 `serde_json`、框架无关，Tauri 可直接依赖；
  `Library::from_json` 加载 manifest，`Library::query(&Chart)` 返回排序后的 `&Entry`。
  `cd engine && cargo test`（含加载真实 1547 条 manifest 的用例）。
- **Python（参照 / 快速验证）**：`scripts/retrieve_reference.py`，语义与 Rust 一致，
  带 CLI：`python -X utf8 scripts/retrieve_reference.py --chart '{"day_master":["Jia"]}'`；
  回归测试 `python -X utf8 tests/recall_regression.py`（12 例，覆盖精确锚定、格局/神煞
  召回、元数据增强与误标纠错、排序契约、manifest 完整性）。

---

## 六、如何重新构建（可复现）

环境：Python 3.8+；解析 / 索引仅标准库，质量门需 `pip install pyyaml`。

```
# 1. 下载源文到 raw/（命理约言为网页源，用其专用抓取脚本）
python scripts/download_sources.py
python scripts/fetch_mingliyaoyan.py

# 2. 逐部解析（重复运行前请先清空对应输出目录的 *.md）
python scripts/parse_qiongtong.py
python scripts/parse_ziping.py
python scripts/parse_ditianchui.py
python scripts/parse_sanmingtonghui.py
python scripts/parse_yuanhaiziping.py
python scripts/parse_shenfengtongkao.py
python scripts/parse_yuzhaodingzhenjing.py
python scripts/parse_qianliminggao.py
python scripts/parse_wuxingjingji.py
python scripts/parse_mingliyaoyan.py

# 3. 生成人读导航 INDEX.md 与机读总清单 manifest.json（两者均确定性、可重复生成）
python scripts/build_index.py
python scripts/build_manifest.py

# 4. 交付前质量门校验
python scripts/validate_library.py

# 5. 召回回归测试（Python 参考实现）与 Rust engine 单测
python -X utf8 tests/recall_regression.py
cd engine; cargo test; cd ..

# 6.（可选）白话回填：撰写 scripts/baihua_data/*.json 后
python scripts/fill_baihua.py --check
python scripts/fill_baihua.py
```

> **元数据精准增强**：`scripts/enrich_conditions.py --book <wuxingjingji|mingliyaoyan> [--dry]`
> 以行级、幂等方式只改 Frontmatter 的 conditions 目标行（合并去重 / 移除误标），
> 不重排 YAML、不碰正文；用于把早期主要靠 `keywords` 召回的条目补到 `pattern/shensha/ten_god`
> 精确字段。改动后须重跑步骤 3 的 `build_manifest.py` 与步骤 5 测试。
>
> **交叉校勘**：同主题多书对照见 `docs/`（如天乙贵人的起例分歧、阳贵/阴贵命名对调与异文校记），
> 校勘只记于 docs，绝不回改任何条目【原文】。

---

## 七、版本校勘说明（重要）

1. **穷通宝鉴两系统**：余春台辑通行本（本库底本）与徐乐吾《造化元钥评注》条文有别，本库以余春台本为正文，不混入徐注；余本并非严格 120 条，忠实源文得月度 106 + 季度 3 + 参考 13。
2. **子平真诠源文为 UTF-16 LE**，已无损转 UTF-8；正文标题缺失，以 48 章首句指纹切分（见 `parse_ziping.py` 的 CHAPTERS）。
3. **滴天髓**：标题分隔符顿号 / 空格混用已统一为顿号；「原注云：」是任铁樵引述反驳原注，归阐微层；共 135 句口诀、514 命例、3 处若思按单独分层；《从象》源文无口诀，保持原貌。
4. **三命通会为文渊阁四库无标点白文**：卷尾 OCR 把「三命通会」误作「三命通防」、「六己日」误作「六已日」，解析以日柱条目为切分单元；异体「夘」识别归一、正文保留；六十甲子日时断应 720 条，四库本**源文脱漏 5 条**（己丑日酉时、己亥日巳时、辛丑日亥时、己酉日辰时、丁巳日申时），回查源文确认、不凭空补造；1 条源文重出（己亥日乙丑时）加 `_2` 保留。
5. **渊海子平**此本赋论 30 篇，篇名夹全角空格、个别繁体，标题匹配时归一；该本无《继善篇 / 碧渊赋》（版本差异，《继善篇》见于神峰通考第 43 节）。
6. **神峰通考**为带标点本，共 65 节；「衰 墓 辛 冠 生 论」为「十二长生论」OCR 乱序，已规范标题（正文不改）。
7. **玉照定真经**旧题晋郭璞撰、实为后世依托（四库提要已辨），正文为连续口诀流，张颙注整体在【…】内；≤4 字的【囚】【甲木乙草】等为口诀内嵌夹注，原样并入口诀层。
8. **千里命稿**源文前有目录（跳过），正文自「天干篇」起 22 篇；结束标记「千里命稿终」已剔除。
9. **五行精纪（补遗）**：南宋·廖中撰、三十四卷，同源古籍电子本；卷首数字用异体（第二〇卷「〇」= 零、第廿一卷「廿」= 二十、第卅一卷「卅」= 三十），解析时自写中文数字归一，正文保留原字；忠实源文切为序 2 + 七十二节 = 74 条。该书为禄命法**汇编类书**，每节集录《烛神经》《六微指论》《五行要论》《珞琭子》（莹和尚注）、阎东叟、李虚中、《壶中子》《鬼谷遗文》《玉霄宝鉴》《神白经》《三命纂局》《天元变化书》《太乙统记》等诸家，所引书名在原文中保留，白话只概述该节主旨与所集诸家、不改写引文。
10. **命理约言（补遗）**：清·陈素庵（陈之遴）原著、民国韦千里选辑，源为中华典藏标点本（每卷一大页，序 / 卷一至四 / 跋共六页），`fetch_mingliyaoyan.py` 定向抓取并以 `@@PAGE` 分卷合并；站点把「六合」屏蔽为 `****`（共 6 处，上下文皆「六合对三合」），清洗时据语境还原为「六合」；卷一 48 法、卷二 20 赋、卷三 48 论、卷四杂论二十四则整卷 1 条，加序、跋共 119 条（解析时 assert 48/20/48 校验）。
11. **评估后不入库的两部**：
    - **《造化元钥》**：与《穷通宝鉴》是同书异流（栏江网 → 造化元钥 → 穷通宝鉴，即徐乐吾评注系统），仅得 PDF / 付费 / 文档站碎片，无权威干净纯文本，为避免与穷通宝鉴重复、异文混层，不单独入库；
    - **《星平会海》**：仅得识典古籍 OCR 白文、错讹严重，且近半篇幅为五星七政四余、与子平八字无关，四库提要评其「十失其九」，不引入低质数据。

---

## 八、收录路线图

| Phase        | 典籍                        | 联动场景                | 状态 |
| ------------ | ------------------------- | ------------------- | -- |
| Phase-1      | 穷通宝鉴（122）                 | 日干 × 月令调候，100% 精确锚定 | ✅  |
| Phase-1      | 子平真诠评注（48）                | 格局成败救应、十神格局         | ✅  |
| Phase-2      | 滴天髓阐微（63）                 | 旺衰顺逆、从格化格、气象理气、六亲   | ✅  |
| Phase-3      | 三命通会（748：31 神煞 + 717 日时断） | 神煞全库、日柱 × 时柱断语      | ✅  |
| Phase-3      | 渊海子平赋论（30）                | 古歌赋印证               | ✅  |
| Phase-4      | 神峰通考（65）                  | 病药说、雕枯旺弱、实战五行生克     | ✅  |
| Phase-4      | 玉照定真经（256）                | 早期虚中禄命古法、星命流变       | ✅  |
| Phase-4      | 千里命稿（22）                  | 民国系统化、现代取象参照        | ✅  |
| 补遗（清单外扩展）   | 五行精纪（74）                  | 南宋禄命类书、纳音干支禄马古法源流   | ✅  |
| 补遗（清单外扩展）   | 命理约言（119）                 | 清子平法汇、辨惑、法赋论体系      | ✅  |
| 全量白话校补       | 1525 条白话译文（千里 22 条本白话）    | 每条原文配文义串讲、不新增断命      | ✅  |

> 原始需求清单 8 部到 Phase-4 已全部完成，无预设 Phase-5；「补遗」两行为清单外经同源 / 权威源评估后额外扩展。

---

## 九、边界与免责声明

- 本知识库只负责**检索并呈现古籍原文**，系统不得擅自新增吉凶结论；
- 【白话提要】仅作文义解释，不添加现代断命；
- 原始经文与后世注解视觉分层，避免混淆；
- **传统文化内容仅供学术研究与文献整理参考，不构成任何人生决策依据。**
