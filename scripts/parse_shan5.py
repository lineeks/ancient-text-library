# -*- coding: utf-8 -*-
"""
山部第五批·五禽戏解析脚本（纯标准库，确定性输出）

底本：raw/wuqinxi.txt（《太上老君养生诀》，汉末华佗授广陵吴普，中国道教协会）
  2.2KB，五禽戏总述+虎/鹿/熊/猿/鸟5戏+服气吐纳六气+养生真诀+服气诀 = 9条
  中国古代导引养生功法，华佗所创，模仿五种动物动作
切分：按「虎戏/鹿戏/熊戏/猿戏/鸟戏」「服气吐纳六气第二」「养生真诀第三」「服气诀」切分
元数据：category=shan, subcategory=yangsheng, type=chapter, conditions 八键全空
召回：keywords 驱动（五禽戏/华佗/导引/虎戏/鹿戏/熊戏/猿戏/鸟戏/
  服气吐纳/六字诀/养生真诀/玄牝/握固 等）
用法：python -X utf8 scripts/parse_shan5.py
"""
import os
import re

BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def extract_keywords(text):
    kws = ["五禽戏", "山部", "养生", "导引", "华佗"]
    mapping = [
        (r"虎戏", "虎戏"),
        (r"鹿戏", "鹿戏"),
        (r"熊戏", "熊戏"),
        (r"猿戏", "猿戏"),
        (r"鸟戏", "鸟戏"),
        (r"服气吐纳|六气|呬字|呵字|呼字|嘘字|吹字|嘻字", "服气吐纳六气"),
        (r"养生真诀|六害|少思|少念", "养生真诀"),
        (r"服气诀|玄牝|握固|吐故纳新", "服气诀"),
        (r"五禽第一|老君曰|古之仙者", "五禽戏总述"),
        (r"吴普|广陵", "华佗授吴普"),
    ]
    for pattern, kw in mapping:
        if re.search(pattern, text):
            kws.append(kw)
    return list(dict.fromkeys(kws))


def main():
    src = os.path.join(BASE, "raw/wuqinxi.txt")
    out_dir = os.path.join(BASE, "library", "shan", "yangsheng", "wuqinxi")
    os.makedirs(out_dir, exist_ok=True)

    text = open(src, encoding="utf-8").read()
    lines = text.split("\n")

    entries = []
    current_title = None
    current_content = []
    section = ""

    # 切分标记
    markers = [
        ("五禽第一", "五禽戏总述"),
        ("虎戏：", "虎戏"),
        ("鹿戏：", "鹿戏"),
        ("熊戏：", "熊戏"),
        ("猿戏：", "猿戏"),
        ("鸟戏：", "鸟戏"),
        ("服气吐纳六气第二", "服气吐纳六气"),
        ("养生真诀第三", "养生真诀"),
        ("服气诀", "服气诀"),
    ]

    for line in lines:
        s = line.strip()

        # 检查是否是新条目标记
        matched = False
        for marker, title in markers:
            if s.startswith(marker):
                if current_title and current_content:
                    entries.append((section, current_title, "\n".join(current_content).strip()))
                current_title = title
                section = title
                current_content = []
                # 如果标记行后面还有内容，加入正文
                rest = s[len(marker):].strip()
                if rest:
                    current_content.append(rest)
                matched = True
                break

        if not matched and current_title and s:
            current_content.append(s)

    # 最后一条
    if current_title and current_content:
        entries.append((section, current_title, "\n".join(current_content).strip()))

    # 写入文件
    for idx, (sec, title, content) in enumerate(entries):
        eid = f"shan5_wqx_{idx:03d}"
        kws = extract_keywords(sec + title + content[:2000])
        tags = ["山部", "养生", "五禽戏", "导引", "华佗"]
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
book: "五禽戏（太上老君养生诀）"
chapter: "{sec}"
section_title: "{title[:30]}"
source_version: "中国道教协会《太上老君养生诀》（汉末华佗授广陵吴普）"
author: "华佗授，吴普传"
dynasty: "汉末"
type: "chapter"
conditions:
{cond}
weight: 4
tags: [{tags_str}]
---
"""
        body = f"### {title}\n\n"
        body += f"**【原文】**\n{content}\n\n"
        body += f"**【白话提要】**\n此条出自《太上老君养生诀》「{title}」，为汉末华佗所授、广陵吴普所传的古代导引养生功法原文。五禽戏模仿虎、鹿、熊、猿、鸟五种动物的动作，通过挽引肤体、动诸关节以求难老，体中不快时起作一禽之戏，以汗出为限，可轻身、消谷气、益气力、除百病。服气吐纳六气以呬呵呼嘘吹嘻六字对应肺心脾肝肾三焦，养生真诀主张除六害、保性命，服气诀以玄牝门为天地根、吐故纳新。五禽戏为中国古代导引养生之经典功法，与八段锦、易筋经并称养生三典。\n"
        with open(os.path.join(out_dir, f"shan5_wqx_{idx:03d}.md"), "w",
                  encoding="utf-8", newline="\n") as f:
            f.write(fm + "\n" + body)

    print(f"  五禽戏: {len(entries)} 条 → {out_dir}")


if __name__ == "__main__":
    main()
