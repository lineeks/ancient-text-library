# -*- coding: utf-8 -*-
"""
《命理约言》（清·陈之遴(素庵) 著，民国韦千里选辑《精选命理约言》）源文获取。
源为中华典藏分卷页（每卷一页），抓 panel-body 的 <p> 段，清洗导航/页脚，
修复站点反垃圾把「六合」替换成的 ****（仅 6 处，上下文皆「六合对三合」，确定还原），
合并输出 raw/mingliyaoyan.txt，以 @@PAGE <key> <标题> @@ 作机器可读分卷标记。
可重复运行（纯标准库）。
"""
import urllib.request, ssl, re, os, time

ctx=ssl.create_default_context(); ctx.check_hostname=False; ctx.verify_mode=ssl.CERT_NONE
UA={"User-Agent":"Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 Chrome/120 Safari/537.36"}
BASE=os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

PAGES=[("xu","序",195795),("juan1","卷一法四十八篇",195796),("juan2","卷二赋二十篇",195797),
       ("juan3","卷三论四十八篇",195798),("juan4","卷四杂论",195799),("ba","跋",195800)]
DROP=("陈之遴作品集","嘉兴韦千里选辑","中华典藏网旨在","吸取国学精华","本站非营利",
      "上一章","下一章","返回目录")
def get(u):
    for t in range(3):
        try:
            req=urllib.request.Request(u,headers=UA)
            return urllib.request.urlopen(req,timeout=45,context=ctx).read().decode("utf-8","replace")
        except Exception as e:
            print("retry",t,type(e).__name__); time.sleep(2)
    raise RuntimeError(u)
def paras(html):
    m=re.search(r'<div class="panel-body">(.*?)<div class="m-page">',html,re.S)
    body=m.group(1) if m else html
    out=[]
    for p in re.findall(r'<p[^>]*>(.*?)</p>',body,flags=re.S):
        t=re.sub(r'<[^>]+>','',p).replace('&nbsp;',' ').strip()
        if not t: continue
        if any(d in t for d in DROP): continue
        t=t.replace("****","六合")          # 站点屏蔽词还原：六合
        out.append(t)
    return out

blocks=[]
for key,title,cid in PAGES:
    html=get(f"https://www.diancang.xyz/xuanxuewushu/9589/{cid}.html")
    ps=paras(html)
    blocks.append((key,title,ps))
    print(f"{key} {title}: {len(ps)} 段")

out=[]
for key,title,ps in blocks:
    out.append(f"@@PAGE {key} {title} @@")
    out.extend(ps)
    out.append("")
raw=os.path.join(BASE,"raw","mingliyaoyan.txt")
open(raw,"w",encoding="utf-8").write("\n".join(out))
# 校验：不应再有 ****
left=open(raw,encoding="utf-8").read().count("****")
print("已写出",raw,"剩余****:",left)
