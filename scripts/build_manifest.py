# -*- coding: utf-8 -*-
"""
Aether-Cycle 古籍知识库 · 机器检索清单 manifest.json 生成器（纯标准库、确定性输出）

扫描 ming/bazi/{core,origin-shensha,extended} 下全部 Markdown，解析 Frontmatter，
聚合为一张供排盘引擎（Rust/Tauri 或任意运行时）一次性加载的总清单，
引擎侧无需再遍历目录、无需 YAML 依赖即可建立 conditions 内存索引。

输出：库根 manifest.json
  - 不写时间戳，entries 按相对路径排序，保证重复生成字节稳定（diff 友好）；
  - 每条含 id / book / type / tier / path / weight / title / chapter / conditions；
  - conditions 八字段齐全（空则 []），匹配语义：声明了的字段必须与命盘有交集才召回。

用法：python -X utf8 scripts/build_manifest.py
"""
import json
import os
import re

BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
# (root_dir, tier_name, category, default_subcategory)
# ming/bazi/{core,origin-shensha,extended} 为八字内部梯队，统一归 category=ming, subcategory=bazi；
# ming/yi/xiang/bu/shan 为五术顶层目录，subcategory 取二级目录名。
ROOTS = [
    ("library/ming/bazi/core", "第一梯队·核心", "ming", "bazi"),
    ("library/ming/bazi/origin-shensha", "第二梯队·渊源神煞", "ming", "bazi"),
    ("library/ming/bazi/extended", "第三梯队·实战与补遗", "ming", "bazi"),
    ("library/ming", "命·命理", "ming", ""),
    ("library/ming/ziwei", "紫微斗数", "ming", "ziwei"),
    ("library/ming/qizheng", "七政四余", "ming", "qizheng"),
    ("library/yi", "医·中医", "yi", ""),
    ("library/xiang", "相·相术", "xiang", ""),
    ("library/bu", "卜·卜筮", "bu", ""),
    ("library/shan", "山·仙学养生", "shan", ""),
]
FIVE_ARTS_ROOTS = {"ming", "yi", "xiang", "bu", "shan"}
LIST_KEYS = {"day_master", "month_branch", "ten_god", "pattern", "shensha",
             "keywords", "tags", "day_pillar", "hour_pillar"}
COND_FIELDS = ["day_master", "month_branch", "day_pillar", "hour_pillar",
               "ten_god", "pattern", "shensha", "keywords"]
OUT = os.path.join(BASE, "manifest.json")


def parse_frontmatter(path):
    with open(path, encoding="utf-8") as f:
        text = f.read()
    m = re.match(r"^---\n(.*?)\n---", text, re.S)
    if not m:
        return {}
    meta = {}
    for line in m.group(1).splitlines():
        mm = re.match(r"^(\w+):\s*(.*)$", line)
        if mm:
            meta[mm.group(1)] = mm.group(2).strip().strip('"')
        mm2 = re.match(r"^\s+(\w+):\s*\[(.*)\]", line)
        if mm2 and mm2.group(1) in LIST_KEYS:
            meta[mm2.group(1)] = [x.strip().strip('"')
                                  for x in mm2.group(2).split(",") if x.strip()]
    return meta


def as_int(v, default=0):
    try:
        return int(v)
    except (TypeError, ValueError):
        return default


def main():
    books = []
    entries = []
    seen_ids = set()
    for root, tier_name, category, default_sub in ROOTS:
        rdir = os.path.join(BASE, root)
        if not os.path.isdir(rdir):
            continue
        for book in sorted(os.listdir(rdir)):
            bdir = os.path.join(rdir, book)
            if not os.path.isdir(bdir):
                continue
            # 五术顶层目录的二级目录即为 subcategory（如 yi/shanghanlun/ -> shanghanlun）
            subcategory = book if root.split("/")[-1] in FIVE_ARTS_ROOTS else default_sub
            n = 0
            for name in sorted(os.listdir(bdir)):
                if not name.endswith(".md") or name == "INDEX.md":
                    continue
                rel = "/".join([root, book, name])
                meta = parse_frontmatter(os.path.join(bdir, name))
                cid = meta.get("id", name[:-3])
                if cid in seen_ids:
                    raise SystemExit(f"[manifest] id 重复: {cid} ({rel})")
                seen_ids.add(cid)
                cond = {k: list(meta.get(k, []) or []) for k in COND_FIELDS}
                entries.append({
                    "id": cid,
                    "book": meta.get("book", book),
                    "type": meta.get("type", ""),
                    "tier": root,
                    "category": category,
                    "subcategory": subcategory,
                    "path": rel,
                    "weight": as_int(meta.get("weight")),
                    "title": meta.get("section_title", ""),
                    "chapter": meta.get("chapter", ""),
                    "conditions": cond,
                })
                n += 1
            books.append({"dir": book, "tier": root, "tier_name": tier_name,
                          "category": category, "subcategory": subcategory, "count": n})
    entries.sort(key=lambda e: e["path"])
    manifest = {
        "schema_version": 2,
        "name": "Aether-Cycle 五术古籍图书馆",
        "match_fields": COND_FIELDS,
        "match_rule": "entry is recalled iff, for every non-empty declared field, "
                      "it intersects the chart's same-field set; results sort by weight desc.",
        "roots": {r: t for r, t, _, _ in ROOTS},
        "categories": ["ming", "yi", "xiang", "bu", "shan"],
        "books": books,
        "total": len(entries),
        "entries": entries,
    }
    with open(OUT, "w", encoding="utf-8", newline="\n") as f:
        json.dump(manifest, f, ensure_ascii=False, indent=2)
        f.write("\n")
    print(f"manifest.json 已生成：{len(entries)} 条，{len(books)} 部。")
    for b in books:
        print(f"  {b['tier']:<16}{b['dir']:<20}{b['count']}")


if __name__ == "__main__":
    main()
