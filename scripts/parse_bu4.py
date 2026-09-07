# -*- coding: utf-8 -*-
"""
卜部第四批典籍入库脚本（纯标准库，确定性输出）

底本：garychowcmu/daizhigev20 GitHub 仓库 易藏/术数/ 目录
  - zengshanbuyi.txt  增删卜易（清野鹤老人著，414KB，六爻纳甲法集大成）

切分策略：
  - 跳过目录（找到第二个"卷之一"即正文开始）
  - 按"XXX章第X"格式切分（如"八卦章第一""用神章第八"）
  - 卷标题作为 chapter 前缀
  - type=chapter，conditions 八键全空，keywords 驱动召回
  - category=bu, subcategory=liuyao（六爻进阶）

输出：library/bu/liuyao/zengshanbuyi/*.md
用法：python -X utf8 scripts/parse_bu4.py
"""
import os
import re

BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def extract_keywords(text):
    kws = ["增删卜易", "六爻"]
    mapping = [
        (r"野鹤|增删|卜易|纳甲|六爻|卜筮", "增删卜易"),
        (r"八卦|卦象|八宫|浑天甲子|六亲|世应|动变|用神", "基础概念"),
        (r"五行相生|五行相克|生克|克处逢生|动静生克", "五行生克"),
        (r"月将|日辰|月建|日建|月令|太岁|旬空|空亡", "日辰月建"),
        (r"六神|青龙|朱雀|勾陈|腾蛇|白虎|玄武", "六神"),
        (r"六合|三合|六冲|冲合|刑害|三刑|六害", "冲合刑害"),
        (r"进神|退神|化进|化退|反吟|伏吟", "进退反伏"),
        (r"飞神|伏神|伏藏|出现|飞伏", "飞伏"),
        (r"独发|乱动|动爻|变爻|静爻|暗动", "动变"),
        (r"占财|求财|买卖|交易|占官|求官|功名|占病|疾病|占婚姻|婚嫁|占行人|出行|失物|官讼|六甲|胎产", "分类占"),
        (r"用神|原神|忌神|仇神|持世|临世|世爻|应爻", "用神世应"),
        (r"旺相|休囚|死绝|长生|帝旺|墓库|绝胎养", "旺衰十二宫"),
        (r"卦身|身爻|卦命|命爻|卦运|运限", "卦身卦运"),
        (r"断卦|断曰|判曰|占断|占验|卦验|应验", "占断验"),
    ]
    for pattern, kw in mapping:
        if re.search(pattern, text):
            kws.append(kw)
    return list(dict.fromkeys(kws))


def write_entry(book_slug, book_name, version, subcategory, chapter, section, text, idx, weight=4):
    eid = f"bu4_{book_slug}_{idx:03d}"
    kws = extract_keywords(chapter + section + text[:2000])
    tags = ["卜部", book_name]
    title = section[:20].replace("\n", "")
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
book: "{book_name}"
chapter: "{chapter}"
section_title: "{title}"
source_version: "{version}"
author: "野鹤老人"
dynasty: "清"
type: "chapter"
conditions:
{cond}
weight: {weight}
tags: [{tags_str}]
---
"""
    body = f"### {title}\n\n"
    body += f"**【原文】**\n{text}\n\n"
    body += f"**【白话提要】**\n此条出自《{book_name}》「{chapter}·{section}」，为六爻纳甲法经典原文。增删卜易由清野鹤老人著，为火珠林派六爻占法之集大成著作，以用神、世应、五行生克、日辰月建、动变飞伏、冲合刑害为核心，系统论述六爻占断之法，附大量占验实例。\n"
    return fm + "\n" + body


def split_zengshan(text):
    """增删卜易：跳过目录，按章标题切分。
    返回 [(chapter, section, content), ...]
    """
    # 找到第二个"卷之一"（正文开始）
    first = text.find("\n卷之一\n")
    if first < 0:
        first = text.find("卷之一")
    second = text.find("\n卷之一\n", first + 1)
    if second < 0:
        second = text.find("卷之一", first + 1)
    if second >= 0:
        text = text[second:]

    lines = text.split("\n")
    entries = []
    current_juan = ""
    current_title = ""
    current_content = []

    def flush():
        if current_title and current_content:
            content = "\n".join(current_content).strip()
            if len(content) > 20:
                entries.append((current_juan, current_title, content))

    juan_pattern = re.compile(r"^　*卷之([一二三四五六七八九十]+)\s*$")
    zhang_pattern = re.compile(r"^　*([\u4e00-\u9fff]{2,12})章第([一二三四五六七八九十百]+)\s*$")

    for line in lines:
        s = line.strip()
        if not s:
            current_content.append(line)
            continue
        jm = juan_pattern.match(line)
        if jm:
            flush()
            current_juan = f"卷之{jm.group(1)}"
            current_title = ""
            current_content = []
            continue
        zm = zhang_pattern.match(line)
        if zm:
            flush()
            current_title = f"{zm.group(1)}章第{zm.group(2)}"
            current_content = []
            continue
        current_content.append(line)

    flush()
    return entries


BOOKS = [
    ("zengshanbuyi", "增删卜易", "清野鹤老人著·通行本", "liuyao", "raw/zengshanbuyi.txt", split_zengshan, 4),
]


def main():
    total = 0
    for book_slug, book_name, version, subcategory, src_rel, splitter, weight in BOOKS:
        src = os.path.join(BASE, src_rel)
        out_dir = os.path.join(BASE, "library", "bu", subcategory, book_slug)
        os.makedirs(out_dir, exist_ok=True)
        text = open(src, encoding="utf-8").read()
        entries = splitter(text)
        for idx, (chapter, section, content) in enumerate(entries):
            md = write_entry(book_slug, book_name, version, subcategory, chapter, section, content, idx, weight)
            with open(os.path.join(out_dir, f"bu4_{book_slug}_{idx:03d}.md"), "w",
                      encoding="utf-8", newline="\n") as f:
                f.write(md)
        total += len(entries)
        print(f"  {book_name}: {len(entries)} 条 → {out_dir}")
    print(f"卜部第四批入库完成：{total} 条")


if __name__ == "__main__":
    main()
