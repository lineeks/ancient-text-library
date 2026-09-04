# -*- coding: utf-8 -*-
"""
《李虚中命书》结构化入库脚本（纯标准库，确定性输出）

底本：GitHub garychowcmu/daizhigev20 易藏·术数·李虚中命书.txt（四库全书本）
旧题鬼谷子撰，唐李虚中注。三柱古法（年月日）纳音论命代表作。

切分策略：
  1. 六十甲子纳音论命（卷上）：60 条，type=nayin，conditions.day_pillar 精确锚定
  2. 卷上贵神/天乙/贵合等论述：按段落切分，type=chapter，shensha/keywords 索引
  3. 卷中（通理物化/真假邪正/升降清浊）：按段落切分，type=chapter，keywords 索引
  4. 卷下（衰旺取时/三元九限/天承地禄/水土名用）：按段落切分，type=chapter

输出：extended/lxzmingshu/*.md（第三梯队扩展，weight=3）
用法：python -X utf8 scripts/parse_lxzmingshu.py
"""
import os
import re

BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SRC = os.path.join(BASE, "raw", "lxzmingshu.txt")
OUT_DIR = os.path.join(BASE, "extended", "lxzmingshu")

# 六十甲子（按顺序）
JIAZI = [
    "甲子", "乙丑", "丙寅", "丁卯", "戊辰", "己巳", "庚午", "辛未", "壬申", "癸酉",
    "甲戌", "乙亥", "丙子", "丁丑", "戊寅", "己卯", "庚辰", "辛巳", "壬午", "癸未",
    "甲申", "乙酉", "丙戌", "丁亥", "戊子", "己丑", "庚寅", "辛卯", "壬辰", "癸巳",
    "甲午", "乙未", "丙申", "丁酉", "戊戌", "己亥", "庚子", "辛丑", "壬寅", "癸卯",
    "甲辰", "乙巳", "丙午", "丁未", "戊申", "己酉", "庚戌", "辛亥", "壬子", "癸丑",
    "甲寅", "乙卯", "丙辰", "丁巳", "戊午", "己未", "庚申", "辛酉", "壬戌", "癸亥",
]

# 卷/主题标记
SECTION_MARKERS = {
    "通理物化": "卷中·通理物化",
    "真假邪正": "卷中·真假邪正",
    "升降清浊": "卷中·升降清浊",
    "衰旺取时": "卷下·衰旺取时",
    "三元九限": "卷下·三元九限",
    "天承地禄": "卷下·天承地禄",
    "水土名用": "卷下·水土名用",
}


def clean_line(line):
    """去除行首空白和末尾空白。"""
    return line.strip()


def parse_sixty_jiazi(lines):
    """从卷上提取六十甲子纳音论命条目。
    返回 {jiazi: text}，text 为完整论述（含括号注）。
    """
    entries = {}
    current = None
    buf = []
    for line in lines:
        s = clean_line(line)
        if not s:
            continue
        # 检测六十甲子开头（如"甲子天官藏"、"乙丑禄官承"）
        matched = None
        for jz in JIAZI:
            if s.startswith(jz) and len(s) > len(jz) + 1:
                # 确保后面跟的是论述（不是"甲子己丑"这种组合）
                rest = s[len(jz):]
                if rest[0] not in "甲乙丙丁戊己庚辛壬癸子丑寅卯辰巳午未申酉戌亥":
                    matched = jz
                    break
        if matched:
            if current:
                entries[current] = "\n".join(buf).strip()
            current = matched
            buf = [s]
        elif current:
            # 六十甲子段结束于"此六十位五行支干相乘"（总论开始）
            if s.startswith("此六十位"):
                entries[current] = "\n".join(buf).strip()
                current = None
                buf = []
                break
            else:
                buf.append(s)
    if current and current not in entries:
        entries[current] = "\n".join(buf).strip()
    return entries


def split_by_topic(lines, start_idx, end_idx, default_chapter):
    """按主题标记切分，返回 [(chapter, section_title, text), ...]。
    主题标记行（如"通理物化"）作为章节分界，该主题下所有非空行合并为一个条目。
    """
    results = []
    current_chapter = default_chapter
    buf = []
    for i in range(start_idx, end_idx):
        s = clean_line(lines[i])
        if not s:
            continue
        # 检测主题标记（短行，4字以内，且在标记表中）
        is_marker = False
        for marker, chap in SECTION_MARKERS.items():
            if s == marker or (s.startswith(marker) and len(s) <= len(marker) + 2):
                if buf:
                    results.append((current_chapter, buf[0][:14].replace("\n", ""), "\n".join(buf).strip()))
                    buf = []
                current_chapter = chap
                is_marker = True
                break
        if not is_marker:
            buf.append(s)
    if buf:
        results.append((current_chapter, buf[0][:14].replace("\n", ""), "\n".join(buf).strip()))
    return results


