# Aether-Cycle・子平命理古籍知识库

> 面向八字排盘引擎的结构化古籍文库：**即时检索・引经据典・原汁原味**。
> 每条古籍条文以 Markdown + YAML Frontmatter 标引，排盘内核输出
> `日干 / 月令 / 格局 / 十神 / 神煞 / 日柱 / 时柱` 后，对 `conditions` 字段做数组交集匹配，
> 毫秒级返回 **原文（经文）/ 古注（阐微）/ 命例 / 白话提要** 分层内容。

截至当前，全库收录 **8 部典籍、1354 个结构化条目**，质量门全部通过。

---

## 一、目录结构

```text
ancient-text-library/
├── README.md                     # 本文件：命名规范 / Frontmatter 规范 / 检索方式
├── INDEX.md                      # 全库总索引（收录进度 + 分书导航 + 检索字段速查）
├── raw/                          # 原始下载文本（统一 UTF-8，不做内容改动）
│   ├── qiongtongbaojian.txt      #   穷通宝鉴（余春台辑本）
│   ├── zipingzhenquan.txt        #   子平真诠评注（源为 UTF-16 LE，已转 UTF-8）
│   ├── ditiansuichanwei.txt      #   滴天髓阐微
│   ├── sanmingtonghui.txt        #   三命通会（四库本白文）
│   ├── yuanhaiziping.txt         #   渊海子平
│   ├── shenfengtongkao.txt       #   神峰通考
│   ├── yuzhaodingzhenjing.txt    #   玉照定真经（四库本）
│   └── qianliminggao.txt         #   千里命稿
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
│   ├── build_index.py            #   扫描 Frontmatter 生成各级 INDEX.md
│   └── validate_library.py       #   交付前质量门：YAML/id/字段/枚举/分层
├── core/                         # 第一梯队核心典籍（weight 8-10）
│   ├── qiongtongbj/              #   穷通宝鉴 122 + INDEX
│   ├── zipingzhenquan/           #   子平真诠评注 48 + INDEX
│   └── ditianchui/               #   滴天髓阐微 63 + INDEX
├── origin-shensha/               # 第二梯队 渊源与神煞（weight 6）
│   ├── sanmingtonghui/           #   三命通会 748（31 神煞 + 717 日时断）+ INDEX
│   └── yuanhaiziping/            #   渊海子平赋论 30 + INDEX
└── extended/                     # 第三梯队 实战辨惑参照（weight 2-3）
    ├── shenfengtongkao/          #   神峰通考 65 + INDEX
    ├── yuzhaodingzhenjing/       #   玉照定真经 256 + INDEX
    └── qianliminggao/            #   千里命稿 22 + INDEX
```

---

## 二、文件命名规范（为什么文件名是英文）

为保证跨平台、跨语言、Git 与代码 `import` / 路径匹配稳定，**所有 Markdown 文件名一律使用 ASCII 英文小写**，
中文标题只出现在文件内的 Frontmatter（`section_title` / `chapter`）与正文标题中。
文件名 = **典籍缩写_定位键**，全局唯一。

### 2.1 天干 / 地支英文对照表（命名与检索共用）

| 天干 | 英文 | 五行 |  | 地支 | 英文 | 节气月 |
| -- | -- | -- | -- | -- | -- | -- |
| 甲 | `Jia` | 木 |  | 寅 | `Yin` | 正月 |
| 乙 | `Yi` | 木 |  | 卯 | `Mao` | 二月 |
| 丙 | `Bing` | 火 |  | 辰 | `Chen` | 三月 |
| 丁 | `Ding` | 火 |  | 巳 | `Si` | 四月 |
| 戊 | `Wu` | 土 |  | 午 | `Wu` | 五月 |
| 己 | `Ji` | 土 |  | 未 | `Wei` | 六月 |
| 庚 | `Geng` | 金 |  | 申 | `Shen` | 七月 |
| 辛 | `Xin` | 金 |  | 酉 | `You` | 八月 |
| 壬 | `Ren` | 水 |  | 戌 | `Xu` | 九月 |
| 癸 | `Gui` | 水 |  | 亥 | `Hai` | 十月 |
|  |  |  |  | 子 | `Zi` | 十一月 |
|  |  |  |  | 丑 | `Chou` | 十二月 |

