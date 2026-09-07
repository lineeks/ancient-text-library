# -*- coding: utf-8 -*-
"""
Aether-Cycle 古籍知识库 · 索引生成脚本（全库）
扫描 core / origin-shensha / extended 下全部 Markdown，解析 Frontmatter，生成：
  - INDEX.md                                   全库总索引
  - 每部典籍子目录下的 INDEX.md
"""
import os
import re
from collections import defaultdict

BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
ROOTS = ["library/ming/bazi/core", "library/ming/bazi/origin-shensha", "library/ming/bazi/extended", "library/ming", "library/yi", "library/xiang", "library/bu", "library/shan"]

STEM_ORDER = ["甲", "乙", "丙", "丁", "戊", "己", "庚", "辛", "壬", "癸"]
STEM_EN = {"甲": "Jia", "乙": "Yi", "丙": "Bing", "丁": "Ding", "戊": "Wu",
           "己": "Ji", "庚": "Geng", "辛": "Xin", "壬": "Ren", "癸": "Gui"}
BRANCH_ORDER = ["Yin", "Mao", "Chen", "Si", "Wu", "Wei", "Shen", "You", "Xu", "Hai", "Zi", "Chou"]
BRANCH_ZH = {"Yin": "寅·正月", "Mao": "卯·二月", "Chen": "辰·三月", "Si": "巳·四月",
             "Wu": "午·五月", "Wei": "未·六月", "Shen": "申·七月", "You": "酉·八月",
             "Xu": "戌·九月", "Hai": "亥·十月", "Zi": "子·十一月", "Chou": "丑·十二月"}
ZH_BRANCH_ORDER = ["子", "丑", "寅", "卯", "辰", "巳", "午", "未", "申", "酉", "戌", "亥"]
ZH_STEM = "甲乙丙丁戊己庚辛壬癸"
ZH_BRANCH = "子丑寅卯辰巳午未申酉戌亥"
JIAZI = [ZH_STEM[i % 10] + ZH_BRANCH[i % 12] for i in range(60)]

LIST_KEYS = {"day_master", "month_branch", "ten_god", "pattern", "shensha",
             "keywords", "tags", "day_pillar", "hour_pillar"}


def parse_frontmatter(path):
    with open(path, encoding="utf-8") as f:
        text = f.read()
    m = re.match(r"^---\n(.*?)\n---", text, re.S)
    if not m:
        return {}, text
    meta = {}
    for line in m.group(1).splitlines():
        mm = re.match(r"^(\w+):\s*(.*)$", line)
        if mm:
            key, val = mm.group(1), mm.group(2).strip().strip('"')
            meta[key] = val
        mm2 = re.match(r"^\s+(\w+):\s*\[(.*)\]", line)
        if mm2 and mm2.group(1) in LIST_KEYS:
            items = [x.strip().strip('"') for x in mm2.group(2).split(",") if x.strip()]
            meta[mm2.group(1)] = items
    return meta, text


def scan(folder):
    result = []
    if not os.path.isdir(folder):
        return result
    for name in sorted(os.listdir(folder)):
        if not name.endswith(".md") or name == "INDEX.md":
            continue
        meta, _ = parse_frontmatter(os.path.join(folder, name))
        meta["_file"] = name
        result.append(meta)
    return result


def num_key(x):
    try:
        return int(x.get("chapter_num", "999"))
    except (ValueError, TypeError):
        return 999


def simple_chapter_index(title, intro, items):
    """通用篇章表：篇号 | 标题 | pattern | ten_god | 关键词 | 文件。"""
    lines = [f"# {title}", "", *[f"> {x}" for x in intro], ""]
    lines += ["| 序号 | 标题 | 格局 pattern | 十神 ten_god | 关键词 | 文件 |",
              "|---|---|---|---|---|---|"]
    for it in sorted(items, key=num_key):
        lines.append(
            f"| {it.get('chapter_num','')} | {it.get('section_title','')} "
            f"| {', '.join(it.get('pattern',[])) or '—'} "
            f"| {', '.join(it.get('ten_god',[])) or '—'} "
            f"| {', '.join(it.get('keywords',[])[:3])} "
            f"| [{it['_file']}](./{it['_file']}) |")
    lines.append("")
    lines.append(f"**统计：共 {len(items)} 个条目。**")
    lines.append("")
    return "\n".join(lines)


