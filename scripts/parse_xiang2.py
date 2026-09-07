# -*- coding: utf-8 -*-
"""
地相经典细分脚本（纯标准库，确定性输出）

将地相三部经典从整书1条细分为多篇章条目：
  - 撼龙经（含疑龙经+葬法倒杖）：按三部分+篇章标题切分，约15条
  - 葬书：按段落主题切分，约10条
  - 青囊奥语：太短（1330字），保持1条（不处理）

底本：raw/hanlongjing.txt, raw/zangshu.txt
输出：library/xiang/dixiang/hanlongjing/*.md, library/xiang/dixiang/zangshu/*.md

注意：运行前需先删除原有的整书1条 md 文件。
用法：python -X utf8 scripts/parse_xiang2.py
"""
import os
import re

BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def extract_keywords_hanlong(text):
    kws = ["撼龙经", "地相", "风水"]
    mapping = [
        (r"撼龙|疑龙|倒杖|葬法|杨筠松|杨公", "撼龙疑龙"),
        (r"贪狼|巨门|禄存|文曲|廉贞|武曲|破军|左辅|右弼|九星", "九星"),
        (r"龙|龙脉|龙势|龙形|干龙|枝龙|真龙|假龙", "龙法"),
        (r"穴|穴位|穴星|点穴|窝穴|钳穴|乳穴|突穴", "穴法"),
        (r"砂|青龙砂|白虎砂|朝砂|案砂|护砂", "砂法"),
        (r"水|水口|水城|朝水|去水|聚水|得水", "水法"),
        (r"倒杖|顺杖|逆杖|缩杖|离杖|没杖|穿杖|斗杖|截杖|对杖|缀杖|犯杖", "倒杖十二法"),
        (r"二十四砂|担凹|正葬|打开|悬棺|垒坟|浮葬|沉葬|吐葬", "二十四砂葬法"),
        (r"疑龙十问|抱养|公位|阳宅|阴宅|主客|形真假|花假|博换", "疑龙十问"),
        (r"卫龙|变星|分两仪|求四象|倍八卦", "理气"),
        (r"生气|乘气|藏风|界水|风水|峦头|理气", "风水基础"),
    ]
    for pattern, kw in mapping:
        if re.search(pattern, text):
            kws.append(kw)
    return list(dict.fromkeys(kws))


def extract_keywords_zangshu(text):
    kws = ["葬书", "地相", "风水"]
    mapping = [
        (r"生气|乘生气|五气|发而生乎万物", "生气论"),
        (r"气感|鬼福|铜山西崩|灵钟东应", "气感论"),
        (r"丘垅|冈阜|气之所随|支龙|垅龙", "龙法"),
        (r"气乘风则散|界水则止|聚之使不散|行之使有止|谓之风水", "风水定义"),
        (r"得水|藏风|得水为上|藏风次之", "藏风得水"),
        (r"乘金|贮水|乘风|则火|四灵|朱雀|玄武|青龙|白虎", "四灵乘气"),
        (r"乾流|坤流|阳龙|阴龙|阳基|阴基", "阴阳龙"),
        (r"穴|穴位|穴法|点穴|葬穴", "穴法"),
        (r"砂|朝砂|案砂|护砂|青龙|白虎|朱雀|玄武", "砂法"),
        (r"水|水口|朝水|去水|聚水|水城", "水法"),
        (r"龙脉|来龙|入首|束气|过峡|穿帐", "龙脉"),
        (r"明堂|小明堂|中明堂|大明堂|内明堂|外明堂", "明堂"),
        (r"风水|峦头|理气|堪舆|青乌|青囊", "风水基础"),
    ]
    for pattern, kw in mapping:
        if re.search(pattern, text):
            kws.append(kw)
    return list(dict.fromkeys(kws))