> 时柱 / 日柱文件名用「天干+地支」小写连拼，如 甲子=`jiazi`、丙寅=`bingyin`、己亥=`jihai`。

### 2.2 各典籍文件名规则

| 典籍（缩写） | 规则 | 示例 |
| -- | -- | -- |
| 穷通宝鉴 `qtbj` | `qtbj_<日干>_<月令>`；合并月两支连写；季度用 spring/summer/autumn/winter；参考用 `qtbj_ref_*` | `qtbj_jia_yin.md`=甲日寅月；`qtbj_ji_summer.md`=己土三夏 |
| 子平真诠 `zpzq` | `zpzq_ch<两位章号>_<拼音>` | `zpzq_ch31_zhengguan.md`=第31章论正官 |
| 滴天髓 `dtcs` | `dtcs_<ts\|lq><两位篇号>_<拼音>`（ts=通神论，lq=六亲论） | `dtcs_ts29_hannuan.md`=通神论29寒暖；`dtcs_lq12_congxiang.md`=六亲论12从象 |
| 三命通会 `smth` | 神煞 `smth_ss_<拼音>`；日时断 `smth_rs_<日柱拼音>_<时柱拼音>`（源文重出加 `_2`） | `smth_ss_tianyiguiren.md`=天乙贵人；`smth_rs_gengzi_jimao.md`=庚子日己卯时 |
| 渊海子平 `yhzp` | `yhzp_<两位序号>_<拼音>` | `yhzp_25_wuyandubu.md`=第25篇五言独步 |
| 神峰通考 `sftk` | `sftk_<两位序号>_<拼音>` | `sftk_08_bingyao.md`=第8节病药说类 |
| 玉照定真经 `yzzj` | `yzzj_<三位序号>`（000=四库提要） | `yzzj_001.md`=第1条口诀 |
| 千里命稿 `qlmg` | `qlmg_<两位序号>_<拼音>` | `qlmg_06_liushen.md`=第6篇六神篇 |

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

| type | 用于 | 说明 |
| -- | -- | -- |
| `monthly` / `seasonal` / `reference` | 穷通宝鉴 | 月度 / 季度合并 / 总论参考 |
| `chapter` | 子平真诠、神峰通考、千里命稿 | 按章节 |
| （part+chapter_num） | 滴天髓 | 通神论/六亲论分篇 |
| `shensha` | 三命通会 | 神煞/干支关系，必填 `shensha` |
| `rishi` | 三命通会 | 日时断，必填 `day_pillar`+`hour_pillar` |
| `fuwen` | 渊海子平 | 歌赋 |
| `koujue` | 玉照定真经 | 逐条口诀 |

### 3.2 weight 权重（多书命中时降序展示）

穷通宝鉴月度 **10** ＞ 滴天髓 / 子平格局 **9** ＞ 穷通宝鉴季度 **8** ＞
第二梯队（三命通会、渊海子平）**6** ＞ 神峰通考 **3** ＞ 玉照定真经 / 千里命稿 **2**；
穷通宝鉴总论参考类固定 **5**。

### 3.3 各典籍检索差异

- **穷通宝鉴（调候）**：只填 `day_master`+`month_branch`，日干月令 **100% 精确锚定**。
- **子平真诠（格局）**：填 `pattern`+`ten_god`，格局评定后召回。
- **滴天髓（气象理气）**：以 `pattern`/`ten_god`/`keywords` 主题召回，作理论依据层。
- **三命通会（神煞 + 日时断）**：神煞条填 `shensha`（检出神煞即召回原始出处）；日时断填 `day_pillar`+`hour_pillar`（日柱×时柱精确命中，717 条）。
- **渊海子平（古歌赋印证）**：以 `keywords` 主题召回，作排盘下方歌赋佐证。
- **神峰通考（病药实战）**：以 `keywords`（病药、雕枯旺弱、盖头、动静等）召回，weight=3。
- **玉照定真经 / 千里命稿（古法流变 / 现代参照）**：玉照以口诀条目供溯源；千里命稿本身为民国白话，按 `ten_god`/`pattern`/`keywords` 召回，weight=2。