def make_id(prefix, idx):
    return f"lxz_{prefix}_{idx:03d}"


def write_entry(eid, book, chapter, section_title, stype, conditions, weight, tags, original, annotation="", vernacular=""):
    """生成单个 Markdown 条目。"""
    cond_lines = []
    for k in ["day_master", "month_branch", "day_pillar", "hour_pillar",
              "ten_god", "pattern", "shensha", "keywords"]:
        vals = conditions.get(k, [])
        if vals:
            quoted = ", ".join(f'"{v}"' for v in vals)
            cond_lines.append(f"  {k}: [{quoted}]")
        else:
            cond_lines.append(f"  {k}: []")
    cond_str = "\n".join(cond_lines)
    tags_str = ", ".join(f'"{t}"' for t in tags) if tags else ""

    body = f"### {section_title}\n\n"
    body += f"**【原文】**\n{original}\n\n"
    if annotation:
        body += f"**【古注】**\n{annotation}\n\n"
    body += f"**【白话提要】**\n{vernacular}\n"

    fm = f"""---
id: "{eid}"
book: "{book}"
chapter: "{chapter}"
section_title: "{section_title}"
source_version: "四库全书本（旧题鬼谷子撰，唐李虚中注）"
author: "李虚中（注）"
dynasty: "唐（托名周·鬼谷子）"
type: "{stype}"
conditions:
{cond_str}
weight: {weight}
tags: [{tags_str}]
---
"""
    return fm + "\n" + body


def infer_conditions_for_paragraph(text, chapter):
    """根据段落内容推断 conditions（shensha/keywords）。"""
    shensha = []
    keywords = []
    if "天乙贵人" in text or "天乙贵神" in text:
        shensha.append("天乙贵人")
    if "羊刃" in text:
        shensha.append("羊刃")
    if "华盖" in text:
        shensha.append("华盖")
    if "驿马" in text or "禄马" in text:
        shensha.append("驿马")
    if "空亡" in text:
        shensha.append("空亡")
    if "三奇" in text:
        shensha.append("三奇贵人")
    if "天月德" in text or "天德" in text or "月德" in text:
        shensha.append("天月二德")
    if "魁罡" in text:
        shensha.append("魁罡")
    if "孤辰" in text:
        shensha.append("孤辰")
    if "寡宿" in text:
        shensha.append("寡宿")
    if "元辰" in text:
        shensha.append("元辰")
    if "六厄" in text:
        shensha.append("六厄")

    # keywords
    if "纳音" in text:
        keywords.append("纳音")
    if "三元" in text:
        keywords.append("三元")
    if "四柱" in text:
        keywords.append("四柱")
    if "小运" in text or "大运" in text:
        keywords.append("大运小运")
    if "衰旺" in text or "旺衰" in text:
        keywords.append("衰旺")
    if "轻重" in text:
        keywords.append("五行轻重")
    if "性情" in text or "情性" in text:
        keywords.append("性情")
    if "富贵" in text:
        keywords.append("富贵")
    if "贫贱" in text:
        keywords.append("贫贱")
    if "神煞" in text:
        keywords.append("神煞")
    if "干禄" in text:
        keywords.append("干禄")
    if "支命" in text:
        keywords.append("支命")
    if "六合" in text:
        keywords.append("六合")
    if "三合" in text:
        keywords.append("三合")
    if "刑冲" in text or "刑害" in text:
        keywords.append("刑冲")
    if "德合" in text:
        keywords.append("德合")
    if "贵合" in text:
        keywords.append("贵合")
    if "贵食" in text:
        keywords.append("贵食")
    if "胎月" in text or "胎元" in text:
        keywords.append("胎元")
    if "九限" in text or "运限" in text:
        keywords.append("运限")
    if "神头禄" in text:
        keywords.append("神头禄")

    # 去重保序
    shensha = list(dict.fromkeys(shensha))
    keywords = list(dict.fromkeys(keywords))
    return {"shensha": shensha, "keywords": keywords}


