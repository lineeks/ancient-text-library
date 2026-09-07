# -*- coding: utf-8 -*-
"""
山部第一批典籍入库脚本（纯标准库，确定性输出）

底本：
  - cantongqi.txt   周易参同契分章通真义（五代彭晓注，道藏太玄部，105KB）
  - taijilun.txt     太极拳论（清王宗岳，艺藏武术，19KB）
  - yijinjing.txt    达摩洗髓易筋经（艺藏武术，131KB）

切分策略：
  - 参同契：按90章标题切分（"乾坤者易之门户章第一"等，去重取正文）
  - 太极拳论：整本书1条（原文+顾留馨解说）
  - 易筋经：按"图说/篇"大类切分（原理源流、正身图说、侧身图说等约15条）
  - type=chapter，conditions 八键全空，keywords 驱动召回
  - category=shan, subcategory=dandao（丹道）/ wushu（武术）/ yangsheng（养生）

输出：library/shan/{dandao,wushu,yangsheng}/*.md
用法：python -X utf8 scripts/parse_shan.py
"""
import os
import re

BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def extract_keywords(text):
    kws = ["山术"]
    mapping = [
        ("参同契|魏伯阳|彭晓|丹道|金丹|外丹|内丹|炉火", "丹道"),
        ("太极|王宗岳|太极拳|阴阳|刚柔|动静|虚实", "太极拳"),
        ("易筋|洗髓|达摩|导引|养生|八段锦|十二段锦|内功|外功|吐纳", "养生导引"),
        ("乾坤|坎离|水火|龙虎|铅汞|乌兔|夫妻|牝牡", "丹道象喻"),
        ("火候|进阳火|退阴符|朔望|晦朔|弦望", "丹道火候"),
        ("武术|拳|功夫|技击|内家|外家", "武术"),
        ("经络|气血|筋骨|肌肉|脏腑|三焦|脾胃|肾腰", "养生经络"),
        ("五行|金木水火土|相生|相克", "五行"),
        ("阴阳|太极|无极|两仪|四象|八卦", "阴阳易理"),
        ("精气神|性命|性命双修|炼精化气|炼气化神|炼神还虚", "内丹三要"),
        ("黄庭|泥丸|丹田|绛宫|关元|气海", "丹道部位"),
    ]
    for pattern, kw in mapping:
        if re.search(pattern, text):
            kws.append(kw)
    return list(dict.fromkeys(kws))


def write_entry(book_slug, book_name, version, subcategory, chapter, text, idx, weight=3):
    eid = f"shan_{book_slug}_{idx:03d}"
    kws = extract_keywords(chapter + text[:2000])
    tags = ["山部", book_name]
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
author: "见版本"
dynasty: "汉五代清"
type: "chapter"
conditions:
{cond}
weight: {weight}
tags: [{tags_str}]
---
"""
    body = f"### {title}\n\n"
    body += f"**【原文】**\n{text}\n\n"
    body += f"**【白话提要】**\n此条出自《{book_name}》「{chapter}」，为山部典籍原文。山部以丹道修炼、养生导引、武术技击为核心，讲求性命双修、天人合一，与命医相卜同属五术体系。\n"
    return fm + "\n" + body


def split_cantongqi(text):
    """周易参同契分章通真义：按90章切分。
    章标题在目录和正文中各出现一次，去重取正文（第二次出现）。
    """
    pattern = r"^　*([^　\n]+章第[一二三四五六七八九十百]+)\s*$"
    matches = list(re.finditer(pattern, text, re.M))
    # 去重：相同章名只取第二次出现（正文部分）
    seen = {}
    for m in matches:
        title = m.group(1).strip()
        if title in seen:
            seen[title] = m  # 第二次出现（正文）
        else:
            seen[title] = None  # 第一次出现（目录），标记但不保留
    # 保留第二次出现的章标题
    body_matches = [m for m in seen.values() if m is not None]
    body_matches.sort(key=lambda x: x.start())

    entries = []
    for i, m in enumerate(body_matches):
        title = m.group(1).strip()
        start = m.end()
        end = body_matches[i + 1].start() if i + 1 < len(body_matches) else len(text)
        content = text[start:end].strip()
        if len(content) > 30:
            entries.append((title, content))
    return entries


def split_taiji(text):
    """太极拳论：整本书1条。"""
    lines = text.split("\n")
    content_lines = []
    for line in lines:
        s = line.strip()
        if s and not re.match(r'^《[^》]+》$', s):
            content_lines.append(line)
    content = "\n".join(content_lines).strip()
    return [("太极拳论", content)] if content else []


def split_yijinjing(text):
    """达摩洗髓易筋经：按"图说/篇"大类切分。
    主要篇章：原理源流、易筋经总论、洗髓经总义、养身养心论说、练功歌诀、
    正身图说、侧身图说、半身图说、屈身图说、折身图说、扭身图说、倒身图说、
    翻身图说、行身图说、坐身图说、定身图说、卧身图说、韦驮劲十二势图说、
    十二大劲图说、立八段锦图说、坐十二段锦图说、操腹九冲图说
    """
    # 匹配"XX图说"或"XX论"或"XX篇"标题（短行，独立成行）
    pattern = r"^　*([^\n]{2,12}(?:图说|总论|总义|论说|歌诀|篇))\s*$"
    matches = list(re.finditer(pattern, text, re.M))
    # 去重：相同标题只取第一次出现
    seen = set()
    unique_matches = []
    for m in matches:
        title = m.group(1).strip()
        if title not in seen:
            seen.add(title)
            unique_matches.append(m)

    entries = []
    for i, m in enumerate(unique_matches):
        title = m.group(1).strip()
        start = m.end()
        end = unique_matches[i + 1].start() if i + 1 < len(unique_matches) else len(text)
        content = text[start:end].strip()
        if len(content) > 30:
            entries.append((title, content))
    return entries


BOOKS = [
    ("cantongqi", "周易参同契分章通真义", "五代彭晓注·正统道藏太玄部", "dandao", "raw/cantongqi.txt", split_cantongqi, 4),
    ("taijilun", "太极拳论", "清王宗岳撰·艺藏武术本", "wushu", "raw/taijilun.txt", split_taiji, 3),
    ("yijinjing", "达摩洗髓易筋经", "艺藏武术本", "yangsheng", "raw/yijinjing.txt", split_yijinjing, 3),
]


def main():
    total = 0
    for book_slug, book_name, version, subcategory, src_rel, splitter, weight in BOOKS:
        src = os.path.join(BASE, src_rel)
        out_dir = os.path.join(BASE, "library", "shan", subcategory, book_slug)
        os.makedirs(out_dir, exist_ok=True)
        text = open(src, encoding="utf-8").read()
        entries = splitter(text)
        for idx, (chapter, content) in enumerate(entries):
            md = write_entry(book_slug, book_name, version, subcategory, chapter, content, idx, weight)
            with open(os.path.join(out_dir, f"shan_{book_slug}_{idx:03d}.md"), "w",
                      encoding="utf-8", newline="\n") as f:
                f.write(md)
        total += len(entries)
        print(f"  {book_name}: {len(entries)} 条 → {out_dir}")
    print(f"山部第一批入库完成：{total} 条")


if __name__ == "__main__":
    main()
