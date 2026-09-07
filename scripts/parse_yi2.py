# -*- coding: utf-8 -*-
"""
医部第二批典籍入库脚本（纯标准库，确定性输出）

底本：garychowcmu/daizhigev20 GitHub 仓库 医藏/ 目录
  - qianjinfang.txt    备急千金要方（唐孙思邈，30卷，1.6MB）
  - waitaimiyao.txt    外台秘要（唐王焘，40卷，2.3MB）
  - wenbingtiaobian.txt 温病条辨（清吴鞠通，6卷，359KB）
  - zhenjiujiayi.txt   针灸甲乙经（晋皇甫谧，12卷，422KB）
  - maijing.txt        脉经（晋王叔和，10卷，283KB）

切分策略：按卷切分（卷标题正则匹配，去重取首次出现）
  - 千金方/温病条辨：卷X篇名
  - 外台秘要：卷第X
  - 针灸甲乙经/脉经：卷X
  - type=chapter，conditions 八键全空，keywords 驱动召回
  - category=yi, subcategory 按书分类（fangshu/wenbing/zhenji/zhenfa）

输出：library/yi/{fangshu,wenbing,zhenji,zhenfa}/*.md
用法：python -X utf8 scripts/parse_yi2.py
"""
import os
import re

BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def extract_keywords(text):
    kws = ["中医"]
    mapping = [
        ("千金|孙思邈|备急", "备急千金要方"),
        ("外台|王焘|秘要", "外台秘要"),
        ("温病|吴鞠通|上焦|中焦|下焦|银翘|桑菊", "温病条辨"),
        ("针灸|甲乙|皇甫谧|刺|灸|腧穴", "针灸甲乙经"),
        ("脉经|王叔和|脉象|寸口|浮|沉|迟|数|滑|涩", "脉经"),
        ("五脏|肝|心|脾|肺|肾", "五脏"),
        ("六腑|胆|胃|大肠|小肠|膀胱|三焦", "六腑"),
        ("经络|经脉|十二经", "经络"),
        ("方剂|汤|散|丸|膏", "方剂"),
        ("药性|气味|酸|苦|甘|辛|咸|寒|热|温|凉", "药性"),
        ("病机|阴阳|五行|气血|津液", "病机"),
        ("伤寒|太阳|阳明|少阳|太阴|少阴|厥阴", "伤寒"),
        ("病因|外感|内伤|七情|六淫|风|寒|暑|湿|燥|火", "病因"),
        ("诊法|望闻问切|四诊|脉", "诊法"),
        ("治法|治则|汗|吐|下|和|温|清|补|消", "治法"),
        ("方论|方解|君臣佐使", "方剂理论"),
        ("妇人|妇科|调经|带下|胎|产", "妇科"),
        ("小儿|儿科|惊风|疳", "儿科"),
        ("外科|痈|疽|疮|疡|痔", "外科"),
        ("五官|眼|耳|鼻|口|齿|咽喉", "五官科"),
        ("养生|养生|食疗|食治|养性|辟谷|导引|吐纳|行气", "养生"),
        ("针灸|刺法|灸法|针刺|艾灸|穴位|腧穴|经穴", "针灸"),
        ("脉象|脉学|脉理|脉诀|脉赋", "脉学"),
        ("温病|瘟疫|疫疠|温疫|热病|暑温|湿温|伏暑|秋燥|冬温", "温病"),
    ]
    for pattern, kw in mapping:
        if re.search(pattern, text):
            kws.append(kw)
    return list(dict.fromkeys(kws))


def write_entry(book_slug, book_name, version, subcategory, chapter, text, idx, weight=3):
    eid = f"yi2_{book_slug}_{idx:03d}"
    kws = extract_keywords(chapter + text[:2000])
    tags = ["医部", book_name]
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
dynasty: "晋唐清"
type: "chapter"
conditions:
{cond}
weight: {weight}
tags: [{tags_str}]
---
"""
    body = f"### {title}\n\n"
    body += f"**【原文】**\n{text}\n\n"
    body += f"**【白话提要】**\n此卷出自《{book_name}》「{chapter}」，为中医典籍原文。医部典籍以阴阳五行为理论框架，论脏腑经络、病机诊法、治则方药，与命部同属五术体系中的重要分支。\n"
    return fm + "\n" + body


def split_by_juan(text, pattern=r"^　*(?:[\u4e00-\u9fff]{1,6}\s+)?卷第?[一二三四五六七八九十百]+[^\n]{0,20}$"):
    """按卷标题切分，去重（只取每个卷号的首次出现）。
    支持 '卷一'、'卷第一'、'脉经 卷一' 等格式。
    返回 [(title, content), ...]
    """
    matches = list(re.finditer(pattern, text, re.M))
    # 去重：相同卷号只取第一次
    seen = set()
    unique_matches = []
    for m in matches:
        title = m.group(0).strip()
        # 提取卷号（卷一/卷第一/脉经 卷一 → 一）
        num_match = re.search(r"卷第?([一二三四五六七八九十百]+)", title)
        num = num_match.group(1) if num_match else title
        if num not in seen:
            seen.add(num)
            unique_matches.append(m)
    entries = []
    for i, m in enumerate(unique_matches):
        title = m.group(0).strip()
        # 去掉书名前缀（如 '脉经 卷一' → '卷一'）
        clean_title = re.sub(r"^[\u4e00-\u9fff]{1,6}\s+", "", title)
        start = m.end()
        end = unique_matches[i + 1].start() if i + 1 < len(unique_matches) else len(text)
        content = text[start:end].strip()
        if len(content) > 50:
            entries.append((clean_title, content))
    return entries


BOOKS = [
    ("qianjinfang", "备急千金要方", "唐孙思邈撰·四库全书本", "fangshu", "raw/qianjinfang.txt", 3),
    ("waitaimiyao", "外台秘要", "唐王焘撰·明程衍道校", "fangshu", "raw/waitaimiyao.txt", 3),
    ("wenbingtiaobian", "温病条辨", "清吴鞠通撰·通行本", "wenbing", "raw/wenbingtiaobian.txt", 4),
    ("zhenjiujiayi", "针灸甲乙经", "晋皇甫谧撰·四库全书本", "zhenji", "raw/zhenjiujiayi.txt", 3),
    ("maijing", "脉经", "晋王叔和撰·四库全书本", "zhenfa", "raw/maijing.txt", 3),
]


def main():
    total = 0
    for book_slug, book_name, version, subcategory, src_rel, weight in BOOKS:
        src = os.path.join(BASE, src_rel)
        out_dir = os.path.join(BASE, "library", "yi", subcategory, book_slug)
        os.makedirs(out_dir, exist_ok=True)
        text = open(src, encoding="utf-8").read()
        entries = split_by_juan(text)
        for idx, (chapter, content) in enumerate(entries):
            md = write_entry(book_slug, book_name, version, subcategory, chapter, content, idx, weight)
            with open(os.path.join(out_dir, f"yi2_{book_slug}_{idx:03d}.md"), "w",
                      encoding="utf-8", newline="\n") as f:
                f.write(md)
        total += len(entries)
        print(f"  {book_name}: {len(entries)} 卷 → {out_dir}")
    print(f"医部第二批入库完成：{total} 卷")


if __name__ == "__main__":
    main()
