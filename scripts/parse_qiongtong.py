# -*- coding: utf-8 -*-
"""
Aether-Cycle 古籍知识库 · 《穷通宝鉴》结构化解析脚本（v4）
将 raw/qiongtongbaojian.txt 切分为「日干×月令」条目 + 季节/总论参考条目。

标题识别策略（两遍扫描）：
  第一遍：识别全部「标题行」
    T_WUXING        五行总论 / 论木 / 论水 / 论土 / 论金
    T_STEM          论X干（X=甲乙丙丁戊己庚辛壬癸，后带五行字）
    T_SEASON_TOTAL  三春X木总论 / 三夏X木总论 …
    T_SEASON        三春X / 三夏X / 三秋X / 三冬X（分组标题）
    T_MONTH         月度条目：
                      短行：「正月丙火：」「十一二月：」
                      长行段首：「正月甲木，初春尚有余寒…」「正二月甲木，素无取…」
  第二遍：分配正文；判定季节标题为「分组」或「季度条目」。
"""
import os
import re

BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
RAW = os.path.join(BASE, "raw", "qiongtongbaojian.txt")
OUT_DIR = os.path.join(BASE, "library", "ming", "bazi", "core", "qiongtongbj")
os.makedirs(OUT_DIR, exist_ok=True)

STEM_EN = {"甲": "Jia", "乙": "Yi", "丙": "Bing", "丁": "Ding", "戊": "Wu",
           "己": "Ji", "庚": "Geng", "辛": "Xin", "壬": "Ren", "癸": "Gui"}
STEM_ZH = {"甲": "甲木", "乙": "乙木", "丙": "丙火", "丁": "丁火", "戊": "戊土",
           "己": "己土", "庚": "庚金", "辛": "辛金", "壬": "壬水", "癸": "癸水"}
ELEMENT_OF = {"甲": "木", "乙": "木", "丙": "火", "丁": "火", "戊": "土",
              "己": "土", "庚": "金", "辛": "金", "壬": "水", "癸": "水"}

MONTH_BRANCH = {
    "正月": ["Yin"], "二月": ["Mao"], "三月": ["Chen"], "四月": ["Si"],
    "五月": ["Wu"], "六月": ["Wei"], "七月": ["Shen"], "八月": ["You"],
    "九月": ["Xu"], "十月": ["Hai"], "十一月": ["Zi"], "十二月": ["Chou"],
    "正二月": ["Yin", "Mao"], "五六月": ["Wu", "Wei"], "八九月": ["You", "Xu"],
    "十一二月": ["Zi", "Chou"],
}
MONTH_ZH = {
    "正月": "寅月", "二月": "卯月", "三月": "辰月", "四月": "巳月",
    "五月": "午月", "六月": "未月", "七月": "申月", "八月": "酉月",
    "九月": "戌月", "十月": "亥月", "十一月": "子月", "十二月": "丑月",
    "正二月": "寅卯月", "五六月": "午未月", "八九月": "酉戌月", "十一二月": "子丑月",
}
SEASON_ZH = {"三春": "春季", "三夏": "夏季", "三秋": "秋季", "三冬": "冬季"}
SEASON_EN = {"三春": "spring", "三夏": "summer", "三秋": "autumn", "三冬": "winter"}
SEASON_BRANCH = {
    "三春": ["Yin", "Mao", "Chen"], "三夏": ["Si", "Wu", "Wei"],
    "三秋": ["Shen", "You", "Xu"], "三冬": ["Hai", "Zi", "Chou"],
}

