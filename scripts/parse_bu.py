# -*- coding: utf-8 -*-
"""
卜部第一批典籍入库脚本（纯标准库，确定性输出）

底本：garychowcmu/daizhigev20 GitHub 仓库 易藏/易经/ 目录
  - zhouyi.txt     周易（经传合编，102KB，64卦+十翼）

切分策略：
  - 64卦：按"01. 乾（卦一）"格式标题切分，每条含卦辞、爻辞、彖传、象传、文言传
  - 易传4篇：系辞上下、说卦、序卦、杂卦（在64卦之后）
  - type=chapter，conditions 八键全空，keywords 驱动召回
  - category=bu, subcategory=yijing（易经）

输出：library/bu/yijing/zhouyi/*.md
用法：python -X utf8 scripts/parse_bu.py
"""
import os
import re

BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def extract_keywords(text):
    kws = ["易经"]
    mapping = [
        ("周易|易经|卦|爻|彖|象|文言", "周易经传"),
        ("乾|坤|屯|蒙|需|讼|师|比|小畜|履|泰|否|同人|大有|谦|豫|随|蛊|临|观|噬嗑|贲|剥|复|无妄|大畜|颐|大过|坎|离", "上经三十卦"),
        ("咸|恒|遯|大壮|晋|明夷|家人|睽|蹇|解|损|益|夬|姤|萃|升|困|井|革|鼎|震|艮|渐|归妹|丰|旅|巽|兑|涣|节|中孚|小过|既济|未济", "下经三十四卦"),
        ("系辞|说卦|序卦|杂卦", "易传十翼"),
        ("阴阳|太极|两仪|四象|八卦|六十四卦", "易理"),
        ("元亨利贞|吉凶悔吝|无咎|利贞", "卦辞爻辞"),
        ("刚柔|动静|进退|消长|盈虚", "阴阳变化"),
        ("君子|大人|圣人|先王", "易传义理"),
        ("天行健|地势坤|自强不息|厚德载物", "易传名句"),
        ("河图|洛书|先后天|八卦方位", "易图"),
        ("卜筮|占筮|蓍草|变卦|之卦", "占筮法"),
    ]
    for pattern, kw in mapping:
        if re.search(pattern, text):
            kws.append(kw)
    return list(dict.fromkeys(kws))


def write_entry(book_slug, book_name, version, subcategory, chapter, text, idx, weight=4):
    eid = f"bu_{book_slug}_{idx:03d}"
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
author: "见版本"
dynasty: "周"
type: "chapter"
conditions:
{cond}
weight: {weight}
tags: [{tags_str}]
---
"""
    body = f"### {title}\n\n"
    body += f"**【原文】**\n{text}\n\n"
    body += f"**【白话提要】**\n此条出自《{book_name}》「{chapter}」，为周易经传原文。周易以阴阳八卦为框架，论天地人三才之道，为群经之首、大道之源，亦是五术卜部之根本经典。\n"
    return fm + "\n" + body


def split_zhouyi(text):
    """周易：按64卦标题切分，再处理易传4篇。
    卦标题格式：01. 乾（卦一）、02. 坤（卦二）...（序号用半角.或全角．）
    """
    # 匹配64卦标题
    gua_pattern = r"^　*\d{2}[.．]\s*([^\n（]+)（卦[一二三四五六七八九十百]+）\s*$"
    matches = list(re.finditer(gua_pattern, text, re.M))

    entries = []
    # 64卦
    for i, m in enumerate(matches):
        gua_name = m.group(1).strip()
        title = f"{gua_name}卦"
        start = m.end()
        end = matches[i + 1].start() if i + 1 < len(matches) else len(text)
        content = text[start:end].strip()
        # 去掉开头的卦象符号行（如ⅰ（乾下乾上））
        content_lines = content.split("\n")
        cleaned = []
        for line in content_lines:
            s = line.strip()
            if re.match(r'^[ⅰⅱⅲⅳⅴⅵⅶⅷⅸⅹⅺⅻ]', s):
                continue
            cleaned.append(line)
        content = "\n".join(cleaned).strip()
        if len(content) > 30:
            entries.append((title, content))

    # 易传4篇（在64卦之后，匹配"系辞""说卦""序卦""杂卦"标题）
    zhuan_patterns = [
        (r"^　*系辞[上下]\s*$", "系辞传"),
        (r"^　*说卦\s*$", "说卦传"),
        (r"^　*序卦\s*$", "序卦传"),
        (r"^　*杂卦\s*$", "杂卦传"),
    ]
    # 找64卦之后的文本
    if matches:
        after_64 = text[matches[-1].end():]
        zhuan_matches = []
        for pattern, name in zhuan_patterns:
            m = re.search(pattern, after_64, re.M)
            if m:
                zhuan_matches.append((m.start(), name, m.group(0).strip()))
        zhuan_matches.sort(key=lambda x: x[0])
        for i, (pos, name, raw_title) in enumerate(zhuan_matches):
            start = pos + len(raw_title)
            end = zhuan_matches[i + 1][0] if i + 1 < len(zhuan_matches) else len(after_64)
            content = after_64[start:end].strip()
            if len(content) > 30:
                entries.append((name, content))

    return entries


BOOKS = [
    ("zhouyi", "周易", "周易经传合编·通行本", "yijing", "raw/zhouyi.txt", split_zhouyi, 4),
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
            with open(os.path.join(out_dir, f"bu_{book_slug}_{idx:03d}.md"), "w",
                      encoding="utf-8", newline="\n") as f:
                f.write(md)
        total += len(entries)
        print(f"  {book_name}: {len(entries)} 条 → {out_dir}")
    print(f"卜部第一批入库完成：{total} 条")


if __name__ == "__main__":
    main()
