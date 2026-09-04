# -*- coding: utf-8 -*-
"""
白话提要幂等回填管线。
数据：scripts/baihua_data/*.json，每个文件为 { "条目id": "白话译文", ... }，可分批增量添加。
行为：遍历 core / origin-shensha / extended 全部 md，按 id 匹配，仅把该条目
     「**【白话提要】**」层下的「（待补）」占位替换为译文，Frontmatter 与原文层一字不动。
     - 已补（无占位）的条目跳过，可重复运行；
     - --check 只统计、不写文件；
     - 译文只作文义串讲，不得新增吉凶断语。
"""
import os, re, json, glob, sys

BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
ROOTS = ["core", "origin-shensha", "extended"]
DATA_DIR = os.path.join(BASE, "scripts", "baihua_data")
CHECK = "--check" in sys.argv

# 合并所有数据文件
data = {}
for jf in sorted(glob.glob(os.path.join(DATA_DIR, "*.json"))):
    part = json.load(open(jf, encoding="utf-8"))
    overlap = set(data) & set(part)
    if overlap:
        print("WARN 数据文件 id 重复:", overlap)
    data.update(part)
print("载入白话译文 %d 条（来自 %s）" % (len(data), os.path.relpath(DATA_DIR, BASE)))

ID_RE = re.compile(r'^id:\s*"([^"]+)"', re.M)
PLACEHOLDER = "（待补）"

def iter_md():
    for root in ROOTS:
        rp = os.path.join(BASE, root)
        if not os.path.isdir(rp): continue
        for book in sorted(os.listdir(rp)):
            bp = os.path.join(rp, book)
            if not os.path.isdir(bp): continue
            for name in sorted(os.listdir(bp)):
                if name.endswith(".md") and name != "INDEX.md":
                    yield os.path.join(bp, name)

filled, skipped, nofile, still = 0, 0, [], 0
found_ids = set()
for path in iter_md():
    text = open(path, encoding="utf-8").read()
    m = ID_RE.search(text)
    cid = m.group(1) if m else os.path.basename(path)[:-3]
    if PLACEHOLDER in text: still += 1
    if cid not in data:
        continue
    found_ids.add(cid)
    baihua = data[cid].strip()
    if PLACEHOLDER not in text:
        skipped += 1; continue
    # 仅替换白话层占位（占位只出现在白话层）
    new = text.replace(PLACEHOLDER, baihua, 1)
    if not CHECK:
        open(path, "w", encoding="utf-8").write(new)
    filled += 1

nofile = sorted(set(data) - found_ids)
print("本次回填 %d 条；已是译文跳过 %d 条；%s后仍待补约 %d 条。"
      % (filled, skipped, "校验" if CHECK else "回填", still - (0 if CHECK else filled)))
if nofile:
    print("WARN 数据中找不到对应 md 的 id（%d）:" % len(nofile), nofile[:20])
