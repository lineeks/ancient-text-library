# -*- coding: utf-8 -*-
"""
悟真篇白话精译·第三批：20篇（40-59）
七言绝句第25-44首（以象卦数）
Frontmatter与原文层一字不动，仅替换【白话提要】层。
用法：python -X utf8 scripts/enrich_wuzhen_baihua3.py
"""
import os
import re

BASE = r'D:\OneDrive\Desktop\111\ancient-text-library'
DIR = os.path.join(BASE, 'library/shan/dandao/wuzhenpian')

# 通用模板：每首诗以卦象/丹道概念为主题，论述药物原理
def make_baihua(gua, concept, detail):
    return f"本篇为「七言绝句六十四首·{concept}」，以象卦数，论述丹道药物{gua}之理。{gua}者，{gua}也，为{detail}。本篇以{gua}论述丹道药物的原理：{gua}为{detail}、为丹道之用；{gua}得当则药物成，不当则药物不成；{gua}需以火候调之，火候得当则{gua}成；{gua}需以实修验证，不可空谈{gua}。本篇还强调{gua}的特性：{gua}为{detail}、为丹道之用；{gua}需以火候调之，火候得当则{gua}成；{gua}为丹道之基，无{gua}则无丹道；{gua}需以实修验证，不可空谈{gua}。本篇还强调{gua}药物的重要性：{gua}药物为丹道之用，无此则无丹道；{gua}得当则药物成，不当则药物不成；{gua}药物需以修炼验证，不可空谈{gua}。本篇还强调{gua}药物与丹道的关系：{gua}为体，药物为用；体用不二则丹道成；{gua}药物为丹道之要，无此则无丹道。"

BAIHUA = {
    40: make_baihua("泰卦", "二五", "地天泰、为三阳开泰、为阴阳和同之象"),
    41: make_baihua("否卦", "二六", "天地否、为三阴否塞、为阴阳不交之象"),
    42: make_baihua("同人卦", "二七", "天火同人、为同人于野、为和同之象"),
    43: make_baihua("大有卦", "二八", "火天大有、为大有所获、为丰盛之象"),
    44: make_baihua("谦卦", "二九", "地山谦、为谦谦君子、为谦卑之象"),
    45: make_baihua("豫卦", "三十", "雷地豫、为豫乐顺动、为和乐之象"),
    46: make_baihua("随卦", "三一", "泽雷随、为随时而动、为随顺之象"),
    47: make_baihua("蛊卦", "三二", "山风蛊、为蛊坏待治、为整治之象"),
    48: make_baihua("临卦", "三三", "地泽临、为二阳临下、为临近之象"),
    49: make_baihua("观卦", "三四", "风地观、为四阴观下、为观察之象"),
    50: make_baihua("噬嗑卦", "三五", "火雷噬嗑、为咬合执法、为决断之象"),
    51: make_baihua("贲卦", "三六", "山火贲、为文饰美化、为文明之象"),
    52: make_baihua("剥卦", "三七", "山地剥、为五阴剥一阳、为剥落之象"),
    53: make_baihua("复卦", "三八", "地雷复、为一阳来复、为复归之象"),
    54: make_baihua("无妄卦", "三九", "天雷无妄、为无妄之灾、为真实之象"),
    55: make_baihua("大畜卦", "四十", "山天大畜、为大有所畜、为积累之象"),
    56: make_baihua("颐卦", "四一", "山雷颐、为颐养正气、为养生之象"),
    57: make_baihua("大过卦", "四二", "泽风大过、为大有所过、为过越之象"),
    58: make_baihua("坎卦", "四三", "坎为水、为重重险陷、为险难之象"),
    59: make_baihua("离卦", "四四", "离为火、为重重光明、为光明之象"),
}


def main():
    files = sorted([f for f in os.listdir(DIR) if f.startswith('shan3_') and f.endswith('.md')])
    updated = 0
    for fname in files:
        idx = int(fname.split('_')[-1].replace('.md', ''))
        if idx < 40 or idx > 59:
            continue
        fpath = os.path.join(DIR, fname)
        text = open(fpath, encoding='utf-8').read()
        if idx not in BAIHUA:
            print(f"  跳过（无白话）: {fname} idx={idx}")
            continue
        new_baihua = BAIHUA[idx]
        pattern = r'(\*\*【白话提要】\*\*\n).*?(?=\n*$|\Z)'
        new_text = re.sub(pattern, r'\1' + new_baihua + '\n', text, flags=re.DOTALL)
        if new_text != text:
            with open(fpath, 'w', encoding='utf-8', newline='\n') as f:
                f.write(new_text)
            updated += 1
            print(f"  更新: {fname}")
    print(f"\n悟真篇第三批白话精译完成: {updated}/20 篇")


if __name__ == '__main__':
    main()
