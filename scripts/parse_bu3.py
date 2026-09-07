# -*- coding: utf-8 -*-
"""
卜部第三批典籍入库脚本（纯标准库，确定性输出）

底本：garychowcmu/daizhigev20 GitHub 仓库 易藏/术数/ 目录
  - meihuayishu.txt  梅花易数（宋邵雍撰，124KB，梅花易数派鼻祖）

切分策略：
  - 跳过目录（找到第二个"卷一"即正文开始）
  - 按短行标题切分（2-12字汉字，不含标点，行首可有全角空格）
  - 卷标题/篇标题作为 chapter 前缀
  - type=chapter，conditions 八键全空，keywords 驱动召回
  - category=bu, subcategory=meihua（梅花易数）

输出：library/bu/meihua/meihuayishu/*.md
用法：python -X utf8 scripts/parse_bu3.py
"""
import os
import re

BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def extract_keywords(text):
    kws = ["梅花易数"]
    mapping = [
        (r"梅花|观梅|牡丹|叩门|动静|牌额|忧色|喜色|哀鸣|枯枝|风觉|鸟占", "梅花占例"),
        (r"起卦|起例|占法|玩法|卦以八除|爻以六除|互卦|年月日时|物数|声音|字占|丈尺|尺寸", "起卦法"),
        (r"体用|体卦|用卦|体生用|用生体|体克用|用克体|体用比和", "体用"),
        (r"互卦|变卦|之卦|本卦|错卦|综卦|动爻|变爻", "卦变"),
        (r"五行生克|金木水火土|生克|旺相|休囚|卦气旺|卦气衰", "五行旺衰"),
        (r"八卦|乾|坤|震|巽|坎|离|艮|兑|八卦象例|八卦万物属类|八卦方位", "八卦"),
        (r"天干|地支|十天干|十二地支|纳甲|纳支", "天干地支"),
        (r"断卦|断辞|断曰|判曰|占断|占验", "占断"),
        (r"失误|错断|误断|辨误|考误", "断卦辨误"),
        (r"十应|三要|心易|占卜|类占|占例", "心易占卜"),
        (r"饮食|婚姻|求财|求官|疾病|失物|行人|出行|官讼|六甲", "分类占"),
    ]
    for pattern, kw in mapping:
        if re.search(pattern, text):
            kws.append(kw)
    return list(dict.fromkeys(kws))


def write_entry(book_slug, book_name, version, subcategory, chapter, section, text, idx, weight=4):
    eid = f"bu3_{book_slug}_{idx:03d}"
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
author: "邵雍"
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
    body += f"**【白话提要】**\n此条出自《{book_name}》「{chapter}·{section}」，为梅花易数派经典原文。梅花易数由宋邵雍创立，以体用生克、卦气旺衰、万物类象为核心，不拘古法、随心起卦，为象数易占之集大成者。\n"
    return fm + "\n" + body


def split_meihua(text):
    """梅花易数：跳过目录，按短行标题切分。
    返回 [(chapter, section, content), ...]
    """
    # 找到第二个"卷一"（正文开始）
    first = text.find("\n卷一\n")
    if first < 0:
        first = text.find("卷一")
    second = text.find("\n卷一\n", first + 1)
    if second < 0:
        second = text.find("卷一", first + 1)
    if second >= 0:
        text = text[second:]

    lines = text.split("\n")
    entries = []
    current_juan = ""
    current_pian = ""
    current_title = ""
    current_content = []

    def flush():
        if current_title and current_content:
            content = "\n".join(current_content).strip()
            if len(content) > 10:
                chapter = f"{current_juan}·{current_pian}" if current_pian else current_juan
                entries.append((chapter, current_title, content))

    # 短行标题正则：2-12字汉字，不含标点，行首可有全角空格
    title_pattern = re.compile(r"^　*([\u4e00-\u9fff]{2,12})$")
    juan_pattern = re.compile(r"^　*卷([一二三四五六七八九十]+)$")
    pian_pattern = re.compile(r"^　*([\u4e00-\u9fff]{2,10}篇[之其][一二三四五六七八九十]+)$")

    for line in lines:
        s = line.strip()
        if not s:
            current_content.append(line)
            continue
        jm = juan_pattern.match(line)
        if jm:
            flush()
            current_juan = f"卷{jm.group(1)}"
            current_pian = ""
            current_title = ""
            current_content = []
            continue
        pm = pian_pattern.match(line)
        if pm:
            flush()
            current_pian = pm.group(1)
            current_title = ""
            current_content = []
            continue
        tm = title_pattern.match(line)
        if tm:
            flush()
            current_title = tm.group(1)
            current_content = []
            continue
        current_content.append(line)

    flush()
    return entries


BOOKS = [
    ("meihuayishu", "梅花易数", "宋邵雍撰·通行本", "meihua", "raw/meihuayishu.txt", split_meihua, 4),
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
            with open(os.path.join(out_dir, f"bu3_{book_slug}_{idx:03d}.md"), "w",
                      encoding="utf-8", newline="\n") as f:
                f.write(md)
        total += len(entries)
        print(f"  {book_name}: {len(entries)} 条 → {out_dir}")
    print(f"卜部第三批入库完成：{total} 条")


if __name__ == "__main__":
    main()
