# -*- coding: utf-8 -*-
"""
山部第六批·性命圭旨解析脚本（纯标准库，确定性输出）

底本：raw/xingmingguizhi.txt（中华典藏网，明尹真人高弟撰，约成书于明代）
  5KB，元集核心6篇：大道说/性命说/死生说/邪正说/四图说/太极图说 = 6条
  道教内炼理论著作，分元亨利贞四集，内丹功法通俗化集大成
切分：按「大道说/性命说/死生说/邪正说/普照图.../太极图」标题切分
元数据：category=shan, subcategory=dandao, type=chapter, conditions 八键全空
召回：keywords 驱动（性命圭旨/内丹/丹道/性命/大道/死生/邪正/
  金丹/玄关/任督/太极/先天/后天/炼精化气/炼气化神/炼神还虚 等）
用法：python -X utf8 scripts/parse_shan6.py
"""
import os
import re

BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def extract_keywords(text):
    kws = ["性命圭旨", "山部", "丹道", "内丹", "尹真人"]
    mapping = [
        (r"大道说|一炁|太乙|元始|道生一", "大道说"),
        (r"性命说|元始真如|先天至精|气质之性|天赋之性", "性命说"),
        (r"死生说|阿赖耶|投胎|舍身|元炁六十四铢", "死生说"),
        (r"邪正说|傍门|外道|金丹一道|三千六百", "邪正说"),
        (r"普照图|反照图|时照图|内照图|任督二脉|前三关|后三关", "四图说"),
        (r"太极图|圆觉|无极而太极", "太极图说"),
        (r"金丹|圣胎|婴儿|玄关|药物|火候|采取|抽添|温养", "金丹大道"),
        (r"先天|后天|元炁|精气神|炼精|炼气|炼神", "性命双修"),
        (r"三教|儒曰|道曰|释曰|存心养性|修心炼性|明心见性", "三教合一"),
        (r"九转还丹|涵养本原|安神祖窍|蛰藏气穴|天人合发|乾坤交媾|灵丹入鼎|婴儿现形|移神内院|本体虚空", "九转功夫"),
    ]
    for pattern, kw in mapping:
        if re.search(pattern, text):
            kws.append(kw)
    return list(dict.fromkeys(kws))


def main():
    src = os.path.join(BASE, "raw/xingmingguizhi.txt")
    out_dir = os.path.join(BASE, "library", "shan", "dandao", "xingmingguizhi")
    os.makedirs(out_dir, exist_ok=True)

    text = open(src, encoding="utf-8").read()
    lines = text.split("\n")

    entries = []
    current_title = None
    current_content = []
    section = "元集"

    # 切分标记
    markers = [
        "大道说",
        "性命说",
        "死生说",
        "邪正说",
        "普照图、反照图、时照图、内照图",
        "太极图",
    ]

    for line in lines:
        s = line.strip()

        # 检查是否是新条目标记
        matched = False
        for marker in markers:
            if s == marker or s.startswith(marker + "说") or s.startswith(marker):
                if current_title and current_content:
                    entries.append((section, current_title, "\n".join(current_content).strip()))
                current_title = marker if marker != "普照图、反照图、时照图、内照图" else "四图说"
                current_content = []
                matched = True
                break

        if not matched and current_title and s and s != "元集":
            current_content.append(s)

    # 最后一条
    if current_title and current_content:
        entries.append((section, current_title, "\n".join(current_content).strip()))

    # 写入文件
    for idx, (sec, title, content) in enumerate(entries):
        eid = f"shan6_xmgz_{idx:03d}"
        kws = extract_keywords(sec + title + content[:2000])
        tags = ["山部", "丹道", "性命圭旨", "内丹", "尹真人"]
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
book: "性命圭旨"
chapter: "元集·{title}"
section_title: "{title[:30]}"
source_version: "中华典藏网（明尹真人高弟撰，约成书于明代）"
author: "尹真人高弟撰"
dynasty: "明"
type: "chapter"
conditions:
{cond}
weight: 3
tags: [{tags_str}]
---
"""
        body = f"### {title}\n\n"
        body += f"**【原文】**\n{content}\n\n"
        body += f"**【白话提要】**\n此条出自《性命圭旨》「元集·{title}」，为明代尹真人高弟所撰的道教内炼理论著作原文。性命圭旨分元、亨、利、贞四集，竭力将内丹功法通俗化，使一般人都能接受。元集为全书理论基础，论述大道本源、性命关系、死生根本、邪正辨别、内景图谱、太极本体等核心概念，主张三教合一（儒曰存心养性、道曰修心炼性、释曰明心见性），以性命双修为宗，以金丹大道为唯一正路，提出九转还丹功夫次第（涵养本原→安神祖窍→蛰藏气穴→天人合发→乾坤交媾→灵丹入鼎→婴儿现形→移神内院→本体虚空），为内丹学集大成之作。\n"
        with open(os.path.join(out_dir, f"shan6_xmgz_{idx:03d}.md"), "w",
                  encoding="utf-8", newline="\n") as f:
            f.write(fm + "\n" + body)

    print(f"  性命圭旨: {len(entries)} 条 → {out_dir}")


if __name__ == "__main__":
    main()
