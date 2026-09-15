# -*- coding: utf-8 -*-
"""
山部符咒：北帝七元系列4部经文
从lhw828/GuWen正一部获取
"""
import urllib.request, urllib.parse, re, os, yaml

BASE_URL = 'https://raw.githubusercontent.com/lhw828/GuWen/master/%E9%81%93%E8%97%8F/%E6%AD%A3%E7%BB%9F%E9%81%93%E8%97%8F%E6%AD%A3%E4%B8%80%E9%83%A8/'

BOOKS = [
    {
        'dir': 'beidiqiyuan',
        'file': 'qiyuanzhaomofutian.html',
        'html_name': '七元召魔伏六天神咒经.html',
        'book_name': '七元召魔伏六天神咒经',
        'author': '不详',
        'dynasty': '南北朝',
        'intro': '撰人不详，似出南北朝，出自《正统道藏》正一部。述北帝七元召魔伏六天之神咒，为北帝法符咒经典。',
        'keywords': ['北帝', '七元', '召魔', '神咒'],
    },
    {
        'dir': 'beidiqiyuanxuanji',
        'file': 'qiyuanxuanjizhaomopin.html',
        'html_name': '七元璇玑召魔品经.html',
        'book_name': '七元璇玑召魔品经',
        'author': '不详',
        'dynasty': '南北朝',
        'intro': '撰人不详，出自《正统道藏》正一部。述北帝七元璇玑召魔之法，为北帝法经典。',
        'keywords': ['北帝', '七元', '璇玑', '召魔'],
    },
    {
        'dir': 'beidiqiyuanlingfu',
        'file': 'qiyuanzhenrenshuoshenzhenlingfu.html',
        'html_name': '七元真人说神真灵符经.html',
        'book_name': '七元真人说神真灵符经',
        'author': '不详',
        'dynasty': '南北朝',
        'intro': '撰人不详，出自《正统道藏》正一部。七元真人说神真灵符，为北帝法符箓经典。',
        'keywords': ['北帝', '七元', '灵符', '符箓'],
    },
    {
        'dir': 'beidiqiyuanyuyi',
        'file': 'qiyuanzhenjueyuquyimijing.html',
        'html_name': '七元真诀语驱疫秘经.html',
        'book_name': '七元真诀语驱疫秘经',
        'author': '不详',
        'dynasty': '南北朝',
        'intro': '撰人不详，出自《正统道藏》正一部。述七元真诀驱疫之法，为北帝法驱疫符咒经典。',
        'keywords': ['北帝', '七元', '驱疫', '真诀'],
    },
]

def fetch_html(html_name):
    url = BASE_URL + urllib.parse.quote(html_name)
    req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
    with urllib.request.urlopen(req, timeout=30) as resp:
        return resp.read().decode('utf-8', errors='replace')

def extract_text(html):
    # 去style/script
    html = re.sub(r'<style[^>]*>.*?</style>', '', html, flags=re.S)
    html = re.sub(r'<script[^>]*>.*?</script>', '', html, flags=re.S)
    # 去标签
    text = re.sub(r'<[^>]+>', '', html)
    # 找正文：从"经名："开始到文件末尾
    start = text.find('经名：')
    if start < 0:
        start = text.find('七元')
    text = text[start:]
    # 清理空白行和重复行
    lines = [l.strip() for l in text.split('\n') if l.strip()]
    return '\n'.join(lines)

for book in BOOKS:
    print('获取: %s' % book['book_name'])
    try:
        html = fetch_html(book['html_name'])
        text = extract_text(html)
        print('  正文: %d字' % len(text))
    except Exception as e:
        print('  失败: %s' % e)
        continue
    
    out_dir = 'library/shan/fuzhou/%s' % book['dir']
    os.makedirs(out_dir, exist_ok=True)
    
    eid = 'bdqy_01'
    fm = {
        'id': eid,
        'book': book['book_name'],
        'chapter': '全文',
        'section_title': book['book_name'],
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
        'tags': ['山部', '符咒', '北帝']
    }
    
    fm_str = yaml.dump(fm, allow_unicode=True, default_flow_style=False, sort_keys=False)
    content = '---\n' + fm_str + '---\n\n'
    content += '### %s\n\n' % book['book_name']
    content += '**【原文】**\n\n%s\n\n' % text
    content += '**【白话提要】**\n\n'
    content += '%s\n' % book['intro']
    
    filepath = os.path.join(out_dir, '%s.md' % eid)
    with open(filepath, 'w', encoding='utf-8') as f:
        f.write(content)
    print('  保存: %s' % filepath)

print('全部完成')
