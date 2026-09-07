# -*- coding: utf-8 -*-
"""
Aether-Cycle 古籍知识库 · 《神峰通考》结构化解析脚本（第三梯队·实战辨惑）
源文：明·张楠（张神峰）著，带现代标点电子本。核心为「病药说」「雕枯旺弱四病」
「损益生长四药」，力辟虚妄神煞、重五行生克实战。
章节为独立短标题（以 说类/类/说/论/赋/歌/篇/诀 结尾），自动发现并按顺序切分。
输出：extended/shenfengtongkao/sftk_<两位序号>_<slug>.md
"""
import os
import re

BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
RAW = os.path.join(BASE, "raw", "shenfengtongkao.txt")
OUT = os.path.join(BASE, "library", "ming", "bazi", "extended", "shenfengtongkao")
os.makedirs(OUT, exist_ok=True)

TITLE_RE = re.compile(r"(说类|论|赋|歌|篇|诀|说|类)$")
PUNCT = "，。；：、？！,.;:?!？"

# 标题（规范名）-> slug；按源文顺序
SLUG = {
    "五星正说类": "wuxing_zhengshuo", "五星谬说类": "wuxing_miushuo",
    "男女合婚说": "nanv_hehun", "总论子平谬说类": "ziping_miushuo",
    "动静说": "dongjing", "盖头说": "gaitou", "六亲说": "liuqin",
    "病药说类": "bingyao", "雕枯旺弱四病说类": "diaoku_wangruo_sibing",
    "损益生长四药说类": "sunyi_shengzhang_siyao",
    "古纯杂有有制类": "gu_chunza_youzhi", "近时纯杂有制类": "jinshi_chunza_youzhi",
    "伤官十论": "shangguan_shilun", "认格局生死之歌": "rengeju_shengsi_ge",
    "五星论": "wuxing_lun", "十天干体象全编论": "shigan_tixiang_quanbian",
    "吉神类": "jishen", "凶神类": "xiongshen", "起八字诀": "qi_bazi_jue",
    "十二长生论": "shier_changsheng", "阴阳通变妙诀": "yinyang_tongbian_jue",
    "定格局诀": "ding_geju_jue", "子平泛论": "ziping_fanlun",
    "十干从化定诀": "shigan_conghua_jue", "五阴歌": "wuyin_ge",
    "天元一字歌": "tianyuan_yizi_ge", "运晦歌": "yunhui_ge",
    "运通歌": "yuntong_ge", "刑克歌": "xingke_ge", "刑妻歌": "xingqi_ge",
    "克子歌": "kezi_ge", "带疾歌": "daiji_ge", "寿元歌": "shouyuan_ge",
    "飘荡歌": "piaodang_ge", "女命歌": "nvming_ge", "看命捷歌": "kanming_jie_ge",
    "万尚书琼玑三盘赋": "qiongji_sanpan_fu", "崖泉男命赋": "yaquan_nanming_fu",
    "崖泉女命赋": "yaquan_nvming_fu", "讲命捷径赋": "jiangming_jiejing_fu",
    "身弱论": "shenruo", "喜忌篇": "xiji_pian", "继善篇": "jishan_pian",
    "六神篇": "liushen_pian", "气象篇": "qixiang_pian", "渭泾论": "weijing_lun",
    "定真篇": "dingzhen_pian", "五行元理消息赋": "wuxing_yuanli_xiaoxi_fu",
    "五行生克赋": "wuxing_shengke_fu", "一行禅师天元赋": "yixing_chanshi_tianyuan_fu",
    "捷驰千里马赋": "jiechi_qianlima_fu", "络绎赋": "luoyi_fu",
    "玄机赋": "xuanji_fu", "憎爱赋": "zengai_fu", "万金赋": "wanjin_fu",
    "相心赋": "xiangxin_fu", "仙机赋": "xianji_fu", "金玉赋": "jinyu_fu",
    "人鉴论": "renjian_lun", "渊源集说": "yuanyuan_jishuo",
    "妖祥赋": "yaoxiang_fu", "幽微天干赋": "youwei_tian gan_fu".replace(" ", ""),
    "人元消息赋": "renyuan_xiaoxi_fu", "地支赋": "dizhi_fu", "病源赋": "bingyuan_fu",
}
# 重点章节关键词（其余给通用关键词）
KEYWORDS = {
    "动静说": ["动静", "天干为动", "地支为静", "制化"],
    "盖头说": ["盖头", "截脚", "天干覆载", "生克"],
    "六亲说": ["六亲", "父母兄弟妻财子息", "十神取象"],
    "病药说类": ["病药", "有病为贵", "去病为药", "用神核心"],
    "雕枯旺弱四病说类": ["雕枯旺弱", "四病", "太过不及", "旺弱辩证"],
    "损益生长四药说类": ["损益生长", "四药", "补偏救弊", "病药"],
    "伤官十论": ["伤官", "伤官见官", "佩印生财", "十论"],
    "定格局诀": ["格局", "正官偏官", "财印食伤", "定格"],
    "子平泛论": ["子平", "泛论", "用神", "衰旺"],
    "身弱论": ["身弱", "扶抑", "印比", "从与不从"],
    "气象篇": ["气象", "格局气势", "五行意象"],
    "六神篇": ["六神", "十神", "财官印食比"],
    "继善篇": ["继善", "纲领", "古赋"],
}
# OCR 乱序/异体标题归一（仅用于匹配；正文不改）
TITLE_FIX = {"衰墓辛冠生论": "十二长生论"}


