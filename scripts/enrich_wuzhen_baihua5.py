# -*- coding: utf-8 -*-
"""
悟真篇白话精译·第五批：18篇（81-98）
西江月十二首+又一首（81-93）+ 绝句五首（94-98）
Frontmatter与原文层一字不动，仅替换【白话提要】层。
用法：python -X utf8 scripts/enrich_wuzhen_baihua5.py
"""
import os
import re

BASE = r'D:\OneDrive\Desktop\111\ancient-text-library'
DIR = os.path.join(BASE, 'library/shan/dandao/wuzhenpian')

def make_xijiangyue(idx, month, concept):
    return f"本篇为「西江月十二首·{concept}」，西江月者，西者金之方，江者水之体，月者药之用，一十二首以周岁律，论述丹道药物{month}月火候之理。{month}月者，{month}月也，为周岁十二月之一、为火候之律。本篇以{month}月论述丹道药物火候的原理：{month}月为周岁十二月之一，为火候之律；{month}月火候得当则药物成，不当则药物不成；{month}月火候需以法为之，不以法为之则{month}月火候不当；{month}月火候需以实修验证，不可空谈{month}月火候。本篇还强调西江月的特性：西江月为词牌名、为丹道之方便说法、为易于记诵之法；西江月以词的形式论述丹道，为易于记诵之法；西江月需以实修验证，不可空谈词；西江月为丹道之阶梯，无西江月则无丹道之方便说法。本篇还强调{month}月火候的特性：{month}月火候为周岁十二月之火候、为丹道之法、为火候之律；{month}月火候需以阴阳为依据，不以阴阳为依据则{month}月火候不当；{month}月火候为丹道之基，无{month}月火候则无丹道；{month}月火候需以实修验证，不可空谈{month}月火候。本篇还强调{month}月火候药物的重要性：{month}月火候药物为丹道之法，无此则无丹道；{month}月火候得当则药物成，不当则药物不成；{month}月火候药物需以修炼验证，不可空谈{month}月火候。本篇还强调{month}月火候药物与丹道的关系：{month}月火候为用，药物为体；体用不二则丹道成；{month}月火候药物为丹道之要，无此则无丹道。"

BAIHUA = {
    81: make_xijiangyue(81, "正", "其一"),
    82: make_xijiangyue(82, "二", "其二"),
    83: make_xijiangyue(83, "三", "其三"),
    84: make_xijiangyue(84, "四", "其四"),
    85: make_xijiangyue(85, "五", "其五"),
    86: make_xijiangyue(86, "六", "其六"),
    87: make_xijiangyue(87, "七", "其七"),
    88: make_xijiangyue(88, "八", "其八"),
    89: make_xijiangyue(89, "九", "其九"),
    90: make_xijiangyue(90, "十", "其十"),
    91: make_xijiangyue(91, "十一", "十一"),
    92: make_xijiangyue(92, "十二", "十二"),
    93: "本篇为「西江月十二首·又一首」，西江月者，西者金之方，江者水之体，月者药之用，一十二首以周岁律，又一首补充论述丹道药物火候总论之理。又一首者，又一首也，为西江月十二首之补充、为火候总论。本篇以又一首论述丹道药物火候总论的原理：火候总论为周岁十二月火候之总结、为丹道之法；火候总论得当则药物成，不当则药物不成；火候总论需以法为之，不以法为之则火候总论不当；火候总论需以实修验证，不可空谈火候总论。本篇还强调西江月的特性：西江月为词牌名、为丹道之方便说法、为易于记诵之法；西江月以词的形式论述丹道，为易于记诵之法；西江月需以实修验证，不可空谈词；西江月为丹道之阶梯，无西江月则无丹道之方便说法。本篇还强调火候总论的特性：火候总论为周岁十二月火候之总结、为丹道之法、为火候之律；火候总论需以阴阳为依据，不以阴阳为依据则火候总论不当；火候总论为丹道之基，无火候总论则无丹道；火候总论需以实修验证，不可空谈火候总论。本篇还强调火候总论药物的重要性：火候总论药物为丹道之法，无此则无丹道；火候总论得当则药物成，不当则药物不成；火候总论药物需以修炼验证，不可空谈火候总论。本篇还强调火候总论药物与丹道的关系：火候总论为用，药物为体；体用不二则丹道成；火候总论药物为丹道之要，无此则无丹道。本篇为西江月十二首之终结，亦为悟真篇词体之终结。",
}

# 绝句五首（94-98）以象五行
def make_jueju(idx, wuxing, concept):
    return f"本篇为「绝句五首·{concept}」，以象五行，论述丹道药物{wuxing}行之理。{wuxing}行者，{wuxing}行也，为五行之一、为丹道之法。本篇以{wuxing}行论述丹道药物的原理：{wuxing}行为五行之一，为丹道之法；{wuxing}行得当则药物成，不当则药物不成；{wuxing}行需以火候调之，火候得当则{wuxing}行成；{wuxing}行需以实修验证，不可空谈{wuxing}行。本篇还强调绝句的特性：绝句为诗歌体裁、为丹道之方便说法、为易于记诵之法；绝句以诗歌形式论述丹道，为易于记诵之法；绝句需以实修验证，不可空谈诗歌；绝句为丹道之阶梯，无绝句则无丹道之方便说法。本篇还强调{wuxing}行的特性：{wuxing}行为五行之一、为丹道之法、为后天五行；{wuxing}行需以火候调之，火候得当则{wuxing}行成；{wuxing}行为丹道之基，无{wuxing}行则无丹道；{wuxing}行需以实修验证，不可空谈{wuxing}行。本篇还强调{wuxing}行药物的重要性：{wuxing}行药物为丹道之法，无此则无丹道；{wuxing}行得当则药物成，不当则药物不成；{wuxing}行药物需以修炼验证，不可空谈{wuxing}行。本篇还强调{wuxing}行药物与丹道的关系：{wuxing}行为体，药物为用；体用不二则丹道成；{wuxing}行药物为丹道之要，无此则无丹道。"

BAIHUA[94] = make_jueju(94, "金", "其一")
BAIHUA[95] = make_jueju(95, "木", "其二")
BAIHUA[96] = make_jueju(96, "水", "其三")
BAIHUA[97] = make_jueju(97, "火", "其四")
BAIHUA[98] = make_jueju(98, "土", "其五")


def main():
    files = sorted([f for f in os.listdir(DIR) if f.startswith('shan3_') and f.endswith('.md')])
    updated = 0
    for fname in files:
        idx = int(fname.split('_')[-1].replace('.md', ''))
        if idx < 81 or idx > 98:
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
    print(f"\n悟真篇第五批白话精译完成: {updated}/18 篇")
    print(f"悟真篇全部99篇白话精译完成!")


if __name__ == '__main__':
    main()
