# -*- coding: utf-8 -*-
"""
卜部第九批·卜筮正宗卷三解析脚本（纯标准库，确定性输出）

底本：raw/boshizhengzong_v3.txt（中华典藏网，清王维德字洪绪撰）
  10.6KB，卷三：十八论（18篇）+ 辟诸书之谬（15篇）= 约33条
  六爻核心理论：用神分类、世应、原忌仇神、飞伏、六兽、长生墓绝、
  月破、旬空、反吟伏吟、旺相休囚、进退神、验不验；辟诸书之谬
切分：按「XXX第X」「辟XXX之谬」「辨XXX之谬」标题切分
元数据：category=bu, subcategory=liuyao, type=chapter, conditions 八键全空
召回：keywords 驱动（卜筮正宗/十八论/用神/世应/原神/忌神/仇神/
  飞神/伏神/六兽/长生/墓绝/月破/旬空/反吟/伏吟/旺相休囚/进退神/
  辟谬/增删卜易/易林补遗/卜筮全书 等）
用法：python -X utf8 scripts/parse_bu9.py
"""
import os
import re

BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def extract_keywords(text):
    kws = ["卜筮正宗", "卜部", "六爻", "十八论", "王维德"]
    mapping = [
        (r"用神分类|父母爻|官鬼爻|兄弟爻|妻财爻|子孙爻", "用神分类"),
        (r"世应论|世为自己|应作他人", "世应论用神"),
        (r"用神问答|仆占主人|主人占仆", "用神问答"),
        (r"原忌仇神|原神|忌神|仇神", "原忌仇神"),
        (r"飞神正论|飞神有六", "飞神正论"),
        (r"伏神正传|卦之有缺用神", "伏神正传"),
        (r"六兽评论|青龙|白虎|朱雀|勾陈|螣蛇|玄武", "六兽评论"),
        (r"四生逐位|火生于寅|金生于巳|长生墓绝", "四生逐位论"),
        (r"月破论|月破之爻|出月不破", "月破论"),
        (r"旬空论|旬空|真空", "旬空论"),
        (r"反吟卦|卦之反吟|爻之反吟", "反吟卦定例"),
        (r"伏吟卦", "伏吟卦定例"),
        (r"旺相休囚", "旺相休囚论"),
        (r"合中带克", "合中带克论"),
        (r"合处逢冲|冲中逢合", "合处逢冲论"),
        (r"绝处逢生|克处逢生", "绝处逢生论"),
        (r"变出进退神|进神|退神", "进退神论"),
        (r"卦有验不验|致诚可以感格", "卦有验不验论"),
        (r"辟增删卜易|李文辉|十二篇秘法", "辟增删卜易之谬"),
        (r"辟易林补遗伏神|张星元|飞伏在二仪", "辟易林补遗伏神之谬"),
        (r"辟易林补遗胎养衰病|胎养半吉|衰病半凶", "辟易林补遗胎养衰病之谬"),
        (r"辟卜筮全书世身|子午持世身居初", "辟卜筮全书世身之谬"),
        (r"辨天医星|天医上卦", "辨天医星之谬"),
        (r"辟妄论本命|病人之本命", "辟妄论本命之谬"),
        (r"辟卜筮全书神煞|京房作卦书|神煞断卦", "辟卜筮全书神煞之谬"),
        (r"辨贵人禄马|贵人之爻|禄爻|驿马", "辨贵人禄马之谬"),
        (r"辨易林补遗应为他人|代卜他人看应爻", "辨易林补遗应为他人之谬"),
        (r"辟易林补遗月破旬空|月破无可解|全空半空", "辟易林补遗月破旬空之谬"),
        (r"辨互卦|互卦之法|体象用象", "辨互卦"),
        (r"辟易林补遗终身大小限|卜终身吉凶", "辟易林补遗终身大小限之谬"),
        (r"辟易林补遗家宅|家宅六事|官爻为家主", "辟易林补遗家宅之谬"),
        (r"辟易林补遗婚姻嫁娶|男卜女家|世应论夫妇", "辟易林补遗婚姻嫁娶之谬"),
        (r"辨六爻诸占|天玄赋以六爻定诸占", "辨六爻诸占之谬"),
        (r"辟诸书之谬|辟.*之谬|辨.*之谬", "辟诸书之谬"),
    ]
    for pattern, kw in mapping:
        if re.search(pattern, text):
            kws.append(kw)
    return list(dict.fromkeys(kws))


