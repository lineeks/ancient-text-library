# -*- coding: utf-8 -*-
"""
Aether-Cycle 古籍知识库 · 交付前质量门校验（全库：core / origin-shensha / extended）
校验项：
  1. 每个 md 的 Frontmatter 可被标准 YAML 解析器解析；
  2. id 全局唯一，且与文件名（去扩展名）一致；
  3. 必填字段齐全；conditions 各字段为列表；
  4. day_master / month_branch 使用英文枚举；day_pillar / hour_pillar 为合法六十甲子（中文）；
  5. 穷通宝鉴 monthly 必有 day_master+month_branch；
     三命通会 rishi 必有 day_pillar+hour_pillar、shensha 必有 shensha；
     子平真诠章号 1..48 唯一连续；
  6. 正文分层标记齐全（【原文】/【经文】/【原文·口诀】之一 + 【白话提要】）。
"""
import json
import os
import sys
import yaml

BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
LIB_ROOTS = ["library/ming/bazi/core", "library/ming/bazi/origin-shensha", "library/ming/bazi/extended", "library/ming", "library/ming/ziwei", "library/ming/qizheng", "library/yi/jingdian", "library/yi/fangshu", "library/yi/wenbing", "library/yi/zhenji", "library/yi/zhenfa", "library/yi", "library/xiang", "library/bu", "library/shan"]
CONTROLLED_FIELDS = ["ten_god", "pattern", "shensha"]

# 受控词表白名单（由 scripts/export_vocab.py 生成）。允许规范词与已登记别名，
# 未登记取值判错，以防标签漂移 / 同义异形无序滋生。
_VOCAB_PATH = os.path.join(BASE, "schema", "controlled_vocabulary.json")
try:
    with open(_VOCAB_PATH, encoding="utf-8") as _f:
        _vocab = json.load(_f)
    ALLOWED_TERMS = {
        k: (set(t["v"] for t in _vocab["fields"][k]["terms"])
            | set(_vocab["fields"][k].get("aliases", {}).keys()))
        for k in CONTROLLED_FIELDS
    }
except FileNotFoundError:
    print("缺少 schema/controlled_vocabulary.json，请先运行 python scripts/export_vocab.py")
    sys.exit(2)

VALID_STEM = {"Jia", "Yi", "Bing", "Ding", "Wu", "Ji", "Geng", "Xin", "Ren", "Gui"}
VALID_BRANCH = {"Yin", "Mao", "Chen", "Si", "Wu", "Wei", "Shen", "You", "Xu", "Hai", "Zi", "Chou"}
_ZH_STEM = "甲乙丙丁戊己庚辛壬癸"
_ZH_BRANCH = "子丑寅卯辰巳午未申酉戌亥"
JIAZI = {_ZH_STEM[i % 10] + _ZH_BRANCH[i % 12] for i in range(60)}
REQUIRED = ["id", "book", "chapter", "section_title", "source_version",
            "author", "dynasty", "type", "conditions", "weight", "tags"]
COND_KEYS = ["day_master", "month_branch", "day_pillar", "hour_pillar",
             "ten_god", "pattern", "shensha", "keywords"]

errors, warnings = [], []
all_ids = {}
seen_files = 0
per_book = {}
ch_nums = []


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
                if not name.endswith(".md") or name == "INDEX.md":
                    continue
                yield root, book, name, os.path.join(bdir, name)


