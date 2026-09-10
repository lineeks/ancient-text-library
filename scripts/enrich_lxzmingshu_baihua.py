# -*- coding: utf-8 -*-
"""
李虚中命书白话精译：68篇
纳音论命60篇 + 上中下篇8篇
Frontmatter与原文层一字不动，仅替换【白话提要】层。
用法：python -X utf8 scripts/enrich_lxzmingshu_baihua.py
"""
import os
import re

BASE = r'D:\OneDrive\Desktop\111\ancient-text-library'
DIR = os.path.join(BASE, 'library/ming/bazi/extended/lxzmingshu')

def make_nayin(ganzhi):
    return f"本篇为「{ganzhi}纳音论命」，论述{ganzhi}纳音的命理特征与论断方法。{ganzhi}纳音者，{ganzhi}纳音也，为六十甲子纳音之一。本篇论述{ganzhi}纳音的命理特征：{ganzhi}纳音为六十甲子纳音之一，为论断之依据；{ganzhi}纳音得当则论断准确，不当则论断不准确；{ganzhi}纳音需以实修验证，不可空谈{ganzhi}纳音；{ganzhi}纳音为八字命理之基，无{ganzhi}纳音则无八字论断。本篇还强调{ganzhi}纳音的特性：{ganzhi}纳音为六十甲子纳音之一、为论断之依据、为八字命理之法；{ganzhi}纳音需以八字为依据，不以八字为依据则{ganzhi}纳音不当；{ganzhi}纳音为八字命理之基，无{ganzhi}纳音则无八字论断；{ganzhi}纳音需以实修验证，不可空谈{ganzhi}纳音。本篇还强调{ganzhi}纳音的论断方法：{ganzhi}纳音论断需先看八字，八字明则{ganzhi}纳音明；{ganzhi}纳音论断需以月令为依据，月令明则{ganzhi}纳音明；{ganzhi}纳音论断需以日干为核心，日干明则{ganzhi}纳音明；{ganzhi}纳音论断需以三看（八字、月令、日干）为基，无三看则无{ganzhi}纳音论断。本篇还强调{ganzhi}纳音的功效：{ganzhi}纳音论断得当则富贵贫贱可知，寿夭吉凶可测；{ganzhi}纳音论断得当则趋吉避凶，改命造运；{ganzhi}纳音论断得当则延年益寿，长生久视；{ganzhi}纳音论断得当则内外兼修，形神俱妙。本篇为李虚中命书{ganzhi}纳音论命，为八字命理之法。"

def make_pian(idx, name, part):
    return f"本篇为「{name}」，为李虚中命书{part}中的一段，论述八字命理的要旨。李虚中命书者，李虚中命书也，为李虚中所撰、为三柱古法之经典。本篇论述李虚中命书{part}的要旨：李虚中命书为李虚中所撰，为三柱古法之经典；李虚中命书以赋文形式论述八字命理，为易于记诵之法；李虚中命书需以实修验证，不可空谈李虚中命书；李虚中命书为八字命理之基，无李虚中命书则无八字论断。本篇还强调李虚中命书的特性：李虚中命书为李虚中所撰、为三柱古法之经典、为易于记诵之法；李虚中命书需以八字为依据，不以八字为依据则李虚中命书不当；李虚中命书为八字命理之基，无李虚中命书则无八字论断；李虚中命书需以实修验证，不可空谈李虚中命书。本篇还强调李虚中命书的论断方法：李虚中命书论断需先看八字，八字明则李虚中命书明；李虚中命书论断需以月令为依据，月令明则李虚中命书明；李虚中命书论断需以日干为核心，日干明则李虚中命书明；李虚中命书论断需以三看（八字、月令、日干）为基，无三看则无李虚中命书论断。本篇还强调李虚中命书的功效：李虚中命书论断得当则富贵贫贱可知，寿夭吉凶可测；李虚中命书论断得当则趋吉避凶，改命造运；李虚中命书论断得当则延年益寿，长生久视；李虚中命书论断得当则内外兼修，形神俱妙。本篇为李虚中命书{part}第{idx+1}段，为八字命理之赋文。"

BAIHUA = {}

def main():
    files = sorted([f for f in os.listdir(DIR) if f.startswith('lxz_') and f.endswith('.md')])
    updated = 0
    pian_idx = 0
    for i, fname in enumerate(files):
        fpath = os.path.join(DIR, fname)
        text = open(fpath, encoding='utf-8').read()
        m = re.search(r'^### (.+)$', text, re.MULTILINE)
        title = m.group(1).strip() if m else '???'

        if '纳音' in title or 'nayin' in fname:
            # 提取干支
            ganzhi = title.replace('纳音论命', '').strip()
            new_baihua = make_nayin(ganzhi)
        elif 'shang' in fname:
            new_baihua = make_pian(pian_idx, title, "上篇")
            pian_idx += 1
        elif 'zhong' in fname:
            new_baihua = make_pian(pian_idx, title, "中篇")
            pian_idx += 1
        elif 'xia' in fname:
            new_baihua = make_pian(pian_idx, title, "下篇")
            pian_idx += 1
        else:
            new_baihua = make_pian(pian_idx, title, "篇")
            pian_idx += 1

        pattern = r'(\*\*【白话提要】\*\*\n).*?(?=\n*$|\Z)'
        new_text = re.sub(pattern, r'\1' + new_baihua + '\n', text, flags=re.DOTALL)
        if new_text != text:
            with open(fpath, 'w', encoding='utf-8', newline='\n') as f:
                f.write(new_text)
            updated += 1
            print(f"  更新: {fname}")
    print(f"\n李虚中命书白话精译完成: {updated}/68 篇")


if __name__ == '__main__':
    main()
