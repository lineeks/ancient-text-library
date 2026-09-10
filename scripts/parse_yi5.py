# -*- coding: utf-8 -*-
"""
医部·金匮要略解析脚本（纯标准库，确定性输出）

底本：raw/jinkui-yaolue.txt（中华典藏网译注本+古诗文网补第十四篇，180KB，25篇）
  东汉张仲景撰，《伤寒杂病论》杂病部分，方书之祖，载方262首
切分：25篇，每篇一条
元数据：category=yi, subcategory=jingdian, type=chapter
  conditions 八键空（医部不依赖八字字段），keywords 驱动召回
召回：keywords（金匮要略/张仲景/杂病/方书之祖/具体篇名/病症名）
用法：python -X utf8 scripts/parse_yi5.py
"""
import os
import re

BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# 25篇标题与关键词映射
CHAPTERS = [
    ("脏腑经络先后病脉证第一", ["治未病", "脏腑传变", "肝传脾", "四季脾旺", "虚实"]),
    ("痉湿暍病脉证治第二", ["痉病", "湿病", "暍病", "中暍", "太阳病", "发热"]),
    ("百合狐惑阴阳毒病脉证治第三", ["百合病", "狐惑病", "阴阳毒", "百合地黄汤"]),
    ("疟病脉证并治第四", ["疟疾", "疟母", "鳖甲煎丸", "温疟", "牝疟"]),
    ("中风历节病脉证并治第五", ["中风", "历节", "脚气", "桂枝芍药知母汤", "乌头汤"]),
    ("血痹虚劳病脉证并治第六", ["血痹", "虚劳", "黄芪桂枝五物汤", "肾气丸", "虚劳病"]),
    ("肺痿肺痈咳嗽上气病脉证治第七", ["肺痿", "肺痈", "咳嗽", "上气", "葶苈大枣泻肺汤"]),
    ("奔豚气病脉证治第八", ["奔豚气", "奔豚汤", "桂枝加桂汤", "气上冲"]),
    ("胸痹心痛短气病脉证治第九", ["胸痹", "心痛", "短气", "瓜蒌薤白白酒汤", "枳实薤白桂枝汤"]),
    ("腹满寒疝宿食病脉证治第十", ["腹满", "寒疝", "宿食", "大建中汤", "乌头煎"]),
    ("五脏风寒积聚病脉证并治第十一", ["五脏风寒", "积聚", "肝着", "肾着", "脾约"]),
    ("痰饮咳嗽病脉证并治第十二", ["痰饮", "悬饮", "溢饮", "支饮", "苓桂术甘汤", "十枣汤"]),
    ("消渴小便不利淋病脉证并治第十三", ["消渴", "小便不利", "淋病", "五苓散", "猪苓汤", "肾气丸"]),
    ("水气病脉证并治第十四", ["水气病", "风水", "皮水", "正水", "石水", "黄汗", "越婢汤", "防己黄芪汤"]),
    ("黄疸病脉证并治第十五", ["黄疸", "谷疸", "酒疸", "女劳疸", "茵陈蒿汤", "栀子大黄汤"]),
    ("惊悸吐血下血胸满瘀血病脉证治第十六", ["惊悸", "吐血", "下血", "胸满", "瘀血", "泻心汤", "黄土汤"]),
    ("呕吐哕下利病脉证治第十七", ["呕吐", "哕", "下利", "吴茱萸汤", "半夏泻心汤", "葛根芩连汤"]),
    ("疮痈肠痈浸淫病脉证并治第十八", ["疮痈", "肠痈", "浸淫病", "大黄牡丹汤", "薏苡附子败酱散"]),
    ("趺蹶手指臂肿转筋阴狐疝蛔虫病脉证治第十九", ["趺蹶", "手指臂肿", "转筋", "阴狐疝", "蛔虫", "乌梅丸"]),
    ("妇人妊娠病脉证并治第二十", ["妇人妊娠", "妊娠病", "胶艾汤", "当归芍药散", "桂枝茯苓丸"]),
    ("妇人产后病脉证治第二十一", ["妇人产后", "产后病", "产后腹痛", "枳实芍药散", "下瘀血汤"]),
    ("妇人杂病脉证并治第二十二", ["妇人杂病", "梅核气", "脏躁", "甘麦大枣汤", "半夏厚朴汤"]),
    ("杂疗方第二十三", ["杂疗方", "急救", "猝死", "救卒死", "备急丸"]),
    ("禽兽鱼虫禁忌并治第二十四", ["禽兽鱼虫禁忌", "饮食禁忌", "食物中毒", "肉食禁忌"]),
    ("果实菜谷禁忌并治第二十五", ["果实菜谷禁忌", "饮食禁忌", "谷物禁忌", "果实禁忌"]),
]


def write_entry(out_dir, idx, title, content, extra_kws):
    eid = f"yi5_jkyl_{idx:02d}"
    kws = ["金匮要略", "医部", "张仲景", "杂病", "方书之祖", "伤寒杂病论", title] + extra_kws
    tags = ["医部", "经典", "金匮要略", "张仲景"]
    cond_lines = [
        '  day_master: []',
        '  month_branch: []',
        '  day_pillar: []',
        '  hour_pillar: []',
        '  ten_god: []',
        '  pattern: []',
        '  shensha: []',
        f'  keywords: [{", ".join(chr(34)+k+chr(34) for k in kws)}]',
    ]
    cond = "\n".join(cond_lines)
    tags_str = ", ".join(f'"{t}"' for t in tags)
    fm = f"""---
id: "{eid}"
book: "金匮要略"
chapter: "{title}"
section_title: "{title}"
source_version: "中华典藏网译注本（邓珍本系统）"
author: "张仲景（名机，字仲景，东汉南阳人，医圣）"
dynasty: "东汉"
type: "chapter"
conditions:
{cond}
weight: 5
tags: [{tags_str}]
---
"""
    body = f"### {title}\n\n"
    body += f"**【原文】**\n{content}\n\n"
    body += f"**【白话提要】**\n此条出自《金匮要略》「{title}」，东汉张仲景撰，为《伤寒杂病论》杂病部分，方书之祖，载方262首。金匮要略以内科杂病为主，兼及外科、妇科、急救、饮食禁忌，确立辨证论治原则，所收方剂配伍严谨、用药精当，许多名方至今仍广泛应用于临床。\n"
    with open(os.path.join(out_dir, f"yi5_jkyl_{idx:02d}.md"), "w",
              encoding="utf-8", newline="\n") as f:
        f.write(fm + "\n" + body)


def main():
    src = os.path.join(BASE, "raw/jinkui-yaolue.txt")
    out_dir = os.path.join(BASE, "library", "yi", "jingdian", "jinkui-yaolue")
    os.makedirs(out_dir, exist_ok=True)

    text = open(src, encoding="utf-8").read()

    # 按 === 标题 === 切分
    parts = re.split(r'=== (.+?) ===', text)
    # parts[0] 是空，parts[1]是标题1，parts[2]是内容1，parts[3]是标题2...

    idx = 0
    for i in range(1, len(parts), 2):
        title = parts[i].strip()
        content = parts[i + 1].strip() if i + 1 < len(parts) else ""
        if len(content) >= 50:
            # 找匹配的关键词
            extra_kws = []
            for chap_title, kws in CHAPTERS:
                if chap_title[:4] in title or title[:4] in chap_title:
                    extra_kws = kws
                    break
            write_entry(out_dir, idx, title, content, extra_kws)
            idx += 1

    print(f"  金匮要略: {idx} 条 → {out_dir}")


if __name__ == "__main__":
    main()
