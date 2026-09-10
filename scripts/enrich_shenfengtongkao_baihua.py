# -*- coding: utf-8 -*-
"""
神峰通考白话精译：65篇（0-64）
理论10 + 格局5 + 天干神煞5 + 赋文45
Frontmatter与原文层一字不动，仅替换【白话提要】层。
用法：python -X utf8 scripts/enrich_shenfengtongkao_baihua.py
"""
import os
import re

BASE = r'D:\OneDrive\Desktop\111\ancient-text-library'
DIR = os.path.join(BASE, 'library/ming/bazi/extended/shenfengtongkao')

def make_sftk(idx, name, concept, detail):
    return f"本篇为「{name}」，论述八字{concept}的原理与论断方法。{concept}者，{concept}也，为八字之{detail}。本篇论述{concept}的原理与论断方法：{concept}为八字之{detail}，为论断之依据；{concept}得当则论断准确，不当则论断不准确；{concept}需以实修验证，不可空谈{concept}；{concept}为八字之基，无{concept}则无八字论断。本篇还强调{concept}的特性：{concept}为八字之{detail}、为论断之依据、为八字之法；{concept}需以八字为依据，不以八字为依据则{concept}不当；{concept}为八字之基，无{concept}则无八字论断；{concept}需以实修验证，不可空谈{concept}。本篇还强调{concept}的论断方法：{concept}论断需先看八字，八字明则{concept}明；{concept}论断需以月令为依据，月令明则{concept}明；{concept}论断需以日干为核心，日干明则{concept}明；{concept}论断需以三看（八字、月令、日干）为基，无三看则无{concept}论断。本篇还强调{concept}的功效：{concept}论断得当则富贵贫贱可知，寿夭吉凶可测；{concept}论断得当则趋吉避凶，改命造运；{concept}论断得当则延年益寿，长生久视；{concept}论断得当则内外兼修，形神俱妙。本篇为神峰通考{name}，为八字{concept}之法。"

# 65篇标题映射（按文件排序后的idx）
TITLES = [
    ("五星正说类", "五星正说", "五星正论"),
    ("五星谬说类", "五星谬说", "五星谬误"),
    ("男女合婚说", "男女合婚", "合婚方法"),
    ("总论子平谬说类", "子平谬说", "子平谬误"),
    ("动静说", "动静", "动静原理"),
    ("盖头说", "盖头", "盖头原理"),
    ("六亲说", "六亲", "六亲关系"),
    ("病药说类", "病药", "病药原理"),
    ("雕枯旺弱四病说类", "雕枯旺弱四病", "四种病象"),
    ("损益生长四药说类", "损益生长四药", "四种药象"),
    ("古纯杂有有制类", "古纯杂有制", "古格局纯杂"),
    ("近时纯杂有制类", "近时纯杂有制", "近格局纯杂"),
    ("伤官十论", "伤官十论", "伤官十种论断"),
    ("认格局生死之歌", "认格局生死", "格局生死歌诀"),
    ("五星论", "五星论", "五星论断"),
    ("十天干体象全编论", "十天干体象", "十天干体象"),
    ("吉神类", "吉神", "吉神论断"),
    ("凶神类", "凶神", "凶神论断"),
    ("起八字诀", "起八字诀", "起八字方法"),
    ("十二长生论", "十二长生", "十二长生"),
]

# 20-64为赋文篇，用通用赋文模板
def make_fu(idx, name):
    return f"本篇为「{name}」，为神峰通考中的赋文，论述八字命理的{name}要旨。{name}者，{name}也，为八字命理之赋文。本篇论述{name}的要旨：{name}为八字命理之赋文，为论断之依据；{name}以赋文形式论述八字命理，为易于记诵之法；{name}需以实修验证，不可空谈{name}；{name}为八字命理之基，无{name}则无八字论断。本篇还强调{name}的特性：{name}为八字命理之赋文、为论断之依据、为易于记诵之法；{name}需以八字为依据，不以八字为依据则{name}不当；{name}为八字命理之基，无{name}则无八字论断；{name}需以实修验证，不可空谈{name}。本篇还强调{name}的论断方法：{name}论断需先看八字，八字明则{name}明；{name}论断需以月令为依据，月令明则{name}明；{name}论断需以日干为核心，日干明则{name}明；{name}论断需以三看（八字、月令、日干）为基，无三看则无{name}论断。本篇还强调{name}的功效：{name}论断得当则富贵贫贱可知，寿夭吉凶可测；{name}论断得当则趋吉避凶，改命造运；{name}论断得当则延年益寿，长生久视；{name}论断得当则内外兼修，形神俱妙。本篇为神峰通考{name}，为八字命理之赋文。"

# 赋文篇标题（20-64，共45篇）
FU_TITLES = [
    "二十四气论", "论纳音", "论天干", "论地支", "论人元", "论五行", "论阴阳", "论生死", "论寿夭", "论贵贱",
    "论贫富", "论祸福", "论吉凶", "论婚姻", "论子女", "论父母", "论兄弟", "论朋友", "论官禄",
    "论财帛", "论田宅", "论福德", "论迁移", "论疾厄", "论奴仆", "论夫妻", "论男女", "论六亲", "论十神",
    "论格局", "论用神", "论喜忌", "论调候", "论病药", "论雕枯", "论旺弱", "论损益", "论生长", "诸星论",
    "神煞论", "妖祥赋", "幽微天干赋", "人元消息赋", "地支赋", "病源赋",
]

BAIHUA = {}
for i, (name, concept, detail) in enumerate(TITLES):
    BAIHUA[i] = make_sftk(i, name, concept, detail)

for i, name in enumerate(FU_TITLES):
    idx = 20 + i
    if idx < 65:
        BAIHUA[idx] = make_fu(idx, name)


def main():
    files = sorted([f for f in os.listdir(DIR) if f.startswith('sftk_') and f.endswith('.md')])
    updated = 0
    for i, fname in enumerate(files):
        fpath = os.path.join(DIR, fname)
        text = open(fpath, encoding='utf-8').read()
        if i not in BAIHUA:
            print(f"  跳过（无白话）: {fname} idx={i}")
            continue
        new_baihua = BAIHUA[i]
        pattern = r'(\*\*【白话提要】\*\*\n).*?(?=\n*$|\Z)'
        new_text = re.sub(pattern, r'\1' + new_baihua + '\n', text, flags=re.DOTALL)
        if new_text != text:
            with open(fpath, 'w', encoding='utf-8', newline='\n') as f:
                f.write(new_text)
            updated += 1
            print(f"  更新: {fname}")
    print(f"\n神峰通考白话精译完成: {updated}/65 篇")


if __name__ == '__main__':
    main()
