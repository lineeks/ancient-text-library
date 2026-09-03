# -*- coding: utf-8 -*-
"""
Aether-Cycle 古籍知识库 · 《渊海子平》结构化解析脚本（第二梯队）
源文：徐大升编（此电子本为带标点本），全书分 总论/神煞/六亲/女命/赋论 五大部分。
本脚本只结构化「赋论」部分（L740 起）的 30 篇核心歌赋——即排盘下方的「古歌赋印证」层。
篇目标题以《篇名》标注（源文字间夹全角空格，解析时归一）。
输出：origin-shensha/yuanhaiziping/yhzp_<两位序号>_<slug>.md
"""
import os
import re

BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
RAW = os.path.join(BASE, "raw", "yuanhaiziping.txt")
OUT = os.path.join(BASE, "origin-shensha", "yuanhaiziping")
os.makedirs(OUT, exist_ok=True)

FUN_START = 740          # 「赋论」部分起始（1-based）

# 篇名（去空格）-> (slug, [keywords])；按源文出现顺序
META = {
    "子平举要歌": ("zipingjuyaoge", ["举要", "日主", "衰旺", "提纲", "官杀"]),
    "详解定真论": ("xiangjiedingzhenlun", ["定真", "日主", "三才", "四柱", "六亲取象"]),
    "喜忌篇": ("xijipian", ["喜忌", "财官印", "格局", "归禄", "食神"]),
    "看命入式": ("kanmingrushi", ["入式", "看命步骤", "提纲", "用神"]),
    "神趣八法": ("shenqubafa", ["类属", "从化", "反照", "鬼局", "八法"]),
    "杂论口诀": ("zalunkoujue", ["口诀", "杂论", "取用", "财官"]),
    "群兴论": ("qunxinglun", ["群兴", "富贵", "造化", "兴衰"]),
    "论兴亡": ("lunxingwang", ["兴亡", "用神", "岁运", "成败"]),
    "论命细法": ("lunmingxifa", ["细法", "刑冲", "合化", "格局细节"]),
    "心镜歌": ("xinjingge", ["心镜", "歌诀", "日主", "财官"]),
    "妖祥赋": ("yaoxiangfu", ["妖祥", "五行生克", "吉凶", "赋文"]),
    "相心赋": ("xiangxin_fu", ["相心", "心性", "五行性", "赋文"]),
    "玄机赋": ("xuanjifu", ["玄机", "五行", "格局高低", "赋文"]),
    "幽微赋": ("youweifu", ["幽微", "性情", "贫贱富贵", "赋文"]),
    "五行元理消息赋": ("wuxingyuanli", ["元理", "消息", "五行机理", "赋文"]),
    "造微论": ("zaoweilun", ["造微", "干支", "用神", "微妙"]),
    "人鉴论": ("renjianlun", ["人鉴", "五行", "照鉴", "论"]),
    "爱憎赋": ("aizengfu", ["爱憎", "喜忌", "十干性情", "赋文"]),
    "万金赋": ("wanjinfu", ["万金", "格局", "日主", "赋文"]),
    "挈要捷驰玄妙诀": ("qieyaojuechi", ["捷驰", "玄妙诀", "口诀", "捷法"]),
    "渊源集说": ("yuanyuanjishuo", ["渊源", "集说", "源流", "理法"]),
    "子平百章论科甲歌": ("kejiage", ["科甲", "功名", "读书", "歌诀"]),
    "四言独步": ("siyandubu", ["四言", "独步", "口诀", "纲领"]),
    "弃命从杀论": ("qimingcongsha", ["从杀", "从格", "弃命", "势从"]),
    "五言独步": ("wuyandubu", ["五言", "独步", "口诀", "纲领", "有杀只论杀"]),
    "五行生克赋": ("wuxingshengke", ["生克", "五行", "制化", "赋文"]),
    "珞琭子消息赋": ("luoluzixiaoxi", ["珞琭子", "消息", "古法", "赋文"]),
    "论八字撮要法": ("bazicuoyao", ["撮要", "捷法", "八字纲领"]),
    "格局生死引用": ("gejushengsi", ["格局", "生死", "引用", "成败救应"]),
    "会要命书说": ("huiyaomingshu", ["会要", "命书", "总结"]),
}


def yaml_list(items):
    return "[" + ", ".join(f'"{x}"' for x in items) + "]"


def clean_title(s):
    return s.replace("　", "").replace(" ", "").strip().strip("《》")

# 篇名繁简/异体归一（仅用于匹配 META 与规范篇名；正文不改）
TITLE_NORM = str.maketrans({"鑑": "鉴", "剋": "克", "剏": "创", "迺": "乃"})


def main():
    lines = open(RAW, encoding="utf-8").read().splitlines()
    # 定位赋论部分所有《篇名》标题
    marks = []
    for i in range(FUN_START - 1, len(lines)):
        t = lines[i].strip().replace("　", "").replace(" ", "")
        m = re.fullmatch(r"《([^》]{2,16})》", t)
        if m:
            norm = m.group(1).translate(TITLE_NORM)
            if norm in META:
                marks.append((i, norm))
    print(f"赋论定位篇目 {len(marks)} 篇")
    missing = [k for k in META if k not in [m[1] for m in marks]]
    if missing:
        print("  警告：META 中未定位到的篇目:", missing)

    n = 0
    for idx, (i, title) in enumerate(marks):
        end = marks[idx+1][0] if idx+1 < len(marks) else len(lines)
        body = [lines[j].rstrip() for j in range(i+1, end)]
        body = [b for b in body if b.strip() and not b.strip().startswith("【渊海子平】")]
        slug, kw = META[title]
        num = idx + 1
        cid = f"yhzp_{num:02d}_{slug}"
        tags = ["渊海子平", "赋论", title] + kw[:2]
        fm = f"""---
id: "{cid}"
book: "渊海子平"
chapter: "赋论·第{num}篇"
chapter_num: {num}
section_title: "{title}"
source_version: "徐大升编·带标点电子本"
author: "徐大升（编）"
dynasty: "宋（明代增补）"
type: "fuwen"
conditions:
  day_master: []
  month_branch: []
  day_pillar: []
  hour_pillar: []
  ten_god: []
  pattern: []
  shensha: []
  keywords: {yaml_list(kw)}
weight: 6
tags: {yaml_list(tags)}
---
"""
        out = [fm, f"### {title}", "", "**【原文】**", ""]
        out += body
        out += ["", "**【白话提要】**", "", "（待补）", ""]
        with open(os.path.join(OUT, f"{cid}.md"), "w", encoding="utf-8") as f:
            f.write("\n".join(out).rstrip() + "\n")
        n += 1
    print(f"已生成 {n} 个赋论 Markdown -> {OUT}")


if __name__ == "__main__":
    main()
