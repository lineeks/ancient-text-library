# -*- coding: utf-8 -*-
"""
《命理约言》（清·陈之遴(素庵)撰，民国韦千里选辑《精选命理约言》）解析为结构化 Markdown。
源：raw/mingliyaoyan.txt（fetch_mingliyaoyan.py 抓中华典藏标点本、清洗合并，@@PAGE 分卷）。
切分：序/跋各 1；卷一「看…法」48 法；卷二 20 赋；卷三 48 论（含诸格/带夹注标题）；卷四杂论整卷 1。
文件名 ASCII：mlyy_{xu,ba,fa,fu,lun,za}{两位序号}。运行前手动清空 extended/mingliyaoyan/*.md。
"""
import os, re, sys
BASE=os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
RAW=os.path.join(BASE,"raw","mingliyaoyan.txt")
OUT=os.path.join(BASE,"library", "ming", "bazi", "extended", "mingliyaoyan")
DRY="--write" not in sys.argv

raw=open(RAW,encoding="utf-8").read().splitlines()
pages={}; order=[]; cur=None; buf=[]
for l in raw:
    m=re.match(r"^@@PAGE (\w+) (.+?) @@$",l.strip())
    if m:
        if cur: pages[cur]=buf
        cur=m.group(1); order.append((cur,m.group(2))); buf=[]
    elif cur is not None: buf.append(l.strip())
if cur: pages[cur]=buf

NOPUN=lambda s: not re.search(r"[，。、；：？！,.;:?!]",s)
def fa_head(s):
    return bool(s) and len(s)<=16 and NOPUN(s) and bool(re.match(r"^看[一-鿿]{1,12}法[一二三四五六七八九十百零〇\d]*$",s))
def fu_head(s):
    return bool(s) and len(s)<=14 and NOPUN(s) and bool(re.match(r"^[一-鿿]{1,12}赋$",s))
def lun_head(s):
    if not s or len(s)>18 or not NOPUN(s): return False
    core=re.sub(r"（.*?）","",s)
    return bool(re.search(r"(论[一二三四五六七八九十]?|格|败)$",core)) or core.startswith("诸神煞")

def split_by(lines, is_head):
    items=[]; t=None; b=[]
    for s in lines:
        if is_head(s):
            if t is not None: items.append((t,b))
            t=s; b=[]
        elif t is not None and s: b.append(s)
    if t is not None: items.append((t,b))
    return items

fa=split_by(pages["juan1"],fa_head)
fu=split_by(pages["juan2"],fu_head)
lun=split_by(pages["juan3"],lun_head)
print("法 %d / 赋 %d / 论 %d"%(len(fa),len(fu),len(lun)))
assert len(fa)==48 and len(fu)==20 and len(lun)==48,(len(fa),len(fu),len(lun))

# ---- conditions 映射（子平旺衰派，十神/格局为主）----
def meta(title):
    t=title; tg=[]; pat=[]; ss=[]
    def add(xs,x):
        if x not in xs: xs.append(x)
    if "正官" in t: add(tg,"正官"); add(pat,"正官格")
    if ("偏官" in t) or ("官煞" in t) or ("煞" in t): add(tg,"七杀"); add(pat,"七杀格")
    if "印" in t: add(tg,"正印"); add(tg,"偏印")
    if "财" in t: add(tg,"正财"); add(tg,"偏财")
    if "食神" in t: add(tg,"食神")
    if "伤官" in t: add(tg,"伤官")
    if ("比劫" in t) or ("禄刃" in t): add(tg,"比肩"); add(tg,"劫财")
    if "从局" in t: add(pat,"从格")
    if "化局" in t: add(pat,"化格")
    for k in ["一行得气","两神成象","暗冲","暗合","拱夹","六阴朝阳","魁罡","金神","合禄",
              "时格","遥合","六乙鼠贵","壬骑龙背","青龙伏形","福德秀气"]:
        if k in t: add(pat,k+"格" if not k.endswith("格") else k)
    sm=[("天月二德","天月二德"),("贵人","天乙贵人"),("驿马","驿马"),("空亡","空亡"),
        ("劫煞","劫煞"),("三奇","三奇"),("学堂","学堂"),("金神","金神"),("月煞","月煞"),
        ("十恶大败","十恶大败"),("魁罡","魁罡"),("神煞","神煞")]
    for k,v in sm:
        if k in t: add(ss,v)
    core=re.sub(r"^(看)|(法[一二三四五六七八九十]?$)|(论[一二三四五六七八九十]?$)|赋$|格$","",t)
    core=re.sub(r"（.*?）","",core)
    kw=[core] if core else [t]
    return tg,pat,ss,kw

def yl(xs): return "["+", ".join('"%s"'%x for x in xs)+"]"
def render(rid,title,chap,body_paras):
    tg,pat,ss,kw=meta(title)
    body="\n\n".join(body_paras)
    tags=["命理约言",chap]+kw[:2]
    return f"""---
id: "{rid}"
book: "命理约言"
chapter: "{chap}"
section_title: "{title}"
source_version: "清·陈之遴(素庵)撰·民国韦千里选辑《精选命理约言》中华典藏标点本"
author: "陈之遴（陈素庵）"
dynasty: "清"
type: "chapter"
conditions:
  day_master: []
  month_branch: []
  day_pillar: []
  hour_pillar: []
  ten_god: {yl(tg)}
  pattern: {yl(pat)}
  shensha: {yl(ss)}
  keywords: {yl(kw)}
weight: 2
tags: {yl(tags)}
---

### {title}

**【原文】**

{body}

**【白话提要】**

（待补）
"""

records=[]
xu=[x for x in pages["xu"] if x]; records.append(("mlyy_xu01","序","序",xu))
for i,(t,b) in enumerate(fa,1): records.append((f"mlyy_fa{i:02d}",t,"卷一·法四十八篇",b))
for i,(t,b) in enumerate(fu,1): records.append((f"mlyy_fu{i:02d}",t,"卷二·赋二十篇",b))
for i,(t,b) in enumerate(lun,1): records.append((f"mlyy_lun{i:02d}",t,"卷三·论四十八篇",b))
za=[x for x in pages["juan4"] if x]
# 去掉首行“杂论二十四则”标题本身，作为 section_title
if za and za[0].startswith("杂论"): za=za[1:]
records.append(("mlyy_za01","杂论二十四则（附张神峰辟五行诸谬）","卷四·杂论",za))
ba=[x for x in pages["ba"] if x]; records.append(("mlyy_ba01","跋","跋",ba))

empty=[r[0] for r in records if not r[3]]
print("总条目",len(records),"空正文",empty)
if DRY:
    for rid,t,c,b in records: print(f"  {rid:14s} {c} {t} ({sum(len(x) for x in b)}字)")
    print("[dry-run] 加 --write 生成"); sys.exit(0)

os.makedirs(OUT,exist_ok=True)
for rid,t,c,b in records:
    open(os.path.join(OUT,rid+".md"),"w",encoding="utf-8").write(render(rid,t,c,b))
print("已写入",OUT)
