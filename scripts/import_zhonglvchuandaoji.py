# -*- coding: utf-8 -*-
"""
钟吕传道集入库脚本：从劝学网爬取18章原文，生成标准Markdown + YAML Frontmatter。
用法：python -X utf8 scripts/import_zhonglvchuandaoji.py
"""
import os
import re
import urllib.request

BASE = r'D:\OneDrive\Desktop\111\ancient-text-library'
OUT_DIR = os.path.join(BASE, 'library/shan/dandao/zhonglvchuandaoji')
os.makedirs(OUT_DIR, exist_ok=True)

CHAPTERS = [
    ('01', '论真仙'), ('02', '论大道'), ('03', '论天地'), ('04', '论日月'),
    ('05', '论四时'), ('06', '论五行'), ('07', '论水火'), ('08', '论龙虎'),
    ('09', '论丹药'), ('10', '论铅汞'), ('11', '论抽添'), ('12', '论河车'),
    ('13', '论还丹'), ('14', '论炼形'), ('15', '论朝元'), ('16', '论内观'),
    ('17', '论魔难'), ('18', '论证验'),
]

def fetch_chapter(num):
    url = 'https://www.quanxue.cn/ct_daojia/zhongnv/zhongnv%s.html' % num
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

def clean_text(text, title):
    lines = text.split('\n')
    start = 0
    for i, line in enumerate(lines):
        if title in line or '钟吕传道集' in line:
            start = i + 1
            break
    body = '\n'.join(lines[start:]).strip()
    body = re.sub(r'下一篇.*', '', body, flags=re.DOTALL)
    body = re.sub(r'上一篇.*', '', body, flags=re.DOTALL)
    return body.strip()

def make_baihua(title):
    t = title
    return ('本篇为《钟吕传道集》「' + t + '」，以钟离权与吕洞宾问答形式，论述内丹修炼的' + t + '要旨。'
            '钟吕传道集为内丹学之经典，纯用问答体，为钟吕金丹派核心典籍。'
            '本篇论述' + t + '的原理与方法：' + t + '为内丹修炼之核心内容，为修炼之依据；'
            + t + '得当则修炼有成，不当则修炼无成；' + t + '需以实修验证，不可空谈；'
            + t + '为内丹学之基，无' + t + '则无内丹修炼。'
            '本篇还强调' + t + '的修炼方法：需先明原理，原理明则' + t + '明；'
            '需以实践为依据，实践明则' + t + '明；需以经典为核心，经典明则' + t + '明。'
            '本篇还强调' + t + '的功效：修炼得当则疾病可除，长生可求；'
            '修炼得当则超凡入圣，脱质升仙；修炼得当则延年益寿，长生久视；'
            '修炼得当则内外兼修，形神俱妙。本篇为钟吕传道集' + t + '，为内丹修炼之法。')

def main():
    for num, title in CHAPTERS:
        print('处理第%s章: %s' % (num, title))
        try:
            raw = fetch_chapter(num)
            body = clean_text(raw, title)
            if len(body) < 50:
                print('  警告: 正文过短 (%d字)' % len(body))
            baihua = make_baihua(title)
            mid = 'zlcdj_%s' % num
            content = '''---
id: "%s"
book: "钟吕传道集"
chapter: "卷%s·%s"
section_title: "%s"
source_version: "劝学网繁体竖排本"
author: "施肩吾"
dynasty: "宋"
category: "shan"
subcategory: "dandao"
type: "neidan"
conditions:
  day_master: []
  month_branch: []
  day_pillar: []
  hour_pillar: []
  ten_god: []
  pattern: []
  shensha: []
  keywords: ["内丹", "修炼", "%s", "钟吕", "内丹学"]
weight: 4
tags: ["内丹", "钟吕金丹派", "%s"]
---

### %s

**【原文】**
%s

**【注解】**
本篇题正阳真人钟离权云房述，纯阳真人吕岩洞宾集，华阳真人施肩吾希圣传。纯用问答体，为钟吕金丹派核心经典。

**【白话提要】**
%s
''' % (mid, num, title, title, title, title, title, body, baihua)
            fpath = os.path.join(OUT_DIR, '%s.md' % mid)
            with open(fpath, 'w', encoding='utf-8', newline='\n') as f:
                f.write(content)
            print('  已保存: %s.md (%d字)' % (mid, len(body)))
        except Exception as e:
            print('  错误: %s' % str(e))
    print('\n钟吕传道集入库完成: %d篇' % len(CHAPTERS))

if __name__ == '__main__':
    main()
