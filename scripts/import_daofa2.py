# -*- coding: utf-8 -*-
"""
批量获取：道法会元卷四至卷十 + 太上正一盟威法箓
"""
import urllib.request, urllib.parse, re, os, yaml

BASE_URL = 'https://raw.githubusercontent.com/lhw828/GuWen/master/%E9%81%93%E8%97%8F/%E6%AD%A3%E7%BB%9F%E9%81%93%E8%97%8F%E6%AD%A3%E4%B8%80%E9%83%A8/'

def fetch_text(html_name):
    url = BASE_URL + urllib.parse.quote(html_name)
    req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
    with urllib.request.urlopen(req, timeout=30) as resp:
        html = resp.read().decode('utf-8', errors='replace')
    html = re.sub(r'<style[^>]*>.*?</style>', '', html, flags=re.S)
    html = re.sub(r'<script[^>]*>.*?</script>', '', html, flags=re.S)
    text = re.sub(r'<[^>]+>', '', html)
    start = text.find('经名：')
    if start < 0:
        start = text.find('道法')
    text = text[start:]
    lines = [l.strip() for l in text.split('\n') if l.strip()]
    return '\n'.join(lines)

# 1. 道法会元 page4-page10
print('=== 道法会元卷四至卷十 ===')
all_text = ''
for i in range(4, 11):
    p = '道法会元_page%d.html' % i
    try:
        t = fetch_text(p)
        print('  %s: %d字' % (p, len(t)))
        all_text += t + '\n\n'
    except Exception as e:
        print('  %s: 失败 %s' % (p, e))

print('  总计: %d字' % len(all_text))

# 保存
OUT_DIR = 'library/shan/fuzhou/daohuihuiyuan'
os.makedirs(OUT_DIR, exist_ok=True)

fm = {
    'id': 'dwhy_02',
    'book': '道法会元',
    'chapter': '卷四至卷十',
    'section_title': '道法会元精选（卷四至卷十）',
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
content += '### 道法会元精选（卷四至卷十）\n\n'
content += '**【原文】**\n\n%s\n\n' % all_text[:15000]
content += '**【白话提要】**\n\n'
content += '《道法会元》卷四至卷十，续收雷法、符咒、斋醮科仪等内容。'
with open(os.path.join(OUT_DIR, 'dwhy_02.md'), 'w', encoding='utf-8') as f:
    f.write(content)
print('  保存: dwhy_02.md')

# 2. 太上正一盟威法箓
print('\n=== 太上正一盟威法箓 ===')
try:
    t = fetch_text('太上正一盟威法箓.html')
    print('  正文: %d字' % len(t))
    OUT_DIR2 = 'library/shan/fuzhou/mengweifalu'
    os.makedirs(OUT_DIR2, exist_ok=True)
    fm2 = {
        'id': 'mwl_01',
        'book': '太上正一盟威法箓',
        'chapter': '全文',
        'section_title': '太上正一盟威法箓',
        'source_version': '正统道藏正一部',
        'author': '不详',
        'dynasty': '南北朝',
        'category': 'shan',
        'subcategory': 'fuzhou',
        'type': 'original',
        'conditions': {
            'day_master': [], 'month_branch': [],
            'day_pillar': [], 'hour_pillar': [],
            'ten_god': [], 'pattern': [], 'shensha': []
        },
        'keywords': ['盟威法箓', '正一', '符箓'],
        'weight': 2,
        'tags': ['山部', '符咒', '法箓']
    }
    fm_str2 = yaml.dump(fm2, allow_unicode=True, default_flow_style=False, sort_keys=False)
    content2 = '---\n' + fm_str2 + '---\n\n'
    content2 += '### 太上正一盟威法箓\n\n'
    content2 += '**【原文】**\n\n%s\n\n' % t
    content2 += '**【白话提要】**\n\n'
    content2 += '《太上正一盟威法箓》为正一盟威之道符箓文献，述正一法箓授受制度，出自《正统道藏》正一部。'
    with open(os.path.join(OUT_DIR2, 'mwl_01.md'), 'w', encoding='utf-8') as f:
        f.write(content2)
    print('  保存: mwl_01.md')
except Exception as e:
    print('  失败: %s' % e)

print('\n全部完成')
