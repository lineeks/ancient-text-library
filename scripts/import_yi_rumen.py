# -*- coding: utf-8 -*-
"""
医部入门四典批量入库：汤头歌诀、药性赋、医学三字经、濒湖脉学
来源：GitHub wenyuange/medicine 纯文本
用法：python -X utf8 scripts/import_yi_rumen.py
"""
import os, re, urllib.request, urllib.parse

BASE = r'D:\OneDrive\Desktop\111\ancient-text-library'

BOOKS = [
    {
        'name': '汤头歌诀',
        'dir': 'library/yi/fangshu/tangtougejue',
        'prefix': 'ttgj',
        'author': '汪昂',
        'dynasty': '清',
        'subcategory': 'fangshu',
        'type': 'gejue',
        'keywords': '汤头歌诀,方剂,歌诀,入门',
    },
    {
        'name': '药性赋',
        'dir': 'library/yi/jingdian/yaoxingfu',
        'prefix': 'yxf',
        'author': '佚名',
        'dynasty': '宋',
        'subcategory': 'jingdian',
        'type': 'gejue',
        'keywords': '药性赋,药性,歌诀,入门',
    },
    {
        'name': '医学三字经',
        'dir': 'library/yi/jingdian/yixuesanzijing',
        'prefix': 'yxszj',
        'author': '陈修园',
        'dynasty': '清',
        'subcategory': 'jingdian',
        'type': 'rumen',
        'keywords': '医学三字经,入门,歌诀,陈修园',
    },
    {
        'name': '濒湖脉学',
        'dir': 'library/yi/zhenfa/binhuimaixue',
        'prefix': 'bhmmx',
        'author': '李时珍',
        'dynasty': '明',
        'subcategory': 'zhenfa',
        'type': 'maixue',
        'keywords': '濒湖脉学,脉学,李时珍,二十七脉',
    },
]

def download_txt(name):
    encoded = urllib.parse.quote(name)
    url = 'https://raw.githubusercontent.com/wenyuange/medicine/master/%s.txt' % encoded
    req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
    text = urllib.request.urlopen(req, timeout=30).read().decode('utf-8', errors='ignore')
    return text.strip()

def split_sections(text, book_name):
    """按自然段落或章节标记切分。如果没有明确章节标记，按段落切分。"""
    # 尝试找常见章节标记
    sections = []
    
    # 汤头歌诀：按"一、二、三..."或方剂名切分
    # 药性赋：按"寒性、热性、温性、平性"切分
    # 医学三字经：按"一、二、三..."或"卷一、卷二"切分
    # 濒湖脉学：按"浮脉、沉脉..."等脉象切分
    
    lines = [l.strip() for l in text.split('\n') if l.strip()]
    if len(lines) < 5:
        return [(book_name, text)]
    
    # 如果行数少，作为单篇
    if len(lines) < 30:
        return [(book_name, text)]
    
    # 按行切分，每行作为一个section（歌诀类书籍通常每行一歌）
    # 但太长的行合并
    current = ''
    count = 0
    for line in lines:
        if len(current) > 0 and (len(current) + len(line) > 500 or count >= 10):
            sections.append(('第%d篇' % (len(sections)+1), current))
            current = line
            count = 0
        else:
            current = current + '\n' + line if current else line
            count += 1
    if current:
        sections.append(('第%d篇' % (len(sections)+1), current))
    
    return sections

def make_baihua(book, section_name, body_len):
    return ('本篇为《%s》「%s」。%s%s撰，为中医入门经典。'
            '本篇论述%s的核心内容，以歌赋形式便于记诵。'
            '传统上为中医学子入门必读，文辞浅显，韵律铿锵。'
            '本篇约%d字，为%s的重要组成部分。'
            '传统释读强调：入门须先明药性、汤头、脉理，'
            '三者既明，方可言辨证论治。'
            '本篇为中医入门参考书籍，仅作文献研究与传统文化参考。'
            % (book, section_name, book, '', book, body_len, book))

def import_book(book_info):
    name = book_info['name']
    out_dir = os.path.join(BASE, book_info['dir'])
    os.makedirs(out_dir, exist_ok=True)
    
    print('下载%s...' % name)
    try:
        full = download_txt(name)
    except Exception as e:
        print('  下载失败: %s' % str(e)[:80])
        return 0
    print('  全文长度: %d字' % len(full))
    
    sections = split_sections(full, name)
    print('  切分为%d篇' % len(sections))
    
    success = 0
    for i, (sname, sbody) in enumerate(sections):
        if len(sbody) < 50:
            continue
        baihua = make_baihua(name, sname, len(sbody))
        mid = '%s_%02d' % (book_info['prefix'], i+1)
        
        content = '''---
id: "%s"
book: "%s"
chapter: "%s"
section_title: "%s"
source_version: "GitHub wenyuange/medicine 纯文本"
author: "%s"
dynasty: "%s"
category: "yi"
subcategory: "%s"
type: "%s"
conditions:
  day_master: []
  month_branch: []
  day_pillar: []
  hour_pillar: []
  ten_god: []
  pattern: []
  shensha: []
  keywords: ["%s", "%s"]
weight: 3
tags: ["%s", "入门", "中医"]
---

### %s

**【原文】**
%s

**【注解】**
《%s》，%s%s撰。中医入门经典，以歌赋形式便于记诵。

**【白话提要】**
%s
''' % (mid, name, sname, sname,
       book_info['author'], book_info['dynasty'],
       book_info['subcategory'], book_info['type'],
       book_info['keywords'], sname,
       name,
       sname, sbody,
       name, book_info['dynasty'], book_info['author'],
       baihua)
        
        fpath = os.path.join(out_dir, '%s.md' % mid)
        with open(fpath, 'w', encoding='utf-8', newline='\n') as f:
            f.write(content)
        success += 1
    
    # INDEX
    idx = '# %s\n\n%s%s撰。来源：GitHub wenyuange/medicine 纯文本\n\n## 目录\n\n' % (name, book_info['dynasty'], book_info['author'])
    for i in range(success):
        idx += '- [第%d篇](%s_%02d.md)\n' % (i+1, book_info['prefix'], i+1)
    with open(os.path.join(out_dir, 'INDEX.md'), 'w', encoding='utf-8', newline='\n') as f:
        f.write(idx)
    
    print('  %s入库完成: %d篇' % (name, success))
    return success

def main():
    total = 0
    for book in BOOKS:
        total += import_book(book)
    print('\n医部入门四典入库完成: 共%d篇' % total)

if __name__ == '__main__':
    main()
