# -*- coding: utf-8 -*-
"""
山部第四批·八段锦解析脚本（纯标准库，确定性输出）

底本：raw/baduanjin.txt（抖音百科整理，起源宋朝）
  2KB，立式八段锦8式 + 坐式八段锦口诀 = 10条
  中国古代导引养生功法，分立功、坐功两部分，共八段
切分：按「第X式 XXX」标题切分立式8式，坐式口诀独立1条，总述1条
元数据：category=shan, subcategory=yangsheng, type=chapter, conditions 八键全空
召回：keywords 驱动（八段锦/导引/养生/立式/坐式/三焦/脾胃/心火/
  肾腰/气力/百病消/叩齿/咽津/意守丹田 等）
用法：python -X utf8 scripts/parse_shan4.py
"""
import os
import re

BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def extract_keywords(text):
    kws = ["八段锦", "山部", "养生", "导引"]
    mapping = [
        (r"三焦|托天|两手托天", "两手托天理三焦"),
        (r"开弓|射雕|左右开弓", "左右开弓似射雕"),
        (r"脾胃|单举|调理脾胃", "调理脾胃须单举"),
        (r"摇头|摆尾|心火", "摇头摆尾去心火"),
        (r"五劳|七伤|往后瞧", "五劳七伤往后瞧"),
        (r"攀足|固肾|肾腰", "两手攀足固肾腰"),
        (r"攒拳|怒目|增气力", "攒拳怒目增气力"),
        (r"七颠|百病消|背后", "背后七颠百病消"),
        (r"坐式|闭目冥心|叩齿|握固", "坐式八段锦"),
        (r"立式|站式|定步", "立式八段锦"),
        (r"意守丹田|呼吸|吐纳", "意守丹田"),
        (r"叩齿|咽津|津液|鼓漱", "叩齿咽津"),
        (r"任督|小周天|运气", "任督运转"),
        (r"总述|概述|简介", "八段锦总述"),
    ]
    for pattern, kw in mapping:
        if re.search(pattern, text):
            kws.append(kw)
    return list(dict.fromkeys(kws))


def main():
    src = os.path.join(BASE, "raw/baduanjin.txt")
    out_dir = os.path.join(BASE, "library", "shan", "yangsheng", "baduanjin")
    os.makedirs(out_dir, exist_ok=True)

    text = open(src, encoding="utf-8").read()
    lines = text.split("\n")

    entries = []
    current_title = None
    current_content = []
    section = ""

    for line in lines:
        s = line.strip()

        # 分段标记
        if s == "八段锦总述":
            if current_title and current_content:
                entries.append((section, current_title, "\n".join(current_content).strip()))
            section = "总述"
            current_title = "八段锦总述"
            current_content = []
            continue
        if s == "立式八段锦":
            if current_title and current_content:
                entries.append((section, current_title, "\n".join(current_content).strip()))
            section = "立式八段锦"
            current_title = None
            current_content = []
            continue
        if s == "坐式八段锦口诀":
            if current_title and current_content:
                entries.append((section, current_title, "\n".join(current_content).strip()))
            section = "坐式八段锦"
            current_title = "坐式八段锦口诀"
            current_content = []
            continue

        # 立式标题：第X式 XXX
        m = re.match(r'^第[一二三四五六七八]式\s+(.+)$', s)
        if m:
            if current_title and current_content:
                entries.append((section, current_title, "\n".join(current_content).strip()))
            current_title = s
            current_content = []
            continue

        # 正文
        if current_title and s:
            current_content.append(s)

    # 最后一条
    if current_title and current_content:
        entries.append((section, current_title, "\n".join(current_content).strip()))

    # 写入文件
    for idx, (sec, title, content) in enumerate(entries):
        eid = f"shan4_bdj_{idx:03d}"
        kws = extract_keywords(sec + title + content[:2000])
        tags = ["山部", "养生", "八段锦", "导引"]
        if sec == "立式八段锦":
            tags.append("立式八段锦")
        elif sec == "坐式八段锦":
            tags.append("坐式八段锦")
        elif sec == "总述":
            tags.append("八段锦总述")
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
book: "八段锦"
chapter: "{sec}"
section_title: "{title[:30]}"
source_version: "抖音百科整理（起源宋朝）"
author: "佚名（古代导引功法）"
dynasty: "宋"
type: "chapter"
conditions:
{cond}
weight: 4
tags: [{tags_str}]
---
"""
        body = f"### {title}\n\n"
        body += f"**【原文】**\n{content}\n\n"
        body += f"**【白话提要】**\n此条出自《八段锦》「{sec}·{title}」，为中国古代导引养生功法原文。八段锦起源于宋朝，分立功、坐功两部分，共八段，每段一个动作，包括肢体运动和气息调理，练习时应配合意守、呼吸及以意领气，以内功为主，内外相合。八段锦简单易学，历史悠久，流传广泛，深受人民喜爱，为养生导引之经典功法。\n"
        with open(os.path.join(out_dir, f"shan4_bdj_{idx:03d}.md"), "w",
                  encoding="utf-8", newline="\n") as f:
            f.write(fm + "\n" + body)

    print(f"  八段锦: {len(entries)} 条 → {out_dir}")


if __name__ == "__main__":
    main()
