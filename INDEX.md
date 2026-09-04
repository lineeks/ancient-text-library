# Aether-Cycle 子平命理古籍知识库 · 总索引

本知识库面向八字排盘引擎的**即时检索、引经据典、原汁原味**需求构建。
每条古籍条文以 Markdown + YAML Frontmatter 标引，排盘内核输出 `日干 / 月令 / 格局 / 十神 / 神煞 / 日柱 / 时柱` 后，
对 `conditions` 字段做数组交集匹配，毫秒级返回分层内容（原文/经文、古注、阐微、命例、白话提要）。

## 典籍收录进度

| 梯队 | 典籍 | 版本 | 文件数 | 索引 | 状态 |
|---|---|---|---|---|---|
| 第一梯队 | 穷通宝鉴 | 余春台辑本 | 122 | [索引](./core/qiongtongbj/INDEX.md) | ✅ |
| 第一梯队 | 子平真诠评注 | 沈孝瞻·徐乐吾评注 | 48 | [索引](./core/zipingzhenquan/INDEX.md) | ✅ |
| 第一梯队 | 滴天髓阐微 | 京图(传)·刘伯温·任铁樵 | 63 | [索引](./core/ditianchui/INDEX.md) | ✅ |
| 第二梯队 | 三命通会 | 万民英·四库本 | 748 | [索引](./origin-shensha/sanmingtonghui/INDEX.md) | ✅ |
| 第二梯队 | 渊海子平 | 徐大升编·赋论30篇 | 30 | [索引](./origin-shensha/yuanhaiziping/INDEX.md) | ✅ |
| 第三梯队 | 神峰通考 | 张楠（明） | 65 | [索引](./extended/shenfengtongkao/INDEX.md) | ✅ |
| 第三梯队 | 玉照定真经 | 旧题郭璞·张颙注 | 256 | [索引](./extended/yuzhaodingzhenjing/INDEX.md) | ✅ |
| 第三梯队 | 千里命稿 | 韦千里（民国） | 22 | [索引](./extended/qianliminggao/INDEX.md) | ✅ |
| 补遗·渊源 | 五行精纪 | 廖中（宋）·34卷 | 74 | [索引](./extended/wuxingjingji/INDEX.md) | ✅ |
| 补遗·子平法汇 | 命理约言 | 陈素庵（清）·韦千里选辑 | 119 | [索引](./extended/mingliyaoyan/INDEX.md) | ✅ |
| **合计** | **10 部** | — | **1547** | — | — |

## 目录结构

```text
ancient-text-library/
├── README.md                  # 项目说明、命名规范、Frontmatter 规范、检索方式
├── INDEX.md                   # 本文件：全库总索引
├── raw/                       # 原始下载文本（UTF-8，不修改）
├── scripts/                   # 下载 / 解析 / 索引 / 校验脚本
├── core/                      # 第一梯队核心典籍（weight 8-10）
│   ├── qiongtongbj/          # 穷通宝鉴 122
│   ├── zipingzhenquan/       # 子平真诠评注 48
│   └── ditianchui/           # 滴天髓阐微 63
├── origin-shensha/           # 第二梯队 渊源与神煞（weight 6）
│   ├── sanmingtonghui/       # 三命通会 31神煞 + 717日时断
│   └── yuanhaiziping/        # 渊海子平赋论 30
└── extended/                 # 第三梯队 实战辨惑参照（weight 2-3）
    ├── shenfengtongkao/      # 神峰通考 65
    ├── yuzhaodingzhenjing/   # 玉照定真经 256
    ├── qianliminggao/        # 千里命稿 22
    ├── wuxingjingji/         # 五行精纪 74（宋·禄命纳音神煞类书）
    └── mingliyaoyan/         # 命理约言 119（清·子平旺衰法汇）
```

## 检索字段速查

| 场景 | 匹配字段 | 示例 |
|---|---|---|
| 日干×月令调候（穷通宝鉴） | `day_master` + `month_branch` | 甲日寅月 → `qtbj_jia_yin.md` |
| 格局判定（子平真诠/滴天髓/千里命稿） | `pattern` | 正官格 → 相关章节 |
| 旺衰顺逆/从化/气象（滴天髓） | `pattern`/`ten_god`/`keywords` | 从格 → 从象/化象 |
| 日柱×时柱断语（三命通会） | `day_pillar` + `hour_pillar` | 庚子日己卯时 → `smth_rs_gengzi_jimao.md` |
| 神煞出处（三命通会） | `shensha` | 天乙贵人/驿马/羊刃/文昌… |
| 古歌赋印证（渊海子平） | `keywords` | 五言独步/继善篇/喜忌篇 |
| 实战病药（神峰通考） | `keywords` | 病药/雕枯旺弱/盖头 |
| 早期禄命/纳音/神煞源流（五行精纪） | `day_master`/`shensha`/`keywords` | 论甲乙→日干；论禄/马/天乙→神煞 |
| 子平旺衰法汇（命理约言） | `ten_god`/`pattern` | 看正官法/从局法/诸神煞论 |
| 十神专题 | `ten_god` | 正官/七杀/正财/偏财/正印/偏印/伤官/食神/比肩/劫财 |

## 权重（weight）排序

穷通宝鉴月度 10 ＞ 滴天髓/子平格局 9 ＞ 穷通宝鉴季度 8 ＞ 第二梯队（三命/渊海）6 ＞ 神峰通考 3 ＞ 玉照/千里/五行精纪/命理约言 2 ＞ 穷通总论参考 5（参考类独立排序）。多书同时命中时按 weight 降序展示。

> 免责声明：本库仅作传统命理文献的结构化整理与研究参考，原文保持原貌，不构成任何人生决策建议。
