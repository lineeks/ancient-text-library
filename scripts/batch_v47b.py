# -*- coding: utf-8 -*-
"""
继续扩充山部符咒类：尝试更多道经文件名
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
        start = text.find('太上')
    text = text[start:]
    lines = [l.strip() for l in text.split('\n') if l.strip()]
    return '\n'.join(lines)

# 从目录列表中看到的其他可能存在的文件名
books = [
    ('太清金液神丹经', '太清金液神丹经.html', 'jinyechendan', '《太清金液神丹经》为道教炼丹经典，出自《正统道藏》正一部。'),
    ('上清金书玉字', '上清金书玉字.html', 'jinshuyuzi', '《上清金书玉字》为上清派经典，出自《正统道藏》正一部。'),
    ('上清骨髓灵文鬼律', '上清骨髓灵文鬼律.html', 'guishengguilv', '《上清骨髓灵文鬼律》为道教鬼律经典，出自《正统道藏》正一部。'),
    ('高上神霄玉清真王紫书大法', '高上神霄玉清真王紫书大法.html', 'zishudafa', '《高上神霄玉清真王紫书大法》为神霄派雷法经典，出自《正统道藏》正一部。'),
]

for name, html_name, short, intro in books:
    print('尝试: %s' % name)
    try:
        t = fetch_text(html_name)
        print('  正文: %d字' % len(t))
        out_dir = 'library/shan/fuzhou/%s' % short
        os.makedirs(out_dir, exist_ok=True)
        fm = {
            'id': '%s_01' % short,
            'book': name,
            'chapter': '全文',
            'section_title': name,
            'source_version': '正统道藏正一部',
            'author': '不详',
            'dynasty': '宋',
            'category': 'shan',
            'subcategory': 'fuzhou',
            'type': 'original',
            'conditions': {
                'day_master': [], 'month_branch': [],
                'day_pillar': [], 'hour_pillar': [],
                'ten_god': [], 'pattern': [], 'shensha': []
            },
            'keywords': [name, '道经'],
            'weight': 2,
            'tags': ['山部', '符咒', '道经']
        }
        fm_str = yaml.dump(fm, allow_unicode=True, default_flow_style=False, sort_keys=False)
        content = '---\n' + fm_str + '---\n\n'
        content += '### %s\n\n' % name
        content += '**【原文】**\n\n%s\n\n' % t
        content += '**【白话提要】**\n\n'
        content += '%s' % intro
        with open(os.path.join(out_dir, '%s_01.md' % short), 'w', encoding='utf-8') as f:
            f.write(content)
        print('  保存成功')
    except Exception as e:
        print('  失败: %s' % e)

print('\n全部完成')
