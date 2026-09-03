# -*- coding: utf-8 -*-
"""
Aether-Cycle 古籍知识库 · 《子平真诠评注》结构化解析脚本
源文正文章节标题缺失（仅首尾保留），采用「48章首句指纹」精确定位章节边界并切分。
沈孝瞻原文为【原文】层；以「徐注：」起始的段落归入【注解】层。
输出：core/zipingzhenquan/
"""
import os
import re

BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
RAW = os.path.join(BASE, "raw", "zipingzhenquan.txt")
OUT_DIR = os.path.join(BASE, "core", "zipingzhenquan")
os.makedirs(OUT_DIR, exist_ok=True)

# 48 章元数据：(序号, 章名, 首句指纹, slug, [pattern], [ten_god], [keywords])
CHAPTERS = [
    (1,  "论十干十二支", "天地之间，一气而已", "ganzhi", [], [], ["天干", "地支", "五行", "阴阳"]),
    (2,  "论阴阳生克", "四时之运，相生而成", "yinyangshengke", [], [], ["相生", "相克", "五行"]),
    (3,  "论阴阳生死", "五行干支之说，已详论于干支篇", "yinyangshengsi", [], [], ["长生", "十二宫", "旺衰"]),
    (4,  "论十干配合性情", "合化之义，以十干阴阳相配而成", "ganpeihexingqing", [], [], ["天干五合", "合化", "性情"]),
    (5,  "论十干合而不合", "十干化合之义，前篇既明之矣", "ganhebuhe", [], [], ["天干五合", "争合", "妒合"]),
    (6,  "论十干得时不旺失时不弱", "书云，得时俱为旺论", "deshibuwang", [], [], ["旺衰", "强弱", "得时", "失时"]),
    (7,  "论刑冲会合解法", "刑者，三刑也", "xingchonghuihe", [], [], ["三刑", "六冲", "三合", "六合"]),
    (8,  "论用神", "八字用神，专求月令", "yongshen", [], [], ["用神", "月令", "扶抑", "病药", "调候", "通关"]),
    (9,  "论用神成败救应", "用神专寻月令，以四柱配之", "yongshenchengbai", [], [], ["用神", "成格", "破格", "救应"]),
    (10, "论用神变化", "用神既主月令矣", "yongshenbianhua", [], [], ["用神", "变化", "透干", "会支"]),
    (11, "论用神纯杂", "用神既有变化", "yongshenchunza", [], [], ["用神", "纯杂", "清浊"]),
    (12, "论用神格局高低", "八字既有用神", "gejugaodi", [], [], ["格局高低", "有情", "有力"]),
    (13, "论用神因成得败因败得成", "八字之中，变化不一", "yinchengbaibai", [], [], ["用神", "因成得败", "因败得成"]),
    (14, "论用神配气候得失", "论命惟以月令用神为主", "peiqihou", [], [], ["调候", "气候", "寒暖燥湿"]),
    (15, "论相神紧要", "月令既得用神", "xiangshen", [], [], ["相神", "用神", "辅佐"]),
    (16, "论杂气如何取用", "四墓者，杂气也", "zaqi", ["杂气格"], [], ["杂气", "辰戌丑未", "透干会支"]),
    (17, "论墓库刑冲之说", "辰戌丑未，最喜刑冲", "mukuxingchong", [], [], ["墓库", "刑冲", "四库"]),
    (18, "论四吉神能破格", "财官印食，四吉神也", "jishenpoge", [], ["正官", "正财", "正印", "食神"], ["吉神", "破格"]),
    (19, "论四凶神能成格", "煞伤枭刃，四凶神也", "xiongshenchengge", [], ["七杀", "伤官", "偏印", "阳刃"], ["凶神", "成格", "制化"]),
    (20, "论生克先后分吉凶", "月令用神，配以四柱", "shengkexianhou", [], [], ["生克", "先后", "吉凶"]),
    (21, "论星辰无关格局", "八字格局，专以月令配四柱", "xingchen", [], [], ["神煞", "星辰", "格局批判"]),
    (22, "论外格用舍", "八字用神既专主月令", "waige", ["外格"], [], ["外格", "月令", "从格", "化格"]),
    (23, "论宫分用神配六亲", "人有六亲，配之八字", "liuqin", [], [], ["六亲", "宫分", "父母兄弟"]),
    (24, "论妻子", "大凡命中吉凶", "qizi", [], [], ["妻宫", "妻星", "子息"]),
    (25, "论行运", "论运与看命无二法也", "xingyun", [], [], ["大运", "喜忌", "行运"]),
    (26, "论行运成格变格", "命之格局，成于八字", "xingyunchengbian", [], [], ["大运", "成格", "变格"]),
    (27, "论喜忌干支有别", "命中喜忌，虽支干俱有", "xijiganzhi", [], [], ["天干", "地支", "喜忌"]),
    (28, "论支中喜忌逢运透清", "支中喜忌，固与干有别矣", "zhizhongxiji", [], [], ["地支", "透清", "大运"]),
    (29, "论时说拘泥格局", "八字用神专凭月令", "junigeju", [], [], ["时上格局", "格局批判", "归禄"]),
    (30, "论时说以讹传讹", "八字本有定理", "yiechuane", [], [], ["格局批判", "谬说"]),
    (31, "论正官", "官以克身", "zhengguan", ["正官格"], ["正官"], ["正官", "官格", "刑冲破害"]),
    (32, "论正官取运", "取运之道", "zhengguanquyun", ["正官格"], ["正官"], ["正官", "取运", "大运"]),
    (33, "论财", "财为我克", "cai", ["财格"], ["正财", "偏财"], ["财格", "财旺生官", "食神生财"]),
    (34, "论财取运", "财格取运", "caiquyun", ["财格"], ["正财", "偏财"], ["财格", "取运"]),
    (35, "论印绶", "印绶喜其生身", "yinshou", ["印绶格"], ["正印", "偏印"], ["印绶", "官印双全", "杀印相生"]),
    (36, "论印绶取运", "印格取运", "yinshouquyun", ["印绶格"], ["正印", "偏印"], ["印绶", "取运"]),
    (37, "论食神", "食神本属泄气", "shishen", ["食神格"], ["食神"], ["食神", "食神生财", "食神制杀"]),
    (38, "论食神取运", "食神取运", "shishenquyun", ["食神格"], ["食神"], ["食神", "取运"]),
    (39, "论偏官", "煞以攻身", "pianguan", ["七杀格"], ["七杀"], ["偏官", "七杀", "食神制杀", "杀印相生"]),
    (40, "论偏官取运", "偏官取运", "pianguanquyun", ["七杀格"], ["七杀"], ["偏官", "七杀", "取运"]),
    (41, "论伤官", "伤官虽非吉神", "shangguan", ["伤官格"], ["伤官"], ["伤官", "伤官生财", "伤官佩印", "金水伤官"]),
    (42, "论伤官取运", "伤官取运", "shangguanquyun", ["伤官格"], ["伤官"], ["伤官", "取运"]),
    (43, "论阳刃", "阳刃者，劫我正财之神", "yangren", ["阳刃格"], ["阳刃", "劫财"], ["阳刃", "官煞制刃"]),
    (44, "论阳刃取运", "阳刃用官，则运喜助官", "yangrenquyun", ["阳刃格"], ["阳刃"], ["阳刃", "取运"]),
    (45, "论建禄月劫", "建禄者，月建逢禄堂也", "jianluyuejie", ["建禄格", "月劫格"], ["比肩", "劫财"], ["建禄", "月劫", "禄堂"]),
    (46, "论建禄月劫取运", "禄劫取运", "jianluyuejiequyun", ["建禄格", "月劫格"], ["比肩", "劫财"], ["建禄", "月劫", "取运"]),
    (47, "论杂格", "杂格者，月令无用", "zage", ["杂格", "外格"], [], ["杂格", "曲直", "化气", "从格", "井栏"]),
    (48, "附论杂格取运", "徐注：杂格不一", "zagequyun", ["杂格", "外格"], [], ["杂格", "取运", "气势"]),
]


