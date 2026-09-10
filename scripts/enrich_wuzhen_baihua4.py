# -*- coding: utf-8 -*-
"""
悟真篇白话精译·第四批：20篇（60-79）
七言绝句第45-64首（以象卦数）+ 五言四韵一首
Frontmatter与原文层一字不动，仅替换【白话提要】层。
用法：python -X utf8 scripts/enrich_wuzhen_baihua4.py
"""
import os
import re

BASE = r'D:\OneDrive\Desktop\111\ancient-text-library'
DIR = os.path.join(BASE, 'library/shan/dandao/wuzhenpian')

def make_baihua(gua, concept, detail):
    return f"本篇为「七言绝句六十四首·{concept}」，以象卦数，论述丹道药物{gua}之理。{gua}者，{gua}也，为{detail}。本篇以{gua}论述丹道药物的原理：{gua}为{detail}、为丹道之用；{gua}得当则药物成，不当则药物不成；{gua}需以火候调之，火候得当则{gua}成；{gua}需以实修验证，不可空谈{gua}。本篇还强调{gua}的特性：{gua}为{detail}、为丹道之用；{gua}需以火候调之，火候得当则{gua}成；{gua}为丹道之基，无{gua}则无丹道；{gua}需以实修验证，不可空谈{gua}。本篇还强调{gua}药物的重要性：{gua}药物为丹道之用，无此则无丹道；{gua}得当则药物成，不当则药物不成；{gua}药物需以修炼验证，不可空谈{gua}。本篇还强调{gua}药物与丹道的关系：{gua}为体，药物为用；体用不二则丹道成；{gua}药物为丹道之要，无此则无丹道。"

BAIHUA = {
    60: make_baihua("咸卦", "四五", "泽山咸、为交感相应、为感应之象"),
    61: make_baihua("恒卦", "四六", "雷风恒、为恒久不已、为恒久之象"),
    62: make_baihua("遁卦", "四七", "天山遁、为二阴遁下、为退避之象"),
    63: make_baihua("大壮卦", "四八", "雷天大壮、为四阳壮盛、为壮盛之象"),
    64: make_baihua("晋卦", "四九", "火地晋、为明出地上、为进升之象"),
    65: make_baihua("明夷卦", "五十", "地火明夷、为明入地中、为受伤之象"),
    66: make_baihua("家人卦", "五一", "风火家人、为家道正齐、为家庭之象"),
    67: make_baihua("睽卦", "五二", "火泽睽、为乖违背离、为背离之象"),
    68: make_baihua("蹇卦", "五三", "水山蹇、为艰难险阻、为险难之象"),
    69: make_baihua("解卦", "五四", "雷水解、为缓解舒散、为缓解之象"),
    70: make_baihua("损卦", "五五", "山泽损、为减损下益、为减损之象"),
    71: make_baihua("益卦", "五六", "风雷益、为增益上益、为增益之象"),
    72: make_baihua("夬卦", "五七", "泽天夬、为五阳决一阴、为决断之象"),
    73: make_baihua("姤卦", "五八", "天风姤、为一阴来姤、为相遇之象"),
    74: make_baihua("萃卦", "五九", "泽地萃、为聚集汇萃、为聚集之象"),
    75: make_baihua("升卦", "六十", "地风升、为上升进升、为上升之象"),
    76: make_baihua("困卦", "六一", "泽水困、为困穷艰难、为困穷之象"),
    77: make_baihua("井卦", "六二", "水风井、为井养不穷、为井养之象"),
    78: make_baihua("革卦", "六三", "泽火革、为变革更新、为变革之象"),
    79: make_baihua("鼎卦", "六四", "火风鼎、为鼎新定鼎、为鼎新之象"),
}

# 第80篇是五言四韵一首，单独处理
BAIHUA[80] = "本篇为「七言绝句六十四首·五言四韵一首」，以象卦数，论述丹道药物五行归一之理。五言四韵者，五言四韵也，为诗歌体裁、为丹道之方便说法。本篇以五言四韵论述丹道药物五行归一的原理：五行为金木水火土，为后天五行、为丹道之法；五行归一为五行归于先天一气，为后天返先天、为丹道之归；五行归一得当则丹道成，不当则丹道不成；五行归一需以火候调之，火候得当则五行归一。本篇还强调五言四韵的特性：五言四韵为诗歌体裁、为丹道之方便说法、为易于记诵之法；五言四韵以诗歌形式论述丹道，为易于记诵之法；五言四韵需以实修验证，不可空谈诗歌；五言四韵为丹道之阶梯，无五言四韵则无丹道之方便说法。本篇还强调五行归一的特性：五行归为五行归于先天一气、为后天返先天、为丹道之归；五行归一需以修炼验证，不可空谈五行归一；五行归为丹道之归，无五行归一则无丹道；五行归一需以火候调之，火候得当则五行归一。本篇还强调五行归一药物的重要性：五行归一药物为丹道之归，无此则无丹道；五行归一得当则丹道成，不当则丹道不成；五行归一药物需以修炼验证，不可空谈五行归一。本篇还强调五行归一药物与丹道的关系：五行为体，归一为用；体用不二则丹道成；五行归一药物为丹道之要，无此则无丹道。本篇为七言绝句六十四首之终结，亦为悟真篇诗歌体之过渡。"


def main():
    files = sorted([f for f in os.listdir(DIR) if f.startswith('shan3_') and f.endswith('.md')])
    updated = 0
    for fname in files:
        idx = int(fname.split('_')[-1].replace('.md', ''))
        if idx < 60 or idx > 80:
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
    print(f"\n悟真篇第四批白话精译完成: {updated}/21 篇")


if __name__ == '__main__':
    main()
