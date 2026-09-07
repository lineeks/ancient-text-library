# -*- coding: utf-8 -*-
"""
卜部第五批·奇门遁甲秘笈大全解析脚本（纯标准库，确定性输出）

底本：raw/qimen-dunjia-miji.txt（garychowcmu/daizhigev20 易藏/术数）
  393KB / 6340行 / 13.6万字，题明刘基（伯温）辑
切分：按「卷X」分卷跟踪，按短行篇章标题切分（烟波钓叟歌/奇门总要诀/
  阳遁九宫起例/天蓬星/开门克应/静应/动应 等），约100+条
元数据：category=bu, subcategory=qimen, type=chapter, conditions 八键全空
召回：keywords 驱动（奇门/遁甲/九星/八门/三奇/六仪/阴阳遁/九宫/
  天盘地盘/直符直使/克应/格局/神煞/方位/占断 等）
用法：python -X utf8 scripts/parse_bu5.py
"""
import os
import re

BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def extract_keywords(text):
    kws = ["奇门遁甲", "卜部", "奇门"]
    mapping = [
        (r"烟波钓叟|钓叟歌", "烟波钓叟歌"),
        (r"九星|天蓬|天芮|天冲|天辅|天禽|天心|天柱|天任|天英", "九星"),
        (r"八门|开门|休门|生门|伤门|杜门|景门|死门|惊门", "八门"),
        (r"三奇|乙奇|丙奇|丁奇|六仪|戊己庚辛壬癸", "三奇六仪"),
        (r"阳遁|阴遁|九宫起例|起例|置闰|超神|接气", "阴阳遁起例"),
        (r"直符|值符|直使|值使|天盘|地盘|人盘|神盘", "直符直使"),
        (r"克应|十干克应|八门克应|三奇到宫|静应|动应", "克应"),
        (r"格局|青龙|朱雀|白虎|玄武|勾陈|螣蛇|九地|九天", "格局神煞"),
        (r"九宫|坎宫|离宫|震宫|兑宫|坤宫|艮宫|巽宫|中宫", "九宫"),
        (r"方位|喜神|贵人|日禄|旬空|纳甲|合化|墓库", "方位神煞"),
        (r"占断|占法|预测|吉凶|应验", "占断"),
        (r"十二神|黄黑道|月例|时例|神将", "十二神"),
        (r"遁甲|奇门|符头|节气|三元|上中下元", "遁甲基础"),
    ]
    for pattern, kw in mapping:
        if re.search(pattern, text):
            kws.append(kw)
    return list(dict.fromkeys(kws))


def is_title(line):
    """判断是否为篇章标题行：短行（2-15字）、无标点、含中文、非卷标题"""
    s = line.strip()
    if not s or len(s) < 2 or len(s) > 15:
        return False
    if re.search(r'[，。、；：！？""''（）]', s):
        return False
    if not re.search(r'[\u4e00-\u9fff]', s):
        return False
    # 排除卷标题
    if re.match(r'^卷[一二三四五六七八九十]+$', s):
        return False
    # 排除作者/日期行
    if '谨识' in s or '岁次' in s or '氏' in s and len(s) <= 10:
        return False
    return True


def main():
    src = os.path.join(BASE, "raw/qimen-dunjia-miji.txt")
    out_dir = os.path.join(BASE, "library", "bu", "qimen", "qimen-dunjia-miji")
    os.makedirs(out_dir, exist_ok=True)

    text = open(src, encoding="utf-8").read()
    lines = text.split("\n")

    # 找到正文开始（跳过总序，从卷一开始）
    start = 0
    for i, line in enumerate(lines):
        if line.strip() == "卷一":
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
        if re.match(r'^卷[一二三四五六七八九十]+$', s):
            if current_title and current_content:
                raw_entries.append((current_juan, current_title, "\n".join(current_content).strip()))
            current_juan = s
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
            # 合并到上一条
            pj, pt, pc = entries[-1]
            entries[-1] = (pj, pt + "·" + title, pc + "\n\n" + content)
        else:
            entries.append((juan, title, content))

    # 写入文件
    for idx, (juan, title, content) in enumerate(entries):
        eid = f"bu5_qimen_{idx:03d}"
        kws = extract_keywords(title + content[:2000])
        tags = ["卜部", "奇门遁甲"]
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
book: "奇门遁甲秘笈大全"
chapter: "{juan}"
section_title: "{title[:25]}"
source_version: "明刘基辑·通行本"
author: "刘基"
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
        body += f"**【白话提要】**\n此条出自《奇门遁甲秘笈大全》「{juan}·{title}」，为奇门遁甲经典原文。奇门遁甲以九宫八卦为框架，排布九星八门三奇六仪，分阴阳二遁一百八十局，审天盘地盘之生克，定直符直使之吉凶，为古代兵占与方位选择之集大成术数。\n"
        with open(os.path.join(out_dir, f"bu5_qimen_{idx:03d}.md"), "w",
                  encoding="utf-8", newline="\n") as f:
            f.write(fm + "\n" + body)

    print(f"  奇门遁甲秘笈大全: {len(entries)} 条 → {out_dir}")


if __name__ == "__main__":
    main()
