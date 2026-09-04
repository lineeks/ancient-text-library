# -*- coding: utf-8 -*-
"""
子平赋文典籍入库脚本（纯标准库，确定性输出）

处理两本赋文体典籍：
  - 兰台妙选（lantaimiaoxuan.txt）：明西窗老人，专论八字格局贵贱
    结构：赋文标题行（顶格）+ 注解段落（全角空格缩进）
  - 三命指迷赋（sanmingzhimifu.txt）：宋岳珂补注（依托），四库全书本
    结构：连续的"赋文【注解】赋文【注解】..."模式

切分策略：
  - 兰台妙选：按非缩进行作为条目边界，标题行+后续缩进行为一条
  - 三命指迷赋：正则匹配"赋文【注解】"模式，每条为一个条目
  - type=fuwen，conditions 八键全空，keywords 驱动召回
  - category=ming, subcategory=bazi（由路径自动推断）

输出：library/ming/bazi/extended/{lantaimiaoxuan,sanmingzhimifu}/*.md
用法：python -X utf8 scripts/parse_fuwen.py
"""
import os
import re

BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def extract_keywords(text):
    """从文本中提取子平八字关键词。"""
    kws = ["子平八字"]
    mapping = [
        ("格局", "格局"),
        ("用神", "用神"),
        ("正官|官星", "正官"),
        ("七杀|偏官|七煞", "七杀"),
        ("正财|偏财|财星", "正财"),
        ("正印|偏印|印绶", "正印"),
        ("伤官", "伤官"),
        ("食神", "食神"),
        ("比肩|劫财", "比肩"),
        ("天乙贵人|天乙", "天乙贵人"),
        ("文昌", "文昌贵人"),
        ("天德|月德|天月德", "天月二德"),
        ("驿马", "驿马"),
        ("华盖", "华盖"),
        ("羊刃|阳刃", "羊刃"),
        ("将星", "将星"),
        ("三奇", "三奇贵人"),
        ("空亡", "空亡"),
        ("孤辰|寡宿", "孤辰寡宿"),
        ("元辰", "元辰"),
        ("亡神", "亡神"),
        ("劫煞|刼煞", "劫煞"),
        ("禄神|建禄|岁禄", "禄神"),
        ("纳音", "纳音"),
        ("调候|寒暖|燥湿", "调候"),
        ("五行", "五行"),
        ("天干|地支", "天干地支"),
        ("四柱|年月日时", "四柱"),
        ("大运|流年", "大运流年"),
        ("胎元", "胎元"),
        ("生旺|死绝|墓库", "生旺死绝"),
        ("刑冲|合害|三刑|六冲|六合|六害", "刑冲合害"),
        ("贵人", "贵人"),
        ("贵格", "贵格"),
        ("贫贱|富贵|吉凶|寿夭", "贵贱吉凶"),
    ]
    for pattern, kw in mapping:
        if re.search(pattern, text):
            kws.append(kw)
    return list(dict.fromkeys(kws))


def write_entry(book_slug, book_name, version, chapter, text, idx, weight=4):
    eid = f"fw_{book_slug}_{idx:03d}"
    kws = extract_keywords(chapter + text)
    tags = ["子平赋文", book_name]
    title = text[:14].replace("\n", "").replace("　", "")
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
author: "见版本"
dynasty: "明清"
type: "fuwen"
conditions:
{cond}
weight: {weight}
tags: [{tags_str}]
---
"""
    body = f"### {title}\n\n"
    body += f"**【原文】**\n{text}\n\n"
    body += f"**【白话提要】**\n此条出自《{book_name}》「{chapter}」，为子平赋文原文。赋文体以凝练韵语概括命理格局与神煞断验，注解逐句阐释取象与用理。\n"
    return fm + "\n" + body


def parse_lantai(path):
    """解析兰台妙选：按非缩进行作为条目边界。
    返回 [(chapter, text), ...]
    """
    with open(path, encoding="utf-8") as f:
        lines = f.readlines()
    entries = []
    current_title = None
    current_lines = []
    chapter = "全篇"
    # 跳过开头的书名行
    start = 0
    for i, line in enumerate(lines):
        stripped = line.strip()
        if stripped and not stripped.startswith("《") and stripped != "兰台妙选":
            start = i
            break
    for line in lines[start:]:
        raw = line.rstrip("\n")
        stripped = raw.strip()
        if not stripped:
            continue
        # 非缩进行（顶格，不以全角空格开头）= 新条目标题
        if not raw.startswith("　") and not raw.startswith(" "):
            if current_title is not None:
                entries.append((chapter, current_title + "\n" + "\n".join(current_lines)))
            current_title = stripped
            current_lines = []
        else:
            # 缩进行 = 注解
            current_lines.append(stripped)
    if current_title is not None:
        entries.append((chapter, current_title + "\n" + "\n".join(current_lines)))
    return entries


def parse_zhimifu(path):
    """解析三命指迷赋：正则匹配"赋文【注解】"模式。
    返回 [(chapter, text), ...]
    """
    with open(path, encoding="utf-8") as f:
        content = f.read()
    # 找到正文开始（跳过四库提要）
    start_marker = "三命指迷赋\n"
    start = content.find(start_marker)
    if start < 0:
        start = 0
    else:
        start += len(start_marker)
    # 找到正文结束（星命总括开始）
    end_marker = "<子部,术数类"
    end = content.find(end_marker, start)
    if end < 0:
        end = len(content)
    body = content[start:end]
    # 匹配"赋文【注解】"模式
    # 赋文：非【的字符，注解：【...】
    pattern = re.compile(r"([^【]{2,200}?)【([^】]{10,2000})】", re.S)
    entries = []
    chapter = "全篇"
    for m in pattern.finditer(body):
        fuwen = m.group(1).strip()
        zhujie = m.group(2).strip()
        if len(fuwen) < 2:
            continue
        text = fuwen + "\n【注解】" + zhujie
        entries.append((chapter, text))
    return entries


def process_book(book_slug, book_name, version, src_rel, parse_func, out_subdir, weight=4):
    src = os.path.join(BASE, src_rel)
    out_dir = os.path.join(BASE, "library", "ming", "bazi", "extended", out_subdir)
    os.makedirs(out_dir, exist_ok=True)
    entries = parse_func(src)
    for idx, (chapter, text) in enumerate(entries):
        content = write_entry(book_slug, book_name, version, chapter, text, idx, weight)
        with open(os.path.join(out_dir, f"fw_{book_slug}_{idx:03d}.md"), "w",
                  encoding="utf-8", newline="\n") as f:
            f.write(content)
    print(f"  {book_name}: {len(entries)} 条 → {out_dir}")
    return len(entries)


def main():
    total = 0
    total += process_book(
        "lantai", "兰台妙选", "明·西窗老人（四库全书本）",
        "raw/lantaimiaoxuan.txt", parse_lantai, "lantaimiaoxuan", weight=4)
    total += process_book(
        "zhimifu", "三命指迷赋", "宋·岳珂补注（依托，四库全书本）",
        "raw/sanmingzhimifu.txt", parse_zhimifu, "sanmingzhimifu", weight=4)
    print(f"子平赋文典籍入库完成：{total} 条")


if __name__ == "__main__":
    main()
