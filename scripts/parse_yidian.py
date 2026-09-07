# -*- coding: utf-8 -*-
"""
医部四大经典入库脚本（纯标准库，确定性输出）

底本：garychowcmu/daizhigev20 GitHub 仓库 医藏/ 目录
  - suwen.txt     重广补注黄帝内经素问（唐王冰注，宋林亿校，81篇）
  - lingshu.txt   灵枢经（81篇）
  - nanjing.txt   八十一难经（旧题扁鹊，81难）
  - shanghan.txt  伤寒论（汉张仲景，10篇）
  - shennong.txt  神农本草经（上中下三品，365药）

切分策略：
  - 素问：按 ○XXX篇第X 切分（81篇）
  - 灵枢：按 XXX第X 切分（81篇）
  - 难经：按 X难 切分（81难）
  - 伤寒论：按 辨XXX病脉证并治 切分（约10篇）
  - 神农本草经：按部类+药名切分（365味药）
  - type=chapter，conditions 八键全空，keywords 驱动召回
  - category=yi, subcategory=jingdian（由路径自动推断）

输出：library/yi/jingdian/{suwen,lingshu,nanjing,shanghan,shennong}/*.md
用法：python -X utf8 scripts/parse_yidian.py
"""
import os
import re

BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def extract_keywords(text):
    """从医书文本中提取关键词。"""
    kws = ["中医"]
    mapping = [
        ("黄帝|素问|灵枢|内经", "黄帝内经"),
        ("难经|扁鹊", "难经"),
        ("伤寒|太阳|阳明|少阳|太阴|少阴|厥阴", "伤寒论"),
        ("金匮|杂病", "金匮要略"),
        ("本草|上药|中药|下药|玉石部|草部|木部|兽部|虫鱼部|果部|米谷部|菜部", "神农本草经"),
        ("五脏|五脏六腑|肝|心|脾|肺|肾", "五脏"),
        ("六腑|胆|胃|大肠|小肠|膀胱|三焦", "六腑"),
        ("经络|经脉|络脉|十二经", "经络"),
        ("脉象|脉浮|脉沉|脉迟|脉数|寸口|人迎", "脉象"),
        ("方剂|汤|散|丸|膏|桂枝汤|麻黄汤|小柴胡|大柴胡", "方剂"),
        ("药性|气味|酸|苦|甘|辛|咸|寒|热|温|凉|有毒|无毒", "药性"),
        ("病机|阴阳|五行|气血|津液|精|神", "病机"),
        ("针灸|九针|刺|灸|穴位|腧穴", "针灸"),
        ("病因|外感|内伤|七情|六淫|风|寒|暑|湿|燥|火", "病因"),
        ("诊法|望闻问切|四诊", "诊法"),
        ("治法|治则|汗|吐|下|和|温|清|补|消", "治法"),
        ("养生|养生|调神|四时|饮食|起居", "养生"),
        ("运气|五运六气|司天|在泉|主气|客气", "五运六气"),
        ("命门|元气|原气|宗气|营气|卫气", "气血津液"),
        ("七方|十剂|君臣佐使|七情合和", "方剂理论"),
        ("服石|服食|辟谷|导引|吐纳|行气", "养生方术"),
    ]
    for pattern, kw in mapping:
        if re.search(pattern, text):
            kws.append(kw)
    return list(dict.fromkeys(kws))


