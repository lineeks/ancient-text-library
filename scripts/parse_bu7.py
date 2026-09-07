# -*- coding: utf-8 -*-
"""
卜部第七批·太乙金镜式经解析脚本（纯标准库，确定性输出）

底本：raw/taiyi-jinjingshijing.txt（garychowcmu/daizhigev20 易藏/术数）
  107KB / 887行 / 3.6万字，唐王希明撰，四库全书本，十卷
切分：跳过四库提要+序+目录（每行多条目），按正文中「推XXX」短行标题切分
  （推上元积年/推太岁所在/推天目所在/推计神/推八门/推太乙考时 等），约60-80条
元数据：category=bu, subcategory=taiyi, type=chapter, conditions 八键全空
召回：keywords 驱动（太乙/三式/上元积年/太岁/天目/计神/八门/阴阳遁/
  直使/二十四气/黄道/分野/占岁/月计/日计/时计 等）
用法：python -X utf8 scripts/parse_bu7.py
"""
import os
import re

BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def extract_keywords(text):
    kws = ["太乙金镜式经", "卜部", "太乙", "三式"]
    mapping = [
        (r"上元积年|积年|章月|章岁", "上元积年"),
        (r"太岁|岁计|占岁", "太岁岁计"),
        (r"天目|文昌|主算|客算", "天目主客算"),
        (r"计神|始击|参相|大神", "计神"),
        (r"八门|开门|休门|生门|伤门|杜门|景门|死门|惊门", "八门"),
        (r"阴阳遁|阳遁|阴遁", "阴阳遁"),
        (r"直使|直符", "直使"),
        (r"二十四气|冬至|夏至|节气|次气", "二十四气"),
        (r"黄道|日度|列宿|分野|立成", "黄道分野"),
        (r"月计|日计|时计|计差", "月日时计"),
        (r"太乙|天帝|九宫|皇极", "太乙基础"),
        (r"推命|考时|占断|吉凶", "占断"),
        (r"六纪|三元|三元法", "六纪三元"),
    ]
    for pattern, kw in mapping:
        if re.search(pattern, text):
            kws.append(kw)
    return list(dict.fromkeys(kws))


def is_title(line):
    """判断是否为正文篇章标题行：以「推」开头，3-15字，纯中文"""
    s = line.strip()
    if not s or len(s) < 3 or len(s) > 15:
        return False
    if not s.startswith("推"):
        return False
    # 纯中文（不含空格、标点、数字）
    if re.search(r'[\s，。、；：！？0-9]', s):
        return False
    if not re.search(r'[\u4e00-\u9fff]', s):
        return False
    return True


def main():
    src = os.path.join(BASE, "raw/taiyi-jinjingshijing.txt")
    out_dir = os.path.join(BASE, "library", "bu", "taiyi", "taiyi-jinjingshijing")
    os.makedirs(out_dir, exist_ok=True)

    text = open(src, encoding="utf-8").read()
    lines = text.split("\n")

    # 找到正文开始：跳过提要+序，找到第一个"太乙金镜式经卷一"，然后跳过目录
    # 目录特征：每行有多个"推XXX"用全角空格分隔（>20字或含多个全角空格）
    # 正文特征：每行一个"推XXX"标题（<15字，纯中文）
    start = 0
    in_body = False
    for i, line in enumerate(lines):
        s = line.strip()
        if re.match(r'^太乙金镜式经卷[一二三四五六七八九十]+', s):
            # 找到卷标题，从下一行开始找正文
            in_body = False
            continue
        if not in_body and is_title(line):
            # 第一个正文标题行
            start = i
            in_body = True
            break

    # 按篇章标题切分
    raw_entries = []
    current_juan = "卷一"
    current_title = None
    current_content = []

    for i in range(start, len(lines)):
        line = lines[i]
        s = line.strip()

        # 卷标题
        juan_match = re.match(r'^太乙金镜式经卷([一二三四五六七八九十]+)', s)
        if juan_match:
            if current_title and current_content:
                raw_entries.append((current_juan, current_title, "\n".join(current_content).strip()))
            current_juan = f"卷{juan_match.group(1)}"
            current_title = None
            current_content = []
            continue

        # 篇章标题
        if is_title(line):
            if current_title and current_content:
                raw_entries.append((current_juan, current_title, "\n".join(current_content).strip()))
            current_title = s
            current_content = []
            continue

        # 正文
        if current_title:
            if s:
                current_content.append(s)

    # 最后一条
    if current_title and current_content:
        raw_entries.append((current_juan, current_title, "\n".join(current_content).strip()))

    # 合并过短条目（<50字）到上一条
    entries = []
    for juan, title, content in raw_entries:
        if len(content) < 50 and entries:
            pj, pt, pc = entries[-1]
            entries[-1] = (pj, pt + "·" + title, pc + "\n\n" + content)
        else:
            entries.append((juan, title, content))

    # 写入文件
    for idx, (juan, title, content) in enumerate(entries):
        eid = f"bu7_taiyi_{idx:03d}"
        kws = extract_keywords(title + content[:2000])
        tags = ["卜部", "太乙神数"]
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
book: "太乙金镜式经"
chapter: "{juan}"
section_title: "{title[:25]}"
source_version: "唐王希明撰·四库全书本"
author: "王希明"
dynasty: "唐"
type: "chapter"
conditions:
{cond}
weight: 4
tags: [{tags_str}]
---
"""
        body = f"### {title}\n\n"
        body += f"**【原文】**\n{content}\n\n"
        body += f"**【白话提要】**\n此条出自《太乙金镜式经》「{juan}·{title}」，为太乙神数经典原文。太乙与奇门遁甲、大六壬并称「三式」，以太乙为天帝之神，下司九宫，以上元积年起算，推太岁、天目、计神之所在，定主算客算之长短，审八门阴阳遁之吉凶，为古代天文占验与历算之集大成术数。\n"
        with open(os.path.join(out_dir, f"bu7_taiyi_{idx:03d}.md"), "w",
                  encoding="utf-8", newline="\n") as f:
            f.write(fm + "\n" + body)

    print(f"  太乙金镜式经: {len(entries)} 条 → {out_dir}")


if __name__ == "__main__":
    main()
