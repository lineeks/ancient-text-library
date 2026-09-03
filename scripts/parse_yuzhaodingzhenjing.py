# -*- coding: utf-8 -*-
"""
Aether-Cycle 古籍知识库 · 《玉照定真经》结构化解析脚本（第三梯队·古法源流）
旧题晋·郭璞撰，张颙注（四库全书本）。为早期虚中禄命古法，口诀 + 张颙注体例：
  - 正文为连续口诀流，张颙注整体置于【…】内，紧跟所注口诀；
  - 极短【…】块（≤4字，如「囚」「甲木乙草」）是口诀内嵌夹注，原样并入口诀层；
  - 其余【…】块为张颙详注，作为一条之注层并结束该条。
另将卷首四库提要单独成篇（文献辨伪：旧题郭璞，实为后世依托）。
输出：extended/yuzhaodingzhenjing/yzzj_<三位序号>.md
"""
import os
import re

BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
RAW = os.path.join(BASE, "raw", "yuzhaodingzhenjing.txt")
OUT = os.path.join(BASE, "extended", "yuzhaodingzhenjing")
os.makedirs(OUT, exist_ok=True)

INLINE_NOTE_MAX = 4        # ≤4 字的【】块视为口诀内嵌夹注


def yaml_list(items):
    return "[" + ", ".join(f'"{x}"' for x in items) + "]"


def write_md(cid, num, section_title, chapter, body_layers, kw=("古法禄命", "张颙注")):
    tags = ["玉照定真经", "古法", section_title]
    fm = f"""---
id: "{cid}"
book: "玉照定真经"
chapter: "{chapter}"
chapter_num: {num}
section_title: "{section_title}"
source_version: "文渊阁四库全书本（旧题郭璞撰·张颙注）"
author: "旧题郭璞·张颙注"
dynasty: "旧题晋（后世依托）"
type: "koujue"
conditions:
  day_master: []
  month_branch: []
  day_pillar: []
  hour_pillar: []
  ten_god: []
  pattern: []
  shensha: []
  keywords: {yaml_list(list(kw))}
weight: 2
tags: {yaml_list(tags)}
---
"""
    out = [fm, f"### {section_title}", ""]
    out += body_layers
    out += ["**【白话提要】**", "", "（待补）", ""]
    with open(os.path.join(OUT, f"{cid}.md"), "w", encoding="utf-8") as f:
        f.write("\n".join(out).rstrip() + "\n")


def main():
    lines = open(RAW, encoding="utf-8").read().splitlines()
    # 卷首四库提要（L3，0-based 2）
    tiyao = lines[2].strip()
    write_md(
        "yzzj_000_tiyao", 0, "四库全书提要", "卷首·提要",
        ["**【原文（四库提要）】**", "", tiyao, ""],
        kw=("四库提要", "文献辨伪", "成书源流"),
    )

    body = "\n".join(lines[17:19])           # L18-L19 正文
    tokens = re.split(r"(【[^】]*】)", body)  # 交替：口诀文本 / 【注】
    entries = []
    koujue = []
    for tok in tokens:
        if not tok:
            continue
        m = re.fullmatch(r"【([^】]*)】", tok, re.S)
        if not m:
            t = tok.strip().strip("　")
            if t:
                koujue.append(t)
            continue
        note = m.group(1).strip()
        if len(note) <= INLINE_NOTE_MAX:
            # 内嵌夹注，原样保留入口诀
            koujue.append(tok)
            continue
        # 张颙详注：收尾一条
        if koujue:
            entries.append((koujue, note))
            koujue = []
    if koujue:  # 末尾无注的余口诀
        entries.append((koujue, ""))

    n = 0
    for idx, (kj, note) in enumerate(entries, start=1):
        cid = f"yzzj_{idx:03d}"
        first = kj[0]
        title = (first[:14] + "…") if len(first) > 14 else first
        layers = ["**【原文·口诀】**", ""] + [k for k in kj] + [""]
        if note:
            layers += ["**【张颙注】**", "", note, ""]
        write_md(cid, idx, title, f"正文·第{idx}条", layers)
        n += 1
    print(f"四库提要 1 篇 + 正文口诀 {n} 条，共 {n+1} 个 Markdown -> {OUT}")


if __name__ == "__main__":
    main()
