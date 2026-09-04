# -*- coding: utf-8 -*-
"""
Aether-Cycle 古籍知识库 · 《千里命稿》结构化解析脚本（第三梯队·民国通俗参照）
民国·韦千里著，白话系统讲授子平格局与现代取象。源文前有目录（跳过），正文自「天干篇」起，
共 22 篇，篇名为独立短行。连贯白话讲解（含命例）整体入【原文】层，不再拆命例。
输出：extended/qianliminggao/qlmg_<两位序号>_<slug>.md
"""
import os
import re

BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
RAW = os.path.join(BASE, "raw", "qianliminggao.txt")
OUT = os.path.join(BASE, "library", "ming", "bazi", "extended", "qianliminggao")
os.makedirs(OUT, exist_ok=True)

BODY_START = 374 - 1     # 正文「天干篇」起始（0-based）

# 篇名 -> (slug, [ten_god], [pattern], [keywords])
META = {
    "天干篇": ("tiangan", [], [], ["天干", "十干性情", "五行"]),
    "地支篇": ("dizhi", [], [], ["地支", "十二支", "藏干"]),
    "人元篇": ("renyuan", [], [], ["人元", "藏干", "司令"]),
    "五行篇": ("wuxing", [], [], ["五行", "生克", "五行性情"]),
    "强弱篇": ("qiangruo", [], [], ["日主强弱", "得令", "得地得势"]),
    "六神篇": ("liushen", ["正官", "七杀", "正财", "偏财", "正印", "偏印", "伤官", "食神", "比肩", "劫财"], [], ["六神", "十神精义", "现代取象"]),
    "比劫禄刃篇": ("bijie_luren", ["比肩", "劫财"], [], ["比肩", "劫财", "禄", "羊刃"]),
    "格局篇": ("geju", [], ["正官格", "七杀格", "财格", "印绶格", "食神格", "伤官格"], ["格局", "成格破格", "取用"]),
    "外格篇": ("waige", [], ["从格", "化格", "从旺格", "从强格"], ["外格", "特殊格局", "从化"]),
    "外格结论": ("waige_jielun", [], ["从格", "化格"], ["外格", "结论", "真从假从"]),
    "运限篇": ("yunxian", [], [], ["大运", "运限", "行运吉凶"]),
    "运之善恶总论": ("yunzhi_shane", [], [], ["大运善恶", "行运总论", "喜忌"]),
    "流年篇": ("liunian", [], [], ["流年", "太岁", "岁运并临"]),
    "月建篇": ("yuejian", [], [], ["月建", "提纲", "月令"]),
    "六亲篇": ("liuqin", [], [], ["六亲", "父母兄弟妻财子息", "十神配六亲"]),
    "六亲分论": ("liuqin_fenlun", ["正印", "偏财", "比肩", "食神", "伤官"], [], ["六亲分论", "父母", "夫妻", "子女"]),
    "女命篇": ("nvming", [], [], ["女命", "夫星", "子星", "贞静"]),
    "富贵吉寿篇": ("fugui_jishou", [], [], ["富贵", "吉寿", "格局层次", "福寿"]),
    "贫贱凶夭篇": ("pinjian_xiongyao", [], [], ["贫贱", "凶夭", "破败", "偏枯"]),
    "补充篇": ("buchong", [], [], ["补充", "杂论", "发挥"]),
    "评断篇": ("pingduan", [], [], ["评断", "实断", "命例分析"]),
    "应运篇": ("yingyun", [], [], ["应运", "名造举例", "实战命例"]),
}


def yaml_list(items):
    return "[" + ", ".join(f'"{x}"' for x in items) + "]"


def main():
    lines = open(RAW, encoding="utf-8").read().splitlines()
    marks = []
    for i in range(BODY_START, len(lines)):
        s = lines[i].strip()
        if s in META:
            marks.append((i, s))
    print(f"正文定位篇章 {len(marks)} 篇")
    assert len(marks) == len(META), f"篇章数不符：{len(marks)} vs {len(META)}"

    n = 0
    for idx, (i, title) in enumerate(marks):
        end = marks[idx+1][0] if idx+1 < len(marks) else len(lines)
        body = [lines[j].rstrip() for j in range(i+1, end) if lines[j].strip()]
        body = [b for b in body if b.strip() != "千里命稿终"]
        slug, tg, pat, kw = META[title]
        num = idx + 1
        cid = f"qlmg_{num:02d}_{slug}"
        tags = ["千里命稿", "韦千里", "民国通俗", title] + tg[:2] + kw[:2]
        fm = f"""---
id: "{cid}"
book: "千里命稿"
chapter: "正文·第{num}篇"
chapter_num: {num}
section_title: "{title}"
source_version: "民国·韦千里著·白话电子本"
author: "韦千里"
dynasty: "民国"
type: "chapter"
conditions:
  day_master: []
  month_branch: []
  day_pillar: []
  hour_pillar: []
  ten_god: {yaml_list(tg)}
  pattern: {yaml_list(pat)}
  shensha: []
  keywords: {yaml_list(kw)}
weight: 2
tags: {yaml_list(tags)}
---
"""
        out = [fm, f"### {title}", "", "**【原文】**", ""]
        out += body
        out += ["", "**【白话提要】**", "", "（本篇本身为民国白话讲解，无需另译）", ""]
        with open(os.path.join(OUT, f"{cid}.md"), "w", encoding="utf-8") as f:
            f.write("\n".join(out).rstrip() + "\n")
        n += 1
    print(f"已生成 {n} 篇 Markdown -> {OUT}")


if __name__ == "__main__":
    main()
