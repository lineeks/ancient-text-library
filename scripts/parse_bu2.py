# -*- coding: utf-8 -*-
"""
卜部第二批典籍入库脚本（纯标准库，确定性输出）

底本：garychowcmu/daizhigev20 GitHub 仓库 易藏/术数/ 目录
  - huozhulin.txt  火珠林（题麻衣道者著，65KB，六爻纳甲法鼻祖）

切分策略：
  - 火珠林：按"数字．标题"格式切分（如"1．易中明义"）
  - type=chapter，conditions 八键全空，keywords 驱动召回
  - category=bu, subcategory=liuyao（六爻）

输出：library/bu/liuyao/huozhulin/*.md
用法：python -X utf8 scripts/parse_bu2.py
"""
import os
import re

BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def extract_keywords(text):
    kws = ["六爻"]
    mapping = [
        ("火珠林|麻衣|纳甲|六爻|卜筮", "火珠林"),
        ("六亲|父母|兄弟|子孙|妻财|官鬼", "六亲"),
        ("世应|持世|应爻|世爻", "世应"),
        ("五行|金木水火土|生克|旺相|休囚", "五行旺衰"),
        ("动爻|变爻|独发|乱动|静爻", "动变"),
        ("日辰|月建|月令|日建|太岁", "日辰月建"),
        ("伏神|飞神|伏藏|出现", "飞伏"),
        ("冲|合|刑|害|破|三合|六合", "冲合刑害"),
        ("空亡|真空|假空|旬空", "空亡"),
        ("进神|退神|化进|化退", "进退神"),
        ("反吟|伏吟|反卦", "反伏吟"),
        ("占财|求财|买卖|交易|生意", "占财"),
        ("占官|求官|功名|仕途|官职", "占官"),
        ("占病|疾病|医药|病源", "占病"),
        ("占婚姻|婚嫁|配偶|夫妻", "占婚姻"),
        ("占行人|出行|行人|走失", "占行人"),
        ("卦体|卦象|卦名|乾|坤|震|巽|坎|离|艮|兑", "卦体"),
        ("用神|原神|忌神|仇神", "用神"),
    ]
    for pattern, kw in mapping:
        if re.search(pattern, text):
            kws.append(kw)
    return list(dict.fromkeys(kws))


def write_entry(book_slug, book_name, version, subcategory, chapter, text, idx, weight=4):
    eid = f"bu2_{book_slug}_{idx:03d}"
    kws = extract_keywords(chapter + text[:2000])
    tags = ["卜部", book_name]
    title = chapter[:20].replace("\n", "")
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
author: "题麻衣道者"
dynasty: "宋"
type: "chapter"
conditions:
{cond}
weight: {weight}
tags: [{tags_str}]
---
"""
    body = f"### {title}\n\n"
    body += f"**【原文】**\n{text}\n\n"
    body += f"**【白话提要】**\n此条出自《{book_name}》「{chapter}」，为六爻纳甲法经典原文。火珠林以六亲、世应、五行旺衰、动变、飞伏、冲合刑害为核心，系统论述六爻占断之法，为后世火珠林派（纳甲筮法）之宗。\n"
    return fm + "\n" + body


def split_huozhulin(text):
    """火珠林：按'数字．标题'格式切分。"""
    pattern = r"^　*(\d+[.．][^\n]{2,20})\s*$"
    matches = list(re.finditer(pattern, text, re.M))
    entries = []
    for i, m in enumerate(matches):
        title = m.group(1).strip()
        start = m.end()
        end = matches[i + 1].start() if i + 1 < len(matches) else len(text)
        content = text[start:end].strip()
        if len(content) > 10:
            entries.append((title, content))
    return entries


BOOKS = [
    ("huozhulin", "火珠林", "题麻衣道者著·通行本", "liuyao", "raw/huozhulin.txt", split_huozhulin, 4),
]


def main():
    total = 0
    for book_slug, book_name, version, subcategory, src_rel, splitter, weight in BOOKS:
        src = os.path.join(BASE, src_rel)
        out_dir = os.path.join(BASE, "library", "bu", subcategory, book_slug)
        os.makedirs(out_dir, exist_ok=True)
        text = open(src, encoding="utf-8").read()
        entries = splitter(text)
        for idx, (chapter, content) in enumerate(entries):
            md = write_entry(book_slug, book_name, version, subcategory, chapter, content, idx, weight)
            with open(os.path.join(out_dir, f"bu2_{book_slug}_{idx:03d}.md"), "w",
                      encoding="utf-8", newline="\n") as f:
                f.write(md)
        total += len(entries)
        print(f"  {book_name}: {len(entries)} 条 → {out_dir}")
    print(f"卜部第二批入库完成：{total} 条")


if __name__ == "__main__":
    main()
