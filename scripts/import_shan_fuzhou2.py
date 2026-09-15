# -*- coding: utf-8 -*-
"""
山部符咒经典批量入库：洞渊神咒+正一法文+玄坛刊误论
"""
import urllib.request, urllib.parse, re, os, yaml

SOURCE = 'https://github.com/lhw828/GuWen'
BASE = 'https://raw.githubusercontent.com/lhw828/GuWen/master/'

BOOKS = [
    {
        'name': '太上洞神洞渊神咒治病口章',
        'path': '道藏/正统道藏正一部/太上洞神洞渊神咒治病口章.html',
        'out_dir': 'library/shan/fuzhou/dongyuanshenzhou',
        'id_prefix': 'dysz',
        'author': '撰人不详',
        'dynasty': '南北朝',
        'tags': ['符咒', '洞渊', '治病'],
        'keywords': ['神咒', '治病', '洞渊'],
        'intro': '此经述洞渊神咒治病之法，为正一道符咒治病类经典。',
    },
    {
        'name': '太上正一法文经',
        'path': '道藏/正统道藏正一部/太上正一法文经.html',
        'out_dir': 'library/shan/fuzhou/zhengyifawen',
        'id_prefix': 'zyfw',
        'author': '撰人不详',
        'dynasty': '南北朝',
        'tags': ['正一', '法文', '戒律'],
        'keywords': ['正一', '法文', '戒律'],
        'intro': '此经述正一法文科仪戒律，为正一道经典法义文献。',
    },
    {
        'name': '玄坛刊误论',
        'path': '道藏/正统道藏正一部/玄坛刊误论.html',
        'out_dir': 'library/shan/fuzhou/xuantankanwu',
        'id_prefix': 'xtkw',
        'author': '撰人不详',
        'dynasty': '宋',
        'tags': ['仪轨', '科仪', '刊误'],
        'keywords': ['玄坛', '科仪', '刊误'],
        'intro': '此书订正道教玄坛科仪之误，为道教仪轨类参考文献。',
    },
]

for book in BOOKS:
    # 获取HTML
    url = BASE + urllib.parse.quote(book['path'])
    req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
    html = urllib.request.urlopen(req, timeout=30).read().decode('utf-8', errors='ignore')
    
    # 去标签
    text = re.sub(r'<style[^>]*>.*?</style>', '', html, flags=re.DOTALL)
    text = re.sub(r'<script[^>]*>.*?</script>', '', text, flags=re.DOTALL)
    text = re.sub(r'<[^>]+>', '\n', text)
    text = re.sub(r'\n+', '\n', text)
    text = re.sub(r'[ \t]+', ' ', text)
    
    # 提取正文
    start = text.find('经名：')
    if start < 0:
        start = text.find(book['name'])
    end = text.find('🏯', start) if start > 0 else -1
    body = text[start:end].strip() if start >= 0 else text.strip()
    
    # 生成md
    os.makedirs(book['out_dir'], exist_ok=True)
    
    eid = '%s_01' % book['id_prefix']
    fm = {
        'id': eid,
        'book': book['name'],
        'chapter': '正一部',
        'section_title': book['name'],
        'source_version': '正统道藏正一部',
        'author': book['author'],
        'dynasty': book['dynasty'],
        'category': 'shan',
        'subcategory': 'fuzhou',
        'type': 'original',
        'conditions': {
            'day_master': [], 'month_branch': [],
            'day_pillar': [], 'hour_pillar': [],
            'ten_god': [], 'pattern': [], 'shensha': []
        },
        'keywords': book['keywords'],
        'weight': 2,
        'tags': book['tags']
    }
    
    fm_str = yaml.dump(fm, allow_unicode=True, default_flow_style=False, sort_keys=False)
    
    content = '---\n' + fm_str + '---\n\n'
    content += '### %s\n\n' % book['name']
    content += '**【原文】**\n\n%s\n\n' % body
    content += '**【白话提要】**\n\n'
    content += '%s此经出自《正统道藏》正一部。\n' % book['intro']
    
    filepath = os.path.join(book['out_dir'], '%s.md' % eid)
    with open(filepath, 'w', encoding='utf-8') as f:
        f.write(content)
    
    # INDEX.md
    index = [
        '# %s' % book['name'],
        '',
        '**朝代**：%s  ' % book['dynasty'],
        '**作者**：%s  ' % book['author'],
        '**来源**：%s  ' % SOURCE,
        '',
        '## 简介',
        '',
        book['intro'],
        '',
        '## 目录',
        '',
        '- [%s_01](./%s_01.md) %s' % (book['id_prefix'], book['id_prefix'], book['name']),
        ''
    ]
    with open(os.path.join(book['out_dir'], 'INDEX.md'), 'w', encoding='utf-8') as f:
        f.write('\n'.join(index))
    
    print('%s: %d字 -> %s' % (book['name'], len(body), filepath))

print('全部完成')
