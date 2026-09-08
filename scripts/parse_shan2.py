# -*- coding: utf-8 -*-
"""
山部第二批·黄庭经解析脚本（纯标准库，确定性输出）

底本：raw/huangtingjing.txt（流芳阁道藏藏外本）
  5.7KB，内景经36章 + 外景经3章 + 高上玉皇胎息经1章 = 40条
  题太上老君授，魏晋上清派核心经典，七言歌诀体，存思五脏六腑之神
切分：按「XXX章第X」标题切分（内景），「X部经第X」（外景），胎息经独立
元数据：category=shan, subcategory=dandao, type=chapter, conditions 八键全空
召回：keywords 驱动（黄庭经/内景/外景/胎息/存思/五脏神/丹田/泥丸/
  三关/精气神/长生/上清派 等）
用法：python -X utf8 scripts/parse_shan2.py
"""
import os
import re

BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def extract_keywords(text):
    kws = ["黄庭经", "山部", "丹道", "存思", "上清派"]
    mapping = [
        (r"内景|上清章|心神章|肝部章", "黄庭内景"),
        (r"外景|上部经|中部经|下部经", "黄庭外景"),
        (r"胎息|伏气|神气", "胎息"),
        (r"泥丸|脑神|发神|眼神", "泥丸九真"),
        (r"心神|丹元|肺神|肝神|肾神|脾神|胆神", "五脏神"),
        (r"丹田|关元|命门|黄庭", "丹田命门"),
        (r"三关|天关|地关|人关", "三关"),
        (r"精气|神气|魂魄|精气神", "精气神"),
        (r"长生|飞升|仙人|真人", "长生飞升"),
        (r"沐浴|存思|存神|念神", "存思修炼"),
        (r"玉池|灵液|金醴|玉英", "津液"),
        (r"三田|上田|中田|下田", "三田"),
    ]
    for pattern, kw in mapping:
        if re.search(pattern, text):
            kws.append(kw)
    return list(dict.fromkeys(kws))


def is_chapter_title(line):
    """判断是否为章节标题行：内景「XXX章第X」、外景「X部经第X」"""
    s = line.strip()
    if not s or len(s) < 4 or len(s) > 15:
        return False
    # 内景：上清章第一、上有章第二...
    if re.match(r'^[\u4e00-\u9fff]{2,8}章第[一二三四五六七八九十]+$', s):
        return True
    # 外景：上部经第一、中部经第二、下部经第三
    if re.match(r'^[上中下]部经第[一二三]$', s):
        return True
    return False


def main():
    src = os.path.join(BASE, "raw/huangtingjing.txt")
    out_dir = os.path.join(BASE, "library", "shan", "dandao", "huangtingjing")
    os.makedirs(out_dir, exist_ok=True)

    text = open(src, encoding="utf-8").read()
    # 校勘：raw中"肺部间第九"为"肺部章第九"异写，统一为章第格式
    text = text.replace("肺部间第九", "肺部章第九")
    lines = text.split("\n")

    # 找到正文开始（跳过书名行）
    entries = []
    current_part = "内景经"
    current_title = None
    current_content = []

    for line in lines:
        s = line.strip()

        # 部分标题
        if s == "内景经":
            current_part = "内景经"
            continue
        if s == "外景经":
            current_part = "外景经"
            # 保存上一条
            if current_title and current_content:
                entries.append((current_part, current_title, "\n".join(current_content).strip()))
            current_title = None
            current_content = []
            continue
        if s == "高上玉皇胎息经":
            current_part = "胎息经"
            if current_title and current_content:
                entries.append((current_part, current_title, "\n".join(current_content).strip()))
            current_title = "高上玉皇胎息经"
            current_content = []
            continue

        # 章节标题
        if is_chapter_title(s):
            if current_title and current_content:
                entries.append((current_part, current_title, "\n".join(current_content).strip()))
            current_title = s
            current_content = []
            continue

        # 正文
        if current_title and s:
            current_content.append(s)

    # 最后一条
    if current_title and current_content:
        entries.append((current_part, current_title, "\n".join(current_content).strip()))

    # 写入文件
    for idx, (part, title, content) in enumerate(entries):
        eid = f"shan2_htj_{idx:03d}"
        kws = extract_keywords(title + content[:2000])
        tags = ["山部", "丹道", "黄庭经"]
        if part == "内景经":
            tags.append("黄庭内景")
        elif part == "外景经":
            tags.append("黄庭外景")
        elif part == "胎息经":
            tags.append("胎息")
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
book: "黄庭经"
chapter: "{part}"
section_title: "{title[:25]}"
source_version: "流芳阁道藏藏外本"
author: "太上老君授（题）"
dynasty: "魏晋"
type: "chapter"
conditions:
{cond}
weight: 5
tags: [{tags_str}]
---
"""
        body = f"### {title}\n\n"
        body += f"**【原文】**\n{content}\n\n"
        body += f"**【白话提要】**\n此条出自《黄庭经》「{part}·{title}」，为上清派存思修炼经典原文。黄庭经以七言歌诀体，详述人身五脏六腑、三丹田、泥丸九宫之神真名号与形貌，教人存思身中诸神、漱咽灵液、固精守气，以达长生久视之道。内景经重在存思身内脏腑之神，外景经重在观照天地与人身对应，胎息经则述神气相守、伏气结胎之要。\n"
        with open(os.path.join(out_dir, f"shan2_htj_{idx:03d}.md"), "w",
                  encoding="utf-8", newline="\n") as f:
            f.write(fm + "\n" + body)

    print(f"  黄庭经: {len(entries)} 条 → {out_dir}")


if __name__ == "__main__":
    main()
