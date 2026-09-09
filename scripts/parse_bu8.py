# -*- coding: utf-8 -*-
"""
卜部第八批·卜筮正宗解析脚本（纯标准库，确定性输出）

底本：raw/boshizhengzong.txt（中华典藏网，清王维德字洪绪号林屋先生撰）
  4.8KB，卷一·启蒙节要，按大主题切分约12条
  六爻进阶核心典籍，14卷，本次入库卷一启蒙节要（基础歌赋全）
切分：按「六十花甲纳音歌/五行属性/地支论/以钱代蓍法/六十四卦名/
  纳甲装卦歌/六兽歌/三合会局歌/通玄赋/碎金赋/诸爻持世诀/
  飞伏生克吉凶歌/六爻安静诀/忌神歌/原神歌/用神不上卦诀/
  用神空亡诀/用神发动诀/六亲发动诀/六亲变化歌/六兽歌断/
  六甲旬空起例/月破定例」等标题切分，过短条目合并
元数据：category=bu, subcategory=liuyao, type=chapter, conditions 八键全空
召回：keywords 驱动（卜筮正宗/六爻/启蒙节要/纳音/五行/地支/六亲/
  以钱代蓍/六十四卦/纳甲/六兽/三合/长生/禄马/羊刃/三刑/六害/
  通玄赋/碎金赋/持世/世应/飞伏/用神/原神/忌神/旬空/月破 等）
用法：python -X utf8 scripts/parse_bu8.py
"""
import os
import re

BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def extract_keywords(text):
    kws = ["卜筮正宗", "卜部", "六爻", "启蒙节要", "王维德"]
    mapping = [
        (r"六十花甲|纳音|海中金|炉中火", "六十花甲纳音"),
        (r"五行属性|相生|相克|五脏|五腑", "五行属性"),
        (r"地支论|藏干|合局|六冲|六破|六穿|六刑", "地支论"),
        (r"六亲相生相克|生我者|我生者|克我者|我克者", "六亲"),
        (r"以钱代蓍|掷钱|三背为重|三字为交", "以钱代蓍法"),
        (r"六十四卦|乾宫|兑宫|离宫|震宫|巽宫|坎宫|艮宫|坤宫", "六十四卦"),
        (r"纳甲装卦|干金甲子|坎水戊寅", "纳甲装卦"),
        (r"六兽歌|青龙|朱雀|勾陈|螣蛇|白虎|玄武", "六兽"),
        (r"三合会局|申子辰|巳酉丑|寅午戌|亥卯未", "三合会局"),
        (r"长生掌诀|长生|沐浴|冠带|临官|帝旺", "长生掌诀"),
        (r"禄马羊刃|甲禄在寅|驿马|羊刃", "禄马羊刃"),
        (r"三刑六害|寅刑巳|子未相害", "三刑六害"),
        (r"通玄赋", "通玄赋"),
        (r"碎金赋|贪生忘克", "碎金赋"),
        (r"诸爻持世|世爻旺相|子孙持世|官鬼持世|父母持世|妻财持世|兄弟持世", "诸爻持世"),
        (r"世应生克|世应相生|世应相克", "世应生克"),
        (r"飞伏生克|伏克飞神|飞来克伏", "飞伏生克"),
        (r"断易勿泥神煞|神煞休将定吉凶", "断易勿泥神煞"),
        (r"六爻安静|六爻乱动", "六爻动静"),
        (r"忌神歌|忌神宜静", "忌神"),
        (r"原神歌|原神发动", "原神"),
        (r"用神不上卦|用神空亡|用神发动", "用神"),
        (r"六亲发动|父动当头|子孙发动|官鬼从来|财爻发动|兄弟交重", "六亲发动"),
        (r"六亲变化|父母化父母|子孙化退神|官化进神|妻财化进神", "六亲变化"),
        (r"六兽歌断|发动青龙|朱雀交重|勾陈发动", "六兽歌断"),
        (r"日月建传符|日建加青龙", "日月建传符"),
        (r"六甲旬空|甲子旬中|旬空", "六甲旬空"),
        (r"月破定例|建寅破申|月破", "月破"),
        (r"八卦相配|干为老父|坤为老母", "八卦相配"),
        (r"安月卦身|卦身喜忌", "卦身"),
        (r"年上起月|甲己还加甲", "年上起月"),
        (r"八宫诸身|乾为首|坤为腹", "八宫诸身"),
    ]
    for pattern, kw in mapping:
        if re.search(pattern, text):
            kws.append(kw)
    return list(dict.fromkeys(kws))


