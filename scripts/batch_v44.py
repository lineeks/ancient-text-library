# -*- coding: utf-8 -*-
"""
道法会元卷三十七至卷四十六 + 其他道经扩充
"""
import os, yaml, urllib.request, urllib.parse, re

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

# 1. 道法会元卷三十七至卷四十六
print('=== 道法会元卷三十七至卷四十六 ===')
all_text = ''
for i in range(37, 47):
    p = '道法会元_page%d.html' % i
    try:
        t = fetch_text(p)
        print('  %s: %d字' % (p, len(t)))
        all_text += t + '\n\n'
    except Exception as e:
        print('  %s: 失败 %s' % (p, e))

print('  总计: %d字' % len(all_text))

if all_text:
    OUT_DIR = 'library/shan/fuzhou/daohuihuiyuan'
    os.makedirs(OUT_DIR, exist_ok=True)
    fm = {
        'id': 'dwhy_06',
        'book': '道法会元',
        'chapter': '卷三十七至卷四十六',
        'section_title': '道法会元精选（卷三十七至卷四十六）',
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
    content += '### 道法会元精选（卷三十七至卷四十六）\n\n'
    content += '**【原文】**\n\n%s\n\n' % all_text[:15000]
    content += '**【白话提要】**\n\n'
    content += '《道法会元》卷三十七至卷四十六，续收雷法、符咒、斋醮科仪等内容。'
    with open(os.path.join(OUT_DIR, 'dwhy_06.md'), 'w', encoding='utf-8') as f:
        f.write(content)
    print('  保存: dwhy_06.md')

# 2. 其他道经：三洞道士居山修炼科 + 上清修身要事经
print('\n=== 三洞道士居山修炼科 ===')
try:
    t = fetch_text('三洞道士居山修炼科.html')
    print('  正文: %d字' % len(t))
    out_dir2 = 'library/shan/fuzhou/sandongxiudaoke'
    os.makedirs(out_dir2, exist_ok=True)
    fm2 = {
        'id': 'sdxdk_01',
        'book': '三洞道士居山修炼科',
        'chapter': '全文',
        'section_title': '三洞道士居山修炼科',
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
        'keywords': ['三洞', '修炼科', '居山'],
        'weight': 2,
        'tags': ['山部', '符咒', '修炼']
    }
    fm_str2 = yaml.dump(fm2, allow_unicode=True, default_flow_style=False, sort_keys=False)
    content2 = '---\n' + fm_str2 + '---\n\n'
    content2 += '### 三洞道士居山修炼科\n\n'
    content2 += '**【原文】**\n\n%s\n\n' % t
    content2 += '**【白话提要】**\n\n'
    content2 += '《三洞道士居山修炼科》述三洞道士居山修炼科仪，出自《正统道藏》正一部。'
    with open(os.path.join(out_dir2, 'sdxdk_01.md'), 'w', encoding='utf-8') as f:
        f.write(content2)
    print('  保存成功')
except Exception as e:
    print('  失败: %s' % e)

print('\n=== 上清修身要事经 ===')
try:
    t = fetch_text('上清修身要事经.html')
    print('  正文: %d字' % len(t))
    out_dir3 = 'library/shan/fuzhou/shangqingxiuxian'
    os.makedirs(out_dir3, exist_ok=True)
    fm3 = {
        'id': 'sqxx_01',
        'book': '上清修身要事经',
        'chapter': '全文',
        'section_title': '上清修身要事经',
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
        'keywords': ['上清', '修身', '要事经'],
        'weight': 2,
        'tags': ['山部', '符咒', '上清']
    }
    fm_str3 = yaml.dump(fm3, allow_unicode=True, default_flow_style=False, sort_keys=False)
    content3 = '---\n' + fm_str3 + '---\n\n'
    content3 += '### 上清修身要事经\n\n'
    content3 += '**【原文】**\n\n%s\n\n' % t
    content3 += '**【白话提要】**\n\n'
    content3 += '《上清修身要事经》为上清派修身经典，述修身要法，出自《正统道藏》正一部。'
    with open(os.path.join(out_dir3, 'sqxx_01.md'), 'w', encoding='utf-8') as f:
        f.write(content3)
    print('  保存成功')
except Exception as e:
    print('  失败: %s' % e)

print('\n全部完成')
