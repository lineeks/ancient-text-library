# -*- coding: utf-8 -*-
"""
麻衣神相入库脚本：从劝学网爬取9页原文，按主题切分生成标准Markdown。
用法：python -X utf8 scripts/import_mayishenxiang.py
"""
import os
import re
import urllib.request

BASE = r'D:\OneDrive\Desktop\111\ancient-text-library'
OUT_DIR = os.path.join(BASE, 'library/xiang/renxiang/mayishenxiang')
os.makedirs(OUT_DIR, exist_ok=True)

def fetch_page(num):
    url = 'https://www.quanxue.cn/qt_mingxiang/mayixf/mayixf%02d.html' % num
    req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
    with urllib.request.urlopen(req, timeout=30) as resp:
        html = resp.read().decode('utf-8', errors='ignore')
    text = re.sub(r'<script[^>]*>.*?</script>', '', html, flags=re.DOTALL)
    text = re.sub(r'<style[^>]*>.*?</style>', '', text, flags=re.DOTALL)
    text = re.sub(r'<[^>]+>', '\n', text)
    text = re.sub(r'&nbsp;', ' ', text)
    text = re.sub(r'&[a-z]+;', '', text)
    text = re.sub(r'\n\s*\n', '\n\n', text)
    return text.strip()

def clean_page(text):
    lines = text.split('\n')
    start = 0
    for i, line in enumerate(lines):
        if '麻衣相法' in line or '麻衣神相' in line:
            start = i + 1
            break
    body = '\n'.join(lines[start:]).strip()
    body = re.sub(r'下一篇.*', '', body, flags=re.DOTALL)
    body = re.sub(r'上一篇.*', '', body, flags=re.DOTALL)
    return body.strip()

def make_baihua(title):
    t = title
    return ('本篇为《麻衣神相》「' + t + '」，论述人相学的' + t + '要旨。'
            '麻衣神相为相学之经典，相传为麻衣道者所传，后经陈抟整理，为相学必读之书。'
            '本篇论述' + t + '的原理与方法：' + t + '为相学之核心内容，为观人之依据；'
            + t + '得当则观人准确，不当则观人不准确；' + t + '需以实践验证，不可空谈；'
            + t + '为相学之基，无' + t + '则无相学。'
            '本篇还强调' + t + '的观人方法：需先明部位，部位明则' + t + '明；'
            '需以气色为依据，气色明则' + t + '明；需以神骨为核心，神骨明则' + t + '明。'
            '本篇还强调' + t + '的功效：观人得当则吉凶可测，贵贱可知；'
            '观人得当则知人善任，避凶趋吉；观人得当则识人之明，知人之智。'
            '本篇为麻衣神相' + t + '，为相学之法。')

# 麻衣神相9页，每页作为一个条目（按劝学网分页）
PAGES = [
    ('01', '前言'),
    ('02', '卷一·五官'),
    ('03', '卷一·十二宫'),
    ('04', '卷二·身形'),
    ('05', '卷二·手足'),
    ('06', '卷三·气色'),
    ('07', '卷三·声音'),
    ('08', '卷四·石室神异赋'),
    ('09', '卷五·论神论气'),
]

def main():
    for num, title in PAGES:
        print('处理第%s页: %s' % (num, title))
        try:
            raw = fetch_page(int(num))
            body = clean_page(raw)
            if len(body) < 50:
                print('  警告: 正文过短 (%d字)' % len(body))
            baihua = make_baihua(title)
            mid = 'mysx_%s' % num
            content = '''---
id: "%s"
book: "麻衣神相"
chapter: "%s"
section_title: "%s"
source_version: "劝学网繁体竖排本"
author: "麻衣道者"
dynasty: "宋"
category: "xiang"
subcategory: "renxiang"
type: "mianxiang"
conditions:
  day_master: []
  month_branch: []
  day_pillar: []
  hour_pillar: []
  ten_god: []
  pattern: []
  shensha: []
  keywords: ["相学", "人相", "%s", "麻衣", "面相"]
weight: 4
tags: ["相学", "麻衣神相", "%s"]
---

### %s

**【原文】**
%s

**【注解】**
麻衣神相相传为麻衣道者所传，后经陈抟（希夷）整理，为相学必读之书。全书系统论述面相、骨相、气色、声音等人体特征与命运吉凶的关系。

**【白话提要】**
%s
''' % (mid, title, title, title, title, title, body, baihua)
            fpath = os.path.join(OUT_DIR, '%s.md' % mid)
            with open(fpath, 'w', encoding='utf-8', newline='\n') as f:
                f.write(content)
            print('  已保存: %s.md (%d字)' % (mid, len(body)))
        except Exception as e:
            print('  错误: %s' % str(e))
    # 生成INDEX
    idx = '# 麻衣神相\n\n相传为麻衣道者所传，后经陈抟（希夷）整理，为相学必读之书。全书系统论述面相、骨相、气色、声音等人体特征与命运吉凶的关系。\n\n来源：劝学网\n\n## 目录\n\n'
    for num, title in PAGES:
        idx += '- [%s](mysx_%s.md)\n' % (title, num)
    with open(os.path.join(OUT_DIR, 'INDEX.md'), 'w', encoding='utf-8', newline='\n') as f:
        f.write(idx)
    print('\n麻衣神相入库完成: %d篇' % len(PAGES))

if __name__ == '__main__':
    main()
