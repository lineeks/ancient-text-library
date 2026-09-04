# -*- coding: utf-8 -*-
"""
Aether-Cycle 古籍知识库 · 《滴天髓阐微》结构化解析脚本
源文结构（规整）：
  通神论 34 篇 + 六亲论 29 篇 = 63 篇；
  每篇 = 经文赋文（口诀） + 「原注：」(刘伯温) + 「任氏曰：」(任铁樵阐微) + 大量四柱/大运命例；
  另有 3 处现代人「若思按」校勘语，单独分层，不混入古籍。
分层：
  【经文】传世口诀；【刘伯温原注】；【任铁樵阐微】（命例分析归此层）；
  【附：命例】四柱+大运纯干支序列，```text 代码块；【校勘按语】若思按。
输出：core/ditianchui/
"""
import os
import re

BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
RAW = os.path.join(BASE, "raw", "ditiansuichanwei.txt")
OUT_DIR = os.path.join(BASE, "library", "ming", "bazi", "core", "ditianchui")
os.makedirs(OUT_DIR, exist_ok=True)

TITLE_RE = re.compile(r'^([一二三四五六七八九十]+)[、\s]+([^\s，。：；、？！,.]{1,6})$')
GZ_CHARS = set("甲乙丙丁戊己庚辛壬癸子丑寅卯辰巳午未申酉戌亥")
# 层标记：兼容冒号/分号/逗号（源文标点不统一）；「原注云：…」是任氏引述原注，不在此列
YUANZHU_RE = re.compile(r'^原注[:：，,；;]\s*')
RENSHI_RE = re.compile(r'^任氏曰[:：，,；;]\s*')

