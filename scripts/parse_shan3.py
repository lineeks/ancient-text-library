# -*- coding: utf-8 -*-
"""
山部第三批·悟真篇解析脚本（纯标准库，确定性输出）

底本：raw/wuzhenpian.txt（中华典藏网，宋张伯端撰）
  4.7KB，卷之上七言四韵16首 + 卷之中七言绝句64首+五言1首
  + 卷之下西江月12首+又1首+绝句5首 = 99条
  北宋张伯端（紫阳真人）撰，道教内丹学核心经典，以诗词形式阐述金丹大道
切分：按「其一/其二.../十六/二一.../六四」等序号标题切分
元数据：category=shan, subcategory=dandao, type=poem, conditions 八键全空
召回：keywords 驱动（悟真篇/张伯端/紫阳真人/金丹/内丹/铅汞/坎离/
  龙虎/火候/抽添/沐浴/玄关/玄牝/性命双修 等）
用法：python -X utf8 scripts/parse_shan3.py
"""
import os
import re

BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def extract_keywords(text):
    kws = ["悟真篇", "山部", "丹道", "内丹", "张伯端", "紫阳真人"]
    mapping = [
        (r"金丹|大药|还丹|灵胎|圣胎", "金丹"),
        (r"铅汞|真铅|汞铅|黑铅|朱砂", "铅汞"),
        (r"坎离|离坎|水火|既济|未济", "坎离水火"),
        (r"龙虎|青龙|白虎|金公|姹女", "龙虎"),
        (r"火候|运火|进火|抽添|温养", "火候"),
        (r"沐浴|刑德|防危|危险", "沐浴防危"),
        (r"玄关|玄牝|玄珠|玄窍|黄庭", "玄关玄牝"),
        (r"性命|神气|魂魄|精神|性命双修", "性命神气"),
        (r"阴阳|乾坤|戊己|黄婆|媒娉", "阴阳乾坤"),
        (r"五行|四象|三才|八卦|九宫", "五行四象"),
        (r"西江月|词|十二首", "西江月词"),
        (r"七言四韵|律诗|一十六首", "七言律诗"),
        (r"七言绝句|六十四首|卦数", "七言绝句"),
        (r"五言|太乙之奇", "五言"),
        (r"无为|清静|自然|混俗|和光", "清静无为"),
        (r"长生|飞升|仙人|真人|神仙", "长生飞升"),
        (r"阴德|德行|功行|三千功行", "德行阴功"),
    ]
    for pattern, kw in mapping:
        if re.search(pattern, text):
            kws.append(kw)
    return list(dict.fromkeys(kws))


def is_poem_title(line):
    """判断是否为诗词序号标题：其一/其二.../十六/二一.../六四/十一/十二/五言四韵一首"""
    s = line.strip()
    if not s or len(s) > 8:
        return False
    # 特殊：五言四韵一首（单首，无序号）
    if s == "五言四韵一首":
        return True
    # 序号格式：其一、其二...其十、十一、十二...十六、二一...六四
    nums = "一二三四五六七八九十"
    if s == "又一首":
        return True
    if re.match(r'^其[一二三四五六七八九十]+$', s):
        return True
    # 十一到十九、二一到六四等（两位中文数字）
    if re.match(r'^[一二三四五六七八九十]{2}$', s):
        if s[0] in nums and s[1] in nums:
            return True
    return False


def main():
    src = os.path.join(BASE, "raw/wuzhenpian.txt")
    out_dir = os.path.join(BASE, "library", "shan", "dandao", "wuzhenpian")
    os.makedirs(out_dir, exist_ok=True)

    text = open(src, encoding="utf-8").read()
    lines = text.split("\n")

    entries = []
    current_juan = "卷之上"
    current_genre = "七言四韵一十六首"
    current_title = None
    current_content = []
    genre_note = ""

    for line in lines:
        s = line.strip()

        # 卷标题
        if s in ("卷之上", "卷之中", "卷之下"):
            if current_title and current_content:
                entries.append((current_juan, current_genre, genre_note, current_title, "\n".join(current_content).strip()))
            current_juan = s
            current_title = None
            current_content = []
            genre_note = ""
            continue

        # 体裁标题（如"七言四韵一十六首"）
        if s and s.endswith("首") and len(s) <= 15 and not is_poem_title(s):
            if current_title and current_content:
                entries.append((current_juan, current_genre, genre_note, current_title, "\n".join(current_content).strip()))
            current_genre = s
            current_title = None
            current_content = []
            genre_note = ""
            continue

        # 体裁注释（如"（以表二八一斤之数）"）
        if s.startswith("（") and s.endswith("）") and current_title is None:
            genre_note = s
            continue

        # 诗词序号标题
        if is_poem_title(s):
            if current_title and current_content:
                entries.append((current_juan, current_genre, genre_note, current_title, "\n".join(current_content).strip()))
            current_title = s
            current_content = []
            continue

        # 正文
        if current_title and s:
            current_content.append(s)

    # 最后一条
    if current_title and current_content:
        entries.append((current_juan, current_genre, genre_note, current_title, "\n".join(current_content).strip()))

    # 写入文件
    for idx, (juan, genre, note, title, content) in enumerate(entries):
        eid = f"shan3_wzp_{idx:03d}"
        full_title = f"{genre}·{title}"
        if note:
            full_title += f" {note}"
        kws = extract_keywords(genre + title + content[:2000])
        tags = ["山部", "丹道", "悟真篇", "内丹"]
        if "律诗" in genre or "四韵" in genre:
            tags.append("七言律诗")
        elif "绝句" in genre and "六十四" in genre:
            tags.append("七言绝句")
        elif "西江月" in genre:
            tags.append("西江月词")
        elif "五言" in genre:
            tags.append("五言")
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
book: "悟真篇"
chapter: "{juan}"
section_title: "{full_title[:30]}"
source_version: "中华典藏网"
author: "张伯端"
dynasty: "北宋"
type: "poem"
conditions:
{cond}
weight: 5
tags: [{tags_str}]
---
"""
        body = f"### {full_title}\n\n"
        body += f"**【原文】**\n{content}\n\n"
        body += f"**【白话提要】**\n此条出自《悟真篇》「{juan}·{genre}·{title}」{note}，为北宋紫阳真人张伯端所述金丹大道原文。悟真篇以诗词形式阐述内丹修炼之要，以铅汞为药物、坎离为水火、龙虎为魂魄、火候为抽添，教人识阴阳颠倒之理、明性命双修之旨，为道教内丹学与周易参同契齐名的核心经典。\n"
        with open(os.path.join(out_dir, f"shan3_wzp_{idx:03d}.md"), "w",
                  encoding="utf-8", newline="\n") as f:
            f.write(fm + "\n" + body)

    print(f"  悟真篇: {len(entries)} 条 → {out_dir}")


if __name__ == "__main__":
    main()