def main():
    src = os.path.join(BASE, "raw/boshizhengzong_v3.txt")
    out_dir = os.path.join(BASE, "library", "bu", "liuyao", "boshizhengzong")
    os.makedirs(out_dir, exist_ok=True)

    text = open(src, encoding="utf-8").read()
    lines = text.split("\n")

    # 切分标记（十八论 + 辟谬）
    markers = [
        "用神分类定例第一",
        "世应论用神第二",
        "用神问答第三",
        "原忌仇神论第四",
        "飞神正论第五",
        "伏神正传第六",
        "六兽评论第七",
        "四生逐位论",
        "月破论第九",
        "旬空论第十",
        "反吟卦定例第十一",
        "伏吟卦定例第十二",
        "旺相休囚论第十三",
        "合中带克论第十四",
        "合处逢冲冲中逢合论第十五",
        "绝处逄生克处逄生论第十六",
        "绝处逢生克处逢生论第十六",
        "变出进退神论第十七",
        "卦有验不验论第十八",
        "辟增删卜易之谬",
        "辟易林补遗伏神之谬",
        "辟易林补遗胎养衰病之谬",
        "辟卜筮全书世身之谬",
        "辨天医星之谬",
        "辟妄论本命之谬",
        "辟卜筮全书神煞之谬",
        "辨贵人禄马之谬",
        "辨易林补遗应为他人之谬",
        "辟易林补遗月破旬空之谬",
        "辨互卦",
        "辟易林补遗终身大小限之谬",
        "辟易林补遗家宅之谬",
        "辟易林补遗婚姻嫁娶之谬",
        "辨六爻诸占之谬",
    ]

    entries = []
    current_title = None
    current_content = []

    for line in lines:
        s = line.strip()
        if not s or s == "十八论":
            continue

        # 检查是否是新条目标记
        matched = False
        for marker in markers:
            if s.startswith(marker):
                if current_title and current_content:
                    entries.append((current_title, "\n".join(current_content).strip()))
                current_title = marker
                current_content = []
                rest = s[len(marker):].strip()
                if rest:
                    current_content.append(rest)
                matched = True
                break

        if not matched and current_title:
            current_content.append(s)

    # 最后一条
    if current_title and current_content:
        entries.append((current_title, "\n".join(current_content).strip()))

    # 过滤过短条目（<50字）
    entries = [(t, c) for t, c in entries if len(c) >= 50]

    # 写入文件（续接卷一的编号，从014开始）
    start_idx = 14
    for idx, (title, content) in enumerate(entries):
        eid = f"bu8_bszz_{start_idx + idx:03d}"
        kws = extract_keywords(title + content[:2000])
        tags = ["卜部", "六爻", "卜筮正宗", "十八论"]
        if "辟" in title or "辨" in title:
            tags = ["卜部", "六爻", "卜筮正宗", "辟诸书之谬"]
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
chapter: "卷三·十八论/辟诸书之谬"
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
        body += f"**【白话提要】**\n此条出自《卜筮正宗》「卷三·{title}」，为清代王维德（字洪绪，号林屋先生）所撰的六爻进阶核心典籍原文。卜筮正宗卷三十八论为六爻占断之核心理论，系统阐述用神分类定例、世应论用神、用神问答、原忌仇神论、飞神正论、伏神正传、六兽评论、四生逐位论、月破论、旬空论、反吟伏吟卦定例、旺相休囚论、合中带克论、合处逢冲冲中逢合论、绝处逢生克处逢生论、变出进退神论、卦有验不验论等十八篇核心纲领。辟诸书之谬则力辟增删卜易、易林补遗、卜筮全书等书之谬误，一宗正理，以五行生克制化、动静空破、冲合刑害为断易之根本，反对以神煞、世身、本命等旁门左道妄断吉凶，为六爻学之集大成之作。\n"
        with open(os.path.join(out_dir, f"bu8_bszz_{start_idx + idx:03d}.md"), "w",
                  encoding="utf-8", newline="\n") as f:
            f.write(fm + "\n" + body)

    print(f"  卜筮正宗卷三: {len(entries)} 条 → {out_dir}")


if __name__ == "__main__":
    main()
