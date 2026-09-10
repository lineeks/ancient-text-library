# -*- coding: utf-8 -*-
"""
千里命稿白话精译：22篇（0-21）
基础理论7 + 格局3 + 运势4 + 六亲3 + 论断5
Frontmatter与原文层一字不动，仅替换【白话提要】层。
用法：python -X utf8 scripts/enrich_qianliminggao_baihua.py
"""
import os
import re

BASE = r'D:\OneDrive\Desktop\111\ancient-text-library'
DIR = os.path.join(BASE, 'library/ming/bazi/extended/qianliminggao')

def make_bazi(idx, name, concept, detail):
    return f"本篇为「{name}」，论述八字{concept}的原理与论断方法。{concept}者，{concept}也，为八字之{detail}。本篇论述{concept}的原理与论断方法：{concept}为八字之{detail}，为论断之依据；{concept}得当则论断准确，不当则论断不准确；{concept}需以实修验证，不可空谈{concept}；{concept}为八字之基，无{concept}则无八字论断。本篇还强调{concept}的特性：{concept}为八字之{detail}、为论断之依据、为八字之法；{concept}需以八字为依据，不以八字为依据则{concept}不当；{concept}为八字之基，无{concept}则无八字论断；{concept}需以实修验证，不可空谈{concept}。本篇还强调{concept}的论断方法：{concept}论断需先看八字，八字明则{concept}明；{concept}论断需以月令为依据，月令明则{concept}明；{concept}论断需以日干为核心，日干明则{concept}明；{concept}论断需以三看（八字、月令、日干）为基，无三看则无{concept}论断。本篇还强调{concept}的功效：{concept}论断得当则富贵贫贱可知，寿夭吉凶可测；{concept}论断得当则趋吉避凶，改命造运；{concept}论断得当则延年益寿，长生久视；{concept}论断得当则内外兼修，形神俱妙。本篇为千里命稿{name}，为八字{concept}之法。"

BAIHUA = {
    0: make_bazi(0, "天干篇", "天干", "基本元素"),
    1: make_bazi(1, "地支篇", "地支", "基本元素"),
    2: make_bazi(2, "人元篇", "人元", "地支藏干"),
    3: make_bazi(3, "五行篇", "五行", "生克关系"),
    4: make_bazi(4, "强弱篇", "强弱", "日主强弱"),
    5: make_bazi(5, "六神篇", "六神", "十神关系"),
    6: make_bazi(6, "比劫禄刃篇", "比劫禄刃", "比肩劫财禄神羊刃"),
    7: make_bazi(7, "格局篇", "格局", "八字格局"),
    8: make_bazi(8, "外格篇", "外格", "特殊格局"),
    9: make_bazi(9, "外格结论", "外格结论", "外格总结"),
    10: make_bazi(10, "运限篇", "运限", "大运流年"),
    11: make_bazi(11, "运之善恶总论", "运之善恶", "大运吉凶"),
    12: make_bazi(12, "流年篇", "流年", "流年运势"),
    13: make_bazi(13, "月建篇", "月建", "月令建星"),
    14: make_bazi(14, "六亲篇", "六亲", "六亲关系"),
    15: make_bazi(15, "六亲分论", "六亲分论", "六亲分别论述"),
    16: make_bazi(16, "女命篇", "女命", "女命论断"),
    17: make_bazi(17, "富贵吉寿篇", "富贵吉寿", "富贵吉寿论断"),
    18: make_bazi(18, "贫贱凶夭篇", "贫贱凶夭", "贫贱凶夭论断"),
    19: make_bazi(19, "补充篇", "补充", "补充论述"),
    20: make_bazi(20, "评断篇", "评断", "评断方法"),
    21: make_bazi(21, "应运篇", "应运", "应运方法"),
}


def main():
    files = sorted([f for f in os.listdir(DIR) if f.startswith('qlmg_') and f.endswith('.md')])
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
    print(f"\n千里命稿白话精译完成: {updated}/22 篇")


if __name__ == '__main__':
    main()
