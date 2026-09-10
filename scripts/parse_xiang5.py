# -*- coding: utf-8 -*-
"""
相部·地相细分：博山篇(8章) + 催官篇(4卷) 解析脚本

博山篇：五代黄妙应撰，形法派峦头代表作，论龙穴砂水明堂阳宅平地
催官篇：宋赖文俊(赖布衣)撰，天星风水代表作，评龙穴砂水四篇
元数据：category=xiang, subcategory=dixiang, type=chapter
  conditions 八键空，keywords 驱动召回
用法：python -X utf8 scripts/parse_xiang5.py
"""
import os
import re

BASE = r'D:\OneDrive\Desktop\111\ancient-text-library'


def write_entry(out_dir, idx_prefix, idx, book, title, content, author, dynasty, extra_kws, weight=4):
    eid = f"{idx_prefix}_{idx:02d}"
    kws = [book, "相部", "地相", "风水", "堪舆", author, title] + extra_kws
    tags = ["相部", "地相", "风水", book]
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
book: "{book}"
chapter: "{title}"
section_title: "{title}"
source_version: "中华典藏网"
author: "{author}"
dynasty: "{dynasty}"
type: "chapter"
conditions:
{cond}
weight: {weight}
tags: [{tags_str}]
---
"""
    body = f"### {title}\n\n"
    body += f"**【原文】**\n{content}\n\n"
    baihua = get_baihua(book, title, content)
    body += f"**【白话提要】**\n{baihua}\n"
    with open(os.path.join(out_dir, f"{idx_prefix}_{idx:02d}.md"), "w",
              encoding="utf-8", newline="\n") as f:
        f.write(fm + "\n" + body)


def get_baihua(book, title, content):
    if book == "博山篇":
        base = "本篇出自《博山篇》「" + title + "」，五代黄妙应（妙应禅师）撰，为形法派峦头风水代表作，专论山法龙穴砂水。博山篇以口诀体写成，语言简练，重在寻龙点穴的实操法则，论龙则辨枝干起伏、论穴则辨窝钳乳突、论砂则辨青龙白虎朝案、论水则辨来去曲折、论明堂则辨宽窄聚散、论阳宅则辨城乡格局、论平地则辨支干水法，为峦头风水入门之经典。"
        specific = {
            "概论相地法": "本篇为博山篇总纲，论相地之法，先看水来水去以定龙气发源与止聚，次看龙穴砂水明堂以定格局吉凶，强调到山场实地勘验，不可凭图臆断。",
            "论龙": "本篇专论寻龙之法，辨龙之枝干、起伏、剥换、过峡、入首，以龙之行止定气之聚散，以龙之贵贱定穴之吉凶，强调龙要起伏活动、剥换有情、过峡周密、入首端正。",
            "论穴": "本篇专论点穴之法，辨穴之窝钳乳突、阴阳动静、深浅高低，以穴证（毡唇、虾须、蟹眼、金鱼）定真穴，强调穴要乘气、藏风、得水，不可妄扦。",
            "论砂": "本篇专论认砂之法，辨青龙白虎、朝山案山、乐山鬼星、罗城水口，以砂之向背定穴之吉凶，强调砂要环抱有情、朝案端正、水口周密。",
            "论水": "本篇专论观水之法，辨水之来去、曲折、环抱、冲射、出口，以水之形势定气之聚散，强调水要弯环朝抱、出口有关，忌直冲反背。",
            "论明堂": "本篇专论明堂之法，辨明堂之宽窄、聚散、深浅、明暗，以明堂之格局定穴之吉凶，强调明堂要藏风聚气、宽狭得宜，忌空旷无收、逼窄难堪。",
            "论阳宅": "本篇专论阳宅之法，辨乡居与城居之不同，论胎息、阴阳、缓急、浮沉、起伏、龙虎、缠托、穿凿等九条杠，强调阳宅要乘气纳和、藏风聚气、人宅相扶。",
            "论平地": "本篇专论平地龙穴之法，以高山之理推平地，龙砂水堂原无二致，起一起便是山、低一低便是水、开一开便是钳，强调平地龙要支干分明、水法朝抱、穴位端正。",
        }
        return specific.get(title, base)
    elif book == "催官篇":
        base = "本篇出自《催官篇》「" + title + "」，宋赖文俊（字太素，号布衣子，世称赖布衣）撰，为天星风水代表作，以二十四山分阴阳、三吉六秀论龙穴砂水之吉凶。催官篇以歌诀体写成，专论天星方位与龙穴砂水的配合，以亥艮巽辛兑丁丙庚震壬癸十二位为三吉六秀，论其变换受穴之吉凶应，为理气派天星风水之经典。"
        specific = {
            "评龙章": "本篇专论评龙之法，以二十四山天星方位论龙之贵贱吉凶，首重天皇（亥）、天市（艮）、阳枢（巽）、阴枢（辛）等三吉六秀之龙，论其剥换、入首、受穴之吉凶，强调龙要得三吉六秀之位、剥换有情、入首端正。",
            "评穴章": "本篇专论评穴之法，以二十四山天星方位论穴之吉凶，分亥龙、艮龙、巽龙、辛龙、兑龙、丁龙、丙龙、庚龙、震龙、壬龙、癸龙等十二龙各论其立穴方位、耳受气法、朝向吉凶，强调穴要乘天星之气、耳受左气或右气、朝向合三吉六秀。",
            "评砂章": "本篇专论评砂之法，以二十四山天星方位论砂之吉凶，首言四维（乾坤艮巽）为贵人禄马之乡，次论二十四山各砂之尖秀、方圆、破碎所主吉凶，强调砂要尖秀耸拔、朝抱有情、合三吉六秀之位。",
            "评水章": "本篇专论评水之法，以二十四山天星方位论水之吉凶，首言催官之水惟三阳（巽丙丁），水朝砂秀则官爵强，次论二十四山各水之来去、朝抱、出口所主吉凶，强调水要朝抱有情、出口有关、合三阳六秀之位。",
        }
        return specific.get(title, base)
    return "本篇出自《" + book + "》「" + title + "」。"


def parse_book(src_file, out_dir, book, author, dynasty, idx_prefix, extra_kws_map):
    text = open(src_file, encoding='utf-8').read()
    parts = re.split(r'=== (.+?) ===', text)
    os.makedirs(out_dir, exist_ok=True)
    idx = 0
    for i in range(1, len(parts), 2):
        title = parts[i].strip()
        content = parts[i + 1].strip() if i + 1 < len(parts) else ""
        if len(content) >= 50:
            extra = extra_kws_map.get(title, [])
            write_entry(out_dir, idx_prefix, idx, book, title, content, author, dynasty, extra)
            idx += 1
    print(f"  {book}: {idx} 条 → {out_dir}")


def main():
    # 博山篇
    parse_book(
        os.path.join(BASE, 'raw/boshan-pian.txt'),
        os.path.join(BASE, 'library/xiang/dixiang/boshan-pian'),
        "博山篇", "黄妙应（妙应禅师）", "五代",
        "xiang5_bsp",
        {"概论相地法": ["相地法", "总纲", "寻龙"], "论龙": ["寻龙", "枝干", "剥换", "过峡"],
         "论穴": ["点穴", "窝钳乳突", "穴证"], "论砂": ["认砂", "青龙白虎", "朝案"],
         "论水": ["观水", "水法", "来去水"], "论明堂": ["明堂", "藏风聚气"],
         "论阳宅": ["阳宅", "阳宅风水", "城乡"], "论平地": ["平地龙", "平阳风水"]}
    )

    # 催官篇
    parse_book(
        os.path.join(BASE, 'raw/cuiguan-pian.txt'),
        os.path.join(BASE, 'library/xiang/dixiang/cuiguan-pian'),
        "催官篇", "赖文俊（字太素，号布衣子，赖布衣）", "宋",
        "xiang5_cgp",
        {"评龙章": ["天星龙", "三吉六秀", "亥龙", "艮龙"],
         "评穴章": ["天星穴", "二十四山", "耳受气", "立穴"],
         "评砂章": ["天星砂", "四维", "贵人禄马", "尖秀"],
         "评水章": ["天星水", "三阳水", "巽丙丁", "水朝"]}
    )


if __name__ == '__main__':
    main()