def yaml_list(items):
    return "[" + ", ".join(f'"{x}"' for x in items) + "]"


def main():
    with open(RAW, encoding="utf-8") as f:
        lines = f.read().splitlines()

    # 正文起点：第一个「一、论十干十二支」标题行
    body_start = None
    for i, ln in enumerate(lines):
        if ln.strip().startswith("一、论十干十二支"):
            body_start = i
            break
    assert body_start is not None, "未找到正文起点"
    print("正文起始行:", body_start + 1)

    # 定位每章首句指纹所在行
    anchors = []
    for num, title, fingerprint, slug, patterns, tengods, kws in CHAPTERS:
        hits = [i for i in range(body_start, len(lines)) if fingerprint in lines[i]]
        if len(hits) != 1:
            print(f"!! 第{num}章《{title}》指纹命中 {len(hits)} 次: {[h+1 for h in hits]}")
        else:
            anchors.append((num, title, slug, patterns, tengods, kws, hits[0]))
            print(f"  ch{num:02d} {title:<16} L{hits[0]+1}")

    if len(anchors) != 48:
        print(f"\n!! 仅定位 {len(anchors)}/48 章，请修正指纹后重试")
        return

    # 切分并生成
    for idx, (num, title, slug, patterns, tengods, kws, start) in enumerate(anchors):
        end = anchors[idx + 1][6] if idx + 1 < len(anchors) else len(lines)
        # 收集正文段落；分离「徐注：」
        original, zhuzhu = [], []
        for ln in lines[start:end]:
            s = ln.strip()
            if not s:
                continue
            # 跳过章标题行本身（形如「一、论十干十二支」「四十八、附论杂格取运」）
            if re.match(r"^[一二三四五六七八九十]+、", s) and len(s) < 20:
                continue
            if s.startswith("徐注：") or s.startswith("徐注:"):
                zhuzhu.append(s[3:].strip())
            else:
                original.append(s)

        cid = f"zpzq_ch{num:02d}_{slug}"
        # 权重：格局专论（31-48）与用神核心（8-15）权重高
        if 31 <= num <= 48 or 8 <= num <= 15:
            weight = 10
        elif num in (16, 17, 22):
            weight = 9
        else:
            weight = 8
        fm = f"""---
id: "{cid}"
book: "子平真诠评注"
chapter: "第{num}章·{title}"
chapter_num: {num}
section_title: "{title}"
source_version: "沈孝瞻原著·徐乐吾评注(节本)"
author: "沈孝瞻"
dynasty: "清"
type: "chapter"
conditions:
  day_master: []
  month_branch: []
  day_pillar: []
  hour_pillar: []
  ten_god: {yaml_list(tengods)}
  pattern: {yaml_list(patterns)}
  shensha: []
  keywords: {yaml_list(kws)}
weight: {weight}
tags: {yaml_list(["子平真诠", title] + patterns + tengods)}
---
"""
        md = [fm, f"### 第{num}章 {title}", "", "**【原文】**", ""]
        for p in original:
            md.append(p); md.append("")
        if zhuzhu:
            md.append("**【徐乐吾评注】**"); md.append("")
            for p in zhuzhu:
                md.append(p); md.append("")
        md.append("**【白话提要】**"); md.append(""); md.append("（待补）"); md.append("")
        with open(os.path.join(OUT_DIR, f"{cid}.md"), "w", encoding="utf-8") as f:
            f.write("\n".join(md).rstrip() + "\n")

    print(f"\n已生成 48 个章节 Markdown -> {OUT_DIR}")


if __name__ == "__main__":
    main()
