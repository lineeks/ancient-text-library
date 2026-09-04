# -*- coding: utf-8 -*-
"""
Aether-Cycle 古籍知识库 · conditions 检索元数据精准增强（行级、幂等、只动 Frontmatter）

设计原则：
  1. 只修改 Frontmatter 内 conditions 的目标字段行（ten_god / pattern / shensha），
     不重排 YAML、不改其它字段、绝不触碰正文；
  2. 行级解析单行 flow-style 列表（  key: ["a", "b"] ），合并去重（保留原顺序，新词追加），
     REMOVE 表用于纠正早期解析的误标（如把“诸神煞/月煞/劫煞”误判为“七杀格”）；
  3. 幂等：重复运行结果一致，已含有的值不重复添加，无变化的文件不写入；
  4. 用词与全库既有词表对齐（见 validate / build_index 与既有典籍 frontmatter）。

用法：
  python -X utf8 scripts/enrich_conditions.py --book wuxingjingji
  python -X utf8 scripts/enrich_conditions.py --book mingliyaoyan
  python -X utf8 scripts/enrich_conditions.py --book wuxingjingji --dry   # 只打印计划不落盘
"""
import argparse
import ast
import os
import re

BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
BOOK_DIR = {
    "wuxingjingji": os.path.join("library", "ming", "bazi", "extended", "wuxingjingji"),
    "mingliyaoyan": os.path.join("library", "ming", "bazi", "extended", "mingliyaoyan"),
}
FIELDS = ("day_master", "month_branch", "day_pillar", "hour_pillar",
          "ten_god", "pattern", "shensha", "keywords")
LINE_RE = re.compile(r"^  (" + "|".join(FIELDS) + r"): (\[.*\])\s*$")

# ---------------------------------------------------------------------------
# 五行精纪：为主题明确对应十神 / 格局 / 神煞的条目补精确召回字段；
# 泛论五行、干支、运限、六亲、形貌者一律不加（宁缺毋滥，避免主题查询被古法条文污染）。
# ---------------------------------------------------------------------------
WXJJ_ADD = {
    "wxjj_v04_01": {"shensha": ["十干合", "化气"], "pattern": ["化格"]},        # 十干合化
    "wxjj_v12_01": {"shensha": ["天月二德", "天德贵人", "月德贵人"]},            # 十二月节气天月德
    "wxjj_v13_01": {"shensha": ["太极贵人"]},                                  # 吉贵神例(天乙/阴官/福星/太极/文昌)
    "wxjj_v17_02": {"ten_god": ["七杀"]},                                      # 官神兼正偏官
    "wxjj_v18_01": {"ten_god": ["偏印"]},                                      # 印绶兼正偏印
    "wxjj_v18_02": {"ten_god": ["偏印"]},                                      # 食神兼倒食(枭神=偏印)
    "wxjj_v18_04": {"shensha": ["六合", "三合"]},                              # 吉神专论“合”
    "wxjj_v19_04": {"ten_god": ["偏财"]},                                      # 财兼正偏财
    "wxjj_v20_03": {"shensha": ["词馆"]},                                      # 学堂文章兼词馆
    "wxjj_v20_04": {"shensha": ["科名星", "魁星"]},                            # 科名
    "wxjj_v23_01": {"shensha": ["空亡"]},                                      # 凶神例含截路空亡
    "wxjj_v26_01": {"shensha": ["刑冲"]},                                      # 冲破
    "wxjj_v27_01": {"shensha": ["天罗地网"]},                                  # 凶杀含四杀五鬼天罗地网
}
WXJJ_REMOVE = {}