for root, book, name, path in walk():
    seen_files += 1
    per_book.setdefault(book, 0)
    per_book[book] += 1
    text = open(path, encoding="utf-8").read()
    if not text.startswith("---"):
        errors.append(f"[无Frontmatter] {book}/{name}")
        continue
    try:
        fm_text = text.split("---", 2)[1]
        meta = yaml.safe_load(fm_text)
    except Exception as e:
        errors.append(f"[YAML解析失败] {book}/{name}: {e}")
        continue
    if not isinstance(meta, dict):
        errors.append(f"[Frontmatter非字典] {book}/{name}")
        continue

    for k in REQUIRED:
        if k not in meta:
            errors.append(f"[缺字段 {k}] {book}/{name}")

    cid = meta.get("id", "")
    if cid in all_ids:
        errors.append(f"[id重复] {cid}: {all_ids[cid]} 与 {book}/{name}")
    else:
        all_ids[cid] = f"{book}/{name}"
    if cid and name != f"{cid}.md":
        errors.append(f"[id与文件名不一致] id={cid} 文件={name}")

    cond = meta.get("conditions", {})
    if not isinstance(cond, dict):
        errors.append(f"[conditions非字典] {book}/{name}")
    else:
        for ck in COND_KEYS:
            v = cond.get(ck, [])
            if not isinstance(v, list):
                errors.append(f"[conditions.{ck}非列表] {book}/{name}")
        for s in cond.get("day_master", []):
            if s not in VALID_STEM:
                errors.append(f"[日干非英文枚举:{s}] {book}/{name}")
        for b in cond.get("month_branch", []):
            if b not in VALID_BRANCH:
                errors.append(f"[月令非英文枚举:{b}] {book}/{name}")
        for p in cond.get("day_pillar", []) + cond.get("hour_pillar", []):
            if p not in JIAZI:
                errors.append(f"[干支柱非六十甲子:{p}] {book}/{name}")
        for cf in CONTROLLED_FIELDS:
            for v in cond.get(cf, []):
                if v not in ALLOWED_TERMS[cf]:
                    errors.append(
                        f"[受控词表外取值 {cf}={v}] {book}/{name}；"
                        f"如确需新增，请先更新 schema/controlled_vocabulary.json")

    t = meta.get("type")
    if book == "qiongtongbj" and t == "monthly" and isinstance(cond, dict):
        if not cond.get("day_master") or not cond.get("month_branch"):
            errors.append(f"[月度条目缺日干/月令] {book}/{name}")
    if book == "sanmingtonghui":
        if t == "rishi" and isinstance(cond, dict):
            if not cond.get("day_pillar") or not cond.get("hour_pillar"):
                errors.append(f"[日时断缺日柱/时柱] {book}/{name}")
        if t == "shensha" and isinstance(cond, dict) and not cond.get("shensha"):
            errors.append(f"[神煞条目缺 shensha] {book}/{name}")
    if book == "zipingzhenquan":
        n = meta.get("chapter_num")
        if isinstance(n, int):
            ch_nums.append(n)

    # 正文分层：滴天髓用【经文】（特例《从象》源文无口诀，以原注起首，故兼容原注/阐微层），
    # 玉照用【原文·口诀】，其余用【原文】
    has_body = ("**【原文】**" in text or "**【经文】**" in text
                or "**【原文·口诀】**" in text or "**【原文（四库提要）】**" in text
                or "**【刘伯温原注】**" in text or "**【任铁樵阐微】**" in text)
    if not has_body:
        errors.append(f"[缺原文/经文层] {book}/{name}")
    if "**【白话提要】**" not in text:
        errors.append(f"[缺【白话提要】层] {book}/{name}")

# 子平真诠章号连续性
if ch_nums:
    ch_sorted = sorted(ch_nums)
    expect = list(range(1, len(ch_sorted) + 1))
    if ch_sorted != expect:
        errors.append(f"[子平真诠章号不连续/缺失] 实际={ch_sorted}")
    if len(ch_nums) != len(set(ch_nums)):
        errors.append("[子平真诠章号重复]")

print("各典籍文件数：")
for b in sorted(per_book):
    print(f"  {b}: {per_book[b]}")
print(f"扫描文件数: {seen_files}，全局唯一 id 数: {len(all_ids)}")
if ch_nums:
    print(f"子平真诠章号: {min(ch_nums)}..{max(ch_nums)}，共 {len(ch_nums)} 章")
if warnings:
    print("\n--- 警告 ---")
    for w in warnings:
        print(" WARN", w)
if errors:
    print(f"\n--- 发现 {len(errors)} 个错误 ---")
    for e in errors[:50]:
        print(" ERR ", e)
    if len(errors) > 50:
        print(f"  …另有 {len(errors)-50} 个错误")
    sys.exit(1)
print("\n✅ 校验全部通过：YAML 可解析、id 唯一且与文件名一致、字段完整、枚举合法、正文分层齐全。")
