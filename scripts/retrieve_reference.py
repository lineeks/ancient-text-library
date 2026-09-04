# -*- coding: utf-8 -*-
"""
Aether-Cycle 古籍知识库 · 参考检索器（纯标准库，Python 版，Rust engine 的等价参照）

检索语义（须与 README 伪代码、Rust 版 engine/ 完全一致）：
  对每条 entry，遍历其 conditions 中“结构化匹配字段”：
    day_master / month_branch / day_pillar / hour_pillar /
    ten_god / pattern / shensha
  - entry 在某字段声明了非空集合，而命盘 chart 同字段与之无交集 → 不召回；
  - entry 声明为空的字段不构成约束；
  - 全部已声明字段均有交集 → 召回。
  keywords 不参与硬匹配，只用于主题包含式召回（keyword_query）。
  结构化命中结果按 weight 降序、再按 path 升序稳定排列。

CLI：
  python -X utf8 scripts/retrieve_reference.py --chart '{"day_master":["Jia"],"month_branch":["Yin"]}'
"""
import argparse
import json
import os

BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
MANIFEST = os.path.join(BASE, "manifest.json")
# 与 README / Rust 保持一致：硬匹配只含 7 个结构化字段（不含 keywords）
HARD_FIELDS = ["day_master", "month_branch", "day_pillar", "hour_pillar",
               "ten_god", "pattern", "shensha"]
# 匹配键分组：复合键“组内 AND”（日干×月令、日柱×时柱必须同时满足），
# 不同检索维度“组间 OR”（格局 / 十神 / 神煞是并列召回理由，任一命中即可）。
MATCH_GROUPS = {
    "tiaohou": ["day_master", "month_branch"],   # 调候复合键
    "rishi": ["day_pillar", "hour_pillar"],      # 日时复合键
    "ten_god": ["ten_god"],
    "pattern": ["pattern"],
    "shensha": ["shensha"],
}


class Library:
    def __init__(self, manifest_path=MANIFEST):
        with open(manifest_path, encoding="utf-8") as f:
            data = json.load(f)
        self.meta = data
        self.entries = data["entries"]

    @staticmethod
    def match(conditions, chart):
        """组内 AND、组间 OR 的结构化匹配。

        - 复合键组（调候 day_master+month_branch、日时 day_pillar+hour_pillar）：
          组内所有已声明字段都与命盘有交集，该组才算命中；
        - 单维组（ten_god / pattern / shensha）：该字段有交集即该组命中；
        - 条目在任一“已声明的组”命中即召回（组间 OR，不同维度互为并列召回理由）；
        - 条目未声明任何硬字段（序、泛论）为通用条，恒可召回。
        """
        declared_any = False
        for fields in MATCH_GROUPS.values():
            declared = [f for f in fields if conditions.get(f)]
            if not declared:
                continue
            declared_any = True
            group_hit = all(
                set(conditions[f]) & set(chart.get(f) or []) for f in declared)
            if group_hit:
                return True
        return not declared_any

    @staticmethod
    def specificity(cond):
        """命中精确度：声明了几个非空结构化字段（0=无约束通论条）。"""
        return sum(1 for k in HARD_FIELDS if cond.get(k))

    def structured_query(self, chart):
        """命中条目排序：精确度优先（精准锚定在前、无约束通论沉底），
        同精确度内按 weight（典籍梯队）降序，再按 path 升序稳定。"""
        hits = [e for e in self.entries if self.match(e["conditions"], chart)]
        hits.sort(key=lambda e: (-self.specificity(e["conditions"]),
                                 -e["weight"], e["path"]))
        return hits

    def keyword_query(self, text):
        """主题包含式召回：命中文本出现在任一 keyword / 标题 / 章节中。"""
        t = (text or "").strip()
        if not t:
            return []
        out = []
        for e in self.entries:
            c = e["conditions"]
            hay = list(c.get("keywords", [])) + [e.get("title", ""), e.get("chapter", "")]
            if any(t in s for s in hay):
                out.append(e)
        out.sort(key=lambda e: (-self.specificity(e["conditions"]),
                                -e["weight"], e["path"]))
        return out


def brief(e):
    c = e["conditions"]
    return (f"  w{e['weight']:<2} {e['id']:<28} {e['book']}《{e['title']}》 "
            f"[dm={c['day_master']} mb={c['month_branch']} pat={c['pattern']} "
            f"tg={c['ten_god']} ss={c['shensha']} dp={c['day_pillar']} hp={c['hour_pillar']}]")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--chart", default="{}", help="命盘结构化字段 JSON")
    ap.add_argument("--keyword", default="", help="主题关键词包含召回")
    ap.add_argument("--limit", type=int, default=30)
    args = ap.parse_args()
    lib = Library()
    if args.keyword:
        hits = lib.keyword_query(args.keyword)
        print(f"关键词「{args.keyword}」命中 {len(hits)} 条（前 {args.limit}）：")
    else:
        chart = json.loads(args.chart)
        hits = lib.structured_query(chart)
        print(f"结构化命盘 {chart} 命中 {len(hits)} 条（前 {args.limit}）：")
    for e in hits[:args.limit]:
        print(brief(e))


if __name__ == "__main__":
    main()