# ============================ 第一梯队 ============================
def build_qtbj_index(items):
    monthly = [x for x in items if x.get("type") == "monthly"]
    seasonal = [x for x in items if x.get("type") == "seasonal"]
    refs = [x for x in items if x.get("type") == "reference"]
    lines = ["# 《穷通宝鉴》条目索引", "",
             "> 余春台辑本（清）。文件名规则：`qtbj_<天干英文>_<地支英文>.md`。",
             "> 合并月以两支连写（如 `wuwei`=午未月、`youxu`=酉戌月、`yinmao`=寅卯月、`zichou`=子丑月）。", ""]
    lines += ["## 一、十干 × 十二月 覆盖矩阵", "",
              "说明：单元格内为该「日干×月令」条目文件名（去掉 `qtbj_` 前缀与 `.md` 后缀）；`—` 表示源文该月并入相邻条目或未单列。", ""]
    header = "| 日干＼月令 | " + " | ".join(BRANCH_ZH[b].split("·")[0] for b in BRANCH_ORDER) + " |"
    lines += [header, "|" + "---|" * 13]
    grid = {}
    for it in monthly + seasonal:
        dm = it.get("day_master", [""])[0] if it.get("day_master") else ""
        stem_short = it["_file"].replace("qtbj_", "").replace(".md", "")
        for b in it.get("month_branch", []):
            grid.setdefault(dm, {}).setdefault(b, stem_short)
    for zh in STEM_ORDER:
        en = STEM_EN[zh]
        row = [f"**{zh}** {en}"]
        for b in BRANCH_ORDER:
            row.append(grid.get(en, {}).get(b, "—"))
        lines.append("| " + " | ".join(row) + " |")
    lines.append("")
    lines += ["## 二、月度调候条目明细（排盘日干×月令精确命中）", "",
              "| ID | 标题 | 章节 | 匹配日干 | 匹配月令 | 文件 |",
              "|---|---|---|---|---|---|"]
    def sort_key(x):
        dm = x.get("day_master", [""])[0] if x.get("day_master") else ""
        mb = x.get("month_branch", [""])[0] if x.get("month_branch") else ""
        os_ = list(STEM_EN.values()).index(dm) if dm in STEM_EN.values() else 99
        ob = BRANCH_ORDER.index(mb) if mb in BRANCH_ORDER else 99
        return (os_, ob)
    for it in sorted(monthly, key=sort_key):
        lines.append(f"| `{it.get('id','')}` | {it.get('section_title','')} | {it.get('chapter','')} | {', '.join(it.get('day_master',[]))} | {', '.join(it.get('month_branch',[]))} | [{it['_file']}](./{it['_file']}) |")
    lines.append("")
    if seasonal:
        lines += ["## 三、季度条目（源文按季合并，如己土三夏/三秋/三冬）", "",
                  "| ID | 标题 | 匹配日干 | 匹配月令 | 文件 |", "|---|---|---|---|---|"]
        for it in seasonal:
            lines.append(f"| `{it.get('id','')}` | {it.get('section_title','')} | {', '.join(it.get('day_master',[]))} | {', '.join(it.get('month_branch',[]))} | [{it['_file']}](./{it['_file']}) |")
        lines.append("")
    lines += ["## 四、总论 / 参考条目（不参与月令精确匹配，weight=5）", "",
              "| ID | 标题 | 文件 |", "|---|---|---|"]
    for it in sorted(refs, key=lambda x: x["_file"]):
        lines.append(f"| `{it.get('id','')}` | {it.get('section_title','')} | [{it['_file']}](./{it['_file']}) |")
    lines += ["", f"**统计：月度 {len(monthly)}、季度 {len(seasonal)}、参考 {len(refs)}，合计 {len(items)} 个文件。**", ""]
    return "\n".join(lines)


def build_zpqz_index(items):
    lines = ["# 《子平真诠评注》48章索引", "",
             "> 清·沈孝瞻原著，徐乐吾评注（节本）。文件名规则：`zpzq_ch<两位章号>_<主题拼音>.md`。",
             "> 排盘完成格局评定后，按 `pattern`（格局）或 `ten_god`（十神）字段检索对应章节。", "",
             "| 章 | 标题 | 格局 pattern | 十神 ten_god | 关键词 | 文件 |",
             "|---|---|---|---|---|---|"]
    for it in sorted(items, key=num_key):
        lines.append(f"| {it.get('chapter_num','')} | {it.get('section_title','')} | {', '.join(it.get('pattern',[])) or '—'} | {', '.join(it.get('ten_god',[])) or '—'} | {', '.join(it.get('keywords',[])[:4])} | [{it['_file']}](./{it['_file']}) |")
    lines += ["", f"**统计：共 {len(items)} 章。**", ""]
    return "\n".join(lines)


def build_dts_index(items):
    lines = ["# 《滴天髓阐微》篇章索引", "",
             "> 原文传宋·京图，明·刘伯温原注，清·任铁樵阐微（含若思校勘按语）。",
             "> 文件名规则：`dtcs_<ts|lq><两位篇号>_<主题拼音>.md`（ts=通神论，lq=六亲论）。",
             "> 每篇按「经文口诀 → 刘伯温原注 → 任铁樵阐微 → 附命例」就地分层；属命理哲学/气象理气，",
             "> 排盘判定旺衰、顺逆、从格化格、寒暖燥湿、六亲时按 `pattern` / `ten_god` / `keywords` 召回。", ""]
    for part, zh in [("通神论", "一、通神论（34 篇）：理气·干支·格局·衰旺调候"),
                     ("六亲论", "二、六亲论（29 篇）：六亲·从化·象法·性情岁运")]:
        sub = sorted([x for x in items if x.get("part") == part], key=num_key)
        lines += [f"## {zh}", "",
                  "| 篇 | 标题 | 格局 pattern | 十神 ten_god | 关键词 | 文件 |",
                  "|---|---|---|---|---|---|"]
        for it in sub:
            lines.append(f"| {it.get('chapter_num','')} | {it.get('section_title','')} | {', '.join(it.get('pattern',[])) or '—'} | {', '.join(it.get('ten_god',[])) or '—'} | {', '.join(it.get('keywords',[])[:3])} | [{it['_file']}](./{it['_file']}) |")
        lines.append("")
    lines += ["**统计：共 63 篇（通神论 34 + 六亲论 29），经文口诀 135 句，附四柱/大运命例 514 处，现代校勘按语 3 处单独分层。**", ""]
    return "\n".join(lines)


