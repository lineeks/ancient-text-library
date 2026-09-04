# -*- coding: utf-8 -*-
"""
星学大成入库脚本（纯标准库，确定性输出）

底本：garychowcmu/daizhigev20 GitHub 仓库 raw/xingxuedacheng.txt
  明万民英撰，四库全书本，三十卷，七政四余（五星禄命）集大成之作。

切分策略：
  - 按"星学大成卷X"作为卷边界，共30卷
  - 跳过四库提要、原序、分页标记（<子部,...>）
  - 每卷作为一个条目，type=chapter
  - conditions 八键全空（七政四余不依赖八字字段），keywords 驱动召回
  - category=ming, subcategory=qizheng（由路径自动推断）

输出：library/ming/qizheng/xingxuedacheng/*.md
用法：python -X utf8 scripts/parse_xingxuedacheng.py
"""
import os
import re

BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def extract_keywords(text):
    """从文本中提取七政四余关键词。"""
    kws = ["七政四余", "星命"]
    mapping = [
        ("星曜|五星|七政", "星曜"),
        ("太阳|日星", "太阳"),
        ("太阴|月星", "太阴"),
        ("木星|岁星", "木星"),
        ("火星|荧惑", "火星"),
        ("土星|镇星", "土星"),
        ("金星|太白", "金星"),
        ("水星|辰星", "水星"),
        ("罗睺|计都|紫气|月孛", "四余"),
        ("宫度|十二宫|宫位", "宫度"),
        ("命宫|身宫", "命宫身宫"),
        ("庙旺|落陷|庙|乐|旺|陷", "庙旺落陷"),
        ("限运|大限|小限|流年", "限运"),
        ("格局", "格局"),
        ("神煞", "神煞"),
        ("天乙贵人|天乙", "天乙贵人"),
        ("文昌", "文昌"),
        ("驿马", "驿马"),
        ("羊刃|阳刃", "羊刃"),
        ("空亡", "空亡"),
        ("纳音", "纳音"),
        ("五行", "五行"),
        ("天干|地支", "天干地支"),
        ("四柱|年月日时", "四柱"),
        ("胎元", "胎元"),
        ("生旺|死绝|墓库", "生旺死绝"),
        ("刑冲|合害", "刑冲合害"),
        ("贵贱|吉凶|寿夭|祸福", "贵贱吉凶"),
        ("星曜图例", "星曜图例"),
        ("观星节要", "观星节要"),
        ("诸家限例|琴堂虚实", "诸家限例"),
        ("耶律秘诀", "耶律秘诀"),
        ("三辰通载|仙城望斗", "三辰通载"),
        ("总龟|紫府|星经", "星经杂著"),
        ("碧玉真经|邓史|乔拗", "碧玉真经"),
        ("光矞渊微|星曜格局", "星曜格局"),
        ("果老|星宗", "果老星宗"),
    ]
    for pattern, kw in mapping:
        if re.search(pattern, text):
            kws.append(kw)
    return list(dict.fromkeys(kws))


def parse_xingxue(path):
    """解析星学大成：按"星学大成卷X"切分30卷。
    返回 [(juan_title, text), ...]
    """
    with open(path, encoding="utf-8") as f:
        content = f.read()
    # 找到第一卷开始
    first = content.find("星学大成卷一")
    if first < 0:
        return []
    body = content[first:]
    # 按"星学大成卷X"切分
    pattern = re.compile(r"星学大成卷([一二三四五六七八九十]+)")
    matches = list(pattern.finditer(body))
    entries = []
    for i, m in enumerate(matches):
        juan_num = m.group(1)
        start = m.end()
        end = matches[i + 1].start() if i + 1 < len(matches) else len(body)
        text = body[start:end]
        # 清理分页标记
        text = re.sub(r"<子部,术数类,命书相书之属,星学大成,卷[一二三四五六七八九十]+>", "", text)
        # 清理多余空行
        text = re.sub(r"\n{3,}", "\n\n", text)
        text = text.strip()
        if len(text) > 50:  # 跳过空卷
            entries.append((f"卷{juan_num}", text))
    return entries


def write_entry(juan_title, text, idx):
    eid = f"xxdc_juan_{idx:02d}"
    kws = extract_keywords(juan_title + text[:2000])
    tags = ["七政四余", "星学大成"]
    title = f"星学大成{juan_title}"
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
book: "星学大成"
chapter: "{juan_title}"
section_title: "{title}"
source_version: "明万民英撰·四库全书本"
author: "万民英"
dynasty: "明"
type: "chapter"
conditions:
{cond}
weight: 3
tags: [{tags_str}]
---
"""
    body = f"### {title}\n\n"
    body += f"**【原文】**\n{text}\n\n"
    body += f"**【白话提要】**\n此卷出自《星学大成》「{juan_title}」，为明代万民英编撰的七政四余（五星禄命）集大成之作，汇集星曜图例、观星节要、诸家限例、耶律秘诀、三辰通载等星家古法。七政四余以出生时日月五星四余躔度论命，与子平八字同为命部重要体系。\n"
    return fm + "\n" + body


def main():
    src = os.path.join(BASE, "raw", "xingxuedacheng.txt")
    out_dir = os.path.join(BASE, "library", "ming", "qizheng", "xingxuedacheng")
    os.makedirs(out_dir, exist_ok=True)
    entries = parse_xingxue(src)
    for idx, (juan_title, text) in enumerate(entries):
        content = write_entry(juan_title, text, idx)
        with open(os.path.join(out_dir, f"xxdc_juan_{idx:02d}.md"), "w",
                  encoding="utf-8", newline="\n") as f:
            f.write(content)
    print(f"星学大成入库完成：{len(entries)} 卷 → {out_dir}")


if __name__ == "__main__":
    main()
