# -*- coding: utf-8 -*-
"""
Aether-Cycle 古籍知识库 · 索引生成脚本
扫描 core/ 下全部 Markdown，解析 Frontmatter，生成：
  - INDEX.md                         全库总索引（概览 + 分书导航）
  - core/qiongtongbj/INDEX.md        穷通宝鉴条目索引（含十干×十二月覆盖矩阵）
  - core/zipingzhenquan/INDEX.md     子平真诠48章目录
"""
import os
import re

BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CORE = os.path.join(BASE, "core")

STEM_ORDER = ["甲", "乙", "丙", "丁", "戊", "己", "庚", "辛", "壬", "癸"]
STEM_EN = {"甲": "Jia", "乙": "Yi", "丙": "Bing", "丁": "Ding", "戊": "Wu",
           "己": "Ji", "庚": "Geng", "辛": "Xin", "壬": "Ren", "癸": "Gui"}
STEM_ZH = {"甲": "甲木", "乙": "乙木", "丙": "丙火", "丁": "丁火", "戊": "戊土",
           "己": "己土", "庚": "庚金", "辛": "辛金", "壬": "壬水", "癸": "癸水"}
BRANCH_ORDER = ["Yin", "Mao", "Chen", "Si", "Wu", "Wei", "Shen", "You", "Xu", "Hai", "Zi", "Chou"]
BRANCH_ZH = {"Yin": "寅·正月", "Mao": "卯·二月", "Chen": "辰·三月", "Si": "巳·四月",
             "Wu": "午·五月", "Wei": "未·六月", "Shen": "申·七月", "You": "酉·八月",
             "Xu": "戌·九月", "Hai": "亥·十月", "Zi": "子·十一月", "Chou": "丑·十二月"}


def parse_frontmatter(path):
    with open(path, encoding="utf-8") as f:
        text = f.read()
    m = re.match(r"^---\n(.*?)\n---", text, re.S)
    if not m:
        return {}, text
    fm_text = m.group(1)
    meta = {}
    for line in fm_text.splitlines():
        mm = re.match(r"^(\w+):\s*(.*)$", line)
        if mm:
            key, val = mm.group(1), mm.group(2).strip()
            val = val.strip('"')
            meta[key] = val
        mm2 = re.match(r"^\s+(day_master|month_branch|ten_god|pattern|shensha|keywords|tags):\s*\[(.*)\]", line)
        if mm2:
            items = [x.strip().strip('"') for x in mm2.group(2).split(",") if x.strip()]
            meta[mm2.group(1)] = items
    return meta, text


def scan(folder):
    result = []
    for name in sorted(os.listdir(folder)):
        if not name.endswith(".md") or name == "INDEX.md":
            continue
        meta, _ = parse_frontmatter(os.path.join(folder, name))
        meta["_file"] = name
        result.append(meta)
    return result


def build_qtbj_index(items):
    monthly = [x for x in items if x.get("type") == "monthly"]
    seasonal = [x for x in items if x.get("type") == "seasonal"]
    refs = [x for x in items if x.get("type") == "reference"]

    lines = ["# 《穷通宝鉴》条目索引", "",
             "> 余春台辑本（清）。文件名规则：`qtbj_<天干英文>_<地支英文>.md`。",
             "> 合并月以两支连写（如 `wuwei`=午未月、`youxu`=酉戌月、`yinmao`=寅卯月、`zichou`=子丑月）。", ""]

    # ---------- 十干 × 十二月 覆盖矩阵 ----------
    lines += ["## 一、十干 × 十二月 覆盖矩阵", ""]
    lines.append("说明：单元格内为该「日干×月令」条目文件名（去掉 `qtbj_` 前缀与 `.md` 后缀）；`—` 表示源文该月并入相邻条目或未单列。")
    lines.append("")
    header = "| 日干＼月令 | " + " | ".join(BRANCH_ZH[b].split("·")[0] for b in BRANCH_ORDER) + " |"
    sep = "|" + "---|" * 13
    lines.append(header)
    lines.append(sep)
    # 建立 (stem_en -> branch -> file stem) 映射（月度 + 季度条目均纳入）
    grid = {}
    for it in monthly + seasonal:
        dm = it.get("day_master", [""])[0] if it.get("day_master") else ""
        branches = it.get("month_branch", [])
        stem_short = it["_file"].replace("qtbj_", "").replace(".md", "")
        for b in branches:
            # 同一格若已有独立月度条目，则优先保留月度条目；季度条目仅在无月度条目时填充
            grid.setdefault(dm, {}).setdefault(b, stem_short)
    for zh in STEM_ORDER:
        en = STEM_EN[zh]
        row = [f"**{zh}** {en}"]
        for b in BRANCH_ORDER:
            cell = grid.get(en, {}).get(b, "—")
            row.append(cell if cell != "—" else "—")
        lines.append("| " + " | ".join(row) + " |")
    lines.append("")

    # ---------- 月度条目明细 ----------
    lines += ["## 二、月度调候条目明细（排盘日干×月令精确命中）", ""]
    lines.append("| ID | 标题 | 章节 | 匹配日干 | 匹配月令 | 文件 |")
    lines.append("|---|---|---|---|---|---|")
    def sort_key(x):
        dm = x.get("day_master", [""])[0] if x.get("day_master") else ""
        mb = x.get("month_branch", [""])[0] if x.get("month_branch") else ""
        order_stem = list(STEM_EN.values()).index(dm) if dm in STEM_EN.values() else 99
        order_branch = BRANCH_ORDER.index(mb) if mb in BRANCH_ORDER else 99
        return (order_stem, order_branch)
    for it in sorted(monthly, key=sort_key):
        lines.append(f"| `{it.get('id','')}` | {it.get('section_title','')} | {it.get('chapter','')} | {', '.join(it.get('day_master',[]))} | {', '.join(it.get('month_branch',[]))} | [{it['_file']}](./{it['_file']}) |")
    lines.append("")

    # ---------- 季度条目 ----------
    if seasonal:
        lines += ["## 三、季度条目（源文按季合并，如己土三夏/三秋/三冬）", ""]
        lines.append("| ID | 标题 | 匹配日干 | 匹配月令 | 文件 |")
        lines.append("|---|---|---|---|---|")
        for it in seasonal:
            lines.append(f"| `{it.get('id','')}` | {it.get('section_title','')} | {', '.join(it.get('day_master',[]))} | {', '.join(it.get('month_branch',[]))} | [{it['_file']}](./{it['_file']}) |")
        lines.append("")

    # ---------- 参考条目 ----------
    lines += ["## 四、总论 / 参考条目（不参与月令精确匹配，weight=5）", ""]
    lines.append("| ID | 标题 | 文件 |")
    lines.append("|---|---|---|")
    for it in sorted(refs, key=lambda x: x["_file"]):
        lines.append(f"| `{it.get('id','')}` | {it.get('section_title','')} | [{it['_file']}](./{it['_file']}) |")
    lines.append("")
    lines.append(f"**统计：月度条目 {len(monthly)} 条，季度条目 {len(seasonal)} 条，参考条目 {len(refs)} 条，合计 {len(items)} 个文件。**")
    lines.append("")
    return "\n".join(lines)


