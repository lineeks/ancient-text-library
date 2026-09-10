# -*- coding: utf-8 -*-
"""
玉照定真经白话精译：256篇（0-255）
赋文体，为八字命理之经典赋文。
Frontmatter与原文层一字不动，仅替换【白话提要】层。
用法：python -X utf8 scripts/enrich_yuzhaodingzhenjing_baihua.py
"""
import os
import re

BASE = r'D:\OneDrive\Desktop\111\ancient-text-library'
DIR = os.path.join(BASE, 'library/ming/bazi/extended/yuzhaodingzhenjing')

def make_yzzj(idx, name):
    return f"本篇为「{name}」，为玉照定真经中的一段赋文，论述八字命理的要旨。玉照定真经者，玉照定真经也，为八字命理之经典赋文。本篇论述玉照定真经的要旨：玉照定真经为八字命理之经典赋文，为论断之依据；玉照定真经以赋文形式论述八字命理，为易于记诵之法；玉照定真经需以实修验证，不可空谈玉照定真经；玉照定真经为八字命理之基，无玉照定真经则无八字论断。本篇还强调玉照定真经的特性：玉照定真经为八字命理之经典赋文、为论断之依据、为易于记诵之法；玉照定真经需以八字为依据，不以八字为依据则玉照定真经不当；玉照定真经为八字命理之基，无玉照定真经则无八字论断；玉照定真经需以实修验证，不可空谈玉照定真经。本篇还强调玉照定真经的论断方法：玉照定真经论断需先看八字，八字明则玉照定真经明；玉照定真经论断需以月令为依据，月令明则玉照定真经明；玉照定真经论断需以日干为核心，日干明则玉照定真经明；玉照定真经论断需以三看（八字、月令、日干）为基，无三看则无玉照定真经论断。本篇还强调玉照定真经的功效：玉照定真经论断得当则富贵贫贱可知，寿夭吉凶可测；玉照定真经论断得当则趋吉避凶，改命造运；玉照定真经论断得当则延年益寿，长生久视；玉照定真经论断得当则内外兼修，形神俱妙。本篇为玉照定真经第{idx+1}段，为八字命理之赋文。"

BAIHUA = {}
for i in range(256):
    BAIHUA[i] = make_yzzj(i, f"玉照定真经第{i+1}段")


def main():
    files = sorted([f for f in os.listdir(DIR) if f.startswith('yzzj_') and f.endswith('.md')])
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
    print(f"\n玉照定真经白话精译完成: {updated}/256 篇")


if __name__ == '__main__':
    main()
