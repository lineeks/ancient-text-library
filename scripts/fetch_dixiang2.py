# -*- coding: utf-8 -*-
"""获取博山篇(8章) + 催官篇(4卷) 全文"""
import urllib.request, re, time, os

BASE = r'D:\OneDrive\Desktop\111\ancient-text-library'

def fetch(url, timeout=20):
    req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
    return urllib.request.urlopen(req, timeout=timeout).read().decode('utf-8', errors='ignore')

def clean(html):
    text = re.sub(r'<[^>]+>', '', html)
    text = re.sub(r'&nbsp;', ' ', text)
    text = re.sub(r'&[a-z]+;', '', text)
    text = re.sub(r'\s+', ' ', text)
    return text.strip()

# ===== 博山篇 8章 (ID 230309-230316) =====
BS_CHAPTERS = [
    (230309, "概论相地法"),
    (230310, "论龙"),
    (230311, "论穴"),
    (230312, "论砂"),
    (230313, "论水"),
    (230314, "论明堂"),
    (230315, "论阳宅"),
    (230316, "论平地"),
]

print("=== 博山篇 ===")
bs_text = []
for pid, title in BS_CHAPTERS:
    url = f'https://www.diancang.xyz/xuanxuewushu/11586/{pid}.html'
    try:
        html = fetch(url)
        text = clean(html)
        # 找正文开始
        starts = [text.find('论曰'), text.find('善知识'), text.find('博山'),
                  text.find('凡看山'), text.find('论龙'), text.find('论穴')]
        start = min([s for s in starts if s >= 0]) if any(s >= 0 for s in starts) else 0
        text = text[start:]
        end = min([x for x in [text.find('上一篇'), text.find('下一篇'), text.find('目录'),
                                text.find('原创内容')] if x > 0] + [len(text)])
        text = text[:end].strip()
        bs_text.append(f'=== {title} ===\n{text}')
        print(f'  {title}: {len(text)} 字符')
        time.sleep(0.3)
    except Exception as e:
        print(f'  {title}: 错误 {e}')

with open(os.path.join(BASE, 'raw/boshan-pian.txt'), 'w', encoding='utf-8') as f:
    f.write('\n\n'.join(bs_text))
print(f'  博山篇保存: {sum(len(t) for t in bs_text)} 字符')

# ===== 催官篇 4卷 (ID 41871-41874) =====
CG_CHAPTERS = [
    (41871, "评龙章"),
    (41872, "评穴章"),
    (41873, "评砂章"),
    (41874, "评水章"),
]

print("\n=== 催官篇 ===")
cg_text = []
for pid, title in CG_CHAPTERS:
    url = f'https://www.diancang.xyz/xuanxuewushu/cuiguanpian/{pid}.html'
    try:
        html = fetch(url)
        text = clean(html)
        starts = [text.find('催官'), text.find('评龙'), text.find('评穴'),
                  text.find('评砂'), text.find('评水')]
        start = min([s for s in starts if s >= 0]) if any(s >= 0 for s in starts) else 0
        text = text[start:]
        end = min([x for x in [text.find('上一篇'), text.find('下一篇'), text.find('目录'),
                                text.find('原创内容')] if x > 0] + [len(text)])
        text = text[:end].strip()
        cg_text.append(f'=== {title} ===\n{text}')
        print(f'  {title}: {len(text)} 字符')
        time.sleep(0.3)
    except Exception as e:
        print(f'  {title}: 错误 {e}')

with open(os.path.join(BASE, 'raw/cuiguan-pian.txt'), 'w', encoding='utf-8') as f:
    f.write('\n\n'.join(cg_text))
print(f'  催官篇保存: {sum(len(t) for t in cg_text)} 字符')