# ============================ 第二梯队 ============================
def build_smth_index(items):
    rs = [x for x in items if x.get("type") == "rishi"]
    lines = ["# 《三命通会》条目索引", "",
             "> 明·万民英撰，文渊阁四库全书本（无标点白文，原文异体/俗字原样保留）。",
             "> 分两类：① 神煞/干支关系（卷二、卷三）按 `shensha` 召回；",
             "> ② 六十甲子日时断（卷八、卷九）按 `day_pillar` + `hour_pillar` 精确命中。", "",
             "## 一、神煞 / 干支关系（卷二·卷三）", "",
             "| ID | 标题 | 神煞 shensha | 关键词 | 文件 |",
             "|---|---|---|---|---|"]
    # 神煞按固定顺序：用文件名排序即可
    for it in sorted([x for x in items if x.get("type") == "shensha"], key=lambda x: x["_file"]):
        lines.append(f"| `{it.get('id','')}` | {it.get('section_title','')} | {', '.join(it.get('shensha',[]))} | {', '.join(it.get('keywords',[])[:3])} | [{it['_file']}](./{it['_file']}) |")
    lines.append("")

    # 日时断：60 日柱 × 12 时支覆盖
    by_day = defaultdict(dict)
    for it in rs:
        dp = it.get("day_pillar", [""])[0]
        hp = it.get("hour_pillar", [""])[0]
        if dp and hp:
            by_day[dp][hp[1]] = it["_file"]
    lines += ["## 二、六十甲子日时断（卷八·卷九，排盘日柱×时柱精确命中）", "",
              "下表每行为一个日柱，12 列为时支；格内为该「日柱×时柱」条目链接（显示时柱）。`—` 为四库本源文脱漏（共 5 条）。", ""]
    header = "| 日柱＼时支 | " + " | ".join(ZH_BRANCH_ORDER) + " |"
    lines += [header, "|" + "---|" * 13]
    # 时柱英文->中文反查：格内显示时柱中文（取文件名更稳）
    def cell_text(fn):
        # smth_rs_<dp>_<hp>.md -> hp
        stem = fn[:-3].replace("smth_rs_", "")
        parts = stem.split("_")
        hp_en = parts[1] if len(parts) >= 2 else ""
        return f"[{hp_en}](./{fn})"
    n_cover = 0
    for dp in JIAZI:
        row = [f"**{dp}**"]
        for b in ZH_BRANCH_ORDER:
            fn = by_day.get(dp, {}).get(b)
            if fn:
                row.append(cell_text(fn)); n_cover += 1
            else:
                row.append("—")
        lines.append("| " + " | ".join(row) + " |")
    lines.append("")
    lines += [f"**统计：神煞/干支 {len([x for x in items if x.get('type')=='shensha'])} 篇；"
               f"日时断 {len(rs)} 条（覆盖 {n_cover} 个「日柱×时支」格，60×12=720 中源文脱漏 5 条、源文重出 1 条加序号后缀），合计 {len(items)} 个文件。**", ""]
    return "\n".join(lines)


def build_yhzp_index(items):
    return simple_chapter_index(
        "《渊海子平》赋论索引",
        ["宋·徐大升编（明代增补，带标点电子本）。文件名规则：`yhzp_<两位序号>_<拼音>.md`。",
         "本库收录「赋论」部分 30 篇核心歌赋，作为排盘下方的「古歌赋印证」层，按 `keywords` 主题召回。"],
        items)


# ============================ 第三梯队 ============================
def build_sftk_index(items):
    return simple_chapter_index(
        "《神峰通考》章节索引",
        ["明·张楠（张神峰）著，带标点电子本。文件名规则：`sftk_<两位序号>_<拼音>.md`。",
         "核心为「病药说」「雕枯旺弱四病」「损益生长四药」，重五行生克实战、力辟虚妄神煞；按 `keywords` 召回，weight=3。"],
        items)


def build_yzzj_index(items):
    lines = ["# 《玉照定真经》口诀条目索引", "",
             "> 旧题晋·郭璞撰，张颙注（四库本，后世依托）。文件名规则：`yzzj_<三位序号>.md`。",
             "> 早期虚中禄命古法，连续口诀 + 张颙注；000 为四库提要，其余为逐条口诀（原文·口诀 / 张颙注分层），weight=2。", "",
             "| 序号 | 条目（口诀首句） | 文件 |", "|---|---|---|"]
    for it in sorted(items, key=num_key):
        label = it.get("section_title", "")
        lines.append(f"| {it.get('chapter_num','')} | {label} | [{it['_file']}](./{it['_file']}) |")
    lines += ["", f"**统计：四库提要 1 + 口诀 {len(items)-1} 条，合计 {len(items)} 个文件。**", ""]
    return "\n".join(lines)


def build_qlmg_index(items):
    return simple_chapter_index(
        "《千里命稿》篇章索引",
        ["民国·韦千里著，白话系统讲授子平格局与现代取象。文件名规则：`qlmg_<两位序号>_<拼音>.md`。",
         "本篇本身为白话讲解，作为现代参照层，按 `ten_god` / `pattern` / `keywords` 召回，weight=2。"],
        items)


def build_wxjj_index(items):
    """《五行精纪》：序 + 34 卷，按卷分组。"""
    lines = ["# 《五行精纪》条目索引", "",
             "> 宋·廖中撰，岳珂序（南宋绍定元年），34 卷，集早期禄命 / 纳音 / 神煞之大成的类书。",
             "> 文件名规则：`wxjj_xu{1,2}`（序）、`wxjj_v<两位卷>_<两位节>`（卷内小节）。",
             "> 干神条（论甲乙 / 丙丁…）填 `day_master`，禄马贵人 / 刑害空亡等填 `shensha`，十神类填 `ten_god`，余以 `keywords` 召回，weight=2。", ""]

    def vkey(it):
        f = it["_file"]
        if f.startswith("wxjj_xu"):
            return (0, 0, f)
        m = re.search(r"v(\d+)_(\d+)", f)
        return (1, int(m.group(1)) * 100 + int(m.group(2)), f) if m else (9, 0, f)

    lines += ["| ID | 标题 | 日干 | 十神 | 神煞 | 关键词 | 文件 |",
              "|---|---|---|---|---|---|---|"]
    cur = None
    for it in sorted(items, key=vkey):
        chap = it.get("chapter", "")
        if chap != cur:
            cur = chap
            lines.append(f"| **{chap}** |  |  |  |  |  |  |")
        lines.append(
            f"| `{it.get('id','')}` | {it.get('section_title','')} "
            f"| {', '.join(it.get('day_master',[])) or '—'} "
            f"| {', '.join(it.get('ten_god',[])) or '—'} "
            f"| {', '.join(it.get('shensha',[])) or '—'} "
            f"| {', '.join(it.get('keywords',[])[:2])} "
            f"| [{it['_file']}](./{it['_file']}) |")
    xu = len([x for x in items if x["_file"].startswith("wxjj_xu")])
    lines += ["", f"**统计：序 {xu} 篇 + 34 卷分节 {len(items)-xu} 条，合计 {len(items)} 个文件。**", ""]
    return "\n".join(lines)