# 元数据：(part, num) -> (slug, [pattern], [ten_god], [keywords])
# part: ts=通神论, lq=六亲论。标题从源文提取，此处只给英文 slug 与检索标签。
META = {
    # —— 通神论 34 篇 ——
    ("ts", 1):  ("tiandao", [], [], ["三元", "天元地元人元", "阴阳", "五行"]),
    ("ts", 2):  ("didao", [], [], ["坤元", "五气", "偏全", "吉凶"]),
    ("ts", 3):  ("rendao", [], [], ["人为贵", "顺悖", "干支顺遂"]),
    ("ts", 4):  ("zhiming", [], [], ["顺逆之机", "神煞批判", "格局"]),
    ("ts", 5):  ("liqi", [], [], ["理气", "五行升降", "机理"]),
    ("ts", 6):  ("peihe", [], [], ["干支配合", "制化"]),
    ("ts", 7):  ("tiangan", [], [], ["天干", "甲木参天", "脱胎要火", "五阳五阴"]),
    ("ts", 8):  ("dizhi", [], [], ["地支", "藏干", "十二宫"]),
    ("ts", 9):  ("ganzhizonglun", [], [], ["干支总论", "阴阳顺遂", "天覆地载"]),
    ("ts", 10): ("xingxiang", [], [], ["形象", "两神成象", "格局气象", "从象"]),
    ("ts", 11): ("fangju", [], [], ["方局", "三合", "三会", "寅午戌", "申子辰"]),
    ("ts", 12): ("bage", ["正官格", "七杀格", "财格", "印绶格", "食神格", "伤官格"], [], ["八格", "格局成败", "用神"]),
    ("ts", 13): ("tiyong", [], [], ["体用", "用神", "日主"]),
    ("ts", 14): ("jingshen", [], [], ["精神", "精气", "魂魄"]),
    ("ts", 15): ("yueling", [], [], ["月令", "提纲", "司令"]),
    ("ts", 16): ("shengshi", [], [], ["生时", "时柱", "归宿"]),
    ("ts", 17): ("shuaiwang", [], [], ["衰旺", "强弱", "得令失令"]),
    ("ts", 18): ("zhonghe", [], [], ["中和", "平衡", "太过不及"]),
    ("ts", 19): ("yuanliu", [], [], ["源流", "五行流通", "起止"]),
    ("ts", 20): ("tongguan", [], [], ["通关", "两行相战", "调和"]),
    ("ts", 21): ("guansha", [], ["正官", "七杀"], ["官杀", "去留", "混杂", "制化"]),
    ("ts", 22): ("shangguan", [], ["伤官"], ["伤官", "伤官见官", "佩印", "伤官伤尽"]),
    ("ts", 23): ("qingqi", [], [], ["清气", "清纯", "清浊"]),
    ("ts", 24): ("zhuoqi", [], [], ["浊气", "混浊", "清浊"]),
    ("ts", 25): ("zhenshen", [], [], ["真神", "用神真假", "得令"]),
    ("ts", 26): ("jiashen", [], [], ["假神", "失时", "真假"]),
    ("ts", 27): ("gangrou", [], [], ["刚柔", "阴阳", "宽猛"]),
    ("ts", 28): ("shunni", [], [], ["顺逆", "从逆", "顺遂"]),
    ("ts", 29): ("hannuan", [], [], ["寒暖", "调候", "气候", "冬夏"]),
    ("ts", 30): ("zaoshi", [], [], ["燥湿", "调候", "土润", "水火"]),
    ("ts", 31): ("yinxian", [], [], ["隐显", "藏透", "干支"]),
    ("ts", 32): ("zhonggua", [], [], ["众寡", "力量对比", "强弱"]),
    ("ts", 33): ("zhendui", [], [], ["震兑", "金木", "东西", "卯酉"]),
    ("ts", 34): ("kanli", [], [], ["坎离", "水火", "南北", "子午"]),
    # —— 六亲论 29 篇 ——
    ("lq", 1):  ("fuqi", [], [], ["夫妻", "妻宫", "妻星", "婚姻"]),
    ("lq", 2):  ("zinv", [], [], ["子女", "子息", "食伤"]),
    ("lq", 3):  ("fumu", [], ["正印", "偏财"], ["父母", "印绶", "财星"]),
    ("lq", 4):  ("xiongdi", [], ["比肩", "劫财"], ["兄弟", "比劫"]),
    ("lq", 5):  ("hezhizhang", [], [], ["何知章", "断验", "吉凶征兆"]),
    ("lq", 6):  ("nvmzhang", [], [], ["女命", "夫星", "子星", "贞静"]),
    ("lq", 7):  ("xiaoer", [], [], ["小儿", "童限", "幼年"]),
    ("lq", 8):  ("caide", [], [], ["才德", "女命"]),
    ("lq", 9):  ("fenyu", [], [], ["奋郁", "发用", "抑扬"]),
    ("lq", 10): ("enyuan", [], [], ["恩怨", "喜忌", "救应"]),
    ("lq", 11): ("xianshen", [], [], ["闲神", "辅神", "用神"]),
    ("lq", 12): ("congxiang", ["从格"], [], ["从象", "从官从财", "从儿", "从杀"]),
    ("lq", 13): ("huaxiang", ["化格"], [], ["化象", "化气", "合化", "真化"]),
    ("lq", 14): ("jiacong", ["从格"], [], ["假从", "真从", "从格成败"]),
    ("lq", 15): ("jiahua", ["化格"], [], ["假化", "真化", "化格成败"]),
    ("lq", 16): ("shunju", ["从旺格"], [], ["顺局", "从旺", "一行得气", "曲直炎上"]),
    ("lq", 17): ("fanju", [], [], ["反局", "反常", "喜忌反转"]),
    ("lq", 18): ("zhanju", [], [], ["战局", "相战", "两行交战"]),
    ("lq", 19): ("heju", [], [], ["合局", "会合", "三合六合"]),
    ("lq", 20): ("junxiang", ["从强格"], [], ["君象", "从强", "君臣"]),
    ("lq", 21): ("chenxiang", [], [], ["臣象", "君臣", "辅从"]),
    ("lq", 22): ("muxiang", [], ["正印", "偏印"], ["母象", "印绶", "生我"]),
    ("lq", 23): ("zixiang", [], ["食神", "伤官"], ["子象", "食伤", "我生"]),
    ("lq", 24): ("xingqing", [], [], ["性情", "性格取象", "五行性"]),
    ("lq", 25): ("jibing", [], [], ["疾病", "五行偏枯", "健康"]),
    ("lq", 26): ("chushen", [], [], ["出身", "祖业", "门第"]),
    ("lq", 27): ("diwei", [], [], ["地位", "贵贱", "层次"]),
    ("lq", 28): ("suiyun", [], [], ["岁运", "大运", "流年", "贞元"]),
    ("lq", 29): ("zhenyuan", [], [], ["贞元", "造化", "循环", "元亨利贞"]),
}

