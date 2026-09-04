# -*- coding: utf-8 -*-
"""
Aether-Cycle 古籍知识库 · 《三命通会》结构化解析脚本（第二梯队）
源文：四库全书本（无现代标点白文），万民英撰。

产出两部分（均输出到 origin-shensha/sanmingtonghui/）：
  A. 神煞 / 干支关系库（卷二、卷三）：smth_ss_<slug>.md，conditions.shensha / keywords 标引；
  B. 六十甲子日时断（卷八、卷九）：smth_rs_<日柱拼音>_<时柱拼音>.md，
     conditions.day_pillar + hour_pillar 精确标引，排盘按「日柱×时柱」100% 命中。

体例：
  - 原文一字不改，OCR 俗字/异体保留（仅用于标题匹配时做等价归一，不改正文）；
  - 日时断每条：断语入【原文】，行内【…】历代命例引证入【附：历代命例引证】代码块；
  - 大节歌诀 / 六干总论非「日柱×时柱」精确条目不单独入库（原文存 raw/ 可查）。
"""
import os
import re

BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
RAW = os.path.join(BASE, "raw", "sanmingtonghui.txt")
OUT = os.path.join(BASE, "library", "ming", "bazi", "origin-shensha", "sanmingtonghui")
os.makedirs(OUT, exist_ok=True)

STEM = "甲乙丙丁戊己庚辛壬癸"
BRANCH = "子丑寅卯辰巳午未申酉戌亥"
STEM_EN = {"甲":"jia","乙":"yi","丙":"bing","丁":"ding","戊":"wu","己":"ji",
           "庚":"geng","辛":"xin","壬":"ren","癸":"gui"}
BRANCH_EN = {"子":"zi","丑":"chou","寅":"yin","卯":"mao","辰":"chen","巳":"si",
             "午":"wu","未":"wei","申":"shen","酉":"you","戌":"xu","亥":"hai"}
JIAZI = [STEM[i % 10] + BRANCH[i % 12] for i in range(60)]
JIAZI_ALT = "|".join(JIAZI)

# 卷边界（1-based 起始行）
VOL_START = {"二":226, "三":488, "四":982, "八":2373, "九":3696, "十":5112}

# 标题等价归一（仅用于匹配；正文不改）
def norm_title(s):
    s = re.sub(r"【.*?】", "", s)          # 去标题内夹注
    s = s.replace("轝", "舆").replace("徳", "德").replace("刼", "劫").replace("鬭", "斗")
    return s.strip()