def build_mlyy_index(items):
    """《命理约言》：序 + 48法 + 20赋 + 48论 + 杂论 + 跋，按类分组。"""
    lines = ["# 《命理约言》条目索引", "",
             "> 清·陈之遴（号素庵）撰，民国韦千里选辑《精选命理约言》标点本（子平旺衰派，以理驭法、简约严谨）。",
             "> 文件名规则：`mlyy_<xu|fa|fu|lun|za|ba><两位序号>.md`（序 / 法 / 赋 / 论 / 杂论 / 跋）。",
             "> 以 `ten_god`（官煞印财食伤比劫）、`pattern`（正官 / 七杀 / 从局 / 化局及诸变格）、`shensha`、`keywords` 召回，weight=2。", ""]
    gname = {"xu": "序", "fa": "卷一·法四十八篇", "fu": "卷二·赋二十篇",
             "lun": "卷三·论四十八篇", "za": "卷四·杂论", "ba": "跋"}
    order = {"xu": 0, "fa": 1, "fu": 2, "lun": 3, "za": 4, "ba": 5}

    def pref(it):
        m = re.match(r"mlyy_([a-z]+)", it.get("id", ""))
        return m.group(1) if m else "z"

    def num(it):
        m = re.search(r"(\d+)", it.get("id", ""))
        return int(m.group(1)) if m else 0

    lines += ["| ID | 标题 | 格局 pattern | 十神 ten_god | 神煞 | 文件 |",
              "|---|---|---|---|---|---|"]
    cur = None
    for it in sorted(items, key=lambda x: (order.get(pref(x), 9), num(x))):
        g = pref(it)
        if g != cur:
            cur = g
            lines.append(f"| **{gname.get(g, g)}** |  |  |  |  |  |")
        lines.append(
            f"| `{it.get('id','')}` | {it.get('section_title','')} "
            f"| {', '.join(it.get('pattern',[])) or '—'} "
            f"| {', '.join(it.get('ten_god',[])) or '—'} "
            f"| {', '.join(it.get('shensha',[])) or '—'} "
            f"| [{it['_file']}](./{it['_file']}) |")
    nfa = len([x for x in items if pref(x) == "fa"]); nfu = len([x for x in items if pref(x) == "fu"])
    nlun = len([x for x in items if pref(x) == "lun"])
    lines += ["", f"**统计：序 1 + 法 {nfa} + 赋 {nfu} + 论 {nlun} + 杂论 1 + 跋 1，合计 {len(items)} 个文件。**", ""]
    return "\n".join(lines)