MONTH_LIST = "正二月|五六月|八九月|十一二月|正月|二月|三月|四月|五月|六月|七月|八月|九月|十月|十一月|十二月"
STEM_LIST = "甲乙丙丁戊己庚辛壬癸"
# 行首：月名 + 天干（可带五行字）
MONTH_STEM_START = re.compile(rf"^({MONTH_LIST})([{STEM_LIST}])([木火土金水])?")
# 独立短标题行：月名 + 可选天干 + 可选五行 + 冒号，整行很短
SHORT_TITLE = re.compile(rf"^({MONTH_LIST})([{STEM_LIST}])?([木火土金水])?\s*[：:]?$")
WUXING_TITLE_RE = re.compile(r"^(五行总论|论木|论水|论土|论金)\s*$")
STEM_TITLE_RE = re.compile(rf"^论([{STEM_LIST}])([木火土金水])\s*$")
SEASON_TOTAL_RE = re.compile(rf"^(三春|三夏|三秋|三冬)([{STEM_LIST}])([木火土金水])总论\s*$")
SEASON_RE = re.compile(rf"^(三春|三夏|三秋|三冬)([{STEM_LIST}])([木火土金水])?\s*[：:]?$")
MINGLI_RE = re.compile(r"^时日月年")


def clean(s):
    return s.strip()


def read_lines(path):
    with open(path, encoding="utf-8") as f:
        return f.read().splitlines()