# —— A. 神煞 / 干支关系章节白名单：规范标题 -> (slug, [shensha], [keywords], 所属卷) ——
SHENSHA_META = [
    # 卷二·干支作用关系
    ("论十干合",      "shiganhe",     ["十干合"],   ["五合", "甲己合", "乙庚合"], "二"),
    ("论十干化气",    "shiganhuaqi",  ["化气"],     ["合化", "化木化火化金化水化土"], "二"),
    ("论支元六合",    "liuhe",        ["六合"],     ["支元六合", "子丑合", "卯戌合"], "二"),
    ("论支元三合",    "sanhe",        ["三合"],     ["申子辰", "寅午戌", "亥卯未", "巳酉丑"], "二"),
    ("论六害",        "liuhai",       ["六害"],     ["穿害", "子未害"], "二"),
    ("论三刑",        "sanxing",      ["三刑"],     ["寅巳申", "丑戌未", "子卯刑", "自刑"], "二"),
    # 卷三·禄马神煞
    ("论十干禄",      "shiganlu",     ["干禄", "禄神"], ["建禄", "岁禄", "归禄"], "三"),
    ("论金舆",        "jinyu",        ["金舆"],     ["禄前二辰", "金舆扶身"], "三"),
    ("论驿马",        "yima",         ["驿马"],     ["天马", "寅申巳亥", "奔波迁移"], "三"),
    ("总论禄马",      "luma",         ["禄神", "驿马"], ["禄马同乡", "禄马交驰"], "三"),
    ("论天乙贵人",    "tianyiguiren", ["天乙贵人"], ["玉堂贵人", "昼贵夜贵", "吉神之首"], "三"),
    ("论三奇",        "sanqi",        ["三奇贵人"], ["天上三奇", "地下三奇", "人中三奇"], "三"),
    ("论天月德",      "tianyuede",    ["天德贵人", "月德贵人", "天月德"], ["天德合", "月德合", "逢凶化吉"], "三"),
    ("论太极贵",      "taijigui",     ["太极贵人"], ["科名星", "始气"], "三"),
    ("论学堂词馆",    "xuetangciguan",["学堂", "词馆", "魁星", "科名星"], ["文星", "长生学堂"], "三"),
    ("论正印",        "zhengyinsha",  ["正印"],     ["华盖印", "印绶星煞"], "三"),
    ("论德秀",        "dexiu",        ["德秀贵人"], ["德神", "秀气"], "三"),
    ("论劫煞亡神",    "jiesha_wangshen", ["劫煞", "亡神", "大煞", "官符"], ["劫煞十六般", "亡神十六般"], "三"),
    ("论羊刃",        "yangren",      ["羊刃", "飞刃", "唐符"], ["阳刃", "刃头财", "对宫飞刃"], "三"),
    ("论元辰",        "yuanchen",     ["元辰", "毛头星", "大耗"], ["阴阳差错", "破败"], "三"),
    ("论六厄",        "liue",         ["六厄"],     ["剥官", "进退神"], "三"),
    ("论勾绞",        "goujiao",      ["勾绞煞", "爪牙煞"], ["勾神", "绞神"], "三"),
    ("论孤辰寡宿",    "guchenguasu",  ["孤辰", "寡宿", "隔角煞"], ["孤寡", "婚缘薄"], "三"),
    ("论天罗地网",    "tianluodiwang",["天罗地网"], ["戌亥天罗", "辰巳地网"], "三"),
    ("论十恶大败",    "shie dabai",   ["十恶大败"], ["大败日", "禄空"], "三"),
    ("论干支诸字杂犯神煞", "zafanshensha", ["杂煞"], ["诸般杂煞", "干支神煞"], "三"),
    ("总论诸神煞",    "zhulunshensha",["神煞总论"], ["诸神煞", "吉凶权衡"], "三"),
    ("寅申巳亥四宫互换神煞", "huhuan_shen", ["四宫互换神煞"], ["寅申巳亥", "长生四马地"], "三"),
    ("子午卯酉四宫互换神煞", "huhuan_ziwu", ["四宫互换神煞"], ["子午卯酉", "四仲", "桃花地"], "三"),
    ("辰戌丑未四宫互换神煞", "huhuan_chenxu", ["四宫互换神煞"], ["辰戌丑未", "四库", "墓库地"], "三"),
    ("战斗伏降刑冲破合", "zhandoufuxiang", ["刑冲", "破害"], ["战斗", "伏降", "刑冲破合总论"], "三"),
]
SHENSHA_BY_NORM = {t: (slug, ss, kw, vol) for (t, slug, ss, kw, vol) in SHENSHA_META}


def yaml_list(items):
    return "[" + ", ".join(f'"{x}"' for x in items) + "]"


def pillar_en(p):
    return (STEM_EN[p[0]] + BRANCH_EN[p[1]]).lower()


# ============ A. 解析神煞章节 ============
def parse_shensha(lines):
    # 扫描卷二、卷三，定位白名单标题位置
    v2s, v3s, v4s = VOL_START["二"]-1, VOL_START["三"]-1, VOL_START["四"]-1
    marks = []
    for i in range(v2s, v4s):
        nt = norm_title(lines[i].strip())
        if nt in SHENSHA_BY_NORM:
            slug, ss, kw, vol = SHENSHA_BY_NORM[nt]
            marks.append((i, nt, slug, ss, kw, vol))
    docs = []
    for idx, (i, title, slug, ss, kw, vol) in enumerate(marks):
        end = marks[idx+1][0] if idx+1 < len(marks) else VOL_START["四"]-1
        body = [lines[j].strip() for j in range(i+1, end) if lines[j].strip()]
        body = [b for b in body if b != "钦定四库全书" and not b.startswith("明　万民英")]
        docs.append((title, slug, ss, kw, vol, body))
    return docs


def render_shensha(title, slug, ss, kw, vol, body):
    cid = f"smth_ss_{slug}"
    chapter = f"卷{vol}·神煞干支"
    tags = ["三命通会", "神煞", title] + ss + kw[:2]
    fm = f"""---
id: "{cid}"
book: "三命通会"
chapter: "{chapter}"
section_title: "{title}"
source_version: "文渊阁四库全书本（无标点白文）"
author: "万民英"
dynasty: "明"
type: "shensha"
conditions:
  day_master: []
  month_branch: []
  day_pillar: []
  hour_pillar: []
  ten_god: []
  pattern: []
  shensha: {yaml_list(ss)}
  keywords: {yaml_list(kw)}
weight: 6
tags: {yaml_list(tags)}
---
"""
    out = [fm, f"### {title}", "", "**【原文】**", ""]
    out += body
    out += ["", "**【白话提要】**", "", "（待补）", ""]
    return cid, "\n".join(out).rstrip() + "\n"