# ============================ 总索引 ============================
def build_root_index(counts):
    qtbj, zpqz, dts = counts["qiongtongbj"], counts["zipingzhenquan"], counts["ditianchui"]
    smth, yhzp = counts["sanmingtonghui"], counts["yuanhaiziping"]
    sftk, yzzj, qlmg = counts["shenfengtongkao"], counts["yuzhaodingzhenjing"], counts["qianliminggao"]
    wxjj, mlyy = counts["wuxingjingji"], counts["mingliyaoyan"]
    total = sum(counts.values())
    lines = ["# Aether-Cycle 子平命理古籍知识库 · 总索引", "",
             "本知识库面向八字排盘引擎的**即时检索、引经据典、原汁原味**需求构建。",
             "每条古籍条文以 Markdown + YAML Frontmatter 标引，排盘内核输出 `日干 / 月令 / 格局 / 十神 / 神煞 / 日柱 / 时柱` 后，",
             "对 `conditions` 字段做数组交集匹配，毫秒级返回分层内容（原文/经文、古注、阐微、命例、白话提要）。", "",
             "## 典籍收录进度", "",
             "| 梯队 | 典籍 | 版本 | 文件数 | 索引 | 状态 |",
             "|---|---|---|---|---|---|",
             f"| 第一梯队 | 穷通宝鉴 | 余春台辑本 | {qtbj} | [索引](./library/ming/bazi/core/qiongtongbj/INDEX.md) | ✅ |",
             f"| 第一梯队 | 子平真诠评注 | 沈孝瞻·徐乐吾评注 | {zpqz} | [索引](./library/ming/bazi/core/zipingzhenquan/INDEX.md) | ✅ |",
             f"| 第一梯队 | 滴天髓阐微 | 京图(传)·刘伯温·任铁樵 | {dts} | [索引](./library/ming/bazi/core/ditianchui/INDEX.md) | ✅ |",
             f"| 第二梯队 | 三命通会 | 万民英·四库本 | {smth} | [索引](./library/ming/bazi/origin-shensha/sanmingtonghui/INDEX.md) | ✅ |",
             f"| 第二梯队 | 渊海子平 | 徐大升编·赋论30篇 | {yhzp} | [索引](./library/ming/bazi/origin-shensha/yuanhaiziping/INDEX.md) | ✅ |",
             f"| 第三梯队 | 神峰通考 | 张楠（明） | {sftk} | [索引](./library/ming/bazi/extended/shenfengtongkao/INDEX.md) | ✅ |",
             f"| 第三梯队 | 玉照定真经 | 旧题郭璞·张颙注 | {yzzj} | [索引](./library/ming/bazi/extended/yuzhaodingzhenjing/INDEX.md) | ✅ |",
             f"| 第三梯队 | 千里命稿 | 韦千里（民国） | {qlmg} | [索引](./library/ming/bazi/extended/qianliminggao/INDEX.md) | ✅ |",
             f"| 补遗·渊源 | 五行精纪 | 廖中（宋）·34卷 | {wxjj} | [索引](./library/ming/bazi/extended/wuxingjingji/INDEX.md) | ✅ |",
             f"| 补遗·子平法汇 | 命理约言 | 陈素庵（清）·韦千里选辑 | {mlyy} | [索引](./library/ming/bazi/extended/mingliyaoyan/INDEX.md) | ✅ |",
             f"| 民俗·称骨 | 袁天罡称骨歌 | 袁天罡（托名·唐）·通行本 | {counts['chenggu']} | [索引](./library/ming/bazi/extended/chenggu/INDEX.md) | ✅ |",
             f"| 补遗·古法禄命 | 李虚中命书 | 旧题鬼谷子撰·唐李虚中注·四库本 | {counts['lxzmingshu']} | [索引](./library/ming/bazi/extended/lxzmingshu/INDEX.md) | ✅ |",
             f"| 补遗·禄命鼻祖 | 珞琭子赋注 | 宋释昙莹撰·四库本 | {counts['luoluozi']} | [索引](./library/ming/bazi/extended/luoluozi/INDEX.md) | ✅ |",
             f"| 命·紫微 | 紫微斗数全书 | 明罗洪先编·精选 | {counts['quanshu']} | [索引](./library/ming/ziwei/quanshu/INDEX.md) | ✅ |",
             f"| 命·紫微 | 紫微斗数全集 | 清代古本·精选 | {counts['quanji']} | [索引](./library/ming/ziwei/quanji/INDEX.md) | ✅ |",
             f"| 命·紫微 | 斗数骨髓赋 | 紫微核心歌诀 | {counts['gusuifu']} | [索引](./library/ming/ziwei/gusuifu/INDEX.md) | ✅ |",
             f"| 补遗·格局赋文 | 兰台妙选 | 明西窗老人·四库本 | {counts['lantaimiaoxuan']} | [索引](./library/ming/bazi/extended/lantaimiaoxuan/INDEX.md) | ✅ |",
             f"| 补遗·子平赋文 | 三命指迷赋 | 宋岳珂补注·四库本 | {counts['sanmingzhimifu']} | [索引](./library/ming/bazi/extended/sanmingzhimifu/INDEX.md) | ✅ |",
             f"| 命·七政四余 | 星学大成 | 明万民英撰·四库本 | {counts['xingxuedacheng']} | [索引](./library/ming/qizheng/xingxuedacheng/INDEX.md) | ✅ |",
             f"| 医·经典 | 黄帝内经素问 | 唐王冰注·宋林亿校 | {counts['suwen']} | [索引](./library/yi/jingdian/suwen/INDEX.md) | ✅ |",
             f"| 医·经典 | 灵枢经 | 四库本 | {counts['lingshu']} | [索引](./library/yi/jingdian/lingshu/INDEX.md) | ✅ |",
             f"| 医·经典 | 八十一难经 | 旧题扁鹊·四库本 | {counts['nanjing']} | [索引](./library/yi/jingdian/nanjing/INDEX.md) | ✅ |",
             f"| 医·经典 | 伤寒论 | 汉张仲景·通行本 | {counts['shanghan']} | [索引](./library/yi/jingdian/shanghan/INDEX.md) | ✅ |",
             f"| 医·经典 | 神农本草经 | 四库本 | {counts['shennong']} | [索引](./library/yi/jingdian/shennong/INDEX.md) | ✅ |",
             f"| 医·方书 | 备急千金要方 | 唐孙思邈·四库本 | {counts['qianjinfang']} | [索引](./library/yi/fangshu/qianjinfang/INDEX.md) | ✅ |",
             f"| 医·方书 | 外台秘要 | 唐王焘·明程校 | {counts['waitaimiyao']} | [索引](./library/yi/fangshu/waitaimiyao/INDEX.md) | ✅ |",
             f"| 医·温病 | 温病条辨 | 清吴鞠通·通行本 | {counts['wenbingtiaobian']} | [索引](./library/yi/wenbing/wenbingtiaobian/INDEX.md) | ✅ |",
             f"| 医·针灸 | 针灸甲乙经 | 晋皇甫谧·四库本 | {counts['zhenjiujiayi']} | [索引](./library/yi/zhenji/zhenjiujiayi/INDEX.md) | ✅ |",
             f"| 医·诊法 | 脉经 | 晋王叔和·四库本 | {counts['maijing']} | [索引](./library/yi/zhenfa/maijing/INDEX.md) | ✅ |",
             f"| 相·人相 | 神相全编 | 明清相术集大成 | {counts['shenxiangquanbian']} | [索引](./library/xiang/renxiang/shenxiangquanbian/INDEX.md) | ✅ |",
             f"| 相·人相 | 柳庄相法 | 清袁珙·通行本 | {counts['liuzhuangxiangfa']} | [索引](./library/xiang/renxiang/liuzhuangxiangfa/INDEX.md) | ✅ |",
             f"| 相·地相 | 撼龙经 | 唐杨筠松·通行本 | {counts['hanlongjing']} | [索引](./library/xiang/dixiang/hanlongjing/INDEX.md) | ✅ |",
             f"| 相·地相 | 葬书 | 晋郭璞·通行本 | {counts['zangshu']} | [索引](./library/xiang/dixiang/zangshu/INDEX.md) | ✅ |",
             f"| 相·地相 | 青囊奥语 | 唐杨筠松·通行本 | {counts['qingnangaoyu']} | [索引](./library/xiang/dixiang/qingnangaoyu/INDEX.md) | ✅ |",
             f"| 卜·易经 | 周易 | 经传合编·通行本 | {counts['zhouyi']} | [索引](./library/bu/yijing/zhouyi/INDEX.md) | ✅ |",
             f"| 卜·六爻 | 火珠林 | 题麻衣道者·通行本 | {counts['huozhulin']} | [索引](./library/bu/liuyao/huozhulin/INDEX.md) | ✅ |",
             f"| 山·丹道 | 周易参同契分章通真义 | 汉魏伯阳·五代彭晓注 | {counts['cantongqi']} | [索引](./library/shan/dandao/cantongqi/INDEX.md) | ✅ |",
             f"| 山·武术 | 太极拳论 | 清王宗岳·艺藏本 | {counts['taijilun']} | [索引](./library/shan/wushu/taijilun/INDEX.md) | ✅ |",
             f"| 山·养生 | 达摩洗髓易筋经 | 艺藏本 | {counts['yijinjing']} | [索引](./library/shan/yangsheng/yijinjing/INDEX.md) | ✅ |",
             f"| **合计** | **38 部** | — | **{total}** | — | — |", "",
             "## 目录结构", "",
             "```text",
             "ancient-text-library/",
             "├── README.md                  # 项目说明、命名规范、Frontmatter 规范、检索方式",
             "├── INDEX.md                   # 本文件：全库总索引",
             "├── raw/                       # 原始下载文本（UTF-8，不修改）",
             "├── scripts/                   # 下载 / 解析 / 索引 / 校验脚本",
             "├── library/                   # 五术典籍内容（山/医/命/相/卜）",
             "│   └── ming/                  # 命·命理（八字/紫微/七政…）",
             "│       └── bazi/              # 子平八字",
             "│           ├── core/          # 第一梯队核心典籍（weight 8-10）",
             "│           │   ├── qiongtongbj/ # 穷通宝鉴 122",
             "│           │   ├── zipingzhenquan/ # 子平真诠评注 48",
             "│           │   └── ditianchui/ # 滴天髓阐微 63",
             "│           ├── origin-shensha/ # 第二梯队 渊源与神煞（weight 6）",
             "│           │   ├── sanmingtonghui/ # 三命通会 31神煞 + 717日时断",
             "│           │   └── yuanhaiziping/ # 渊海子平赋论 30",
             "│           └── extended/      # 第三梯队 实战辨惑参照（weight 2-4）",
             "│               ├── shenfengtongkao/ # 神峰通考 65",
             "│               ├── yuzhaodingzhenjing/ # 玉照定真经 256",
             "│               ├── qianliminggao/ # 千里命稿 22",
             "│               ├── wuxingjingji/ # 五行精纪 74",
             "│               ├── mingliyaoyan/ # 命理约言 119",
             "│               ├── chenggu/   # 袁天罡称骨歌 57",
             "│               ├── lxzmingshu/ # 李虚中命书 68",
             "│               ├── luoluozi/  # 珞琭子赋注 62",
             "│               ├── lantaimiaoxuan/ # 兰台妙选 303",
             "│               └── sanmingzhimifu/ # 三命指迷赋 82",
             "│           └── qizheng/       # 七政四余（subcategory=qizheng）",
             "│               └── xingxuedacheng/ # 星学大成 30",
             "├── yi/                        # 医·中医（library/yi/）",
             "│   └── jingdian/             # 医部经典（subcategory=jingdian）",
             "│       ├── suwen/            #   黄帝内经素问 81",
             "│       ├── lingshu/          #   灵枢经 71",
             "│       ├── nanjing/          #   八十一难经 81",
             "│       ├── shanghan/         #   伤寒论 10",
             "│       └── shennong/         #   神农本草经 313",
             "│   ├── fangshu/              # 方书（subcategory=fangshu）",
             "│   │   ├── qianjinfang/      #   备急千金要方 30",
             "│   │   └── waitaimiyao/      #   外台秘要 40",
             "│   ├── wenbing/              # 温病（subcategory=wenbing）",
             "│   │   └── wenbingtiaobian/  #   温病条辨 6",
             "│   ├── zhenji/               # 针灸（subcategory=zhenji）",
             "│   │   └── zhenjiujiayi/     #   针灸甲乙经 12",
             "│   └── zhenfa/               # 诊法（subcategory=zhenfa）",
             "│       └── maijing/          #   脉经 1",
             "├── xiang/                     # 相·相术（library/xiang/）",
             "│   ├── renxiang/              # 人相（subcategory=renxiang）",
             "│   │   ├── shenxiangquanbian/ #   神相全编 174",
             "│   │   └── liuzhuangxiangfa/  #   柳庄相法 170",
             "│   └── dixiang/               # 地相（subcategory=dixiang）",
             "│       ├── hanlongjing/       #   撼龙经 1",
             "│       ├── zangshu/           #   葬书 1",
             "│       └── qingnangaoyu/      #   青囊奥语 1",
             "├── bu/                          # 卜·卜筮（library/bu/）",
             "│   └── yijing/                  # 易经（subcategory=yijing）",
             "│       └── zhouyi/              #   周易 68（64卦+4传）",
             "│   └── liuyao/                  # 六爻（subcategory=liuyao）",
             "│       └── huozhulin/           #   火珠林 64",
             "├── shan/                        # 山·山术（library/shan/）",
             "│   ├── dandao/                  # 丹道（subcategory=dandao）",
             "│   │   └── cantongqi/           #   周易参同契分章通真义 66",
             "│   ├── wushu/                   # 武术（subcategory=wushu）",
             "│   │   └── taijilun/            #   太极拳论 1",
             "│   └── yangsheng/               # 养生（subcategory=yangsheng）",
             "│       └── yijinjing/           #   达摩洗髓易筋经 22",
             "│           └── ziwei/         # 紫微斗数（subcategory=ziwei）",
             "│               ├── quanshu/   # 紫微斗数全书 17",
             "│               ├── quanji/    # 紫微斗数全集 29",
             "│               └── gusuifu/   # 斗数骨髓赋 29",
             "├── yi/                        # 医·中医（待建，library/yi/）",
             "├── xiang/                     # 相·相术（待建，library/xiang/）",
             "├── bu/                        # 卜·卜筮（待建，library/bu/）",
             "└── shan/                      # 山·仙学养生（待建，library/shan/）",
             "```", "",
             "## 检索字段速查", "",
             "| 场景 | 匹配字段 | 示例 |",
             "|---|---|---|",
             "| 日干×月令调候（穷通宝鉴） | `day_master` + `month_branch` | 甲日寅月 → `qtbj_jia_yin.md` |",
             "| 格局判定（子平真诠/滴天髓/千里命稿） | `pattern` | 正官格 → 相关章节 |",
             "| 旺衰顺逆/从化/气象（滴天髓） | `pattern`/`ten_god`/`keywords` | 从格 → 从象/化象 |",
             "| 日柱×时柱断语（三命通会） | `day_pillar` + `hour_pillar` | 庚子日己卯时 → `smth_rs_gengzi_jimao.md` |",
             "| 神煞出处（三命通会） | `shensha` | 天乙贵人/驿马/羊刃/文昌… |",
             "| 古歌赋印证（渊海子平） | `keywords` | 五言独步/继善篇/喜忌篇 |",
             "| 实战病药（神峰通考） | `keywords` | 病药/雕枯旺弱/盖头 |",
             "| 早期禄命/纳音/神煞源流（五行精纪） | `day_master`/`shensha`/`keywords` | 论甲乙→日干；论禄/马/天乙→神煞 |",
             "| 子平旺衰法汇（命理约言） | `ten_god`/`pattern` | 看正官法/从局法/诸神煞论 |",
             "| 十神专题 | `ten_god` | 正官/七杀/正财/偏财/正印/偏印/伤官/食神/比肩/劫财 |", "",
             "## 权重（weight）排序", "",
             "穷通宝鉴月度 10 ＞ 滴天髓/子平格局 9 ＞ 穷通宝鉴季度 8 ＞ 第二梯队（三命/渊海）6 ＞ 神峰通考 3 ＞ 玉照/千里/五行精纪/命理约言 2 ＞ 穷通总论参考 5（参考类独立排序）。多书同时命中时按 weight 降序展示。", "",
             "> 免责声明：本库仅作传统命理文献的结构化整理与研究参考，原文保持原貌，不构成任何人生决策建议。", ""]
    return "\n".join(lines)


