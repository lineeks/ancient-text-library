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
import re

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
    def is_general(conditions):
        """无任何结构化硬锚点（序、泛论、纯歌赋/口诀）：不参与结构化命盘召回，
        只通过关键词或书目浏览获取，避免大量通论条在每一命盘下恒命中、稀释精确结果。"""
        return not any(conditions.get(k) for k in HARD_FIELDS)

    @staticmethod
    def match(conditions, chart):
        """严格结构化匹配：至少一个“已声明的匹配组”整体命中才召回。

        - 复合键组（调候 day_master+month_branch、日时 day_pillar+hour_pillar）：
          组内所有已声明字段都与命盘有交集，该组才算命中；
        - 单维组（ten_god / pattern / shensha）：该字段有交集即该组命中；
        - 组间 OR：任一已声明组命中即召回；
        - 无任何硬字段声明的通论条（见 is_general）此处返回 False，不混入命盘召回。
        """
        for fields in MATCH_GROUPS.values():
            declared = [f for f in fields if conditions.get(f)]
            if not declared:
                continue
            if all(set(conditions[f]) & set(chart.get(f) or []) for f in declared):
                return True
        return False

    @staticmethod
    def specificity(cond):
        """命中精确度：声明了几个非空结构化字段（0=无约束通论条）。"""
        return sum(1 for k in HARD_FIELDS if cond.get(k))

    def structured_query(self, chart, include_general=False):
        """结构化召回。默认只返回至少一个硬维度命中的“精确条”，按
        (命中精确度↓, weight↓, path↑) 排序；无锚点通论条默认不返回。
        include_general=True 时把通论条（按 weight↓, path↑）整体附在最后。"""
        precise, general = [], []
        for e in self.entries:
            if self.is_general(e["conditions"]):
                general.append(e)
            elif self.match(e["conditions"], chart):
                precise.append(e)
        precise.sort(key=lambda e: (-self.specificity(e["conditions"]),
                                    -e["weight"], e["path"]))
        if include_general:
            general.sort(key=lambda e: (-e["weight"], e["path"]))
            return precise + general
        return precise

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

    # ── 正文三层加载器（轻量，按标记切分原文/古注/白话） ──────────
    BODY_MARKER = re.compile(r'\*\*【([^】]+)】\*\*')
    ORIGINAL_KEYS = {"原文", "经文", "原文·口诀", "原文（四库提要）"}
    VERNACULAR_KEYS = {"白话提要"}

    @staticmethod
    def load_body(path):
        """读取条目 .md，去掉 Frontmatter，按 **【...】** 标记切分三层正文。
        返回 {'original': 原文, 'annotation': 古注/评注, 'vernacular': 白话提要}。
        未出现的层返回空串。轻量实现，不做复杂排版解析。"""
        text = open(path, encoding="utf-8").read()
        if text.startswith("---"):
            parts = text.split("---", 2)
            body = parts[2] if len(parts) > 2 else text
        else:
            body = text
        markers = list(Library.BODY_MARKER.finditer(body))
        segments = []
        for i, m in enumerate(markers):
            key = m.group(1)
            start = m.end()
            end = markers[i + 1].start() if i + 1 < len(markers) else len(body)
            segments.append((key, body[start:end].strip()))
        original, annotation, vernacular = [], [], []
        for key, content in segments:
            if key in Library.ORIGINAL_KEYS:
                original.append(content)
            elif key in Library.VERNACULAR_KEYS:
                vernacular.append(content)
            else:
                annotation.append(content)
        return {
            "original": "\n".join(original).strip(),
            "annotation": "\n".join(annotation).strip(),
            "vernacular": "\n".join(vernacular).strip(),
        }


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