def write_entry(book_slug, book_name, version, chapter, section, text, idx, weight=4, kw_extractor=None):
    eid = f"xx2_{book_slug}_{idx:03d}"
    if kw_extractor:
        kws = kw_extractor(chapter + section + text[:2000])
    else:
        kws = [book_name, "地相", "风水"]
    tags = ["相部", book_name]
    title = section[:25].replace("\n", "")
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
author: "杨筠松"
dynasty: "唐"
type: "chapter"
conditions:
{cond}
weight: {weight}
tags: [{tags_str}]
---
"""
    body = f"### {title}\n\n"
    body += f"**【原文】**\n{text}\n\n"
    body += f"**【白话提要】**\n此条出自《{book_name}》「{chapter}·{section}」，为地相风水经典原文。地相之学以龙、穴、砂、水、向为核心，察龙脉之起止，辨穴位之真假，审砂水之环抱，定朝向之吉凶，为堪舆学之根本。\n"
    return fm + "\n" + body


def split_hanlong(text):
    """撼龙经（含疑龙经+葬法倒杖）：按三部分+篇章标题切分。
    返回 [(chapter, section, content), ...]
    """
    entries = []

    # 找到三部分的精确起始位置
    # 撼龙经正文："撼龙经　　唐　杨筠松　撰"（后面跟正文"须弥山"）
    m1 = re.search(r"撼龙经\s+唐\s+杨筠松\s+撰\s*须弥山", text)
    start1 = m1.start() if m1 else text.find("撼龙经", 200)

    # 疑龙经正文："疑龙经　　唐　杨筠松　撰上篇"
    m2 = re.search(r"疑龙经\s+唐\s+杨筠松\s+撰上篇", text)
    start2 = m2.start() if m2 else text.find("疑龙经", start1 + 1000)

    # 葬法倒杖正文："葬法倒杖　　唐　杨筠松"
    m3 = re.search(r"葬法倒杖\s+唐\s+杨筠松", text)
    start3 = m3.start() if m3 else text.find("葬法倒杖", start2 + 1000)

    # 第一部分：撼龙经
    hanlong_body = text[start1:start2].strip()
    entries.append(("撼龙经", "九星总论", hanlong_body))

    # 第二部分：疑龙经
    yilong_body = text[start2:start3]
    # 疑龙经按篇章标题切分
    yilong_pattern = re.compile(
        r"^　*(上篇|中篇|下篇|疑龙十问【附】|卫龙篇【附】|变星篇【附】|[一二三四五六七八九十]+问[^\n]{0,20})$",
        re.M
    )
    matches = list(yilong_pattern.finditer(yilong_body))
    for i, m in enumerate(matches):
        title = m.group(1).strip()
        cstart = m.end()
        cend = matches[i+1].start() if i+1 < len(matches) else len(yilong_body)
        content = yilong_body[cstart:cend].strip()
        if len(content) > 20:
            if re.match(r"[一二三四五六七八九十]+问", title):
                chapter = "疑龙经·疑龙十问"
            else:
                chapter = f"疑龙经·{title}"
            entries.append((chapter, title, content))

    # 第三部分：葬法倒杖
    zangfa_body = text[start3:]
    zangfa_pattern = re.compile(
        r"^　*(分两仪|求四象|倍八卦|倒杖十二法|二十四砂葬法【附】|顺杖|逆杖|缩杖|离杖|没杖|穿杖|鬭杖|截杖|对杖|缀杖|犯杖)$",
        re.M
    )
    matches = list(zangfa_pattern.finditer(zangfa_body))
    for i, m in enumerate(matches):
        title = m.group(1).strip()
        cstart = m.end()
        cend = matches[i+1].start() if i+1 < len(matches) else len(zangfa_body)
        content = zangfa_body[cstart:cend].strip()
        if len(content) > 15:
            if title in ["顺杖","逆杖","缩杖","离杖","没杖","穿杖","鬭杖","截杖","对杖","缀杖","犯杖"]:
                chapter = "葬法倒杖·倒杖十二法"
            elif title in ["分两仪","求四象","倍八卦"]:
                chapter = "葬法倒杖·理气篇"
            else:
                chapter = "葬法倒杖·二十四砂葬法"
            entries.append((chapter, title, content))

    return entries


def split_zangshu(text):
    """葬书：按空行分段，每段作为一个条目（内容过短的合并）。
    返回 [(chapter, section, content), ...]
    """
    # 按空行分段
    paragraphs = re.split(r"\n\s*\n", text)
    entries = []
    current = ""
    for p in paragraphs:
        p = p.strip()
        if not p:
            continue
        # 跳过太短的（<15字），合并到下一段
        if len(p) < 15:
            current += p + "\n"
            continue
        if current:
            p = current + p
            current = ""
        # 用第一句作为 section 标题（取前15字）
        first_sentence = re.split(r"[。！？]", p)[0][:15]
        entries.append(("葬书", first_sentence, p))
    if current:
        if entries:
            entries[-1] = (entries[-1][0], entries[-1][1], entries[-1][2] + "\n" + current)
        else:
            entries.append(("葬书", "总论", current))
    return entries


def main():
    # 撼龙经
    src = os.path.join(BASE, "raw/hanlongjing.txt")
    out_dir = os.path.join(BASE, "library", "xiang", "dixiang", "hanlongjing")
    os.makedirs(out_dir, exist_ok=True)
    text = open(src, encoding="utf-8").read()
    entries = split_hanlong(text)
    for idx, (chapter, section, content) in enumerate(entries):
        md = write_entry("hanlongjing", "撼龙经", "唐杨筠松撰·四库全书本",
                         chapter, section, content, idx, 4, extract_keywords_hanlong)
        with open(os.path.join(out_dir, f"xx2_hanlongjing_{idx:03d}.md"), "w",
                  encoding="utf-8", newline="\n") as f:
            f.write(md)
    print(f"  撼龙经: {len(entries)} 条 → {out_dir}")

    # 葬书
    src = os.path.join(BASE, "raw/zangshu.txt")
    out_dir = os.path.join(BASE, "library", "xiang", "dixiang", "zangshu")
    os.makedirs(out_dir, exist_ok=True)
    text = open(src, encoding="utf-8").read()
    entries = split_zangshu(text)
    for idx, (chapter, section, content) in enumerate(entries):
        md = write_entry("zangshu", "葬书", "晋郭璞撰·通行本",
                         chapter, section, content, idx, 4, extract_keywords_zangshu)
        with open(os.path.join(out_dir, f"xx2_zangshu_{idx:03d}.md"), "w",
                  encoding="utf-8", newline="\n") as f:
            f.write(md)
    print(f"  葬书: {len(entries)} 条 → {out_dir}")

    print(f"地相细分完成：撼龙经+葬书")


if __name__ == "__main__":
    main()
