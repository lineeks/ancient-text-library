# -*- coding: utf-8 -*-
"""
山部符咒：道法会元前几卷精选
从lhw828/GuWen正一部获取
"""
import urllib.request, urllib.parse, re, os, yaml

BASE_URL = 'https://raw.githubusercontent.com/lhw828/GuWen/master/%E9%81%93%E8%97%8F/%E6%AD%A3%E7%BB%9F%E9%81%93%E8%97%8F%E6%AD%A3%E4%B8%80%E9%83%A8/'

def fetch_text(html_name):
    url = BASE_URL + urllib.parse.quote(html_name)
    req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
    with urllib.request.urlopen(req, timeout=30) as resp:
        html = resp.read().decode('utf-8', errors='replace')
    # 去style/script
    html = re.sub(r'<style[^>]*>.*?</style>', '', html, flags=re.S)
    html = re.sub(r'<script[^>]*>.*?</script>', '', html, flags=re.S)
    # 去标签
    text = re.sub(r'<[^>]+>', '', html)
    # 找正文
    start = text.find('经名：')
    if start < 0:
        start = text.find('道法')
    text = text[start:]
    lines = [l.strip() for l in text.split('\n') if l.strip()]
    return '\n'.join(lines)

# 道法会元前3页
pages = ['道法会元.html', '道法会元_page2.html', '道法会元_page3.html']
all_text = ''
for p in pages:
    try:
        t = fetch_text(p)
        print('%s: %d字' % (p, len(t)))
        all_text += t + '\n\n'
    except Exception as e:
        print('%s: 失败 %s' % (p, e))

print('总计: %d字' % len(all_text))

# 保存为一个条目
OUT_DIR = 'library/shan/fuzhou/daohuihuiyuan'
os.makedirs(OUT_DIR, exist_ok=True)

fm = {
    'id': 'dwhy_01',
    'book': '道法会元',
    'chapter': '卷一至卷三',
    'section_title': '道法会元精选',
    'source_version': '正统道藏正一部',
    'author': '清微派编集',
    'dynasty': '宋',
    'category': 'shan',
    'subcategory': 'fuzhou',
    'type': 'original',
    'conditions': {
        'day_master': [], 'month_branch': [],
        'day_pillar': [], 'hour_pillar': [],
        'ten_god': [], 'pattern': [], 'shensha': []
    },
    'keywords': ['道法会元', '雷法', '符咒', '清微派'],
    'weight': 2,
    'tags': ['山部', '符咒', '道法会元']
}

fm_str = yaml.dump(fm, allow_unicode=True, default_flow_style=False, sort_keys=False)
content = '---\n' + fm_str + '---\n\n'
content += '### 道法会元精选（卷一至卷三）\n\n'
content += '**【原文】**\n\n%s\n\n' % all_text[:8000]
content += '**【白话提要】**\n\n'
content += '《道法会元》为宋元清微派道法总集，收录雷法、符咒、斋醮科仪等，精选前3卷为道法纲领。'

filepath = os.path.join(OUT_DIR, 'dwhy_01.md')
with open(filepath, 'w', encoding='utf-8') as f:
    f.write(content)
print('保存: %s' % filepath)
