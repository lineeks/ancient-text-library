# -*- coding: utf-8 -*-
"""
医部·伤寒论解析脚本（纯标准库，确定性输出）

底本：raw/shanghan-lun.txt（中华典藏网，22篇，53KB）
  东汉张仲景撰，晋王叔和编次，宋林亿校定，六经辨证奠基之作
  397法，113方，82种药物
切分：22篇，每篇一条
元数据：category=yi, subcategory=jingdian, type=chapter
  conditions 八键空（医部不依赖八字字段），keywords 驱动召回
用法：python -X utf8 scripts/parse_yi6.py
"""
import os
import re

BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# 22篇关键词映射
CHAPTER_KWS = {
    "辩脉法": ["脉法", "脉象", "脉诊", "辨脉", "寸口脉"],
    "平脉法": ["平脉", "脉法", "脉象", "脉诊", "旺脉"],
    "伤寒例": ["伤寒例", "时行", "瘟疫", "寒疫", "四时正气"],
    "辨痉湿暍脉证": ["痉病", "湿病", "暍病", "中暍", "太阳病"],
    "辨太阳病脉证并治法上": ["太阳病", "中风", "伤寒", "桂枝汤", "麻黄汤", "表证"],
    "辨太阳病脉证并治中": ["太阳病", "葛根汤", "青龙汤", "五苓散", "结胸", "痞证"],
    "辨太阳病脉证并治下": ["太阳病", "结胸", "脏结", "痞证", "半夏泻心汤", "火逆"],
    "辨阳明病脉证并治法": ["阳明病", "胃家实", "白虎汤", "承气汤", "下法", "潮热"],
    "辨少阳病脉证并治": ["少阳病", "小柴胡汤", "口苦咽干", "目眩", "半表半里"],
    "辨太阴病脉证并治": ["太阴病", "脾家实", "腹满而吐", "理中汤", "四逆汤"],
    "辨少阴病脉证并治": ["少阴病", "脉微细", "但欲寐", "四逆汤", "真武汤", "黄连阿胶汤"],
    "辨厥阴病脉证并治": ["厥阴病", "消渴", "气上撞心", "厥逆", "乌梅丸", "当归四逆汤"],
    "辨霍乱病脉证并治": ["霍乱", "呕吐", "下利", "五苓散", "理中汤"],
    "辨阴阳易差后劳复病脉证并治": ["阴阳易", "差后劳复", "烧裈散", "枳实栀子豉汤"],
    "辨不可发汗病脉证并治": ["不可发汗", "汗法禁忌", "误汗"],
    "辨可发汗脉证并治": ["可发汗", "汗法", "桂枝汤", "麻黄汤"],
    "辨发汗后病脉证并治": ["发汗后", "汗后变证", "汗后调理"],
    "辨不可吐": ["不可吐", "吐法禁忌"],
    "辨可吐": ["可吐", "吐法", "瓜蒂散"],
    "辨不可下病脉证并治": ["不可下", "下法禁忌", "误下"],
    "辨可下病脉证并治": ["可下", "下法", "承气汤", "大柴胡汤"],
    "辨发汗吐下后脉证并治": ["发汗吐下后", "误治变证", "救逆"],
}


def write_entry(out_dir, idx, title, content):
    eid = f"yi6_shl_{idx:02d}"
    extra_kws = CHAPTER_KWS.get(title, [])
    kws = ["伤寒论", "医部", "张仲景", "六经辨证", "王叔和", "伤寒杂病论", title] + extra_kws
    tags = ["医部", "经典", "伤寒论", "张仲景", "六经辨证"]
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
book: "伤寒论"
chapter: "{title}"
section_title: "{title}"
source_version: "中华典藏网（宋治平二年林亿校定本系统）"
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
    body += f"**【白话提要】**\n此条出自《伤寒论》「{title}」，东汉张仲景撰，晋王叔和编次，宋林亿校定，为六经辨证奠基之作，中医临床医学之经典。伤寒论以六经（太阳、阳明、少阳、太阴、少阴、厥阴）辨证为纲，全面系统论述外感热病各期辨证原则及立法用药规律，共397法、113方、应用药物82种，确立辨证论治原则，所收方剂配伍严谨，许多名方至今仍广泛应用于临床。\n"
    with open(os.path.join(out_dir, f"yi6_shl_{idx:02d}.md"), "w",
              encoding="utf-8", newline="\n") as f:
        f.write(fm + "\n" + body)


def main():
    src = os.path.join(BASE, "raw/shanghan-lun.txt")
    out_dir = os.path.join(BASE, "library", "yi", "jingdian", "shanghan")
    os.makedirs(out_dir, exist_ok=True)

    text = open(src, encoding="utf-8").read()

    # 按 === 标题 === 切分
    parts = re.split(r'=== (.+?) ===', text)

    idx = 0
    for i in range(1, len(parts), 2):
        title = parts[i].strip()
        content = parts[i + 1].strip() if i + 1 < len(parts) else ""
        if len(content) >= 50:
            write_entry(out_dir, idx, title, content)
            idx += 1

    print(f"  伤寒论: {idx} 条 → {out_dir}")


if __name__ == "__main__":
    main()
