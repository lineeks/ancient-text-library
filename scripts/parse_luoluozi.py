# -*- coding: utf-8 -*-
"""
《珞琭子赋注》结构化入库脚本（纯标准库，确定性输出）

底本：GitHub garychowcmu/daizhigev20 易藏·术数·珞琭子赋注.txt（四库全书本）
宋释昙莹撰，兼收王廷光、李仝注。珞琭子三命消息赋为禄命鼻祖，
以赋文体论述命理原理，不依赖八字精确锚定，靠 keywords 索引。

切分策略：
  - 卷上/卷下各按"赋文一句 + 三家注文"交替切分
  - 每条 type=fuwen，conditions 八键全空，keywords 从赋文提取
  - weight=3（扩展梯队）

输出：library/ming/bazi/extended/luoluozi/*.md
用法：python -X utf8 scripts/parse_luoluozi.py
"""
import os
import re

BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SRC = os.path.join(BASE, "raw", "luoluozi.txt")
OUT_DIR = os.path.join(BASE, "library", "ming", "bazi", "extended", "luoluozi")


def clean(line):
    return line.strip().lstrip("\u3000").strip()


def extract_keywords(fuwen, zhuwen):
    """从赋文和注文中提取检索关键词。"""
    kws = ["珞琭子", "三命消息赋", "禄命古法", "五行理论"]
    text = fuwen + zhuwen
    mapping = [
        ("五行", "五行"),
        ("禄", "干禄"),
        ("支为命|支命", "支命"),
        ("大运|行运|一辰十嵗|折除", "大运"),
        ("天乙|贵人", "天乙贵人"),
        ("三奇|乙丙丁|甲戊庚", "三奇贵人"),
        ("将星", "将星"),
        ("羊刃|禄前一辰", "羊刃"),
        ("元辰", "元辰"),
        ("七煞|七杀", "七杀"),
        ("空亡", "空亡"),
        ("孤辰|寡宿", "孤辰寡宿"),
        ("勾陈|真武", "勾陈真武"),
        ("三才", "三才"),
        ("四时|四气", "四时"),
        ("阴阳", "阴阳"),
        ("刚柔", "刚柔"),
        ("君臣|父子|牝牡", "人伦取象"),
        ("消息盈虚|消息", "消息盈虚"),
        ("神煞|贵神|吉神", "神煞"),
        ("纳音", "纳音"),
        ("三元", "三元"),
        ("四柱", "四柱"),
        ("胎月|胎元", "胎元"),
        ("性情|情性", "性情"),
        ("富贵|贫贱|贵贱", "贵贱"),
        ("寿夭|修短", "寿夭"),
        ("吉凶|祸福", "吉凶"),
    ]
    for pattern, kw in mapping:
        if re.search(pattern, text):
            kws.append(kw)
    # 去重保序
    return list(dict.fromkeys(kws))


def write_entry(eid, chapter, fuwen, zhuwen, idx):
    kws = extract_keywords(fuwen, zhuwen)
    tags = ["珞琭子", "三命消息赋", "禄命古法", "赋文"]
    # section_title 取赋文前12字
    title = fuwen[:14].replace("\n", "")
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
book: "珞琭子赋注"
chapter: "{chapter}"
section_title: "{title}"
source_version: "四库全书本（宋释昙莹撰，兼收王廷光、李仝注）"
author: "释昙莹（注）"
dynasty: "宋"
type: "fuwen"
conditions:
{cond}
weight: 3
tags: [{tags_str}]
---
"""
    body = f"### {title}\n\n"
    body += f"**【原文】**\n{fuwen}\n\n"
    body += f"**【古注】**\n{zhuwen}\n\n"
    body += f"**【白话提要】**\n此条出自《珞琭子赋注》{chapter}，为珞琭子三命消息赋原文与宋释昙莹、王廷光、李仝三家注文。珞琭子赋为禄命学鼻祖，以赋文体论述五行、干禄、支命、大运、神煞等命理基本原理，为后世子平八字法的重要理论渊源。\n"
    return fm + "\n" + body


def main():
    os.makedirs(OUT_DIR, exist_ok=True)
    with open(SRC, encoding="utf-8") as f:
        lines = f.readlines()

    # 找到卷上和卷下的赋文起始行
    juan_shang_start = None
    juan_xia_start = None
    for i, l in enumerate(lines):
        s = clean(l)
        if "珞琭子赋注卷上" in s:
            juan_shang_start = i
        if "珞琭子赋注卷下" in s:
            juan_xia_start = i

    written = 0

    # 卷上：从卷上标题后第2行开始（跳过"珞琭子者不知何许人"作者介绍行），
    # 赋文和注文严格交替
    for juan_name, juan_en, start, end in [
        ("卷上", "shang", juan_shang_start + 2, juan_xia_start),
        ("卷下", "xia", juan_xia_start + 1, len(lines)),
    ]:
        pairs = []
        i = start
        while i < end:
            s = clean(lines[i])
            if not s:
                i += 1
                continue
            # 跳过卷标题和作者介绍
            if "珞琭子赋注卷" in s or "钦定四库全书" in s:
                i += 1
                continue
            # 赋文行（较短，通常<80字），注文行（较长，通常>100字）
            # 严格交替：赋文 + 注文
            fuwen = s
            zhuwen = ""
            i += 1
            # 收集注文（可能跨多行，但通常一行）
            while i < end:
                s2 = clean(lines[i])
                if not s2:
                    i += 1
                    continue
                if "珞琭子赋注卷" in s2 or "钦定四库全书" in s2:
                    break
                # 判断是否是下一个赋文：注文通常包含"曰"（王廷光曰/李仝曰/昙莹曰）
                # 赋文通常不包含"曰"，且较短
                if ("曰" in s2 or len(s2) > 80) and not zhuwen:
                    zhuwen = s2
                    i += 1
                    break
                elif zhuwen:
                    # 已经有注文了，这行是下一个赋文
                    break
                else:
                    # 第一行就是注文（可能赋文被跳过），当作注文
                    zhuwen = s2
                    i += 1
                    break
            if fuwen and len(fuwen) < 200:
                pairs.append((fuwen, zhuwen))
            elif fuwen and not zhuwen:
                # 可能是纯赋文（无注），也收录
                pairs.append((fuwen, ""))

        for idx, (fuwen, zhuwen) in enumerate(pairs):
            eid = f"llz_{juan_en}_{idx:03d}"
            content = write_entry(eid, f"珞琭子赋注·{juan_name}", fuwen, zhuwen, idx)
            with open(os.path.join(OUT_DIR, f"{eid}.md"), "w", encoding="utf-8", newline="\n") as f:
                f.write(content)
            written += 1

    print(f"珞琭子赋注入库完成：{written} 条 → {OUT_DIR}")


if __name__ == "__main__":
    main()