def yaml_list(items):
    return "[" + ", ".join(f'"{x}"' for x in items) + "]"


def norm_raw_title(s):
    t = s.replace("　", "").replace(" ", "").replace("\t", "")
    return TITLE_FIX.get(t, t)


def is_title(s):
    if not (2 <= len(s) <= 14):
        return False
    if any(c in s for c in PUNCT):
        return False
    if s.startswith("【"):
        return False
    return bool(TITLE_RE.search(s))


def main():
    lines = open(RAW, encoding="utf-8").read().splitlines()
    marks = []
    for i, ln in enumerate(lines):
        s = ln.strip()
        if is_title(s):
            title = norm_raw_title(s)
            if title in SLUG:
                marks.append((i, title))
    print(f"定位章节 {len(marks)} 个")
    nomatch = []
    # 反向检查：发现的标题是否都有 slug
    for i, ln in enumerate(lines):
        s = ln.strip()
        if is_title(s):
            t = norm_raw_title(s)
            if t not in SLUG and t not in nomatch:
                nomatch.append(t)
    if nomatch:
        print("  警告：以下标题无 slug 映射：", nomatch)

    n = 0
    for idx, (i, title) in enumerate(marks):
        end = marks[idx+1][0] if idx+1 < len(marks) else len(lines)
        body = [lines[j].rstrip() for j in range(i+1, end) if lines[j].strip()]
        body = [b for b in body if not b.startswith("神峰通考")]
        slug = SLUG[title]
        kw = KEYWORDS.get(title, [title.rstrip("说类论赋歌篇诀")])
        num = idx + 1
        cid = f"sftk_{num:02d}_{slug}"
        tags = ["神峰通考", "张楠", "病药实战", title] + kw[:2]
        fm = f"""---
id: "{cid}"
book: "神峰通考"
chapter: "第{num}节"
chapter_num: {num}
section_title: "{title}"
source_version: "明·张楠（神峰）著·带标点电子本"
author: "张楠（张神峰）"
dynasty: "明"
type: "chapter"
conditions:
  day_master: []
  month_branch: []
  day_pillar: []
  hour_pillar: []
  ten_god: []
  pattern: []
  shensha: []
  keywords: {yaml_list(kw)}
weight: 3
tags: {yaml_list(tags)}
---
"""
        out = [fm, f"### {title}", "", "**【原文】**", ""]
        out += body
        out += ["", "**【白话提要】**", "", "（待补）", ""]
        with open(os.path.join(OUT, f"{cid}.md"), "w", encoding="utf-8") as f:
            f.write("\n".join(out).rstrip() + "\n")
        n += 1
    print(f"已生成 {n} 个章节 Markdown -> {OUT}")


if __name__ == "__main__":
    main()