def main():
    src = os.path.join(BASE, "raw/boshizhengzong.txt")
    out_dir = os.path.join(BASE, "library", "bu", "liuyao", "boshizhengzong")
    os.makedirs(out_dir, exist_ok=True)

    text = open(src, encoding="utf-8").read()
    lines = text.split("\n")

    # 切分标记（按大主题）
    markers = [
        "六十花甲纳音歌",
        "五行属性",
        "地支论",
        "以钱代蓍法",
        "六十四卦名（装卦表）",
        "纳甲装卦歌",
        "六兽歌",
        "安月卦身诀",
        "三合会局歌",
        "长生掌诀",
        "禄马羊刃歌",
        "三刑六害歌",
        "八宫诸身",
        "定间爻歌",
        "年上起月法",
        "通玄赋",
        "碎金赋",
        "诸爻持世诀",
        "世应生克空亡动静诀",
        "卦身喜忌诀",
        "飞伏生克吉凶歌",
        "断易勿泥神煞",
        "六爻安静诀",
        "六爻乱动诀",
        "忌神歌",
        "原神歌",
        "用神不上卦诀",
        "用神空亡诀",
        "用神发动诀",
        "日辰诀",
        "六亲发动诀",
        "六亲变化歌",
        "六兽歌断",
        "日月建传符",
        "八卦相配",
        "六甲旬空起例",
        "月破定例",
    ]

    entries = []
    current_title = None
    current_content = []

    for line in lines:
        s = line.strip()

        # 检查是否是新条目标记
        matched = False
        for marker in markers:
            if s == marker or s.startswith(marker):
                if current_title and current_content:
                    entries.append((current_title, "\n".join(current_content).strip()))
                current_title = marker
                current_content = []
                # 如果标记行后面还有内容，加入正文
                rest = s[len(marker):].strip()
                if rest:
                    current_content.append(rest)
                matched = True
                break

        if not matched and current_title and s and s != "卷一·启蒙节要":
            current_content.append(s)

    # 最后一条
    if current_title and current_content:
        entries.append((current_title, "\n".join(current_content).strip()))

    # 合并过短条目（<100字合并到上一条）
    merged = []
    for title, content in entries:
        if len(content) < 100 and merged:
            prev_title, prev_content = merged[-1]
            merged[-1] = (prev_title, prev_content + "\n\n" + title + "：\n" + content)
        else:
            merged.append((title, content))

    # 写入文件
    for idx, (title, content) in enumerate(merged):
        eid = f"bu8_bszz_{idx:03d}"
        kws = extract_keywords(title + content[:2000])
        tags = ["卜部", "六爻", "卜筮正宗", "启蒙节要", "王维德"]
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
chapter: "卷一·启蒙节要"
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
        body += f"**【白话提要】**\n此条出自《卜筮正宗》「卷一·启蒙节要·{title}」，为清代王维德（字洪绪，号林屋先生）所撰的六爻进阶核心典籍原文。卜筮正宗全书14卷，以黄金策为纲，系统阐述六爻占断之法，卷一启蒙节要为六爻基础，涵盖纳音五行、地支藏干、六亲、以钱代蓍起卦法、六十四卦装卦表、纳甲装卦、六兽、三合会局、长生掌诀、禄马羊刃、三刑六害、通玄赋、碎金赋、诸爻持世、世应生克、飞伏生克、用神原神忌神、六亲发动变化、六兽歌断、旬空月破等核心歌赋，为六爻占断之基础纲领。卜筮正宗力辟诸书之谬，一宗正理，为六爻学之集大成之作。\n"
        with open(os.path.join(out_dir, f"bu8_bszz_{idx:03d}.md"), "w",
                  encoding="utf-8", newline="\n") as f:
            f.write(fm + "\n" + body)

    print(f"  卜筮正宗: {len(merged)} 条 → {out_dir}")


if __name__ == "__main__":
    main()
