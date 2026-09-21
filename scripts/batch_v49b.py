# -*- coding: utf-8 -*-
"""
太乙金镜式经 + 道经扩充
"""
import os, yaml, urllib.request, urllib.parse, re

def fetch_text(url, encoding='utf-8'):
    req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
    with urllib.request.urlopen(req, timeout=30) as resp:
        html = resp.read().decode(encoding, errors='replace')
    return html

# 1. 太乙金镜式经（Kanripo）
print('=== 太乙金镜式经 ===')
try:
    # Kanripo是HTML页面，需要提取正文
    url = 'https://www.kanripo.org/text/KR3g0047/001'
    html = fetch_text(url)
    # 去掉HTML标签
    html = re.sub(r'<style[^>]*>.*?</style>', '', html, flags=re.S)
    html = re.sub(r'<script[^>]*>.*?</script>', '', html, flags=re.S)
    text = re.sub(r'<[^>]+>', '', html)
    lines = [l.strip() for l in text.split('\n') if l.strip() and len(l.strip()) > 5]
    text = '\n'.join(lines)
    # 找到正文起始
    start = text.find('太乙')
    if start > 0:
        text = text[start:]
    print('  正文: %d字' % len(text))
    out_dir = 'library/bu/sanshi/taiyi'
    os.makedirs(out_dir, exist_ok=True)
    fm = {
        'id': 'taiyi_jinjing_01',
        'book': '太乙金镜式经', 'chapter': '卷一', 'section_title': '太乙金镜式经（卷一）',
        'source_version': 'Kanripo古本', 'author': '王希明', 'dynasty': '唐',
        'category': 'bu', 'subcategory': 'sanshi', 'type': 'original',
        'conditions': {'day_master': [], 'month_branch': [], 'day_pillar': [], 'hour_pillar': [], 'ten_god': [], 'pattern': [], 'shensha': []},
        'keywords': ['太乙', '金镜式', '三式'], 'weight': 6, 'tags': ['卜部', '三式', '太乙']
    }
    fm_str = yaml.dump(fm, allow_unicode=True, default_flow_style=False, sort_keys=False)
    content = '---\n' + fm_str + '---\n\n### 太乙金镜式经（卷一）\n\n**【原文】**\n\n%s\n\n**【白话提要】**\n\n《太乙金镜式经》为唐代王希明撰，太乙三式经典，述太乙起例、推法、吉凶占验。' % text[:15000]
    with open(os.path.join(out_dir, 'taiyi_jinjing_01.md'), 'w', encoding='utf-8') as f:
        f.write(content)
    print('  保存成功')
except Exception as e:
    print('  失败: %s' % e)

# 2. 道经扩充：尝试从Kanripo获取
print('\n=== 道经扩充 ===')
try:
    url = 'https://raw.githubusercontent.com/lhw828/GuWen/master/%E9%81%93%E8%97%8F/%E6%AD%A3%E7%BB%9F%E9%81%93%E8%97%8F%E6%AD%A3%E4%B8%80%E9%83%A8/%E5%A4%AA%E4%B8%8A%E8%80%81%E5%90%9B%E5%85%A7%E8%A7%82%E7%BB%8F.html'
    req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
    with urllib.request.urlopen(req, timeout=30) as resp:
        html = resp.read().decode('utf-8', errors='replace')
    print('  ✓ 太上老君内观经: %d bytes' % len(html))
except Exception as e:
    print('  ✗ 太上老君内观经: %s' % str(e)[:60])

print('\n全部完成')
