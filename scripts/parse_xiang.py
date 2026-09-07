# -*- coding: utf-8 -*-
"""
相部第一批典籍入库脚本（纯标准库，确定性输出）

底本：garychowcmu/daizhigev20 GitHub 仓库 易藏/术数/ 目录
  - shenxiangquanbian.txt  神相全编（明清相术集大成，113KB）
  - liuzhuangxiangfa.txt   柳庄相法（清袁珙，152KB）
  - hanlongjing.txt        撼龙经（唐杨筠松，峦头派鼻祖，79KB）
  - zangshu.txt            葬书（晋郭璞，风水理论奠基，45KB）
  - qingnangaoyu.txt       青囊奥语（唐杨筠松，理气派经典，3.8KB）

切分策略：
  - 神相全编：按主题标题切分（短行<15字符，不以数字开头，去重）
  - 柳庄相法：按"一、XXX"小节切分
  - 撼龙经/葬书/青囊奥语：整本书作为1条（歌赋体/短文，无明确篇标题）
  - type=chapter，conditions 八键全空，keywords 驱动召回
  - category=xiang, subcategory=renxiang（人相）/ dixiang（地相）

输出：library/xiang/{renxiang,dixiang}/*.md
用法：python -X utf8 scripts/parse_xiang.py
"""
import os
import re

BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def extract_keywords(text):
    kws = ["相术"]
    mapping = [
        ("神相|相法|相术|面相|手相|骨相", "相术"),
        ("麻衣|柳庄|水镜|许负|鬼谷子", "相学名著"),
        ("风水|堪舆|阳宅|阴宅|墓穴|葬", "风水堪舆"),
        ("峦头|龙|砂|水|穴|明堂|朝案", "峦头派"),
        ("理气|三元|三合|玄空|九星|洛书", "理气派"),
        ("杨筠松|杨公|杨救贫", "杨公风水"),
        ("郭璞|葬经|葬书", "郭璞风水"),
        ("五官|六府|三停|五岳|四渎|五星", "面相部位"),
        ("气色|神色|血气|面色", "气色"),
        ("纹|痣|痕|疤", "纹痣"),
        ("骨|骨骼|骨格|头骨", "骨相"),
        ("手|掌|指纹|掌纹", "手相"),
        ("声|音|声音|语声", "声音相"),
        ("行|坐|卧|立|威仪|举止", "行止相"),
        ("富贵|贫贱|吉凶|祸福|寿夭|穷通", "命理吉凶"),
        ("五行|金木水火土|五行形", "五行相"),
        ("阴阳|男女|老幼", "阴阳相"),
        ("龙脉|龙穴|砂水|水口|来龙|去脉", "龙脉"),
        ("青龙|白虎|朱雀|玄武", "四灵"),
        ("河图|洛书|八卦|九宫", "易理"),
    ]
    for pattern, kw in mapping:
        if re.search(pattern, text):
            kws.append(kw)
    return list(dict.fromkeys(kws))


def write_entry(book_slug, book_name, version, subcategory, chapter, text, idx, weight=3):
    eid = f"xiang_{book_slug}_{idx:03d}"
    kws = extract_keywords(chapter + text[:2000])
    tags = ["相部", book_name]
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
dynasty: "晋唐明清"
type: "chapter"
conditions:
{cond}
weight: {weight}
tags: [{tags_str}]
---
"""
    body = f"### {title}\n\n"
    body += f"**【原文】**\n{text}\n\n"
    body += f"**【白话提要】**\n此条出自《{book_name}》「{chapter}」，为相术典籍原文。相部以观察形貌、气色、骨格、举止推断人之吉凶祸福，与命部同属五术体系中的重要分支。\n"
    return fm + "\n" + body


def split_shenxiang(text):
    """神相全编：按主题标题切分。
    主题标题特征：短行（<15字符），不以数字/标点开头，去重。
    """
    lines = text.split("\n")
    entries = []
    current_title = None
    current_lines = []
    seen = set()
    for line in lines:
        s = line.strip()
        # 判断是否为主题标题：短行、非空、不以数字/标点/常见子标题开头
        is_title = (
            len(s) < 15 and len(s) > 1
            and not re.match(r'^[一二三四五六七八九十百千]+[、取看]', s)
            and not re.match(r'^[《【\(（]', s)
            and not re.match(r'^[，。、；：！？]', s)
            and s not in seen
        )
        if is_title:
            if current_title is not None and current_lines:
                content = "\n".join(current_lines).strip()
                if len(content) > 30:
                    entries.append((current_title, content))
            current_title = s
            seen.add(s)
            current_lines = []
        else:
            if current_title is not None:
                current_lines.append(line)
    # 最后一条
    if current_title is not None and current_lines:
        content = "\n".join(current_lines).strip()
        if len(content) > 30:
            entries.append((current_title, content))
    return entries


def split_liuzhuang(text):
    """柳庄相法：按"一、XXX"小节切分。"""
    pattern = r"^　*[一二三四五六七八九十百千]+、[^\n]{1,30}$"
    matches = list(re.finditer(pattern, text, re.M))
    entries = []
    for i, m in enumerate(matches):
        title = m.group(0).strip()
        start = m.end()
        end = matches[i + 1].start() if i + 1 < len(matches) else len(text)
        content = text[start:end].strip()
        if len(content) > 20:
            entries.append((title, content))
    return entries


def split_whole(text):
    """整本书作为1条。"""
    # 去掉开头的书名行
    lines = text.split("\n")
    content_lines = []
    for line in lines:
        s = line.strip()
        if s and not re.match(r'^《[^》]+》$', s):
            content_lines.append(line)
    content = "\n".join(content_lines).strip()
    return [("全书", content)] if content else []


BOOKS = [
    ("shenxiangquanbian", "神相全编", "明清相术集大成·通行本", "renxiang", "raw/shenxiangquanbian.txt", split_shenxiang, 3),
    ("liuzhuangxiangfa", "柳庄相法", "清袁珙撰·通行本", "renxiang", "raw/liuzhuangxiangfa.txt", split_liuzhuang, 3),
    ("hanlongjing", "撼龙经", "唐杨筠松撰·通行本", "dixiang", "raw/hanlongjing.txt", split_whole, 4),
    ("zangshu", "葬书", "晋郭璞撰·通行本", "dixiang", "raw/zangshu.txt", split_whole, 4),
    ("qingnangaoyu", "青囊奥语", "唐杨筠松撰·通行本", "dixiang", "raw/qingnangaoyu.txt", split_whole, 4),
]


def main():
    total = 0
    for book_slug, book_name, version, subcategory, src_rel, splitter, weight in BOOKS:
        src = os.path.join(BASE, src_rel)
        out_dir = os.path.join(BASE, "library", "xiang", subcategory, book_slug)
        os.makedirs(out_dir, exist_ok=True)
        text = open(src, encoding="utf-8").read()
        entries = splitter(text)
        for idx, (chapter, content) in enumerate(entries):
            md = write_entry(book_slug, book_name, version, subcategory, chapter, content, idx, weight)
            with open(os.path.join(out_dir, f"xiang_{book_slug}_{idx:03d}.md"), "w",
                      encoding="utf-8", newline="\n") as f:
                f.write(md)
        total += len(entries)
        print(f"  {book_name}: {len(entries)} 条 → {out_dir}")
    print(f"相部第一批入库完成：{total} 条")


if __name__ == "__main__":
    main()
