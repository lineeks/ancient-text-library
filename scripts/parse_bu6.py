# -*- coding: utf-8 -*-
"""
卜部第六批·六壬大全解析脚本（纯标准库，确定性输出）

底本：raw/liuren-daquan.txt（garychowcmu/daizhigev20 易藏/术数）
  836KB / 7017行 / 29万字，四库全书本，不著撰人名氏，明郭载騋校
切分：按「六壬大全巻X  主题」分卷跟踪，按短行篇章标题切分
  （入手法/十干寄宫/神煞/天将/十二天将/课经/毕法赋 等），
  严格过滤神煞表格行（纯天干地支序列、空格分隔多组数据）
元数据：category=bu, subcategory=liuren, type=chapter, conditions 八键全空
召回：keywords 驱动（六壬/三式/四课/三传/天将/十二天将/课体/
  毕法赋/神煞/月将/占断/贼克/比用/涉害/遥克/昴星/别责/八专/伏吟/返吟 等）
用法：python -X utf8 scripts/parse_bu6.py
"""
import os
import re

BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def extract_keywords(text):
    kws = ["大六壬", "卜部", "六壬", "三式"]
    mapping = [
        (r"四课|三传|初传|中传|末传|发用", "四课三传"),
        (r"天将|十二天将|贵人|螣蛇|朱雀|六合|勾陈|青龙|天空|白虎|太常|玄武|天后", "十二天将"),
        (r"月将|登明|河魁|从魁|传送|小吉|胜光|太乙|天罡|太冲|功曹|大吉", "月将"),
        (r"贼克|比用|涉害|遥克|昴星|别责|八专|伏吟|返吟|元首|重审|知一", "九宗门"),
        (r"课体|课经|六十四课", "课体"),
        (r"毕法赋|毕法|一百二十法", "毕法赋"),
        (r"神煞|岁神煞|月神煞|日神煞|时神煞|天乙贵人|驿马|桃花|华盖|将星", "神煞"),
        (r"占断|占法|预测|吉凶|应验|分类占", "占断"),
        (r"入手法|起例|十干寄宫|天地盘|天盘|地盘|演局|起课", "起例"),
        (r"五行|生克|旺衰|休囚|十二长生|沐浴|冠带|临官|帝旺", "五行旺衰"),
        (r"六亲|父母|兄弟|妻财|子孙|官鬼", "六亲"),
        (r"冲合|刑害|三合|六合|六冲|三刑|六害", "冲合刑害"),
        (r"遁甲|太乙|三式", "三式"),
    ]
    for pattern, kw in mapping:
        if re.search(pattern, text):
            kws.append(kw)
    return list(dict.fromkeys(kws))


def is_title(line):
    """判断是否为篇章标题行：严格过滤神煞表格行"""
    s = line.strip()
    if not s or len(s) < 3 or len(s) > 20:
        return False
    # 必须纯中文（不含空格、制表符、阿拉伯数字、标点）
    if re.search(r'[\s\t0-9，。、；：！？""''（）《》·]', s):
        return False
    # 不含中文
    if not re.search(r'[\u4e00-\u9fff]', s):
        return False
    # 排除卷标题（单独处理）
    if re.match(r'^六壬大全巻[一二三四五六七八九十]+', s):
        return False
    # 排除以数字编号开头的子标题（如"一贼克法""二比用法"）
    if re.match(r'^[一二三四五六七八九十]+', s) and len(s) <= 4:
        return False
    # 排除纯天干/地支序列（含变体如"戊巳"）
    if re.match(r'^[甲乙丙丁戊己巳庚辛壬癸子丑寅卯辰巳午未申酉戌亥]+$', s):
        return False
    # 排除天干+数字/量词模式（如"甲五""乙三""庚四"）
    if re.search(r'[甲乙丙丁戊己庚辛壬癸][一二三四五六七八九十]$', s):
        return False
    # 排除含"占""用""顺""逆"等说明的表格行
    if re.search(r'(占行人|顺六阳|顺十二|三轮|前五辰|前执|岁前|岁后)', s):
        return False
    # 排除作者/日期/校官行
    if '总纂' in s or '总校' in s or '干隆' in s or '臣纪' in s:
        return False
    if s in ['提    要', '钦定四库全书', '《六壬大全》术数类四']:
        return False
    return True


def main():
    src = os.path.join(BASE, "raw/liuren-daquan.txt")
    out_dir = os.path.join(BASE, "library", "bu", "liuren", "liuren-daquan")
    os.makedirs(out_dir, exist_ok=True)

    text = open(src, encoding="utf-8").read()
    lines = text.split("\n")

    # 找到正文开始（跳过提要，从卷一开始）
    start = 0
    for i, line in enumerate(lines):
        if re.match(r'^六壬大全巻[一二三四五六七八九十]+', line.strip()):
            start = i
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
        juan_match = re.match(r'^六壬大全巻([一二三四五六七八九十]+)\s*(.*)$', s)
        if juan_match:
            if current_title and current_content:
                raw_entries.append((current_juan, current_title, "\n".join(current_content).strip()))
            juan_num = juan_match.group(1)
            juan_theme = juan_match.group(2).strip()
            current_juan = f"卷{juan_num}" + (f"·{juan_theme}" if juan_theme else "")
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

    # 合并过短条目（<80字）到上一条
    entries = []
    for juan, title, content in raw_entries:
        if len(content) < 80 and entries:
            pj, pt, pc = entries[-1]
            entries[-1] = (pj, pt + "·" + title, pc + "\n\n" + content)
        else:
            entries.append((juan, title, content))

    # 写入文件
    for idx, (juan, title, content) in enumerate(entries):
        eid = f"bu6_liuren_{idx:03d}"
        kws = extract_keywords(title + content[:2000])
        tags = ["卜部", "大六壬"]
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
book: "六壬大全"
chapter: "{juan}"
section_title: "{title[:25]}"
source_version: "四库全书本·明郭载騋校"
author: "佚名"
dynasty: "明"
type: "chapter"
conditions:
{cond}
weight: 4
tags: [{tags_str}]
---
"""
        body = f"### {title}\n\n"
        body += f"**【原文】**\n{content}\n\n"
        body += f"**【白话提要】**\n此条出自《六壬大全》「{juan}·{title}」，为大六壬经典原文。大六壬与奇门遁甲、太乙神数并称「三式」，以月将加时起天盘，四课三传发用，排布十二天将，审五行生克旺衰，定吉凶祸福，为古代占验术数中最古奥精密之学。\n"
        with open(os.path.join(out_dir, f"bu6_liuren_{idx:03d}.md"), "w",
                  encoding="utf-8", newline="\n") as f:
            f.write(fm + "\n" + body)

    print(f"  六壬大全: {len(entries)} 条 → {out_dir}")


if __name__ == "__main__":
    main()
