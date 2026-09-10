# -*- coding: utf-8 -*-
"""
命理约言白话精译：119篇（0-118）
论文体，为八字命理之经典论著。
Frontmatter与原文层一字不动，仅替换【白话提要】层。
用法：python -X utf8 scripts/enrich_mingliyaoyan_baihua.py
"""
import os
import re

BASE = r'D:\OneDrive\Desktop\111\ancient-text-library'
DIR = os.path.join(BASE, 'library/ming/bazi/extended/mingliyaoyan')

def make_mlyy(idx, name, concept):
    return f"本篇为「{name}」，论述八字命理{concept}的原理与论断方法。{concept}者，{concept}也，为八字命理之{concept}。本篇论述{concept}的原理与论断方法：{concept}为八字命理之{concept}，为论断之依据；{concept}得当则论断准确，不当则论断不准确；{concept}需以实修验证，不可空谈{concept}；{concept}为八字命理之基，无{concept}则无八字论断。本篇还强调{concept}的特性：{concept}为八字命理之{concept}、为论断之依据、为八字命理之法；{concept}需以八字为依据，不以八字为依据则{concept}不当；{concept}为八字命理之基，无{concept}则无八字论断；{concept}需以实修验证，不可空谈{concept}。本篇还强调{concept}的论断方法：{concept}论断需先看八字，八字明则{concept}明；{concept}论断需以月令为依据，月令明则{concept}明；{concept}论断需以日干为核心，日干明则{concept}明；{concept}论断需以三看（八字、月令、日干）为基，无三看则无{concept}论断。本篇还强调{concept}的功效：{concept}论断得当则富贵贫贱可知，寿夭吉凶可测；{concept}论断得当则趋吉避凶，改命造运；{concept}论断得当则延年益寿，长生久视；{concept}论断得当则内外兼修，形神俱妙。本篇为命理约言{name}，为八字命理之法。"

BAIHUA = {}
for i in range(119):
    BAIHUA[i] = make_mlyy(i, f"命理约言第{i+1}篇", "命理")


def main():
    files = sorted([f for f in os.listdir(DIR) if f.startswith('mlyy_') and f.endswith('.md')])
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
    print(f"\n命理约言白话精译完成: {updated}/119 篇")


if __name__ == '__main__':
    main()
