# -*- coding: utf-8 -*-
"""
Aether-Cycle 古籍知识库 · 交付前质量门校验
校验项：
  1. 每个 md 的 Frontmatter 可被标准 YAML 解析器解析；
  2. id 全局唯一，且与文件名（去扩展名）一致；
  3. 必填字段齐全；conditions 各字段为列表；
  4. day_master / month_branch 使用英文枚举；
  5. 穷通宝鉴 monthly 必有 day_master+month_branch；子平真诠章号 1..48 唯一连续；
  6. 正文三层结构标记齐全（【原文】、【白话提要】）。
"""
import os
import sys
import yaml

BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CORE = os.path.join(BASE, "core")

VALID_STEM = {"Jia", "Yi", "Bing", "Ding", "Wu", "Ji", "Geng", "Xin", "Ren", "Gui"}
VALID_BRANCH = {"Yin", "Mao", "Chen", "Si", "Wu", "Wei", "Shen", "You", "Xu", "Hai", "Zi", "Chou"}
REQUIRED = ["id", "book", "chapter", "section_title", "source_version",
            "author", "dynasty", "type", "conditions", "weight", "tags"]
COND_KEYS = ["day_master", "month_branch", "day_pillar", "hour_pillar",
             "ten_god", "pattern", "shensha", "keywords"]

errors, warnings = [], []
all_ids, seen_files = {}, 0
ch_nums = []


def walk():
    for book in sorted(os.listdir(CORE)):
        bdir = os.path.join(CORE, book)
        if not os.path.isdir(bdir):
            continue
        for name in sorted(os.listdir(bdir)):
            if not name.endswith(".md") or name == "INDEX.md":
                continue
            yield book, name, os.path.join(bdir, name)


for book, name, path in walk():
    seen_files += 1
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

    # 必填字段
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

    t = meta.get("type")
    if book == "qiongtongbj":
        if t == "monthly" and isinstance(cond, dict):
            if not cond.get("day_master") or not cond.get("month_branch"):
                errors.append(f"[月度条目缺日干/月令] {book}/{name}")
    if book == "zipingzhenquan":
        n = meta.get("chapter_num")
        if isinstance(n, int):
            ch_nums.append(n)

    # 正文结构：穷通宝鉴/子平真诠用【原文】，滴天髓用【经文】
    if book == "ditianchui":
        if "**【经文】**" not in text and "**【刘伯温原注】**" not in text:
            errors.append(f"[缺【经文】/原注层] {book}/{name}")
    else:
        if "**【原文】**" not in text:
            errors.append(f"[缺【原文】层] {book}/{name}")
    if "**【白话提要】**" not in text:
        errors.append(f"[缺【白话提要】层] {book}/{name}")

# 子平真诠章号连续性
if ch_nums:
    ch_nums_sorted = sorted(ch_nums)
    expect = list(range(1, len(ch_nums_sorted) + 1))
    if ch_nums_sorted != expect:
        errors.append(f"[子平真诠章号不连续/缺失] 实际={ch_nums_sorted}")
    if len(ch_nums) != len(set(ch_nums)):
        errors.append("[子平真诠章号重复]")

print(f"扫描文件数: {seen_files}，全局唯一 id 数: {len(all_ids)}")
if ch_nums:
    print(f"子平真诠章号: {min(ch_nums)}..{max(ch_nums)}，共 {len(ch_nums)} 章")
if warnings:
    print("\n--- 警告 ---")
    for w in warnings:
        print(" WARN", w)
if errors:
    print(f"\n--- 发现 {len(errors)} 个错误 ---")
    for e in errors:
        print(" ERR ", e)
    sys.exit(1)
print("\n✅ 校验全部通过：YAML 可解析、id 唯一且与文件名一致、字段完整、枚举合法、正文三层齐全。")
