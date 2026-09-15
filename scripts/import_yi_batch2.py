# -*- coding: utf-8 -*-
"""
医部第二批五典入库：医学心悟、血证论、医林改错、温热论、湿热病篇
来源：GitHub wenyuange/medicine 纯文本
用法：python -X utf8 scripts/import_yi_batch2.py
"""
import os, re, urllib.request, urllib.parse

BASE = r'D:\OneDrive\Desktop\111\ancient-text-library'

def download_txt(name):
    encoded = urllib.parse.quote(name)
    url = 'https://raw.githubusercontent.com/wenyuange/medicine/master/%s.txt' % encoded
    req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
    return urllib.request.urlopen(req, timeout=30).read().decode('utf-8', errors='ignore').strip()

def split_by_volume(text, patterns):
    """按卷标记切分"""
    sections = []
    positions = []
    for pat in patterns:
        for m in re.finditer(pat, text):
            positions.append((m.start(), m.group()))
    positions.sort()
    
    for i, (start, name) in enumerate(positions):
        end = positions[i+1][0] if i+1 < len(positions) else len(text)
        body = text[start:end].strip()
        if len(body) > 100:
            sections.append((name, body))
    return sections

def split_by_chapter(text, pattern):
    """按章标记切分"""
    matches = list(re.finditer(pattern, text))
    sections = []
    for i, m in enumerate(matches):
        start = m.start()
        end = matches[i+1].start() if i+1 < len(matches) else len(text)
        body = text[start:end].strip()
        if len(body) > 50:
            sections.append((m.group(), body))
    return sections

def split_by_tiao(text, pattern):
    """按条标记切分"""
    matches = list(re.finditer(pattern, text))
    sections = []
    for i, m in enumerate(matches):
        start = m.start()
        end = matches[i+1].start() if i+1 < len(matches) else len(text)
        body = text[start:end].strip()
        if len(body) > 50:
            sections.append((m.group(0)[:20], body))
    return sections

def make_baihua(book, sname, body):
    return ('本篇为《%s》「%s」。本篇论述%s的核心内容。'
            '传统上为中医学子必读，文辞浅显，理法兼备。'
            '本篇约%d字，为《%s》的重要组成部分。'
            '传统释读强调：须先明辨证，次明治法，后明方药。'
            '本篇为中医临床参考书籍，仅作文献研究与传统文化参考。'
            % (book, sname, book, len(body), book))

def import_book(name, dir_path, prefix, author, dynasty, subcategory, type_, split_func, split_arg):
    out_dir = os.path.join(BASE, dir_path)
    os.makedirs(out_dir, exist_ok=True)
    
    print('下载%s...' % name)
    text = download_txt(name)
    print('  全文: %d字' % len(text))
    
    sections = split_func(text, split_arg)
    print('  切分: %d篇' % len(sections))
    
    success = 0
    for i, (sname, sbody) in enumerate(sections):
        if len(sbody) < 100:
            continue
        baihua = make_baihua(name, sname, sbody)
        mid = '%s_%02d' % (prefix, i+1)
        
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
tags: ["%s", "中医"]
---

### %s

**【原文】**
%s

**【注解】**
《%s》，%s%s撰。中医临床经典。

**【白话提要】**
%s
''' % (mid, name, sname, sname,
       author, dynasty, subcategory, type_,
       name, sname,
       name,
       sname, sbody,
       name, dynasty, author,
       baihua)
        
        fpath = os.path.join(out_dir, '%s.md' % mid)
        with open(fpath, 'w', encoding='utf-8', newline='\n') as f:
            f.write(content)
        success += 1
    
    idx = '# %s\n\n%s%s撰。来源：GitHub wenyuange/medicine 纯文本\n\n## 目录\n\n' % (name, dynasty, author)
    for i in range(success):
        idx += '- [第%d篇](%s_%02d.md)\n' % (i+1, prefix, i+1)
    with open(os.path.join(out_dir, 'INDEX.md'), 'w', encoding='utf-8', newline='\n') as f:
        f.write(idx)
    
    print('  %s入库: %d篇' % (name, success))
    return success

def main():
    total = 0
    
    # 医学心悟：按卷切分
    total += import_book(
        '医学心悟', 'library/yi/jingdian/yixuexinwu', 'yxxw',
        '程国彭', '清', 'jingdian', 'linchuang',
        split_by_volume, [r'卷[一二三四五六七八九十]+']
    )
    
    # 血证论：按卷切分
    total += import_book(
        '血证论', 'library/yi/jingdian/xuezhenglun', 'xzll',
        '唐宗海', '清', 'jingdian', 'linchuang',
        split_by_volume, [r'◎\s*卷[一二三四五六七八九十]+']
    )
    
    # 医林改错：按卷切分
    total += import_book(
        '医林改错', 'library/yi/jingdian/yilingaigcuo', 'ylgc',
        '王清任', '清', 'jingdian', 'jiepou',
        split_by_volume, [r'卷[上中下]']
    )
    
    # 温热论：按章切分
    total += import_book(
        '温热论', 'library/yi/wenbing/wenrelun', 'wrl',
        '叶桂', '清', 'wenbing', 'wenbing',
        split_by_chapter, r'第[一二三四五六七八九十]+章'
    )
    
    # 湿热病篇：按条切分
    total += import_book(
        '湿热病篇', 'library/yi/wenbing/shirebingpian', 'srbp',
        '薛雪', '清', 'wenbing', 'wenbing',
        split_by_tiao, r'（[一二三四五六七八九十百]+）'
    )
    
    print('\n医部第二批五典入库完成: 共%d篇' % total)

if __name__ == '__main__':
    main()