# ---------------------------------------------------------------------------
# 命理约言：为十神“法/赋”补对应子平格局；并纠正早期按“煞”字误标为七杀格的神煞论。
# ---------------------------------------------------------------------------
MLYY_ADD = {
    # 卷一·48 法
    "mlyy_fa17": {"ten_god": ["正官"], "pattern": ["正官格"]},   # 官煞去留(官煞混杂)
    "mlyy_fa18": {"ten_god": ["正官"], "pattern": ["正官格"]},
    "mlyy_fa19": {"ten_god": ["正官"], "pattern": ["正官格"]},
    "mlyy_fa20": {"pattern": ["印绶格"]},                        # 看正偏印法
    "mlyy_fa21": {"pattern": ["财格"]},                          # 看偏正财法
    "mlyy_fa22": {"pattern": ["食神格"]},                        # 看食神法
    "mlyy_fa23": {"pattern": ["伤官格"]},                        # 看伤官法
    "mlyy_fa24": {"pattern": ["食神格"]},                        # 看食神法(又)
    "mlyy_fa25": {"pattern": ["建禄格", "阳刃格", "月劫格"]},     # 比劫禄刃
    "mlyy_fa27": {"pattern": ["杂气格"]},                        # 杂气墓库
    # 卷二·20 赋
    "mlyy_fu07": {"pattern": ["印绶格"]},
    "mlyy_fu08": {"pattern": ["印绶格"]},
    "mlyy_fu09": {"pattern": ["财格"]},
    "mlyy_fu10": {"pattern": ["财格"]},
    "mlyy_fu11": {"pattern": ["食神格"]},
    "mlyy_fu12": {"pattern": ["伤官格"]},
    "mlyy_fu13": {"pattern": ["建禄格", "月劫格"]},
    "mlyy_fu14": {"pattern": ["建禄格", "阳刃格", "月劫格"]},
}
# “诸神煞 / 月煞 / 劫煞”是神煞主题，不是子平七杀格，移除早期解析误标的 ten_god/pattern。
MLYY_REMOVE = {
    "mlyy_lun15": {"ten_god": ["七杀"], "pattern": ["七杀格"]},
    "mlyy_lun16": {"ten_god": ["七杀"], "pattern": ["七杀格"]},
    "mlyy_lun18": {"ten_god": ["七杀"], "pattern": ["七杀格"]},
    "mlyy_lun24": {"ten_god": ["七杀"], "pattern": ["七杀格"]},
}

PLAN = {
    "wuxingjingji": (WXJJ_ADD, WXJJ_REMOVE),
    "mingliyaoyan": (MLYY_ADD, MLYY_REMOVE),
}


def merge_values(old, add, remove):
    out = [v for v in old if v not in remove]
    for v in add:
        if v not in out:
            out.append(v)
    return out


def render(field, values):
    return "  " + field + ": [" + ", ".join('"%s"' % v for v in values) + "]"


def process_file(path, add_map, remove_map, dry):
    name = os.path.basename(path)[:-3]
    add = add_map.get(name)
    remove = remove_map.get(name)
    if not add and not remove:
        return None
    text = open(path, encoding="utf-8").read()
    parts = text.split("---", 2)
    if len(parts) < 3:
        print("  [跳过] 无 frontmatter:", name)
        return None
    head, body = parts[1], parts[2]
    changed = []
    new_lines = []
    in_cond = False
    for line in head.splitlines():
        m = LINE_RE.match(line)
        if line.strip() == "conditions:":
            in_cond = True
            new_lines.append(line)
            continue
        if in_cond and m:
            field = m.group(1)
            old = ast.literal_eval(m.group(2))
            a = (add or {}).get(field, [])
            r = (remove or {}).get(field, [])
            new = merge_values(old, a, r)
            if new != old:
                changed.append((field, old, new))
                new_lines.append(render(field, new))
            else:
                new_lines.append(line)
            continue
        if in_cond and line and not line.startswith(" "):
            in_cond = False
        new_lines.append(line)
    if not changed:
        return None
    if dry:
        for field, old, new in changed:
            print(f"  [计划] {name}.{field}: {old} -> {new}")
        return 0
    # head 原以换行结尾（第二个 --- 前），splitlines() 不保留该尾换行，需补回以免与 --- 黏连
    new_head = "\n".join(new_lines)
    rebuilt = "---" + new_head + "\n---" + body
    with open(path, "w", encoding="utf-8", newline="") as f:
        f.write(rebuilt)
    for field, old, new in changed:
        print(f"  [已改] {name}.{field}: {old} -> {new}")
    return 1


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--book", required=True, choices=list(BOOK_DIR))
    ap.add_argument("--dry", action="store_true")
    args = ap.parse_args()
    add_map, remove_map = PLAN[args.book]
    bdir = os.path.join(BASE, BOOK_DIR[args.book])
    touched = 0
    print(f"== 增强 {args.book}（dry={args.dry}）==")
    for nm in sorted(os.listdir(bdir)):
        if nm.endswith(".md") and nm != "INDEX.md":
            r = process_file(os.path.join(bdir, nm), add_map, remove_map, args.dry)
            if r:
                touched += 1
    print(f"涉及条目 {touched} 个。")


if __name__ == "__main__":
    main()