def build_zpqz_index(items):
    lines = ["# 《子平真诠评注》48章索引", "",
             "> 清·沈孝瞻原著，徐乐吾评注（节本）。文件名规则：`zpzq_ch<两位章号>_<主题拼音>.md`。",
             "> 排盘完成格局评定后，按 `pattern`（格局）或 `ten_god`（十神）字段检索对应章节。", ""]
    lines.append("| 章 | 标题 | 格局 pattern | 十神 ten_god | 关键词 | 文件 |")
    lines.append("|---|---|---|---|---|---|")
    def num_key(x):
        try:
            return int(x.get("chapter_num", "999"))
        except ValueError:
            return 999
    for it in sorted(items, key=num_key):
        lines.append(f"| {it.get('chapter_num','')} | {it.get('section_title','')} | {', '.join(it.get('pattern',[])) or '—'} | {', '.join(it.get('ten_god',[])) or '—'} | {', '.join(it.get('keywords',[])[:4])} | [{it['_file']}](./{it['_file']}) |")
    lines.append("")
    lines.append(f"**统计：共 {len(items)} 章。**")
    lines.append("")
    return "\n".join(lines)


def build_dts_index(items):
    lines = ["# 《滴天髓阐微》篇章索引", "",
             "> 原文传宋·京图，明·刘伯温原注，清·任铁樵阐微（含若思校勘按语）。",
             "> 文件名规则：`dtcs_<ts|lq><两位篇号>_<主题拼音>.md`（ts=通神论，lq=六亲论）。",
             "> 每篇按「经文口诀 → 刘伯温原注 → 任铁樵阐微 → 附命例」就地分层；属命理哲学/气象理气，",
             "> 排盘判定旺衰、顺逆、从格化格、寒暖燥湿、六亲时按 `pattern` / `ten_god` / `keywords` 召回。", ""]
    def num_key(x):
        try:
            return int(x.get("chapter_num", "999"))
        except ValueError:
            return 999
    for part, part_zh in [("通神论", "一、通神论（34 篇）：理气·干支·格局·衰旺调候"),
                          ("六亲论", "二、六亲论（29 篇）：六亲·从化·象法·性情岁运")]:
        sub = sorted([x for x in items if x.get("part") == part], key=num_key)
        lines += [f"## {part_zh}", "",
                  "| 篇 | 标题 | 格局 pattern | 十神 ten_god | 关键词 | 文件 |",
                  "|---|---|---|---|---|---|"]
        for it in sub:
            lines.append(f"| {it.get('chapter_num','')} | {it.get('section_title','')} | {', '.join(it.get('pattern',[])) or '—'} | {', '.join(it.get('ten_god',[])) or '—'} | {', '.join(it.get('keywords',[])[:3])} | [{it['_file']}](./{it['_file']}) |")
        lines.append("")
    lines.append(f"**统计：共 {len(items)} 篇（通神论 34 + 六亲论 29），经文口诀 135 句，附四柱/大运命例 514 处，现代校勘按语 3 处单独分层。**")
    lines.append("")
    return "\n".join(lines)


