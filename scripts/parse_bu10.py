# -*- coding: utf-8 -*-
"""
卜部第十批·卜筮正宗卷五解析脚本（纯标准库，确定性输出）

底本：raw/boshizhengzong_v5plus.txt（中华典藏网，清王维德字洪绪撰）
  40.9KB，卷五：何知章 + 十八问答附占验（18问，每问含多个占验卦例）
切分：何知章1条 + 第X问18条 = 19条
元数据：category=bu, subcategory=liuyao, type=chapter, conditions 八键全空
召回：keywords 驱动（卜筮正宗/十八问答/何知章/占验/卦例/回头克/
  冲中逢合/合处逢冲/生墓绝/进神退神/月破旬空/用神多现 等）
用法：python -X utf8 scripts/parse_bu10.py
"""
import os
import re

BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def extract_keywords(text):
    kws = ["卜筮正宗", "卜部", "六爻", "十八问答", "占验", "王维德"]
    mapping = [
        (r"何知章|仙人造出何知章", "何知章"),
        (r"三传年月日建克用|贪生忘克|月克日生", "三传克用"),
        (r"回头克|爻之回头克|卦之回头克", "回头克"),
        (r"冲中逄合|冲中逢合|先散后聚", "冲中逢合"),
        (r"合处逄冲|合处逢冲|先聚后散", "合处逢冲"),
        (r"四生墓绝|生墓绝于日辰|生墓绝于飞爻", "四生墓绝"),
        (r"进神|退神|化进神|化退神", "进退神"),
        (r"月破|旬空|出空|填实", "月破旬空"),
        (r"用神多现|用占破验|有病之爻", "用神多现"),
        (r"独发|暗动|动爻", "动爻"),
        (r"反吟|伏吟|卦之反吟", "反吟伏吟"),
        (r"世爻|应爻|世应", "世应"),
        (r"原神|忌神|仇神", "原忌仇神"),
        (r"飞神|伏神|伏藏", "飞伏神"),
        (r"六兽|青龙|白虎|朱雀|勾陈|螣蛇|玄武", "六兽"),
        (r"占病|疾病|医药|病症", "占病"),
        (r"求财|财爻|买卖|货财", "求财"),
        (r"婚姻|嫁娶|婚配", "婚姻"),
        (r"家宅|阳宅|宅舍", "家宅"),
        (r"坟地|阴宅|葬地|龙脉", "阴宅"),
        (r"出行|行人|归期", "出行行人"),
        (r"官讼|词讼|官司", "官讼"),
        (r"功名|求名|仕宦|官星", "功名"),
        (r"流年|大运|岁运", "流年"),
        (r"生产|产育|胎孕", "生产"),
        (r"六畜|禽鸟|牛马", "六畜"),
        (r"天时|晴雨|风雨", "天时"),
        (r"十八问|第.*问", "十八问答"),
    ]
    for pattern, kw in mapping:
        if re.search(pattern, text):
            kws.append(kw)
    return list(dict.fromkeys(kws))


def main():
    src = os.path.join(BASE, "raw/boshizhengzong_v5plus.txt")
    out_dir = os.path.join(BASE, "library", "bu", "liuyao", "boshizhengzong")
    os.makedirs(out_dir, exist_ok=True)

    text = open(src, encoding="utf-8").read()
    # 去掉卷标记
    text = re.sub(r'=== VOL_\d+ ===', '', text)
    lines = text.split("\n")

    # 切分标记
    markers = ["何知章"] + [f"第{n}问" for n in
        ["一", "二", "三", "四", "五", "六", "七", "八", "九", "十",
         "十一", "十二", "十三", "十四", "十五", "十六", "十七", "十八"]]

    entries = []
    current_title = None
    current_content = []

    for line in lines:
        s = line.strip()
        if not s:
            continue

        matched = False
        for marker in markers:
            if s.startswith(marker) or s.startswith(marker + "：") or s.startswith(marker + ":"):
                if current_title and current_content:
                    entries.append((current_title, "\n".join(current_content).strip()))
                current_title = marker
                current_content = []
                rest = s[len(marker):].strip()
                if rest and rest not in ("：", ":"):
                    current_content.append(rest.lstrip("：:").strip())
                matched = True
                break

        if not matched and current_title:
            current_content.append(s)

    if current_title and current_content:
        entries.append((current_title, "\n".join(current_content).strip()))

    # 过滤过短条目（<100字）
    entries = [(t, c) for t, c in entries if len(c) >= 100]

    # 写入文件（续接卷三的编号，从043开始）
    start_idx = 43
    for idx, (title, content) in enumerate(entries):
        eid = f"bu8_bszz_{start_idx + idx:03d}"
        kws = extract_keywords(title + content[:3000])
        tags = ["卜部", "六爻", "卜筮正宗", "十八问答"]
        if title == "何知章":
            tags = ["卜部", "六爻", "卜筮正宗", "何知章"]
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
chapter: "卷五·何知章/十八问答附占验"
section_title: "{title[:30]}"
source_version: "中华典藏网（清王维德字洪绪号林屋先生撰）"
author: "王维德（字洪绪，号林屋先生）"
dynasty: "清"
type: "chapter"
conditions:
{cond}
weight: 5
tags: [{tags_str}]
---
"""
        body = f"### {title}\n\n"
        body += f"**【原文】**\n{content}\n\n"
        body += f"**【白话提要】**\n此条出自《卜筮正宗》「卷五·{title}」，为清代王维德（字洪绪，号林屋先生）所撰的六爻进阶核心典籍原文。卜筮正宗卷五何知章以歌诀形式总括占断要诀，十八问答附占验则以问答形式系统阐释六爻占断中的核心疑难问题，每问皆附详细占验卦例，涵盖三传克用、回头克、冲中逢合、合处逢冲、四生墓绝、进退神、月破旬空、用神多现、独发暗动、反吟伏吟等核心占断机制，是六爻学从理论走向实战的关键篇章，为后世六爻占断之典范。\n"
        with open(os.path.join(out_dir, f"bu8_bszz_{start_idx + idx:03d}.md"), "w",
                  encoding="utf-8", newline="\n") as f:
            f.write(fm + "\n" + body)

    print(f"  卜筮正宗卷五: {len(entries)} 条 → {out_dir}")


if __name__ == "__main__":
    main()
