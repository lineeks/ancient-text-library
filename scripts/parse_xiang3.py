# -*- coding: utf-8 -*-
"""
相部第二批·雪心赋解析脚本（纯标准库，确定性输出）

底本：raw/xuexinfu.txt（中华典藏网，唐卜应天撰）
  5.9KB，5章（山川理气/地理要略/论山水本源/论水法/论龙脉），约5000字
  唐卜应天（字则巍，号昆仑子）撰，形势峦头风水经典，歌赋体
切分：按「第X章 XXX」标题切分，5条
元数据：category=xiang, subcategory=dixiang, type=chapter, conditions 八键全空
召回：keywords 驱动（雪心赋/地相/风水/峦头/山川理气/龙脉/穴法/
  水法/明堂/水口/龙虎/砂水/阳宅/阴宅 等）
用法：python -X utf8 scripts/parse_xiang3.py
"""
import os
import re

BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def extract_keywords(text):
    kws = ["雪心赋", "相部", "地相", "风水", "峦头"]
    mapping = [
        (r"山川理气|二气|融结|生旺休囚", "山川理气"),
        (r"地理要略|卜宅|葬乘生气|脉认来龙", "地理要略"),
        (r"山水本源|五星|剥换|金木水火土", "山水五星"),
        (r"水法|交锁织结|穿割箭射|水口|明堂", "水法"),
        (r"龙脉|认脉|过峡|剥换|回龙顾祖", "龙脉"),
        (r"穴法|点穴|结穴|真穴|穴位", "穴法"),
        (r"龙虎|青龙|白虎|左龙右虎", "龙虎砂"),
        (r"砂|华表|捍门|罗城|禽星|兽星", "砂法"),
        (r"阳宅|阴宫|阴宅|宅坟", "阳宅阴宅"),
        (r"明堂|水口|朝山|案山|官鬼", "明堂朝案"),
        (r"生气|死气|旺相|休囚|生旺", "生气旺衰"),
        (r"立向|分金|子午针|方位", "立向分金"),
        (r"倒杖|卦例|九星|八卦", "倒杖卦例"),
        (r"藏风|得水|界脉|藏风聚气", "藏风得水"),
    ]
    for pattern, kw in mapping:
        if re.search(pattern, text):
            kws.append(kw)
    return list(dict.fromkeys(kws))


def main():
    src = os.path.join(BASE, "raw/xuexinfu.txt")
    out_dir = os.path.join(BASE, "library", "xiang", "dixiang", "xuexinfu")
    os.makedirs(out_dir, exist_ok=True)

    text = open(src, encoding="utf-8").read()
    lines = text.split("\n")

    entries = []
    current_title = None
    current_content = []

    for line in lines:
        s = line.strip()

        # 章标题：第X章 XXX
        m = re.match(r'^第[一二三四五]章\s+(.+)$', s)
        if m:
            if current_title and current_content:
                entries.append((current_title, "\n".join(current_content).strip()))
            current_title = s
            current_content = []
            continue

        # 正文
        if current_title and s:
            current_content.append(s)

    # 最后一条
    if current_title and current_content:
        entries.append((current_title, "\n".join(current_content).strip()))

    # 写入文件
    for idx, (title, content) in enumerate(entries):
        eid = f"xiang3_xxf_{idx:03d}"
        kws = extract_keywords(title + content[:3000])
        tags = ["相部", "地相", "雪心赋", "峦头风水"]
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
book: "雪心赋"
chapter: "全书五章"
section_title: "{title[:30]}"
source_version: "中华典藏网"
author: "卜应天"
dynasty: "唐"
type: "chapter"
conditions:
{cond}
weight: 5
tags: [{tags_str}]
---
"""
        body = f"### {title}\n\n"
        body += f"**【原文】**\n{content}\n\n"
        body += f"**【白话提要】**\n此条出自《雪心赋》「{title}」，为唐卜应天（字则巍，号昆仑子）所述形势峦头风水经典原文。雪心赋以歌赋体系统阐述地相之学，涵盖山川理气、地理要略、山水本源、水法、龙脉、穴法、砂法、阳宅阴宅等核心内容，教人认龙脉、点真穴、审水法、辨砂水，为形势派（峦头派）风水的经典代表作，与撼龙经、葬书、青囊奥语并称地相四大经典。\n"
        with open(os.path.join(out_dir, f"xiang3_xxf_{idx:03d}.md"), "w",
                  encoding="utf-8", newline="\n") as f:
            f.write(fm + "\n" + body)

    print(f"  雪心赋: {len(entries)} 条 → {out_dir}")


if __name__ == "__main__":
    main()
