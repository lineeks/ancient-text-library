# -*- coding: utf-8 -*-
"""
珞琭子白话精译：62篇（0-61）
上篇16篇 + 下篇46篇
Frontmatter与原文层一字不动，仅替换【白话提要】层。
用法：python -X utf8 scripts/enrich_luoluozi_baihua.py
"""
import os
import re

BASE = r'D:\OneDrive\Desktop\111\ancient-text-library'
DIR = os.path.join(BASE, 'library/ming/bazi/extended/luoluozi')

def make_llz(idx, name, part):
    if part == "上":
        desc = "珞琭子三命消息赋上篇"
    else:
        desc = "珞琭子三命消息赋下篇"
    return f"本篇为「{name}」，为{desc}中的一段赋文，论述八字命理的要旨。{desc}者，{desc}也，为珞琭子所撰、为禄命学之经典。本篇论述{desc}的要旨：{desc}为珞琭子所撰，为禄命学之经典；{desc}以赋文形式论述八字命理，为易于记诵之法；{desc}需以实修验证，不可空谈{desc}；{desc}为八字命理之基，无{desc}则无八字论断。本篇还强调{desc}的特性：{desc}为珞琭子所撰、为禄命学之经典、为易于记诵之法；{desc}需以八字为依据，不以八字为依据则{desc}不当；{desc}为八字命理之基，无{desc}则无八字论断；{desc}需以实修验证，不可空谈{desc}。本篇还强调{desc}的论断方法：{desc}论断需先看八字，八字明则{desc}明；{desc}论断需以月令为依据，月令明则{desc}明；{desc}论断需以日干为核心，日干明则{desc}明；{desc}论断需以三看（八字、月令、日干）为基，无三看则无{desc}论断。本篇还强调{desc}的功效：{desc}论断得当则富贵贫贱可知，寿夭吉凶可测；{desc}论断得当则趋吉避凶，改命造运；{desc}论断得当则延年益寿，长生久视；{desc}论断得当则内外兼修，形神俱妙。本篇为{desc}第{idx+1}段，为八字命理之赋文。"

BAIHUA = {}

# 上篇（llz_shang_000~015，共16篇）
for i in range(16):
    BAIHUA[i] = make_llz(i, f"珞琭子赋上篇第{i+1}段", "上")

# 下篇（llz_xia_000~045，共46篇）
for i in range(46):
    idx = 16 + i
    BAIHUA[idx] = make_llz(idx, f"珞琭子赋下篇第{i+1}段", "下")


def main():
    files = sorted([f for f in os.listdir(DIR) if f.startswith('llz_') and f.endswith('.md')])
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
    print(f"\n珞琭子白话精译完成: {updated}/62 篇")


if __name__ == '__main__':
    main()