CN_NUM = {"一":1,"二":2,"三":3,"四":4,"五":5,"六":6,"七":7,"八":8,"九":9,
          "十":10,"十一":11,"十二":12,"十三":13,"十四":14,"十五":15,"十六":16,
          "十七":17,"十八":18,"十九":19,"二十":20,"二十一":21,"二十二":22,
          "二十三":23,"二十四":24,"二十五":25,"二十六":26,"二十七":27,
          "二十八":28,"二十九":29,"三十":30,"三十一":31,"三十二":32,
          "三十三":33,"三十四":34}


def cn2num(s):
    return CN_NUM.get(s)


def pure_ganzhi(s):
    """纯四柱/大运干支行：去空格后全部为干支字、长度 2~16 且为偶数（整柱数）。"""
    s2 = s.replace(" ", "")
    if not (2 <= len(s2) <= 16 and len(s2) % 2 == 0):
        return False
    return all(c in GZ_CHARS for c in s2)


def yaml_list(items):
    return "[" + ", ".join(f'"{x}"' for x in items) + "]"


def split_chapters(lines):
    """返回 [(part, num, title, start_idx, end_idx)]"""
    marks = []
    for i, ln in enumerate(lines):
        s = ln.strip()
        m = TITLE_RE.match(s)
        if m and i > 66:
            num = cn2num(m.group(1))
            if num:
                norm_title = f"{m.group(1)}、{m.group(2)}"   # 标题分隔符统一为顿号
                marks.append((i, num, norm_title, m.group(2)))
    chapters = []
    for idx, (i, num, full_title, name) in enumerate(marks):
        part = "ts" if i < 3465 - 1 else "lq"   # L3465 是六亲论部分标题（1-based）
        end = marks[idx + 1][0] if idx + 1 < len(marks) else len(lines)
        chapters.append((part, num, full_title, name, i + 1, end))
    return chapters


def build_blocks(body_lines):
    """把篇内文本行转成有序 blocks：jingwen/yuanzhu/renshi/jiaokan/mingli。

    滴天髓体例：一篇含多个赋文口诀，每个口诀后紧跟「原注：」「任氏曰：」。
    故口诀定位法：每个「原注：」行向前最近的非空、非干支行，即为该小节经文口诀。
    """
    # 预扫描：标记口诀行的「局部索引」
    koujue_idx = set()
    for j, ln in enumerate(body_lines):
        s = ln.strip()
        if YUANZHU_RE.match(s):
            k = j - 1
            while k >= 0 and not body_lines[k].strip():
                k -= 1
            if k >= 0 and not pure_ganzhi(body_lines[k].strip()):
                koujue_idx.add(k)

    blocks = []
    mingli = []
    active = None          # 当前文本层

    def flush_ml():
        if mingli:
            blocks.append(("mingli", mingli.copy()))
            mingli.clear()

    def add_text(layer, text):
        if blocks and blocks[-1][0] == layer and isinstance(blocks[-1][1], list):
            blocks[-1][1].append(text)
        else:
            blocks.append((layer, [text]))

    for idx, ln in enumerate(body_lines):
        s = ln.strip()
        if not s:
            continue
        if pure_ganzhi(s):
            mingli.append(s)
            continue
        just_flushed = bool(mingli)
        flush_ml()
        if idx in koujue_idx:
            active = "jingwen"
            add_text("jingwen", s)
        elif YUANZHU_RE.match(s):
            active = "yuanzhu"
            add_text("yuanzhu", YUANZHU_RE.sub("", s, count=1))
        elif RENSHI_RE.match(s):
            active = "renshi"
            add_text("renshi", RENSHI_RE.sub("", s, count=1))
        elif s.startswith("若思按"):
            active = "jiaokan"                    # 校勘按语，延续至命例/层标记
            add_text("jiaokan", s)
        elif s == "滴天髓全文终":
            continue
        else:
            if just_flushed:
                active = "renshi"                 # 命例后的分析恒为任氏阐微
            add_text(active if active else "renshi", s)
    flush_ml()
    return blocks


