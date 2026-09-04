# -*- coding: utf-8 -*-
"""精简导出：仅保留 id/标题 + 【原文】层（剔除注解、命例代码块），供快速通读撰写白话。
用法: python export_compact.py <bookdir> [out_tag]"""
import os, re, sys
BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
rel = sys.argv[1]
bdir = os.path.join(BASE, rel)
tag = sys.argv[2] if len(sys.argv) > 2 else rel.replace("\\", "_").replace("/", "_")
out = os.path.join(BASE, "scripts", "baihua_data", "_compact_%s.txt" % tag)
buf = []
for name in sorted(os.listdir(bdir)):
    if not name.endswith(".md") or name == "INDEX.md":
        continue
    t = open(os.path.join(bdir, name), encoding="utf-8").read()
    cid = re.search(r'^id:\s*"([^"]+)"', t, re.M).group(1)
    mt = re.search(r'^section_title:\s*"([^"]+)"', t, re.M)
    title = mt.group(1) if mt else ""
    body = t.split("---", 2)[2]
    body = re.split(r"\*\*【白话提要】\*\*", body)[0]
    # 只取【原文】段：从 **【原文】** 到下一个 **【 标记
    m = re.search(r"\*\*【原文】\*\*(.*?)(?=\*\*【|$)", body, re.S)
    yuan = m.group(1) if m else body
    yuan = re.sub(r"```.*?```", "", yuan, flags=re.S)  # 兜底去代码块
    yuan = yuan.strip()
    buf.append("@@ %s | %s\n%s" % (cid, title, yuan))
open(out, "w", encoding="utf-8").write("\n".join(buf))
print("精简导出", len(buf), "条 ->", os.path.relpath(out, BASE))
