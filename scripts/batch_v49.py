# -*- coding: utf-8 -*-
"""
三项并行：道经扩充 + 太乙 + 丹道
"""
import os, yaml, urllib.request, urllib.parse, re

# 道经URL
DAOJING_BASE = 'https://raw.githubusercontent.com/lhw828/GuWen/master/%E9%81%93%E8%97%8F/%E6%AD%A3%E7%BB%9F%E9%81%93%E8%97%8F%E6%AD%A3%E4%B8%80%E9%83%A8/'

def fetch_daojing(html_name):
    url = DAOJING_BASE + urllib.parse.quote(html_name)
    req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
    with urllib.request.urlopen(req, timeout=30) as resp:
        html = resp.read().decode('utf-8', errors='replace')
    html = re.sub(r'<style[^>]*>.*?</style>', '', html, flags=re.S)
    html = re.sub(r'<script[^>]*>.*?</script>', '', html, flags=re.S)
    text = re.sub(r'<[^>]+>', '', html)
    start = text.find('经名：')
    if start < 0:
        start = text.find('太上')
    text = text[start:]
    lines = [l.strip() for l in text.split('\n') if l.strip()]
    return '\n'.join(lines)

# 1. 道经扩充
print('=== 道经扩充 ===')
daojing_books = [
    ('太上老君内观经', '太上老君内观经.html', 'laojunneiguan', '《太上老君内观经》述内观心法，出自《正统道藏》正一部。'),
    ('太上老君说了心经', '太上老君说了心经.html', 'laojunshuoxin', '《太上老君说了心经》述老君说心要法，出自《正统道藏》正一部。'),
]
for name, html_name, short, intro in daojing_books:
    try:
        t = fetch_daojing(html_name)
        print('  ✓ %s: %d字' % (name, len(t)))
        out_dir = 'library/shan/fuzhou/%s' % short
        os.makedirs(out_dir, exist_ok=True)
        fm = {
            'id': '%s_01' % short,
            'book': name, 'chapter': '全文', 'section_title': name,
            'source_version': '正统道藏正一部', 'author': '不详', 'dynasty': '唐',
            'category': 'shan', 'subcategory': 'fuzhou', 'type': 'original',
            'conditions': {'day_master': [], 'month_branch': [], 'day_pillar': [], 'hour_pillar': [], 'ten_god': [], 'pattern': [], 'shensha': []},
            'keywords': [name, '道经'], 'weight': 2, 'tags': ['山部', '符咒', '道经']
        }
        fm_str = yaml.dump(fm, allow_unicode=True, default_flow_style=False, sort_keys=False)
        content = '---\n' + fm_str + '---\n\n### %s\n\n**【原文】**\n\n%s\n\n**【白话提要】**\n\n%s' % (name, t, intro)
        with open(os.path.join(out_dir, '%s_01.md' % short), 'w', encoding='utf-8') as f:
            f.write(content)
    except Exception as e:
        print('  ✗ %s: %s' % (name, str(e)[:50]))

# 2. 太乙（从GitHub搜索太乙相关文本）
print('\n=== 太乙 ===')
try:
    # 尝试从GitHub获取太乙神数相关文本
    url = 'https://raw.githubusercontent.com/garychowcmu/daizhigev20/master/%E6%98%93%E8%97%8F/%E6%9C%AF%E6%95%B0/%E5%A4%AA%E4%B9%99%E7%A5%9E%E6%95%B0.txt'
    req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
    with urllib.request.urlopen(req, timeout=30) as resp:
        t = resp.read().decode('utf-8', errors='replace')
    print('  ✓ 太乙神数: %d字' % len(t))
    out_dir = 'library/bu/sanshi/taiyi'
    os.makedirs(out_dir, exist_ok=True)
    fm = {
        'id': 'taiyi_01',
        'book': '太乙神数', 'chapter': '全文', 'section_title': '太乙神数',
        'source_version': '古本', 'author': '不详', 'dynasty': '宋',
        'category': 'bu', 'subcategory': 'sanshi', 'type': 'original',
        'conditions': {'day_master': [], 'month_branch': [], 'day_pillar': [], 'hour_pillar': [], 'ten_god': [], 'pattern': [], 'shensha': []},
        'keywords': ['太乙', '神数', '三式'], 'weight': 6, 'tags': ['卜部', '三式', '太乙']
    }
    fm_str = yaml.dump(fm, allow_unicode=True, default_flow_style=False, sort_keys=False)
    content = '---\n' + fm_str + '---\n\n### 太乙神数\n\n**【原文】**\n\n%s\n\n**【白话提要】**\n\n《太乙神数》为三式之一，古称三式之首，以九宫数演算国运，出自古本。' % t[:15000]
    with open(os.path.join(out_dir, 'taiyi_01.md'), 'w', encoding='utf-8') as f:
        f.write(content)
    print('  保存成功')
except Exception as e:
    print('  ✗ 太乙神数: %s' % str(e)[:80])

# 3. 丹道补充
print('\n=== 丹道补充 ===')
try:
    # 尝试获取黄庭经
    url = 'https://raw.githubusercontent.com/garychowcmu/daizhigev20/master/%E6%98%93%E8%97%8F/%E6%9C%AF%E6%95%B0/%E9%BB%84%E5%BA%AD%E7%BB%8F.txt'
    req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
    with urllib.request.urlopen(req, timeout=30) as resp:
        t = resp.read().decode('utf-8', errors='replace')
    print('  ✓ 黄庭经: %d字' % len(t))
    out_dir = 'library/shan/dandao/huangtingjing'
    os.makedirs(out_dir, exist_ok=True)
    fm = {
        'id': 'htj_01',
        'book': '黄庭经', 'chapter': '全文', 'section_title': '黄庭经',
        'source_version': '古本', 'author': '魏华存', 'dynasty': '晋',
        'category': 'shan', 'subcategory': 'dandao', 'type': 'original',
        'conditions': {'day_master': [], 'month_branch': [], 'day_pillar': [], 'hour_pillar': [], 'ten_god': [], 'pattern': [], 'shensha': []},
        'keywords': ['黄庭经', '丹道', '内丹'], 'weight': 8, 'tags': ['山部', '丹道', '黄庭']
    }
    fm_str = yaml.dump(fm, allow_unicode=True, default_flow_style=False, sort_keys=False)
    content = '---\n' + fm_str + '---\n\n### 黄庭经\n\n**【原文】**\n\n%s\n\n**【白话提要】**\n\n《黄庭经》为道教内丹经典，述脏腑神真修炼，魏华存传，出自古本。' % t[:15000]
    with open(os.path.join(out_dir, 'htj_01.md'), 'w', encoding='utf-8') as f:
        f.write(content)
    print('  保存成功')
except Exception as e:
    print('  ✗ 黄庭经: %s' % str(e)[:80])

print('\n全部完成')