def build_root_index(qtbj, zpqz, dts):
    lines = ["# Aether-Cycle 子平命理古籍知识库 · 总索引", "",
             "本知识库面向八字排盘引擎的**即时检索、引经据典、原汁原味**需求构建。",
             "每条古籍条文以 Markdown + YAML Frontmatter 标引，排盘内核输出 `日干 / 月令 / 格局 / 十神 / 神煞` 后，",
             "对 `conditions` 字段做数组交集匹配，毫秒级返回分层内容（原文/经文、古注、阐微、命例、白话提要）。", "",
             "## 典籍收录进度", "",
             "| 梯队 | 典籍 | 版本 | 文件数 | 索引 | 状态 |",
             "|---|---|---|---|---|---|",
             f"| 第一梯队 | 穷通宝鉴 | 余春台辑本 | {len(qtbj)} | [索引](./core/qiongtongbj/INDEX.md) | ✅ 已入库 |",
             f"| 第一梯队 | 子平真诠评注 | 沈孝瞻原著·徐乐吾评注节本 | {len(zpqz)} | [索引](./core/zipingzhenquan/INDEX.md) | ✅ 已入库 |",
             f"| 第一梯队 | 滴天髓阐微 | 京图(传)·刘伯温原注·任铁樵阐微 | {len(dts)} | [索引](./core/ditianchui/INDEX.md) | ✅ 已入库 |",
             "| 第二梯队 | 三命通会 | 万民英·四库本 | 0 | — | ⏳ 待入库（Phase-3） |",
             "| 第二梯队 | 渊海子平 | 徐大升编 | 0 | — | ⏳ 待入库（Phase-3） |",
             "| 第三梯队 | 神峰通考 / 玉照定真经 / 千里命稿 | — | 0 | — | ⏳ 待入库（Phase-4） |", "",
             "## 目录结构", "",
             "```text",
             "ancient-text-library/",
             "├── README.md                 # 项目说明、命名规范、Frontmatter 规范、检索方式",
             "├── INDEX.md                  # 本文件：全库总索引",
             "├── raw/                      # 原始下载文本（UTF-8，不修改）",
             "├── scripts/                  # 下载 / 解析 / 索引生成脚本",
             "└── core/                     # 第一梯队核心典籍",
             "    ├── qiongtongbj/         # 穷通宝鉴（122 文件 + INDEX）",
             "    ├── zipingzhenquan/      # 子平真诠评注（48 章 + INDEX）",
             "    └── ditianchui/          # 滴天髓阐微（63 篇 + INDEX）",
             "```", "",
             "## 检索字段速查", "",
             "| 场景 | 匹配字段 | 示例 |",
             "|---|---|---|",
             "| 日干×月令调候（穷通宝鉴） | `day_master` + `month_branch` | 甲日寅月 → `qtbj_jia_yin.md` |",
             "| 格局判定（子平真诠） | `pattern` | 正官格 → 第31/32章 |",
             "| 旺衰顺逆/从化/气象（滴天髓） | `pattern`/`ten_god`/`keywords` | 从格 → 从象/化象；调候 → 寒暖/燥湿 |",
             "| 十神专题 | `ten_god` | 正官/七杀/正财/偏财/正印/偏印/伤官/食神/比肩/劫财 |",
             "| 日柱×时柱断语（三命通会，待入库） | `day_pillar` + `hour_pillar` | 甲子日丙寅时 |",
             "| 神煞出处（待入库） | `shensha` | 天乙贵人/文昌/驿马… |", "",
             "> 免责声明：本库仅作传统命理文献的结构化整理与研究参考，原文保持原貌，不构成任何人生决策建议。", ""]
    return "\n".join(lines)


def main():
    q_folder = os.path.join(CORE, "qiongtongbj")
    z_folder = os.path.join(CORE, "zipingzhenquan")
    d_folder = os.path.join(CORE, "ditianchui")
    qtbj = scan(q_folder)
    zpqz = scan(z_folder)
    dts = scan(d_folder)

    with open(os.path.join(q_folder, "INDEX.md"), "w", encoding="utf-8") as f:
        f.write(build_qtbj_index(qtbj))
    with open(os.path.join(z_folder, "INDEX.md"), "w", encoding="utf-8") as f:
        f.write(build_zpqz_index(zpqz))
    with open(os.path.join(d_folder, "INDEX.md"), "w", encoding="utf-8") as f:
        f.write(build_dts_index(dts))
    with open(os.path.join(BASE, "INDEX.md"), "w", encoding="utf-8") as f:
        f.write(build_root_index(qtbj, zpqz, dts))
    print(f"索引生成完成：穷通宝鉴 {len(qtbj)} 条，子平真诠 {len(zpqz)} 章，滴天髓阐微 {len(dts)} 篇")


if __name__ == "__main__":
    main()
