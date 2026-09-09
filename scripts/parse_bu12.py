# -*- coding: utf-8 -*-
"""
卜部第十二批·黄金策总断千金赋直解解析脚本（纯标准库，确定性输出）

底本：raw/huangjince.txt（从 mahavivo/scripta-sinica 卜筮正宗全本提取）
  25.4KB，黄金策总断千金赋直解（明刘诚意伯温撰，清王洪绪注）
  含总断千金赋总论 + 天时/年时/国朝/征战/身命/婚姻/产育/病症/
  病体/医药/鬼神/种作/蚕桑/六畜/求名/仕宦/求财/家宅/坟墓/求师/
  学馆/词讼/避乱/逃亡/失脱/出行/行人/舟船/娼家 等约30个占断类目
切分：总断千金赋1条 + 各占断类目约28条 = 约29条
元数据：category=bu, subcategory=liuyao, type=chapter, conditions 八键全空
召回：keywords 驱动（黄金策/总断千金赋/刘基/刘伯温/王洪绪/各占断类目名）
用法：python -X utf8 scripts/parse_bu12.py
"""
import os
import re

BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# 占断类目（按出现顺序）
CATEGORIES = [
    "总断千金赋",
    "天时",
    "年时",
    "国朝",
    "征战",
    "身命",
    "婚姻",
    "产育",
    "病症",
    "病体",
    "医药",
    "鬼神",
    "种作",
    "蚕桑",
    "六畜",
    "求名",
    "仕宦",
    "求财",
    "家宅",
    "坟墓",
    "求师",
    "学馆",
    "词讼",
    "避乱",
    "逃亡",
    "失脱",
    "出行",
    "行人",
    "舟船",
    "娼家",
]


def extract_keywords(text, category):
    kws = ["黄金策", "总断千金赋", "卜部", "六爻", "刘基", "刘伯温", "王洪绪", category]
    mapping = [
        (r"动静阴阳|太过者损之|生扶拱合|克害刑冲", "总断千金赋"),
        (r"天道杳冥|旱潦|阴晴|妻财发动|父母", "天时占"),
        (r"年时|太岁|岁君|年丰", "年时占"),
        (r"国朝|朝廷|君上|社稷", "国朝占"),
        (r"征战|用兵|将帅|胜负", "征战占"),
        (r"身命|终身|寿夭|贫贱", "身命占"),
        (r"婚姻|嫁娶|婚配|媒妁", "婚姻占"),
        (r"产育|生产|胎孕|临产", "产育占"),
        (r"病症|疾病|病因|症候", "病症占"),
        (r"病体|病人|患者|病情", "病体占"),
        (r"医药|医生|用药|药石", "医药占"),
        (r"鬼神|邪崇|祭祀|祈祷", "鬼神占"),
        (r"种作|农桑|田禾|五谷", "种作占"),
        (r"蚕桑|蚕丝|蚕事|桑叶", "蚕桑占"),
        (r"六畜|牛马|猪羊|禽鸟", "六畜占"),
        (r"求名|功名|科甲|科举", "求名占"),
        (r"仕宦|官运|升迁|官职", "仕宦占"),
        (r"求财|财运|买卖|货财", "求财占"),
        (r"家宅|阳宅|宅舍|门户", "家宅占"),
        (r"坟墓|阴宅|葬地|龙脉", "坟墓占"),
        (r"求师|师傅|老师|学艺", "求师占"),
        (r"学馆|书馆|学堂|读书", "学馆占"),
        (r"词讼|官讼|官司|诉讼", "词讼占"),
        (r"避乱|避祸|逃难|避兵", "避乱占"),
        (r"逃亡|逃人|逃犯|走失", "逃亡占"),
        (r"失脱|失物|丢失|遗失", "失脱占"),
        (r"出行|出门|远行|登程", "出行占"),
        (r"行人|来人|归期|音信", "行人占"),
        (r"舟船|船行|水路|舟楫", "舟船占"),
        (r"娼家|妓院|青楼|花柳", "娼家占"),
    ]
    for pattern, kw in mapping:
        if re.search(pattern, text):
            kws.append(kw)
    return list(dict.fromkeys(kws))