---

## 四、正文分层结构（原文锁死，不可篡改）

通用三层：**【原文】→（古注/阐微/命例，视版本而定）→【白话提要】**。

铁律：
1. **【原文】一字不改**，异体字、通假字、OCR 俗字（如「夘」=卯、「徳」=德、「防」=凶、「刼」=劫）均保留原貌；检索字段（`day_pillar` 等）才用规范字，二者分离。
2. 古注 / 阐微与原文分层渲染，不得混排。
3. 【白话提要】只解释文义、不新增吉凶判断；当前全部标「待补」（千里命稿本身为白话，注明无需另译）。
4. 原书所附四柱 / 大运 / 历代命例统一入代码块或专设层，不与断语混淆。

各书分层一览：

| 典籍 | 分层 |
| -- | -- |
| 穷通宝鉴 / 子平真诠 | 【原文】（+评注，若有）→【白话提要】 |
| 滴天髓阐微 | 【经文】→【刘伯温原注】→【任铁樵阐微】→【附：命例】；另有 3 处现代【校勘按语·若思】单独成层 |
| 三命通会·神煞 | 【原文】（四库白文，夹注保留）→【白话提要】 |
| 三命通会·日时断 | 【原文】断语 →【附：历代命例引证】（【…】内历代名造）→【白话提要】 |
| 渊海子平 | 【原文】歌赋 →【白话提要】 |
| 神峰通考 | 【原文】（现代标点）→【白话提要】 |
| 玉照定真经 | 【原文·口诀】→【张颙注】→【白话提要】；000 为【原文（四库提要）】 |
| 千里命稿 | 【原文】白话讲解（连贯，不拆命例） |

---

## 五、排盘引擎如何检索（调用逻辑）

程序启动一次性扫描全部 `.md`，解析 Frontmatter，将 `conditions` 载入内存索引（HashMap）：

```text
排盘内核输出八字
  ├─ 日干=Jia, 月令=Yin ──► 穷通宝鉴 day_master∩month_branch → qtbj_jia_yin.md（weight 10）
  ├─ 格局=正官格        ──► 子平真诠/滴天髓/千里命稿 pattern 命中
  ├─ 十神=七杀          ──► ten_god 命中（子平 ch39、千里六神篇等）
  ├─ 旺衰/从化/调候     ──► 滴天髓 pattern/keywords；神峰病药 keywords
  ├─ 神煞=天乙贵人      ──► 三命通会 shensha → smth_ss_tianyiguiren.md
  ├─ 日柱=庚子,时柱=己卯 ──► 三命通会 day_pillar∩hour_pillar → smth_rs_gengzi_jimao.md
  └─ 古歌赋佐证         ──► 渊海子平 keywords 召回
结果按 weight 降序合并展示。
```

参考匹配伪代码：

```python
def match(entry: dict, chart: dict) -> bool:
    cond = entry["conditions"]
    for key in ("day_master", "month_branch", "day_pillar", "hour_pillar",
                "pattern", "ten_god", "shensha"):
        if cond.get(key) and not (set(cond[key]) & set(chart.get(key, []))):
            return False        # 声明了该条件但命盘无一命中 → 不召回
    return True                 # 所有已声明条件均有交集 → 召回
```

---

## 六、如何重新构建（可复现）

环境：Python 3.8+；解析 / 索引仅标准库，质量门需 `pip install pyyaml`。

```bash
# 1. 下载源文到 raw/
python scripts/download_sources.py
# 2. 逐部解析（重复运行前请先清空对应输出目录的 *.md）
python scripts/parse_qiongtong.py
python scripts/parse_ziping.py
python scripts/parse_ditianchui.py
python scripts/parse_sanmingtonghui.py
python scripts/parse_yuanhaiziping.py
python scripts/parse_shenfengtongkao.py
python scripts/parse_yuzhaodingzhenjing.py
python scripts/parse_qianliminggao.py
# 3. 生成各级 INDEX.md 与根 INDEX.md
python scripts/build_index.py
# 4. 交付前质量门校验
python scripts/validate_library.py
```

