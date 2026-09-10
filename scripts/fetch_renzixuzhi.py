# -*- coding: utf-8 -*-
"""获取地理人子须知51篇全文（中华典藏网，ID 155901-155951）"""
import urllib.request, re, time, os

BASE = r'D:\OneDrive\Desktop\111\ancient-text-library'
OUT = os.path.join(BASE, 'raw/dili-renzi-xuzhi.txt')

def fetch(url, timeout=25):
    req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
    return urllib.request.urlopen(req, timeout=timeout).read().decode('utf-8', errors='ignore')

def clean(html):
    text = re.sub(r'<[^>]+>', '', html)
    text = re.sub(r'&nbsp;', ' ', text)
    text = re.sub(r'&[a-z]+;', '', text)
    text = re.sub(r'\s+', ' ', text)
    return text.strip()

all_text = []
for pid in range(155901, 155952):
    url = f'https://www.diancang.xyz/xuanxuewushu/renzixuzhi/{pid}.html'
    try:
        html = fetch(url)
        title_m = re.search(r'<title>(.*?)</title>', html)
        title = title_m.group(1).split('_')[0] if title_m else f'篇{pid}'
        text = clean(html)
        # 找正文开始
        starts = [text.find('徐善继'), text.find('卷一'), text.find('卷二'),
                  text.find('卷三'), text.find('卷四'), text.find('卷五'),
                  text.find('卷六'), text.find('卷七'), text.find('卷八'),
                  text.find('凡例'), text.find('序'), text.find('引用')]
        start = min([s for s in starts if s >= 0]) if any(s >= 0 for s in starts) else 0
        text = text[start:]
        end = min([x for x in [text.find('上一篇'), text.find('下一篇'), text.find('目录'),
                                text.find('原创内容')] if x > 0] + [len(text)])
        text = text[:end].strip()
        all_text.append(f'=== {title} ===\n{text}')
        print(f'  {title}: {len(text)} 字符')
        time.sleep(0.3)
    except Exception as e:
        print(f'  ID={pid}: 错误 {e}')

full = '\n\n'.join(all_text)
with open(OUT, 'w', encoding='utf-8') as f:
    f.write(full)
print(f'\n地理人子须知保存: {len(full)} 字符, {len(all_text)} 篇 → {OUT}')
