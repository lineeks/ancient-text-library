# -*- coding: utf-8 -*-
"""获取伤寒论22篇全文（中华典藏网，ID 31456-31477）"""
import urllib.request, re, time, os

BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT = os.path.join(BASE, "raw/shanghan-lun.txt")

CHAPTERS = [
    (31456, "辩脉法"),
    (31457, "平脉法"),
    (31458, "伤寒例"),
    (31459, "辨痉湿暍脉证"),
    (31460, "辨太阳病脉证并治法上"),
    (31461, "辨太阳病脉证并治中"),
    (31462, "辨太阳病脉证并治下"),
    (31463, "辨阳明病脉证并治法"),
    (31464, "辨少阳病脉证并治"),
    (31465, "辨太阴病脉证并治"),
    (31466, "辨少阴病脉证并治"),
    (31467, "辨厥阴病脉证并治"),
    (31468, "辨霍乱病脉证并治"),
    (31469, "辨阴阳易差后劳复病脉证并治"),
    (31470, "辨不可发汗病脉证并治"),
    (31471, "辨可发汗脉证并治"),
    (31472, "辨发汗后病脉证并治"),
    (31473, "辨不可吐"),
    (31474, "辨可吐"),
    (31475, "辨不可下病脉证并治"),
    (31476, "辨可下病脉证并治"),
    (31477, "辨发汗吐下后脉证并治"),
]


def fetch(url, timeout=20):
    req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
    return urllib.request.urlopen(req, timeout=timeout).read().decode('utf-8', errors='ignore')


def clean(html):
    text = re.sub(r'<[^>]+>', '', html)
    text = re.sub(r'&nbsp;', ' ', text)
    text = re.sub(r'&[a-z]+;', '', text)
    text = re.sub(r'\s+', ' ', text)
    return text.strip()


all_text = []
for pid, title in CHAPTERS:
    url = f'https://www.diancang.xyz/xuanxuewushu/shanghanlun/{pid}.html'
    try:
        html = fetch(url)
        text = clean(html)
        # 找正文开始
        starts = [text.find('问曰'), text.find('师曰'), text.find('太阳'), text.find('脉'),
                  text.find('伤寒'), text.find('辨')]
        start = min([s for s in starts if s >= 0]) if any(s >= 0 for s in starts) else 0
        text = text[start:]
        end = min([x for x in [text.find('上一篇'), text.find('下一篇'), text.find('目录'),
                                text.find('原创内容')] if x > 0] + [len(text)])
        text = text[:end].strip()
        all_text.append(f'=== {title} ===\n{text}')
        print(f'  {title}: {len(text)} 字符')
        time.sleep(0.3)
    except Exception as e:
        print(f'  {title}: 错误 {e}')

full = '\n\n'.join(all_text)
with open(OUT, 'w', encoding='utf-8') as f:
    f.write(full)
print(f'\n伤寒论保存: {len(full)} 字符, {len(all_text)} 篇 → {OUT}')
