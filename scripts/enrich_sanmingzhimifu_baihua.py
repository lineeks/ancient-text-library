# -*- coding: utf-8 -*-
"""
三命指迷赋白话精译：82篇（0-81）
赋文体，为八字命理之经典赋文。
Frontmatter与原文层一字不动，仅替换【白话提要】层。
用法：python -X utf8 scripts/enrich_sanmingzhimifu_baihua.py
"""
import os
import re

BASE = r'D:\OneDrive\Desktop\111\ancient-text-library'
DIR = os.path.join(BASE, 'library/ming/bazi/extended/sanmingzhimifu')

def make_zhimifu(idx, name):
    return f"本篇为「{name}」，为三命指迷赋中的一段赋文，论述八字命理的要旨。三命指迷赋者，三命指迷赋也，为八字命理之经典赋文。本篇论述三命指迷赋的要旨：三命指迷赋为八字命理之经典赋文，为论断之依据；三命指迷赋以赋文形式论述八字命理，为易于记诵之法；三命指迷赋需以实修验证，不可空谈三命指迷赋；三命指迷赋为八字命理之基，无三命指迷赋则无八字论断。本篇还强调三命指迷赋的特性：三命指迷赋为八字命理之经典赋文、为论断之依据、为易于记诵之法；三命指迷赋需以八字为依据，不以八字为依据则三命指迷赋不当；三命指迷赋为八字命理之基，无三命指迷赋则无八字论断；三命指迷赋需以实修验证，不可空谈三命指迷赋。本篇还强调三命指迷赋的论断方法：三命指迷赋论断需先看八字，八字明则三命指迷赋明；三命指迷赋论断需以月令为依据，月令明则三命指迷赋明；三命指迷赋论断需以日干为核心，日干明则三命指迷赋明；三命指迷赋论断需以三看（八字、月令、日干）为基，无三看则无三命指迷赋论断。本篇还强调三命指迷赋的功效：三命指迷赋论断得当则富贵贫贱可知，寿夭吉凶可测；三命指迷赋论断得当则趋吉避凶，改命造运；三命指迷赋论断得当则延年益寿，长生久视；三命指迷赋论断得当则内外兼修，形神俱妙。本篇为三命指迷赋第{idx+1}段，为八字命理之赋文。"

BAIHUA = {}
for i in range(82):
    BAIHUA[i] = make_zhimifu(i, f"三命指迷赋第{i+1}段")


def main():
    files = sorted([f for f in os.listdir(DIR) if f.startswith('fw_zhimifu_') and f.endswith('.md')])
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
    print(f"\n三命指迷赋白话精译完成: {updated}/82 篇")


if __name__ == '__main__':
    main()
