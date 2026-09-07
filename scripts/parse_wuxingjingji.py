# -*- coding: utf-8 -*-
"""
《五行精纪》（宋·廖中 撰，岳珂序，34 卷）解析为结构化 Markdown。
源：raw/wuxingjingji.txt（同源 GitHub 古籍仓库，UTF-8）。
切分：序一/序二 + 34 卷；卷内按「论/释/并…」小节标题切，标题以目录(L22-177)为权威依据、正文实际标题为准。
文件名 ASCII：wxjj_xu{1,2} / wxjj_v{卷:02d}_{小节:02d}；中文标题入 Frontmatter。
运行：python scripts/parse_wuxingjingji.py --write（运行前请手动清空 extended/wuxingjingji/*.md）
"""
import os, re, sys

BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
RAW = os.path.join(BASE, "raw", "wuxingjingji.txt")
OUT = os.path.join(BASE, "library", "ming", "bazi", "extended", "wuxingjingji")
DRY = "--write" not in sys.argv

DIGIT = {"零":0,"〇":0,"○":0,"一":1,"二":2,"两":2,"三":3,"四":4,"五":5,"六":6,"七":7,"八":8,"九":9}
def cnnum(s):
    if "廿" in s:
        t=s.replace("廿",""); return 20+(DIGIT.get(t,0) if t else 0)
    if "卅" in s:
        t=s.replace("卅",""); return 30+(DIGIT.get(t,0) if t else 0)
    if "十" in s:
        a,b=s.split("十"); a=DIGIT.get(a,1) if a else 1; b=DIGIT.get(b,0) if b else 0
        return a*10+b
    ds=[DIGIT[c] for c in s if c in DIGIT]; v=0
    for d in ds: v=v*10+d
    return v if ds else None

lines = [l.rstrip() for l in open(RAW, encoding="utf-8").read().splitlines()]

# 1) 目录 -> {卷号:(卷主题,[小节])}
vol_line = re.compile(r"^第([零〇○一二两三四五六七八九十廿卅]+)卷(.+)$")
toc, cur = {}, None
for i in range(22, 177):
    s = lines[i].strip()
    if not s: continue
    m = vol_line.match(s)
    if m:
        cur = cnnum(m.group(1)); toc[cur] = (m.group(2).strip(), [])
    elif cur is not None and s not in ("序一","序二","目录：","五行精纪","宋廖中"):
        toc[cur][1].append(s)

# 2) 正文卷边界
vol_head = re.compile(r"^第([零〇○一二两三四五六七八九十廿卅]+)卷$")
bounds=[]
for i,l in enumerate(lines):
    m=vol_head.match(l.strip())
    if m: bounds.append((i, cnnum(m.group(1))))
assert [b[1] for b in bounds]==list(range(1,35)), [b[1] for b in bounds]

HEAD=re.compile(r"^[论释并辨歌赋解杂][一-鿿]{1,16}$")
def is_head(s, secnames):
    if not s or len(s)>16 or re.search(r"[，。、；：？！,.;:?!]",s): return False
    return s in secnames or bool(HEAD.match(s))

def collect(a,b):
    return "\n\n".join(x.strip() for x in lines[a:b] if x.strip())

# 3) conditions 智能映射（宁空勿错，keywords 保底）
SMAP=[("天乙","天乙贵人"),("贵神","天乙贵人"),("禄","禄神"),("驿马","驿马"),("马","驿马"),
      ("华盖","华盖"),("金舆","金舆"),("学堂","学堂"),("文章","学堂"),("三刑","三刑"),
      ("六害","六害"),("空亡","空亡"),("劫杀","劫煞"),("亡神","亡神"),("三奇","三奇"),
      ("羊刃","羊刃"),("金杀","金煞"),("凶杀","凶煞"),("凶神","凶煞"),("吉神","吉神"),
      ("进神","进神"),("库墓","墓库"),("贵局","贵格")]
TMAP=[("正印","正印"),("印绶","正印"),("食神","食神"),("偏正财","正财"),("财","正财"),("官神","正官")]
def meta_for(title):
    dm=[]; ss=[]; tg=[]
    if "甲乙" in title: dm=["Jia","Yi"]
    elif "丙丁" in title: dm=["Bing","Ding"]
    elif "戊己" in title: dm=["Wu","Ji"]
    elif "庚辛" in title: dm=["Geng","Xin"]
    elif "壬癸" in title: dm=["Ren","Gui"]
    for k,v in SMAP:
        if k in title and v not in ss: ss.append(v)
    for k,v in TMAP:
        if k in title and v not in tg: tg.append(v)
    core=re.sub(r"^(论|释|并|杂)","",title)
    kw=[core] if core else [title]
    return dm,ss,tg,kw

def yml_list(xs):
    return "[" + ", ".join('"%s"'%x for x in xs) + "]"

# 4) 切分 records: (rid,title,chapter,vol,body)
records=[]
records.append(("wxjj_xu1","序一","序",0,collect(2,8)))
records.append(("wxjj_xu2","序二（鄂国岳珂序）","序",0,collect(8,22)))
for k,(ln,n) in enumerate(bounds):
    end = bounds[k+1][0] if k+1<len(bounds) else len(lines)
    vtitle, secnames = toc.get(n,("",))
    heads=[(j,lines[j].strip()) for j in range(ln+1,end) if is_head(lines[j].strip(),set(secnames))]
    if heads:
        lead=collect(ln+1,heads[0][0])
        if lead: records.append((f"wxjj_v{n:02d}_00", vtitle or f"第{n}卷", f"第{n}卷·{vtitle}", n, lead))
        for hi,(hj,ht) in enumerate(heads):
            hnext=heads[hi+1][0] if hi+1<len(heads) else end
            body=collect(hj+1,hnext)
            if body: records.append((f"wxjj_v{n:02d}_{hi+1:02d}", ht, f"第{n}卷·{vtitle}", n, body))
    else:
        records.append((f"wxjj_v{n:02d}_01", vtitle or f"第{n}卷", f"第{n}卷·{vtitle}", n, collect(ln+1,end)))

print("总条目:",len(records))
if DRY:
    for rid,title,chap,v,body in records: print(f"  {rid:14s} {title} ({len(body)}字)")
    print("[dry-run] 加 --write 生成"); sys.exit(0)

os.makedirs(OUT, exist_ok=True)
for rid,title,chap,v,body in records:
    dm,ss,tg,kw=meta_for(title)
    tags=["五行精纪"]+([chap.split("·")[0]] if v else ["序"])+kw[:2]
    fm=f"""---
id: "{rid}"
book: "五行精纪"
chapter: "{chap}"
section_title: "{title}"
source_version: "宋·廖中撰·岳珂序（同源古籍电子本）"
author: "廖中"
dynasty: "宋"
type: "chapter"
conditions:
  day_master: {yml_list(dm)}
  month_branch: []
  day_pillar: []
  hour_pillar: []
  ten_god: {yml_list(tg)}
  pattern: []
  shensha: {yml_list(ss)}
  keywords: {yml_list(kw)}
weight: 2
tags: {yml_list(tags)}
---

### {title}

**【原文】**

{body}

**【白话提要】**

（待补）
"""
    open(os.path.join(OUT,rid+".md"),"w",encoding="utf-8").write(fm)
print("已写入",OUT)