def main():
    lines = [clean(l) for l in read_lines(RAW)]

    # ---------- 第一遍：识别标题行 ----------
    # 月度锚点去重：以 (month, stem) 为键，连续重复视为同一条目续段（并入正文，不新增标题）
    titles = []
    last_month_key = None  # (month, stem)
    for i, s in enumerate(lines):
        if not s:
            continue
        if WUXING_TITLE_RE.match(s):
            titles.append({"type": "T_WUXING", "line": i, "title": s, "stem": None})
            last_month_key = None
            continue
        m = STEM_TITLE_RE.match(s)
        if m:
            titles.append({"type": "T_STEM", "line": i, "title": s, "stem": m.group(1)})
            last_month_key = None
            continue
        m = SEASON_TOTAL_RE.match(s)
        if m:
            titles.append({"type": "T_SEASON_TOTAL", "line": i, "title": s,
                           "stem": m.group(2), "season": m.group(1)})
            last_month_key = None
            continue
        # 独立短标题行（月度）
        m = SHORT_TITLE.match(s)
        if m and len(s) <= 9:
            month = m.group(1)
            stem = m.group(2)
            key = (month, stem)
            if key == last_month_key:
                last_month_key = key
                continue  # 同条目续段标题，忽略（其内容并入上一标题正文）
            last_month_key = key
            titles.append({"type": "T_MONTH", "line": i, "title": s.rstrip("：:"),
                           "month": month, "stem": stem, "inline": False})
            continue
        # 长行段首：月名+天干（如「正月甲木，初春…」「四月甲木退气…」）=> 月度条目
        m = MONTH_STEM_START.match(s)
        if m:
            month = m.group(1)
            stem = m.group(2)
            key = (month, stem)
            if key == last_month_key:
                last_month_key = key
                continue  # 同条目续段，正文并入上一标题
            last_month_key = key
            titles.append({"type": "T_MONTH", "line": i, "title": month + STEM_ZH.get(stem, stem),
                           "month": month, "stem": stem, "inline": True})
            continue
        # 季节分组标题
        m = SEASON_RE.match(s)
        if m and len(s) <= 10:
            titles.append({"type": "T_SEASON", "line": i, "title": s.rstrip("：:"),
                           "stem": m.group(2), "season": m.group(1)})
            last_month_key = None
            continue

    print("=== 标题行（前 140 行预览） ===")
    for t in titles[:140]:
        print(f"  L{t['line']+1:<5} {t['type']:<14} {t['title']}")
    print(f"  ... 共 {len(titles)} 个标题")

    # ---------- 第二遍：分配正文（状态机分离命例块） ----------
    # 命例块：以「时日月年」起始，其后为四干行/四支行（可带 tab+时日月年），到空行或长句正文结束
    PILLAR_RE = re.compile(r"^[甲乙丙丁戊己庚辛壬癸子丑寅卯辰巳午未申酉戌亥]{4}(\s|$|\t)")
    for idx, t in enumerate(titles):
        start = t["line"] + (0 if t.get("inline") else 1)
        end = titles[idx + 1]["line"] if idx + 1 < len(titles) else len(lines)
        body, mingli = [], []
        in_mingli = False
        for raw in lines[start:end]:
            s = raw.strip()
            if not s:  # 空行 / 纯全角空格 => 命例块结束
                in_mingli = False
                continue
            if "时日月年" in s:
                in_mingli = True
                mingli.append(s.replace("\t", "  "))
                continue
            if in_mingli:
                if PILLAR_RE.match(s):
                    mingli.append(s.replace("\t", "  "))
                    continue
                # 非四柱行 => 命例块结束，回到正文
                in_mingli = False
                body.append(s)
                continue
            body.append(s)
        t["body"], t["mingli"] = body, mingli

    # ---------- 第三遍：季节标题判定为「分组」还是「季度条目」 ----------
    for idx, t in enumerate(titles):
        if t["type"] != "T_SEASON":
            continue
        has_month_after = False
        for j in range(idx + 1, len(titles)):
            nt = titles[j]
            if nt["type"] in ("T_STEM", "T_SEASON_TOTAL", "T_WUXING"):
                break
            if nt["type"] == "T_MONTH" and nt["stem"] == t["stem"]:
                has_month_after = True
                break
            if nt["type"] == "T_SEASON":
                break
        t["is_group"] = has_month_after
        if has_month_after:
            t["type"] = "T_SEASON_REF"

    # ---------- 生成 ----------
    from collections import Counter
    gen_counter = Counter()
    monthly_titles = []
    for t in titles:
        # 参考层
        if t["type"] in ("T_WUXING", "T_STEM", "T_SEASON_TOTAL", "T_SEASON_REF"):
            body = t["body"]
            if not body and not t["mingli"]:
                continue
            if t["type"] == "T_WUXING":
                rid = "qtbj_ref_wuxing" if t["title"] == "五行总论" else "qtbj_ref_" + {"论木": "mu", "论水": "shui", "论土": "tu", "论金": "jin"}[t["title"]]
                tags = '["总论", "穷通宝鉴"]'
                kw = '["五行总论"]'
            elif t["type"] == "T_STEM":
                rid = f"qtbj_ref_{STEM_EN[t['stem']].lower()}"
                tags = f'["{STEM_ZH[t["stem"]]}", "天干总论"]'
                kw = '["调候", "总论"]'
            else:
                rid = f"qtbj_ref_{STEM_EN[t['stem']].lower()}_{SEASON_EN[t['season']]}"
                tags = f'["{STEM_ZH[t["stem"]]}", "{SEASON_ZH[t["season"]]}总论"]'
                kw = '["调候", "总论"]'
            fm = f"""---
id: "{rid}"
book: "穷通宝鉴"
chapter: "总论"
section_title: "{t['title']}"
source_version: "余春台辑本"
author: "余春台"
dynasty: "清"
type: "reference"
conditions:
  day_master: []
  month_branch: []
  day_pillar: []
  hour_pillar: []
  ten_god: []
  pattern: []
  shensha: []
  keywords: {kw}
weight: 5
tags: {tags}
---
"""
            md = [fm, f"### {t['title']}", "", "**【原文】**", ""]
            for p in body:
                md.append(p); md.append("")
            if t["mingli"]:
                md.append("**【附：命例】**"); md.append("")
                md.append("```text")
                for ml in t["mingli"]:
                    md.append(ml)
                md.append("```"); md.append("")
            md.append("**【白话提要】**"); md.append(""); md.append("（待补）"); md.append("")
            with open(os.path.join(OUT_DIR, f"{rid}.md"), "w", encoding="utf-8") as f:
                f.write("\n".join(md).rstrip() + "\n")
            gen_counter["ref"] += 1
            continue

        if t["type"] == "T_MONTH":
            stem = t["stem"]
            month = t["month"]
            if stem is None:
                # 继承：向上找最近的 T_STEM 或带天干的 T_MONTH
                for j in range(titles.index(t) - 1, -1, -1):
                    pt = titles[j]
                    if pt["type"] == "T_STEM" and pt["stem"]:
                        stem = pt["stem"]; break
                    if pt["type"] == "T_MONTH" and pt["stem"]:
                        stem = pt["stem"]; break
            if stem is None:
                print("!! 无法推断天干:", t["title"], "L", t["line"] + 1)
                continue
            branches = MONTH_BRANCH.get(month)
            if branches is None:
                print("!! 未知月名:", month); continue
            rid = f"qtbj_{STEM_EN[stem].lower()}_{branches[0].lower()}"
            if len(branches) > 1:
                rid += branches[-1].lower()
            month_zh = MONTH_ZH.get(month, month)
            branch_str = ", ".join(branches)
            fm = f"""---
id: "{rid}"
book: "穷通宝鉴"
chapter: "{STEM_ZH[stem]}·{month_zh}"
section_title: "{t['title']}"
source_version: "余春台辑本"
author: "余春台"
dynasty: "清"
type: "monthly"
conditions:
  day_master: ["{STEM_EN[stem]}"]
  month_branch: [{', '.join(f'"{b}"' for b in branches)}]
  day_pillar: []
  hour_pillar: []
  ten_god: []
  pattern: []
  shensha: []
  keywords: ["调候用神", "{month_zh}"]
weight: 10
tags: ["{STEM_ZH[stem]}", "{month_zh}", "调候"]
---
"""
            md = [fm, f"### {t['title']}", "", "**【原文】**", ""]
            for p in t["body"]:
                md.append(p); md.append("")
            if t["mingli"]:
                md.append("**【附：命例】**"); md.append("")
                md.append("```text")
                for ml in t["mingli"]:
                    md.append(ml)
                md.append("```"); md.append("")
            md.append("**【白话提要】**"); md.append(""); md.append("（待补）"); md.append("")
            with open(os.path.join(OUT_DIR, f"{rid}.md"), "w", encoding="utf-8") as f:
                f.write("\n".join(md).rstrip() + "\n")
            gen_counter["monthly"] += 1
            monthly_titles.append(f"{stem}{month}")
            continue

        if t["type"] == "T_SEASON":
            stem, season = t["stem"], t["season"]
            branches = SEASON_BRANCH[season]
            rid = f"qtbj_{STEM_EN[stem].lower()}_{SEASON_EN[season]}"
            season_zh = SEASON_ZH[season]
            branch_str = ", ".join(f'"{b}"' for b in branches)
            fm = f"""---
id: "{rid}"
book: "穷通宝鉴"
chapter: "{STEM_ZH[stem]}·{season_zh}"
section_title: "{t['title']}"
source_version: "余春台辑本"
author: "余春台"
dynasty: "清"
type: "seasonal"
conditions:
  day_master: ["{STEM_EN[stem]}"]
  month_branch: [{branch_str}]
  day_pillar: []
  hour_pillar: []
  ten_god: []
  pattern: []
  shensha: []
  keywords: ["调候用神", "{season_zh}"]
weight: 8
tags: ["{STEM_ZH[stem]}", "{season_zh}", "调候"]
---
"""
            md = [fm, f"### {t['title']}", "", "**【原文】**", ""]
            for p in t["body"]:
                md.append(p); md.append("")
            if t["mingli"]:
                md.append("**【附：命例】**"); md.append("")
                md.append("```text")
                for ml in t["mingli"]:
                    md.append(ml)
                md.append("```"); md.append("")
            md.append("**【白话提要】**"); md.append(""); md.append("（待补）"); md.append("")
            with open(os.path.join(OUT_DIR, f"{rid}.md"), "w", encoding="utf-8") as f:
                f.write("\n".join(md).rstrip() + "\n")
            gen_counter["seasonal"] += 1
            continue

    print(f"\n=== 生成统计 ===")
    print(f"月度条目: {gen_counter['monthly']}")
    print(f"季度条目: {gen_counter['seasonal']}")
    print(f"参考条目: {gen_counter['ref']}")
    print(f"月度标题列表: {monthly_titles}")


if __name__ == "__main__":
    main()