def main():
    os.makedirs(OUT_DIR, exist_ok=True)
    with open(SRC, encoding="utf-8") as f:
        lines = f.readlines()

    # 找到三卷分界
    juan_shang = next(i for i, l in enumerate(lines) if "李虚中命书卷上" in l)
    juan_zhong = next(i for i, l in enumerate(lines) if "李虚中命书卷中" in l)
    juan_xia = next(i for i, l in enumerate(lines) if "李虚中命书卷下" in l)

    written = 0

    # === 1. 六十甲子纳音论命（卷上） ===
    jiazi_entries = parse_sixty_jiazi(lines[juan_shang:juan_zhong])
    for idx, jz in enumerate(JIAZI):
        if jz not in jiazi_entries:
            print(f"  警告：未找到 {jz}")
            continue
        text = jiazi_entries[jz]
        eid = f"lxz_nayin_{jz}"
        conditions = {"day_pillar": [jz], "keywords": ["纳音", "六十甲子", jz]}
        tags = ["纳音论命", "六十甲子", "三柱古法"]
        content = write_entry(
            eid, "李虚中命书", "卷上·六十甲子纳音", f"{jz}纳音论命",
            "nayin", conditions, 4, tags, text,
            vernacular=f"此条以{jz}纳音为核心，论述该日柱的五行体性、喜忌与贵贱格局。李虚中古法以年月日三柱纳音论命，不涉时柱，与后世子平八字取用神法不同。"
        )
        with open(os.path.join(OUT_DIR, f"{eid}.md"), "w", encoding="utf-8", newline="\n") as f:
            f.write(content)
        written += 1

    # === 2. 卷上论述（六十甲子之后到卷中之前） ===
    # 找到"此六十位"开始的位置
    shang_start = None
    for i in range(juan_shang, juan_zhong):
        if clean_line(lines[i]).startswith("此六十位"):
            shang_start = i
            break
    if shang_start:
        topics = split_by_topic(lines, shang_start, juan_zhong, "卷上·贵神总论")
        for idx, (chapter, title, text) in enumerate(topics):
            if len(text) < 15:
                continue
            eid = make_id("shang", idx)
            cond = infer_conditions_for_paragraph(text, chapter)
            cond["keywords"] = list(dict.fromkeys(cond["keywords"] + ["贵神", "天乙贵人", "三柱古法"]))
            tags = ["贵神", "天乙贵人", "三柱古法"]
            content = write_entry(
                eid, "李虚中命书", chapter, title,
                "chapter", cond, 3, tags, text,
                vernacular="此段论述卷上贵神体系，包括本家贵人、天乙贵人、贵合贵食等，为三柱古法神煞论的重要文献。"
            )
            with open(os.path.join(OUT_DIR, f"{eid}.md"), "w", encoding="utf-8", newline="\n") as f:
                f.write(content)
            written += 1

    # === 3. 卷中论述 ===
    topics_zhong = split_by_topic(lines, juan_zhong + 1, juan_xia, "卷中·通理物化")
    for idx, (chapter, title, text) in enumerate(topics_zhong):
        if len(text) < 10:
            continue
        eid = make_id("zhong", idx)
        cond = infer_conditions_for_paragraph(text, chapter)
        cond["keywords"] = list(dict.fromkeys(cond["keywords"] + ["五行理论", "干支纳音", "三柱古法"]))
        tags = ["五行理论", "干支纳音", "三柱古法"]
        content = write_entry(
            eid, "李虚中命书", chapter, title,
            "chapter", cond, 3, tags, text,
            vernacular=f"此段出自《李虚中命书》{chapter}，论述五行干支纳音的基本理论与论命方法，为三柱古法的理论基础。"
        )
        with open(os.path.join(OUT_DIR, f"{eid}.md"), "w", encoding="utf-8", newline="\n") as f:
            f.write(content)
        written += 1

    # === 4. 卷下论述 ===
    topics_xia = split_by_topic(lines, juan_xia + 1, len(lines), "卷下·衰旺取时")
    for idx, (chapter, title, text) in enumerate(topics_xia):
        if len(text) < 10:
            continue
        eid = make_id("xia", idx)
        cond = infer_conditions_for_paragraph(text, chapter)
        cond["keywords"] = list(dict.fromkeys(cond["keywords"] + ["衰旺", "运限", "三柱古法"]))
        tags = ["衰旺取时", "运限", "三柱古法"]
        content = write_entry(
            eid, "李虚中命书", chapter, title,
            "chapter", cond, 3, tags, text,
            vernacular=f"此段出自《李虚中命书》{chapter}，论述五行衰旺、大运小运与吉凶应期，为三柱古法的实战方法。"
        )
        with open(os.path.join(OUT_DIR, f"{eid}.md"), "w", encoding="utf-8", newline="\n") as f:
            f.write(content)
        written += 1

    print(f"李虚中命书入库完成：{written} 条 → {OUT_DIR}")
    print(f"  六十甲子纳音：{len([f for f in os.listdir(OUT_DIR) if 'nayin' in f])} 条")


if __name__ == "__main__":
    main()
