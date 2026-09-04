# -*- coding: utf-8 -*-
"""导出某书全部条目的 id/标题/正文原文（供撰写白话提要），用法: python export_for_baihua.py <bookdir>"""
import os, re, sys
BASE=os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
rel=sys.argv[1]
bdir=os.path.join(BASE,rel)
out=os.path.join(BASE,"scripts","baihua_data","_src_"+rel.replace("\\","_").replace("/","_")+".txt")
os.makedirs(os.path.dirname(out),exist_ok=True)
buf=[]
for name in sorted(os.listdir(bdir)):
    if not name.endswith(".md") or name=="INDEX.md": continue
    t=open(os.path.join(bdir,name),encoding="utf-8").read()
    cid=re.search(r'^id:\s*"([^"]+)"',t,re.M).group(1)
    title=re.search(r'^section_title:\s*"([^"]+)"',t,re.M).group(1)
    body=t.split("---",2)[2]
    # 取 ### 标题之后、白话层之前
    body=re.split(r"\*\*【白话提要】\*\*",body)[0]
    body=re.sub(r"^### .*$","",body,flags=re.M).strip()
    buf.append("@@ %s | %s\n%s"%(cid,title,body))
open(out,"w",encoding="utf-8").write("\n\n".join(buf))
print("导出",len(buf),"条 ->",os.path.relpath(out,BASE))
