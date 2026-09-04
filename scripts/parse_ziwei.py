# -*- coding: utf-8 -*-
"""
紫微斗数典籍入库脚本（纯标准库，确定性输出）

底本：GitHub itstack-org/ziwei-doushu 仓库 lib/classics/data/ 下的结构化数据
  - quanshu.ts  《紫微斗数全书》（明罗洪先编，核心精选）
  - quanji.ts   《紫微斗数全集》（清代古本，核心精选）
  - gusuifu.ts  《斗数骨髓赋》（紫微斗数核心歌诀）

切分策略：
  - 解析 TS 文件中的 chapters[].paragraphs[].text
  - 每个 paragraph 生成一个条目，type=chapter
  - conditions 八键全空（紫微斗数不依赖八字字段），keywords 驱动召回
  - category=ming, subcategory=ziwei（由路径自动推断）

输出：library/ming/ziwei/{quanshu,quanji,gusuifu}/*.md
用法：python -X utf8 scripts/parse_ziwei.py
"""
import os
import re

BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

BOOKS = [
    ("quanshu", "紫微斗数全书", "明·罗洪先编（核心精选）", "raw/ziwei_quanshu.ts"),
    ("quanji", "紫微斗数全集", "清代古本（核心精选）", "raw/ziwei_quanji.ts"),
    ("gusuifu", "斗数骨髓赋", "紫微斗数核心歌诀", "raw/ziwei_gusuifu.ts"),
]


def parse_ts(path):
    """解析 TS 文件，返回 [(chapter_title, paragraph_text), ...]
    逐字段解析：遇到 title: 开始新 chapter，遇到 text: 添加段落。
    不依赖 subtitle 字段（部分 chapter 无 subtitle）。
    """
    with open(path, encoding="utf-8") as f:
        text = f.read()
    results = []
    current_chapter = None
    # 匹配 title: '...'
    title_pattern = re.compile(r"title:\s*'((?:[^'\\]|\\.)*)'")
    # 匹配 text: '...'（跨行，非贪婪到下一个 ' ）
    text_pattern = re.compile(r"text:\s*'((?:[^'\\]|\\.)*)'", re.S)
    # 找到 chapters 数组的范围
    ch_start = text.find("chapters:")
    if ch_start < 0:
        return results
    # 从 chapters 开始逐字段扫描
    pos = ch_start
    while True:
        # 找下一个 title 或 text
        t_match = title_pattern.search(text, pos)
        if not t_match:
            break
        # 判断这个 title 是 chapter title 还是其他（chapter title 在 paragraphs 数组之外）
        # 简单策略：每个 title 后找最近的 text 集合，直到下一个 title
        chapter_title = t_match.group(1).replace("\\'", "'")
        next_title = title_pattern.search(text, t_match.end())
        end_pos = next_title.start() if next_title else len(text)
        # 在这个范围内找所有 text
        for tm in text_pattern.finditer(text, t_match.end(), end_pos):
            para_text = tm.group(1).replace("\\'", "'").replace("\\n", "\n")
            results.append((chapter_title, para_text))
        pos = t_match.end()
    return results


def extract_keywords(chapter, text):
    """从章节标题和文本中提取紫微斗数关键词。"""
    kws = ["紫微斗数"]
    combined = chapter + text
    mapping = [
        ("命宫", "命宫"),
        ("兄弟宫", "兄弟宫"),
        ("夫妻宫|配偶|婚姻", "夫妻宫"),
        ("子女宫", "子女宫"),
        ("财帛宫|财运|财富", "财帛宫"),
        ("疾厄宫|健康|疾病", "疾厄宫"),
        ("迁移宫|外出|远行", "迁移宫"),
        ("交友宫|朋友|人际", "交友宫"),
        ("官禄宫|事业|官禄", "官禄宫"),
        ("田宅宫|房产|家宅", "田宅宫"),
        ("福德宫|福气|精神", "福德宫"),
        ("父母宫|父母|长辈", "父母宫"),
        ("十二宫", "十二宫"),
        ("四化|化禄|化权|化科|化忌", "四化"),
        ("紫微", "紫微星"),
        ("天机", "天机星"),
        ("太阳", "太阳星"),
        ("武曲", "武曲星"),
        ("天同", "天同星"),
        ("廉贞", "廉贞星"),
        ("天府", "天府星"),
        ("太阴", "太阴星"),
        ("贪狼", "贪狼星"),
        ("巨门", "巨门星"),
        ("天相", "天相星"),
        ("天梁", "天梁星"),
        ("七杀", "七杀星"),
        ("破军", "破军星"),
        ("文昌|文曲", "昌曲"),
        ("左辅|右弼", "辅弼"),
        ("擎羊|陀罗", "羊陀"),
        ("火星|铃星", "火铃"),
        ("地空|地劫", "空劫"),
        ("天魁|天钺", "魁钺"),
        ("禄存", "禄存"),
        ("天马", "天马"),
        ("庙旺|落陷|庙|旺|陷", "庙旺落陷"),
        ("三方四正|会照|对照", "三方四正"),
        ("大限|小限|流年", "大限流年"),
        ("格局", "格局"),
        ("主星", "主星"),
        ("辅星|煞星", "辅煞星"),
    ]
    for pattern, kw in mapping:
        if re.search(pattern, combined):
            kws.append(kw)
    return list(dict.fromkeys(kws))


def write_entry(book_slug, book_name, version, chapter, text, idx):
    eid = f"zw_{book_slug}_{idx:03d}"
    kws = extract_keywords(chapter, text)
    tags = ["紫微斗数", book_name]
    title = text[:14].replace("\n", "")
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
type: "chapter"
conditions:
{cond}
weight: 3
tags: [{tags_str}]
---
"""
    body = f"### {title}\n\n"
    body += f"**【原文】**\n{text}\n\n"
    body += f"**【白话提要】**\n此条出自《{book_name}》「{chapter}」，为紫微斗数原文。紫微斗数以出生时辰排十二宫，以星曜庙旺落陷与四化论命，与子平八字同为命部重要体系。\n"
    return fm + "\n" + body


def main():
    total = 0
    for book_slug, book_name, version, src_rel in BOOKS:
        src = os.path.join(BASE, src_rel)
        out_dir = os.path.join(BASE, "library", "ming", "ziwei", book_slug)
        os.makedirs(out_dir, exist_ok=True)
        pairs = parse_ts(src)
        for idx, (chapter, text) in enumerate(pairs):
            content = write_entry(book_slug, book_name, version, chapter, text, idx)
            with open(os.path.join(out_dir, f"zw_{book_slug}_{idx:03d}.md"), "w",
                      encoding="utf-8", newline="\n") as f:
                f.write(content)
        total += len(pairs)
        print(f"  {book_name}: {len(pairs)} 条 → {out_dir}")
    print(f"紫微斗数典籍入库完成：{total} 条")


if __name__ == "__main__":
    main()