# ============ B. 解析六十甲子日时断 ============
ITEM_RE = re.compile(rf"^({JIAZI_ALT})日({JIAZI_ALT})时")
SEC_RE = re.compile(rf"^六[甲乙丙丁戊己庚辛壬癸已]日{JIAZI_ALT}时断")
# 大节层面的歌诀 / 六干总论（非日柱精确条目）
GEN_RE = re.compile(rf"^六[甲乙丙丁戊己庚辛壬癸已]日生时")
GANGAN_RE = re.compile(r"^[甲乙丙丁戊己庚辛壬癸]日.{1,2}时")
# 干支 OCR 异体归一（仅用于识别与检索字段；正文原文保留异体不改）
GZ_VARIANT = str.maketrans({"夘": "卯"})
def gz_norm(s):
    return s.translate(GZ_VARIANT)


def parse_rishi(lines):
    s = VOL_START["八"]-1
    e = VOL_START["十"]-1
    items = []
    cur = None          # (dp, hp, yuanwen_lines, mingli_lines, in_case)
    def flush():
        if cur:
            items.append((cur[0], cur[1], cur[2], cur[3]))
    for i in range(s, e):
        raw = lines[i].strip()
        if not raw or raw == "钦定四库全书" or raw.startswith("明　万民英") or raw.startswith("三命通"):
            continue
        t = gz_norm(raw)                 # 归一化副本用于识别；raw 保留原文
        m = ITEM_RE.match(t)
        if m:
            flush()
            cur = [m.group(1), m.group(2), [raw], [], False]
            continue
        if SEC_RE.match(t) or GEN_RE.match(t) or t.startswith("以上"):
            flush(); cur = None; continue
        if cur is None:
            continue
        dp, hp, yw, ml, in_case = cur
        # 单干总论（甲日甲子时…）出现即结束当前日柱条目
        if GANGAN_RE.match(t) and not in_case:
            flush(); cur = None; continue
        if in_case:
            ml.append(raw)
            if t.count("】") >= t.count("【"):
                cur[4] = False
            continue
        if t.startswith("【"):
            ml.append(raw)
            if t.count("【") > t.count("】"):
                cur[4] = True
            continue
        # 非命例、非夹注的散文/歌诀行 = 大节层内容，结束当前条目
        flush(); cur = None
    flush()
    return items


def render_rishi(dp, hp, yw, ml, suffix=""):
    cid = f"smth_rs_{pillar_en(dp)}_{pillar_en(hp)}" + suffix
    tags = ["三命通会", "日时断", f"{dp}日", f"{hp}时"]
    fm = f"""---
id: "{cid}"
book: "三命通会"
chapter: "卷八至卷九·六十甲子日时断"
section_title: "{dp}日{hp}时断"
source_version: "文渊阁四库全书本（无标点白文）"
author: "万民英"
dynasty: "明"
type: "rishi"
conditions:
  day_master: []
  month_branch: []
  day_pillar: ["{dp}"]
  hour_pillar: ["{hp}"]
  ten_god: []
  pattern: []
  shensha: []
  keywords: ["日时断", "{dp}日", "{hp}时"]
weight: 6
tags: {yaml_list(tags)}
---
"""
    out = [fm, f"### {dp}日{hp}时断", "", "**【原文】**", ""]
    out += yw
    if ml:
        out += ["", "**【附：历代命例引证】**", "```text"]
        out += ml
        out += ["```"]
    out += ["", "**【白话提要】**", "", "（待补）", ""]
    return cid, "\n".join(out).rstrip() + "\n"


def main():
    lines = open(RAW, encoding="utf-8").read().splitlines()
    # A
    ss_docs = parse_shensha(lines)
    n_ss = 0
    for title, slug, ss, kw, vol, body in ss_docs:
        cid, md = render_shensha(title, slug, ss, kw, vol, body)
        with open(os.path.join(OUT, f"{cid}.md"), "w", encoding="utf-8") as f:
            f.write(md)
        n_ss += 1
    print(f"神煞/干支章节：{n_ss} 个")
    # B
    items = parse_rishi(lines)
    seen = {}
    n_rs = 0
    for dp, hp, yw, ml in items:
        key = (dp, hp)
        seen[key] = seen.get(key, 0) + 1
        suffix = "" if seen[key] == 1 else f"_{seen[key]}"
        cid, md = render_rishi(dp, hp, yw, ml, suffix)
        with open(os.path.join(OUT, f"{cid}.md"), "w", encoding="utf-8") as f:
            f.write(md)
        n_rs += 1
    dup = [k for k, v in seen.items() if v > 1]
    print(f"日时断条目：{n_rs} 条，去重组合 {len(seen)}，重复组合 {dup}")
    print(f"合计输出 {n_ss + n_rs} 个 Markdown -> {OUT}")


if __name__ == "__main__":
    main()
