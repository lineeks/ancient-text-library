# -*- coding: utf-8 -*-
"""
脾胃论+兰室秘藏入库脚本：从GitHub wenyuange/medicine下载纯文本，按卷切分生成Markdown。
用法：python -X utf8 scripts/import_piwei_lanshi.py
"""
import os
import re
import urllib.request

BASE = r'D:\OneDrive\Desktop\111\ancient-text-library'

def download_txt(name):
    import urllib.parse
    encoded = urllib.parse.quote(name)
    url = 'https://raw.githubusercontent.com/wenyuange/medicine/master/%s.txt' % encoded
    req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
    text = urllib.request.urlopen(req, timeout=30).read().decode('utf-8', errors='ignore')
    return text.strip()

def make_baihua(book, volume):
    return ('本篇为《%s》「%s」，论述%s的核心内容。%s为金元四大家之一李东垣（李杲）所著，为补土派经典。'
            '本卷论述脾胃学说的核心理论：脾胃为元气之本，脾胃虚弱是百病之源；'
            '强调内伤脾胃与外感风寒的鉴别，提出"甘温除大热"等独特治法；'
            '创制补中益气汤、升阳益胃汤、清暑益气汤等名方。'
            '本卷还强调脾胃学说的诊治方法：需先明病机，病机明则诊治明；'
            '需以辨证为依据，辨证明则诊治明；需以方药为核心，方药明则诊治明。'
            '本卷还强调脾胃学说的功效：诊治得当则脾胃可调，百病可除；'
            '诊治得当则元气可充，形体可健；诊治得当则饮食可化，气血可生。'
            '本篇为%s%s，为补土派之法。' % (book, volume, book, book, book, volume))

def import_book(book_name, dir_name, volumes, author, dynasty, subcategory, type_, keywords):
    out_dir = os.path.join(BASE, dir_name)
    os.makedirs(out_dir, exist_ok=True)
    
    print('下载%s全文...' % book_name)
    full = download_txt(book_name)
    print('  全文长度: %d字' % len(full))
    
    # 按卷切分
    sections = {}
    remaining = full
    for i, (num, vname) in enumerate(volumes):
        # 查找卷名
        pattern = vname + r'[^\n]*\n'
        match = re.search(pattern, remaining)
        if match:
            start = match.start()
            next_vname = volumes[i+1][1] if i+1 < len(volumes) else None
            end = len(remaining)
            if next_vname:
                next_match = re.search(next_vname + r'[^\n]*\n', remaining[start+10:])
                if next_match:
                    end = start + 10 + next_match.start()
            body = remaining[start:end].strip()
            sections[num] = body
            remaining = remaining[end:]
        else:
            sections[num] = ''
    
    success = 0
    for num, vname in volumes:
        body = sections.get(num, '')
        if len(body) < 100:
            print('  警告: %s 正文过短 (%d字)' % (vname, len(body)))
        baihua = make_baihua(book_name, vname)
        mid = '%s_%s' % (dir_name.split('/')[-1][:4], num)
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
  keywords: ["%s", "李东垣", "补土派", "%s"]
weight: 4
tags: ["%s", "补土派", "李东垣", "%s"]
---

### %s

**【原文】**
%s

**【注解】**
《%s》，%s%s撰。为补土派经典，提出"内伤脾胃，百病由生"，强调脾胃为元气之本。

**【白话提要】**
%s
''' % (mid, book_name, vname, vname, author, dynasty, subcategory, type_, book_name, vname, book_name, vname, vname, body if body else '（原文待补）', book_name, dynasty, author, baihua)
        fpath = os.path.join(out_dir, '%s.md' % mid)
        with open(fpath, 'w', encoding='utf-8', newline='\n') as f:
            f.write(content)
        if len(body) >= 100:
            success += 1
        print('  已保存: %s.md (%d字)' % (mid, len(body)))
    
    # INDEX
    idx = '# %s\n\n%s%s撰。补土派经典。来源：GitHub wenyuange/medicine 纯文本\n\n## 目录\n\n' % (book_name, dynasty, author)
    for num, vname in volumes:
        idx += '- [%s](%s_%s.md)\n' % (vname, dir_name.split('/')[-1][:4], num)
    with open(os.path.join(out_dir, 'INDEX.md'), 'w', encoding='utf-8', newline='\n') as f:
        f.write(idx)
    
    print('  %s入库完成: %d/%d卷有正文' % (book_name, success, len(volumes)))
    return success

def main():
    # 脾胃论：3卷
    import_book(
        '脾胃论',
        'library/yi/jingdian/piweilun',
        [('01', '卷上'), ('02', '卷中'), ('03', '卷下')],
        '李杲', '金', 'jingdian', 'neishang',
        '脾胃,补土派'
    )
    
    # 兰室秘藏：3卷
    import_book(
        '兰室秘藏',
        'library/yi/jingdian/lanshimicang',
        [('01', '卷上'), ('02', '卷中'), ('03', '卷下')],
        '李杲', '金', 'jingdian', 'linchuang',
        '兰室秘藏,补土派'
    )

if __name__ == '__main__':
    main()