---

## 七、版本校勘说明（重要）

1. **穷通宝鉴两系统**：余春台辑通行本（本库底本）与徐乐吾《造化元钥评注》条文有别，本库以余春台本为正文，不混入徐注；余本并非严格 120 条，忠实源文得月度 106 + 季度 3 + 参考 13。
2. **子平真诠源文为 UTF-16 LE**，已无损转 UTF-8；正文标题缺失，以 48 章首句指纹切分（见 `parse_ziping.py` 的 CHAPTERS）。
3. **滴天髓**：标题分隔符顿号 / 空格混用（「十二  从象」已统一为顿号）；「原注」后冒号 / 逗号 / 分号三种标点已兼容；「原注云：」是任铁樵引述反驳原注，归阐微层；共 135 句口诀、514 命例、3 处若思按单独分层；《从象》源文无口诀，保持原貌。
4. **三命通会为文渊阁四库无标点白文**：
   - 卷尾 OCR 把「三命通会」误作「三命通防」、卷九大节标题「六己日」误作「六已日」，解析以**日柱条目**（`XX日XX时`）为切分单元，不依赖大节标题；
   - 时柱 / 日柱异体「夘」（=卯）共影响数十条，**识别时归一、正文保留原字**，检索字段用规范「己卯」等；
   - 六十甲子日时断应为 60 日柱 × 12 时 = 720，四库本**源文脱漏 5 条**（己丑日酉时、己亥日巳时、辛丑日亥时、己酉日辰时、丁巳日申时），经回查源文确认，不凭空补造；另有 1 条源文重出（己亥日乙丑时），加 `_2` 后缀保留；
   - 大节层面的歌诀 / 六干总论非「日柱×时柱」精确条目，不单独入库（原文存 `raw/` 可查）。
5. **渊海子平**此电子本赋论部分 30 篇，篇名《》内夹全角空格、个别用繁体（人鑑论=人鉴论、五行生剋赋=五行生克赋），标题匹配时归一；该版本无《继善篇/碧渊赋》（版本差异，《继善篇》见于神峰通考第 43 节）。
6. **神峰通考**为带标点本，共 65 节；「衰 墓 辛 冠 生 论」为「十二长生论」的 OCR 乱序，已规范标题（正文不改）。
7. **玉照定真经**旧题晋郭璞撰、实为后世依托（四库提要已辨），正文为连续口诀流、无独立篇标题，张颙注整体在【…】内；≤4 字的【囚】【甲木乙草】等是口诀内嵌夹注，原样并入口诀层，其余【…】为张颙详注并作为条目边界。
8. **千里命稿**源文前有目录（跳过），正文自「天干篇」起 22 篇；结束标记「千里命稿终」已剔除。

---

## 八、收录路线图

| Phase | 典籍 | 联动场景 | 状态 |
| -- | -- | -- | -- |
| Phase-1 | 穷通宝鉴（122） | 日干×月令调候，100% 精确锚定 | ✅ |
| Phase-1 | 子平真诠评注（48） | 格局成败救应、十神格局 | ✅ |
| Phase-2 | 滴天髓阐微（63） | 旺衰顺逆、从格化格、气象理气、六亲 | ✅ |
| Phase-3 | 三命通会（748：31 神煞 + 717 日时断） | 神煞全库、日柱×时柱断语 | ✅ |
| Phase-3 | 渊海子平赋论（30） | 古歌赋印证 | ✅ |
| Phase-4 | 神峰通考（65） | 病药说、雕枯旺弱、实战五行生克 | ✅ |
| Phase-4 | 玉照定真经（256） | 早期虚中禄命古法、星命流变 | ✅ |
| Phase-4 | 千里命稿（22） | 民国系统化、现代取象参照 | ✅ |

---

## 九、边界与免责声明

- 本知识库只负责**检索并呈现古籍原文**，系统不得擅自新增吉凶结论；
- 【白话提要】仅作文义解释，不添加现代断命；
- 原始经文与后世注解视觉分层，避免混淆；
- **传统文化内容仅供学术研究与文献整理参考，不构成任何人生决策依据。**