def build_generic_index(title, desc=""):
    """通用书目索引生成器：按 id 排序列出全部条目（适用于结构简单的新增书目）。"""
    def builder(items):
        lines = [f"# {title}", ""]
        if desc:
            lines += [desc, ""]
        lines += ["## 条目索引", ""]
        for it in sorted(items, key=lambda x: x["id"]):
            lines.append(f"- [{it['section_title']}](./{it['id']}.md) — `{it['id']}`")
        lines.append("")
        return "\n".join(lines)
    return builder


def main():
    plan = [
        ("library/ming/bazi/core", "qiongtongbj", build_qtbj_index),
        ("library/ming/bazi/core", "zipingzhenquan", build_zpqz_index),
        ("library/ming/bazi/core", "ditianchui", build_dts_index),
        ("library/ming/bazi/origin-shensha", "sanmingtonghui", build_smth_index),
        ("library/ming/bazi/origin-shensha", "yuanhaiziping", build_yhzp_index),
        ("library/ming/bazi/extended", "shenfengtongkao", build_sftk_index),
        ("library/ming/bazi/extended", "yuzhaodingzhenjing", build_yzzj_index),
        ("library/ming/bazi/extended", "qianliminggao", build_qlmg_index),
        ("library/ming/bazi/extended", "wuxingjingji", build_wxjj_index),
        ("library/ming/bazi/extended", "mingliyaoyan", build_mlyy_index),
        ("library/ming/bazi/extended", "chenggu", build_generic_index(
            "袁天罡称骨歌",
            "称骨算命法：出生年/月/日/时四重量表 + 男命五十二档歌诀（二两一至七两二）。民俗简法，仅供传统文化研究参考。")),
        ("library/ming/bazi/extended", "lxzmingshu", build_generic_index(
            "李虚中命书",
            "旧题鬼谷子撰，唐李虚中注。三柱古法（年月日）纳音论命代表作，四库全书本。含六十甲子纳音论命六十条 + 卷上贵神总论 + 卷中通理物化/真假邪正/升降清浊 + 卷下衰旺取时/三元九限/天承地禄/水土名用。")),
        ("library/ming/bazi/extended", "luoluozi", build_generic_index(
            "珞琭子赋注",
            "宋释昙莹撰，兼收王廷光、李仝注。珞琭子三命消息赋为禄命鼻祖，以赋文体论述五行、干禄、支命、大运、神煞等命理原理，四库全书本。")),
        ("library/ming/ziwei", "quanshu", build_generic_index(
            "紫微斗数全书",
            "明罗洪先编，紫微斗数最系统古籍，强调十二宫与四化关系。核心精选本。")),
        ("library/ming/ziwei", "quanji", build_generic_index(
            "紫微斗数全集",
            "清代古本，紫微斗数重要典籍。核心精选本。")),
        ("library/ming/ziwei", "gusuifu", build_generic_index(
            "斗数骨髓赋",
            "紫微斗数核心歌诀，以赋文体概括星曜性情与宫位断验。")),
        ("library/ming/bazi/extended", "lantaimiaoxuan", build_generic_index(
            "兰台妙选",
            "明西窗老人，专论八字格局贵贱，以赋文体列举贵格贱格与神煞取象，四库全书本。")),
        ("library/ming/bazi/extended", "sanmingzhimifu", build_generic_index(
            "三命指迷赋",
            "宋岳珂补注（依托），专主子平，论夹马夹禄拱库拱贵与五行生克，四库全书本。")),
        ("library/ming/qizheng", "xingxuedacheng", build_generic_index(
            "星学大成",
            "明万民英撰，四库全书本，三十卷，七政四余（五星禄命）集大成之作，汇集星曜图例、观星节要、诸家限例、耶律秘诀、三辰通载等星家古法。")),
        ("library/yi/jingdian", "suwen", build_generic_index(
            "黄帝内经素问",
            "重广补注本，唐王冰注，宋林亿校，81篇，中医理论奠基之作，论阴阳五行、脏腑经络、病机诊法、治则养生。")),
        ("library/yi/jingdian", "lingshu", build_generic_index(
            "灵枢经",
            "四库全书本，81篇，与素问合称黄帝内经，偏重经络针灸、腧穴刺法、病机论治。")),
        ("library/yi/jingdian", "nanjing", build_generic_index(
            "八十一难经",
            "旧题扁鹊撰，四库全书本，81难，以问答体阐释脉学、经络、脏腑、腧穴、针法，为内经要义之提纲。")),
        ("library/yi/jingdian", "shanghan", build_generic_index(
            "伤寒论",
            "汉张仲景撰，通行本，10篇，辨证论治奠基之作，以六经辨证统摄外感热病，载方113首。")),
        ("library/yi/jingdian", "shennong", build_generic_index(
            "神农本草经",
            "四库全书本，上中下三品，313味药，中国现存最早药物学专著，论药物气味、主治、君臣佐使、七情合和。")),
        ("library/yi/fangshu", "qianjinfang", build_generic_index(
            "备急千金要方",
            "唐孙思邈撰，四库全书本，30卷，中国最早临床百科全书，载方5300余首，合方论、针灸、食疗、养生于一体。")),
        ("library/yi/fangshu", "waitaimiyao", build_generic_index(
            "外台秘要",
            "唐王焘撰，明程衍道校，40卷，唐代方书集大成，载方6000余首，集唐以前方书之大成，伤寒遵仲景、论冠病源。")),
        ("library/yi/wenbing", "wenbingtiaobian", build_generic_index(
            "温病条辨",
            "清吴鞠通撰，通行本，6卷，温病学奠基之作，以三焦辨证统摄温病，创银翘散、桑菊饮等名方。")),
        ("library/yi/zhenji", "zhenjiujiayi", build_generic_index(
            "针灸甲乙经",
            "晋皇甫谧撰，四库全书本，12卷，中国现存最早针灸专著，系统整理腧穴、刺法、灸法，为针灸学之祖。")),
        ("library/yi/zhenfa", "maijing", build_generic_index(
            "脉经",
            "晋王叔和撰，四库全书本，10卷，中国现存最早脉学专著，系统整理24种脉象，为脉诊学之祖。")),
        ("library/xiang/renxiang", "shenxiangquanbian", build_generic_index(
            "神相全编",
            "明清相术集大成，通行本，174条，汇集麻衣、柳庄、水镜诸家相法，论五官六府、三停五岳、气色纹痣、骨相声音。")),
        ("library/xiang/renxiang", "liuzhuangxiangfa", build_generic_index(
            "柳庄相法",
            "清袁珙撰，通行本，170条，明清相术代表作，以气色、精神、骨格为相法三要，论男女老幼贵贱寿夭。")),
        ("library/xiang/dixiang", "hanlongjing", build_generic_index(
            "撼龙经",
            "唐杨筠松撰，通行本，峦头派风水鼻祖，专论龙脉行止、星体剥换、龙穴砂水，为地理峦头之宗。")),
        ("library/xiang/dixiang", "zangshu", build_generic_index(
            "葬书",
            "晋郭璞撰，通行本，风水理论奠基之作，首创『气乘风则散，界水则止』之论，为后世堪舆之祖。")),
        ("library/xiang/dixiang", "qingnangaoyu", build_generic_index(
            "青囊奥语",
            "唐杨筠松撰，通行本，理气派风水经典，以阴阳五行、三元九运论龙穴砂水，为玄空理气之宗。")),
        ("library/bu/yijing", "zhouyi", build_generic_index(
            "周易",
            "周易经传合编，通行本，64卦+易传4篇（系辞/说卦/序卦/杂卦），群经之首，大道之源，以阴阳八卦论天地人三才之道，为五术卜部之根本经典。")),
        ("library/bu/liuyao", "huozhulin", build_generic_index(
            "火珠林",
            "题麻衣道者著，通行本，64条，六爻纳甲法鼻祖，以六亲世应、五行旺衰、动变飞伏、冲合刑害论占断，为火珠林派（纳甲筮法）之宗。")),
        ("library/shan/dandao", "cantongqi", build_generic_index(
            "周易参同契分章通真义",
            "汉魏伯阳原著，五代彭晓注，正统道藏太玄部，88章，丹道鼻祖，以周易阴阳象喻论金丹炉火，为内丹学之祖。")),
        ("library/shan/wushu", "taijilun", build_generic_index(
            "太极拳论",
            "清王宗岳撰，艺藏武术本，太极拳经典理论，以阴阳刚柔动静虚实论拳理，为内家拳之宗。")),
        ("library/shan/yangsheng", "yijinjing", build_generic_index(
            "达摩洗髓易筋经",
            "艺藏武术本，22篇，养生导引经典，含易筋经总论、洗髓经总义、正身/侧身/半身/屈身/折身/扭身/倒身/翻身/行身/坐身/定身/卧身十二图说、韦驮劲十二势、立八段锦、坐十二段锦等。")),
    ]
    counts = {}
    for root, book, builder in plan:
        items = scan(os.path.join(BASE, root, book))
        counts[book] = len(items)
        with open(os.path.join(BASE, root, book, "INDEX.md"), "w", encoding="utf-8") as f:
            f.write(builder(items))
        print(f"  {book}: {len(items)} -> INDEX.md")
    with open(os.path.join(BASE, "INDEX.md"), "w", encoding="utf-8") as f:
        f.write(build_root_index(counts))
    print(f"全库总索引已生成，合计 {sum(counts.values())} 个条目。")


if __name__ == "__main__":
    main()
