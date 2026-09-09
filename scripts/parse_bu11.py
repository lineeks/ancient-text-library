# -*- coding: utf-8 -*-
"""
卜部第十一批·卜筮正宗卷二解析脚本（纯标准库，确定性输出）

底本：raw/boshizhengzong_v2.txt（中华典藏网，清王维德字洪绪撰）
  15.2KB，卷二：卦爻呈象并飞伏神卦身定例（八宫64卦飞伏神定例）
切分：按八宫（干/坎/艮/震/巽/离/坤/兑）切分8条，每宫含8卦飞伏定例
元数据：category=bu, subcategory=liuyao, type=chapter, conditions 八键全空
召回：keywords 驱动（卜筮正宗/飞伏神/卦身/八宫/64卦/纳甲/装卦 等）
用法：python -X utf8 scripts/parse_bu11.py
"""
import os
import re

BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

PALACES = [
    ("干宫属金", "干宫"),
    ("坎宫属水", "坎宫"),
    ("艮宫属土", "艮宫"),
    ("震宫属木", "震宫"),
    ("巽宫属木", "巽宫"),
    ("离宫属火", "离宫"),
    ("坤宫属土", "坤宫"),
    ("兑宫属金", "兑宫"),
]


def extract_keywords(text, palace):
    kws = ["卜筮正宗", "卜部", "六爻", "飞伏神", "卦身定例", "纳甲装卦", palace]
    mapping = [
        (r"干为天|天风姤|天山遯|天地否|风地观|山地剥|火地晋|火天大有", "乾宫八卦"),
        (r"坎为水|水泽节|水雷屯|水火既济|泽火革|雷火丰|地火明夷|地水师", "坎宫八卦"),
        (r"艮为山|山火贲|山天大畜|山泽损|火泽睽|天泽履|风泽中孚|风山渐", "艮宫八卦"),
        (r"震为雷|雷地豫|雷水解|雷风恒|地风升|水风井|泽风大过|泽雷随", "震宫八卦"),
        (r"巽为风|风天小畜|风火家人|风雷益|天雷无妄|火雷噬嗑|山雷颐|山风蛊", "巽宫八卦"),
        (r"离为火|火山旅|火风鼎|火水未济|山水蒙|风水涣|天水讼|天火同人", "离宫八卦"),
        (r"坤为地|地雷复|地泽临|地天泰|雷天大壮|泽天夬|水天需|水地比", "坤宫八卦"),
        (r"兑为泽|泽水困|泽地萃|泽山咸|水山蹇|地山谦|雷山小过|雷泽归妹", "兑宫八卦"),
        (r"伏神|飞神|飞来生伏|飞来克伏|伏去生飞|伏神入墓", "飞伏神"),
        (r"缺爻|空亡|卦身", "卦身"),
        (r"八纯|首卦|本宫", "八宫"),
    ]
    for pattern, kw in mapping:
        if re.search(pattern, text):
            kws.append(kw)
    return list(dict.fromkeys(kws))


def main():
    src = os.path.join(BASE, "raw/boshizhengzong_v2.txt")
    out_dir = os.path.join(BASE, "library", "bu", "liuyao", "boshizhengzong")
    os.makedirs(out_dir, exist_ok=True)

    text = open(src, encoding="utf-8").read()

    # 按八宫切分
    entries = []
    positions = []
    for marker, name in PALACES:
        pos = text.find(marker)
        if pos >= 0:
            positions.append((pos, name, marker))
    positions.sort()

    for i, (pos, name, marker) in enumerate(positions):
        end = positions[i + 1][0] if i + 1 < len(positions) else len(text)
        content = text[pos:end].strip()
        if len(content) >= 200:
            entries.append((name, content))

    # 写入文件（续接卷五的编号，从062开始）
    start_idx = 62
    for idx, (name, content) in enumerate(entries):
        eid = f"bu8_bszz_{start_idx + idx:03d}"
        kws = extract_keywords(content[:3000], name)
        tags = ["卜部", "六爻", "卜筮正宗", "飞伏神定例"]
        cond = "\n".join([
            '  day_master: []',
            '  month_branch: []',
            '  day_pillar: []',
            '  hour_pillar: []',
            '  ten_god: []',
            '  pattern: []',
            '  shensha: []',
            f'  keywords: [{", ".join(chr(34)+k+chr(34) for k in kws)}]',
        ])
        tags_str = ", ".join(f'"{t}"' for t in tags)
        fm = f"""---
id: "{eid}"
book: "卜筮正宗"
chapter: "卷二·卦爻呈象并飞伏神卦身定例"
section_title: "{name}八卦飞伏神定例"
source_version: "中华典藏网（清王维德字洪绪号林屋先生撰）"
author: "王维德（字洪绪，号林屋先生）"
dynasty: "清"
type: "chapter"
conditions:
{cond}
weight: 4
tags: [{tags_str}]
---
"""
        body = f"### {name}八卦飞伏神定例\n\n"
        body += f"**【原文】**\n{content}\n\n"
        body += f"**【白话提要】**\n此条出自《卜筮正宗》「卷二·卦爻呈象并飞伏神卦身定例」{name}部分，为清代王维德（字洪绪，号林屋先生）所撰的六爻装卦基础典籍原文。卷二系统阐述八宫64卦的飞伏神定例，每宫首卦（八纯卦）五类俱全，其余七卦如有缺爻，则以本宫首卦对应爻为伏神，飞神为伏神所居之本卦爻，飞来生伏为吉、飞来克伏为凶、伏去生飞为泄气、伏克飞神为出暴，为六爻装卦与寻伏神之基础定例，是六爻学入门之必备。\n"
        with open(os.path.join(out_dir, f"bu8_bszz_{start_idx + idx:03d}.md"), "w",
                  encoding="utf-8", newline="\n") as f:
            f.write(fm + "\n" + body)

    print(f"  卜筮正宗卷二: {len(entries)} 条 → {out_dir}")


if __name__ == "__main__":
    main()
