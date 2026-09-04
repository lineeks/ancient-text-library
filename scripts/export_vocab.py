# -*- coding: utf-8 -*-
"""
Aether-Cycle 古籍知识库 · 受控检索词表导出（治理工具，可用 PyYAML）

扫描全库 Frontmatter，统计 conditions 中受控字段（ten_god / pattern / shensha）
与固定枚举字段（day_master / month_branch）的取值与频次，确定性地写出
schema/controlled_vocabulary.json，作为 validate_library.py 的取值白名单：

  - ten_god / pattern / shensha 为受控词表，新增取值必须先更新本文件（显式、可审计），
    防止标签漂移、同义异形（如“天月德/天月二德”）无序滋生；
  - keywords 为开放主题词，不做受控校验；
  - day_master / month_branch 为固定英文枚举，一并写入供消费方参照。

重复运行输出字节稳定（按频次降序、同频按 Unicode 排序，无时间戳）。
用法：python -X utf8 scripts/export_vocab.py
"""
import json
import os
from collections import Counter

import yaml

BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
LIB_ROOTS = ["core", "origin-shensha", "extended"]
CONTROLLED = ["ten_god", "pattern", "shensha"]
TYPE_CONTROLLED = True  # type 也是受控枚举
FIXED_ENUM = ["day_master", "month_branch"]
OUT = os.path.join(BASE, "schema", "controlled_vocabulary.json")

VALID_STEM = ["Jia", "Yi", "Bing", "Ding", "Wu", "Ji", "Geng", "Xin", "Ren", "Gui"]
VALID_BRANCH = ["Yin", "Mao", "Chen", "Si", "Wu", "Wei", "Shen", "You",
                "Xu", "Hai", "Zi", "Chou"]

# 已登记同义/异形别名 -> 规范词。别名允许存量存在（validate 不报错），
# 但内容增强时应物理归一到规范词，归一后从此处与 terms 中一并移除。
ALIASES = {
    "shensha": {"三奇": "三奇贵人", "天月德": "天月二德"},
}


def walk():
    for root in LIB_ROOTS:
        rdir = os.path.join(BASE, root)
        if not os.path.isdir(rdir):
            continue
        for book in sorted(os.listdir(rdir)):
            bdir = os.path.join(rdir, book)
            if not os.path.isdir(bdir):
                continue
            for name in sorted(os.listdir(bdir)):
                if name.endswith(".md") and name != "INDEX.md":
                    yield os.path.join(bdir, name)


def terms_block(counter):
    items = sorted(counter.items(), key=lambda kv: (-kv[1], kv[0]))
    return {"distinct": len(items),
            "terms": [{"v": v, "n": n} for v, n in items]}


def main():
    counts = {k: Counter() for k in CONTROLLED}
    type_counts = Counter()
    total = 0
    for path in walk():
        text = open(path, encoding="utf-8").read()
        if not text.startswith("---"):
            continue
        meta = yaml.safe_load(text.split("---", 2)[1]) or {}
        cond = meta.get("conditions", {}) or {}
        total += 1
        for k in CONTROLLED:
            counts[k].update(cond.get(k, []) or [])
        if meta.get("type"):
            type_counts.update([meta["type"]])

    fields = {}
    for k in CONTROLLED:
        block = {"open": False, **terms_block(counts[k])}
        if k in ALIASES:
            block["aliases"] = ALIASES[k]  # alias -> canonical（登记存量异形）
        fields[k] = block
    fields["type"] = {"open": False, **terms_block(type_counts),
                       "note": "条目体裁枚举，新增须先在 docs/metadata-spec.md §3 登记"}
    fields["day_master"] = {"open": False, "enum": VALID_STEM}
    fields["month_branch"] = {"open": False, "enum": VALID_BRANCH}
    fields["keywords"] = {"open": True,
                          "note": "开放主题词，不做受控取值校验，仅用于包含式召回。"}

    vocab = {
        "schema_version": 1,
        "name": "Aether-Cycle 受控检索词表",
        "note": "ten_god/pattern/shensha 为受控字段；新增取值须先更新本文件再入库，"
                "validate_library.py 据此做白名单校验。由 scripts/export_vocab.py 统计生成。",
        "scanned_entries": total,
        "fields": fields,
    }
    os.makedirs(os.path.dirname(OUT), exist_ok=True)
    with open(OUT, "w", encoding="utf-8", newline="\n") as f:
        json.dump(vocab, f, ensure_ascii=False, indent=2)
        f.write("\n")
    print(f"受控词表已写出：{OUT}")
    for k in CONTROLLED:
        print(f"  {k}: {fields[k]['distinct']} 个取值，覆盖 {sum(counts[k].values())} 处")
    print(f"  type: {fields['type']['distinct']} 个体裁")


if __name__ == "__main__":
    main()