def main():
    src = os.path.join(BASE, "raw/huangjince.txt")
    out_dir = os.path.join(BASE, "library", "bu", "liuyao", "huangjince")
    os.makedirs(out_dir, exist_ok=True)

    text = open(src, encoding="utf-8").read()

    # 找各类目位置
    positions = []
    # 总断千金赋从开头开始
    positions.append((0, "总断千金赋"))
    for cat in CATEGORIES[1:]:
        # 类目标题通常是独立行（\nXX\n）
        for m in re.finditer(rf'\n{cat}\n', text):
            pos = m.start() + 1
            if pos > 100:  # 跳过开头的总断部分
                positions.append((pos, cat))
                break

    positions.sort()
    # 去重（同一位置只保留一个）
    seen = set()
    unique_positions = []
    for pos, cat in positions:
        if pos not in seen:
            seen.add(pos)
            unique_positions.append((pos, cat))
    positions = unique_positions

    # 切分
    entries = []
    for i, (pos, cat) in enumerate(positions):
        end = positions[i + 1][0] if i + 1 < len(positions) else len(text)
        content = text[pos:end].strip()
        # 去掉标题行
        content = re.sub(rf'^{cat}[：:]\s*', '', content)
        if len(content) >= 100:
            entries.append((cat, content))

    # 写入文件
    for idx, (cat, content) in enumerate(entries):
        eid = f"bu9_hjc_{idx:03d}"
        kws = extract_keywords(content[:3000], cat)
        tags = ["卜部", "六爻", "黄金策", "总断千金赋"]
        cond = "\n".join([
            '  day_master: []',
            '  month_branch: []',
            '  day_pillar: []',
            '  hour_pillar: []',
            '  ten_god: []',
            '  pattern: []',
            '  shensha: []',
            f'  keywords: [{", ".join(chr(34)+k+chr(34) for k in kws)}]',
        ])
        tags_str = ", ".join(f'"{t}"' for t in tags)
        fm = f"""---
id: "{eid}"
book: "黄金策总断千金赋直解"
chapter: "黄金策·{cat}"
section_title: "{cat}"
source_version: "mahavivo/scripta-sinica 卜筮正宗全本（明刘基伯温撰，清王洪绪注）"
author: "刘基（字伯温，号诚意伯）"
dynasty: "明"
annotator: "王洪绪（字维德，号林屋先生）"
type: "chapter"
conditions:
{cond}
weight: 6
tags: [{tags_str}]
---
"""
        body = f"### {cat}\n\n"
        body += f"**【原文】**\n{content}\n\n"
        body += f"**【白话提要】**\n此条出自《黄金策总断千金赋直解》「{cat}」篇，为明代刘基（字伯温，号诚意伯）所撰，清代王洪绪（字维德，号林屋先生）作注的六爻占断总纲原文。黄金策总断千金赋为六爻学之集大成之作，系统阐述六爻占断之核心原理与各类占断法门，以动静阴阳、生克制化、刑冲合害、空破墓绝为根本，分天时、年时、国朝、征战、身命、婚姻、产育、病症、医药、鬼神、种作、蚕桑、六畜、求名、仕宦、求财、家宅、坟墓、词讼、逃亡、失脱、出行、行人等三十余类占断，为后世六爻占断之圭臬，卜筮正宗全书即以诠解黄金策为核心。\n"
        with open(os.path.join(out_dir, f"bu9_hjc_{idx:03d}.md"), "w",
                  encoding="utf-8", newline="\n") as f:
            f.write(fm + "\n" + body)

    print(f"  黄金策: {len(entries)} 条 → {out_dir}")


if __name__ == "__main__":
    main()