def write_entry(book_slug, book_name, version, chapter, text, idx, weight=3):
    eid = f"yd_{book_slug}_{idx:03d}"
    kws = extract_keywords(chapter + text[:2000])
    tags = ["医部经典", book_name]
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
dynasty: "先秦汉"
type: "chapter"
conditions:
{cond}
weight: {weight}
tags: [{tags_str}]
---
"""
    body = f"### {title}\n\n"
    body += f"**【原文】**\n{text}\n\n"
    body += f"**【白话提要】**\n此条出自《{book_name}》「{chapter}」，为中医经典原文。医部典籍以阴阳五行为理论框架，论脏腑经络、病机诊法、治则方药，与命部同属五术体系中的重要分支。\n"
    return fm + "\n" + body


def split_by_pattern(text, pattern, skip_before_first=True):
    """按正则模式切分文本，返回 [(title, content), ...]"""
    matches = list(re.finditer(pattern, text, re.M))
    entries = []
    for i, m in enumerate(matches):
        title = m.group(0).strip().lstrip("○").strip()
        start = m.end()
        end = matches[i + 1].start() if i + 1 < len(matches) else len(text)
        content = text[start:end].strip()
        if len(content) > 20:
            entries.append((title, content))
    return entries


def parse_suwen(path):
    """素问：按 ○XXX篇第X 切分（行首可有全角空格）"""
    text = open(path, encoding="utf-8").read()
    return split_by_pattern(text, r"^　*○.*篇第[一二三四五六七八九十]+")


def parse_lingshu(path):
    """灵枢：按 XXX第X 切分（跳过目录，从正文开始；放宽标题长度到20字）"""
    text = open(path, encoding="utf-8").read()
    # 找到第二个"九针十二原第一"（正文开始处），跳过目录
    first = text.find("九针十二原第一")
    if first >= 0:
        second = text.find("九针十二原第一", first + 1)
        if second >= 0:
            text = text[second:]
    return split_by_pattern(text, r"^　*[\u4e00-\u9fff]{2,20}第[一二三四五六七八九十百]+(?:法[天地人时空音律星民野])?　*$")


def parse_nanjing(path):
    """难经：按 X难 切分"""
    text = open(path, encoding="utf-8").read()
    return split_by_pattern(text, r"^　*[一二三四五六七八九十百]+难\s*$")


def parse_shanghan(path):
    """伤寒论：按 辨XXX病脉证并治 切分"""
    text = open(path, encoding="utf-8").read()
    return split_by_pattern(text, r"^　*辨[\u4e00-\u9fff]{2,15}病脉证并治[\u4e00-\u9fff]*")


def parse_shennong(path):
    """神农本草经：按部类+药名切分。
    部类标题：玉石部上品/草部上品等（单独一行）
    药物条目：药名\\ue5d9正文（同一行，PUA字符分隔）
    """
    lines = open(path, encoding="utf-8").readlines()
    entries = []
    current_category = ""
    PUA = "\ue5d9"

    category_pattern = re.compile(r"^(玉石|草|木|兽|虫鱼|果|米谷|菜)部(上|中|下)品$")

    for line in lines:
        stripped = line.strip()
        if not stripped:
            continue
        # 部类标题
        cat_match = category_pattern.match(stripped)
        if cat_match:
            current_category = stripped
            continue
        # 跳过序文（在第一个部类之前）
        if not current_category:
            continue
        # 药物条目：包含 PUA 分隔符
        if PUA in stripped:
            parts = stripped.split(PUA, 1)
            drug_name = parts[0].strip()
            drug_text = parts[1].strip()
            if drug_name and len(drug_name) <= 8:
                entries.append((f"{current_category}·{drug_name}", f"{drug_name}：{drug_text}"))
        # 无 PUA 的行可能是序文/目录，跳过
    return entries


BOOKS = [
    ("suwen", "黄帝内经素问", "重广补注本·唐王冰注·宋林亿校", "raw/suwen.txt", parse_suwen, 3),
    ("lingshu", "灵枢经", "四库全书本", "raw/lingshu.txt", parse_lingshu, 3),
    ("nanjing", "八十一难经", "旧题扁鹊·四库全书本", "raw/nanjing.txt", parse_nanjing, 3),
    ("shanghan", "伤寒论", "汉张仲景·通行本", "raw/shanghan.txt", parse_shanghan, 4),
    ("shennong", "神农本草经", "四库全书本", "raw/shennong.txt", parse_shennong, 3),
]


def main():
    total = 0
    for book_slug, book_name, version, src_rel, parse_func, weight in BOOKS:
        src = os.path.join(BASE, src_rel)
        out_dir = os.path.join(BASE, "library", "yi", "jingdian", book_slug)
        os.makedirs(out_dir, exist_ok=True)
        entries = parse_func(src)
        for idx, (chapter, text) in enumerate(entries):
            content = write_entry(book_slug, book_name, version, chapter, text, idx, weight)
            with open(os.path.join(out_dir, f"yd_{book_slug}_{idx:03d}.md"), "w",
                      encoding="utf-8", newline="\n") as f:
                f.write(content)
        total += len(entries)
        print(f"  {book_name}: {len(entries)} 条 → {out_dir}")
    print(f"医部经典入库完成：{total} 条")


if __name__ == "__main__":
    main()