def render_md(part, num, full_title, name, blocks):
    slug, patterns, tengods, keywords = META[(part, num)]
    cid = f"dtcs_{part}{num:02d}_{slug}"
    part_zh = "通神论" if part == "ts" else "六亲论"
    tags = ["滴天髓阐微", part_zh, name] + patterns + tengods + keywords[:2]
    fm = f"""---
id: "{cid}"
book: "滴天髓阐微"
chapter: "{part_zh}·{full_title}"
chapter_num: {num}
part: "{part_zh}"
section_title: "{name}"
source_version: "任铁樵阐微注本（含刘伯温原注；若思校勘按语）"
author: "京图(传)·刘伯温原注·任铁樵阐微"
dynasty: "原文传宋·明注·清阐微"
type: "chapter"
conditions:
  day_master: []
  month_branch: []
  day_pillar: []
  hour_pillar: []
  ten_god: {yaml_list(tengods)}
  pattern: {yaml_list(patterns)}
  shensha: []
  keywords: {yaml_list(keywords)}
weight: 9
tags: {yaml_list(tags)}
---
"""
    out = [fm, f"### {full_title}", ""]

    # 各层严格按原书顺序就地渲染；同一文本层被命例/其他层隔开后重新出现时，再次输出层标题
    layer_title = {"jingwen": "**【经文】**", "yuanzhu": "**【刘伯温原注】**",
                   "renshi": "**【任铁樵阐微】**", "jiaokan": "**【校勘按语·若思】**"}
    prev_text_layer = None
    for btype, payload in blocks:
        if btype == "mingli":
            out += ["**【附：命例】**", "```text"]
            out += payload
            out += ["```", ""]
            continue
        if btype != prev_text_layer:
            out += [layer_title[btype], ""]
            prev_text_layer = btype
        for p in payload:
            out += [p, ""]

    out += ["**【白话提要】**", "", "（待补）", ""]
    return cid, "\n".join(out).rstrip() + "\n"


def main():
    lines = open(RAW, encoding="utf-8").read().splitlines()
    chapters = split_chapters(lines)
    print(f"定位篇章 {len(chapters)} 个（通神论/六亲论）")
    ts_n = sum(1 for c in chapters if c[0] == "ts")
    lq_n = sum(1 for c in chapters if c[0] == "lq")
    print(f"  通神论 {ts_n} 篇，六亲论 {lq_n} 篇")
    assert ts_n == 34 and lq_n == 29, f"篇章数异常 ts={ts_n} lq={lq_n}"

    n_mingli = n_jiaokan = n_koujue = 0
    no_koujue = []
    for part, num, full_title, name, start, end in chapters:
        body = lines[start:end]   # start 已指向标题行的下一行(0-based)
        blocks = build_blocks(body)
        n_mingli += sum(1 for b in blocks if b[0] == "mingli")
        n_jiaokan += sum(1 for b in blocks if b[0] == "jiaokan")
        kj = sum(len(b[1]) for b in blocks if b[0] == "jingwen")
        n_koujue += kj
        if kj == 0:
            no_koujue.append(full_title)
        cid, md = render_md(part, num, full_title, name, blocks)
        with open(os.path.join(OUT_DIR, f"{cid}.md"), "w", encoding="utf-8") as f:
            f.write(md)
    print(f"已生成 {len(chapters)} 个 Markdown；经文口诀 {n_koujue} 句，命例块 {n_mingli} 处，校勘按语 {n_jiaokan} 处。")
    if no_koujue:
        print("提示：以下篇章源文未以赋文口诀起首（直接原注/任注，属源文体例，已照常分层）：", no_koujue)


if __name__ == "__main__":
    main()
