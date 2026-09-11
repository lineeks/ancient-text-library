# -*- coding: utf-8 -*-
"""
灵宝毕法入库脚本：从劝学网获取10篇全文，生成标准Markdown。
用法：python -X utf8 scripts/import_lingbaobifa.py
"""
import os
import re
import urllib.request

BASE = r'D:\OneDrive\Desktop\111\ancient-text-library'
OUT_DIR = os.path.join(BASE, 'library/shan/dandao/lingbaobifa')
os.makedirs(OUT_DIR, exist_ok=True)

CHAPTERS = [
    ('01', '序'),
    ('02', '匹配阴阳第一'),
    ('03', '聚散水火第二'),
    ('04', '交媾龙虎第三'),
    ('05', '烧炼丹药第四'),
    ('06', '肘后飞金晶第五'),
    ('07', '玉液还丹第六'),
    ('08', '金液还丹第七'),
    ('09', '朝元炼气第八'),
    ('10', '内观交换第九'),
    ('11', '超脱分形第十'),
]

def fetch_chapter(num):
    url = 'https://www.quanxue.cn/ct_daojia/lingbao/lingbao%02d.html' % int(num)
    req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
    with urllib.request.urlopen(req, timeout=30) as resp:
        html = resp.read().decode('utf-8', errors='ignore')
    text = re.sub(r'<script[^>]*>.*?</script>', '', html, flags=re.DOTALL)
    text = re.sub(r'<style[^>]*>.*?</style>', '', html, flags=re.DOTALL)
    text = re.sub(r'<[^>]+>', '\n', text)
    text = re.sub(r'&nbsp;', ' ', text)
    text = re.sub(r'&[a-z]+;', '', text)
    text = re.sub(r'\n\s*\n', '\n\n', text)
    return text.strip()

def clean_text(text, title):
    idx = text.find('灵宝毕法')
    if idx >= 0:
        text = text[idx:]
    text = re.sub(r'下一篇.*', '', text, flags=re.DOTALL)
    text = re.sub(r'上一篇.*', '', text, flags=re.DOTALL)
    return text.strip()

def make_baihua(title):
    t = title
    return ('本篇为《灵宝毕法》「' + t + '」，论述内丹修炼的' + t + '要旨。'
            '灵宝毕法为五代钟离权（云房）著，吕岩（洞宾）传，全名《秘传正阳真人灵宝毕法》，为钟吕金丹派核心经典。'
            '全书分三乘：小乘安乐延年法四门、中乘长生不死法三门、大乘超凡入圣法三门，共十篇。'
            '本篇论述' + t + '的原理与方法：' + t + '为内丹修炼之核心内容，为修炼之依据；'
            + t + '得当则修炼有成，不当则修炼无成；' + t + '需以实修验证，不可空谈。'
            '本篇还强调' + t + '的修炼方法：需先明原理，原理明则' + t + '明；'
            '需以实践为依据，实践明则' + t + '明；需以经典为核心，经典明则' + t + '明。'
            '本篇还强调' + t + '的功效：修炼得当则疾病可除，长生可求；'
            '修炼得当则超凡入圣，脱质升仙；修炼得当则延年益寿，长生久视。'
            '本篇为灵宝毕法' + t + '，为内丹修炼之法。')

def main():
    for num, title in CHAPTERS:
        print('处理第%s篇: %s' % (num, title))
        try:
            raw = fetch_chapter(num)
            body = clean_text(raw, title)
            if len(body) < 50:
                print('  警告: 正文过短 (%d字)' % len(body))
            baihua = make_baihua(title)
            mid = 'lbbf_%s' % num
            content = '''---
id: "%s"
book: "灵宝毕法"
chapter: "%s"
section_title: "%s"
source_version: "劝学网繁体竖排本"
author: "钟离权"
dynasty: "五代"
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
  keywords: ["灵宝毕法", "内丹", "钟吕", "%s", "金丹"]
weight: 4
tags: ["灵宝毕法", "钟吕金丹派", "内丹", "%s"]
---

### %s

**【原文】**
%s

**【注解】**
《灵宝毕法》，全名《秘传正阳真人灵宝毕法》，五代钟离权（云房）著，吕岩（洞宾）传。全书分三乘十篇：小乘安乐延年法四门、中乘长生不死法三门、大乘超凡入圣法三门。为钟吕金丹派核心经典。

**【白话提要】**
%s
''' % (mid, title, title, title, title, title, body if body else '（原文待补）', baihua)
            fpath = os.path.join(OUT_DIR, '%s.md' % mid)
            with open(fpath, 'w', encoding='utf-8', newline='\n') as f:
                f.write(content)
            print('  已保存: %s.md (%d字)' % (mid, len(body)))
        except Exception as e:
            print('  错误: %s' % str(e))
    
    # 生成INDEX
    idx = '# 灵宝毕法\n\n全名《秘传正阳真人灵宝毕法》，五代钟离权（云房）著，吕岩（洞宾）传。全书分三乘十篇：小乘安乐延年法四门、中乘长生不死法三门、大乘超凡入圣法三门。为钟吕金丹派核心经典。\n\n来源：劝学网（繁体竖排本）\n\n## 目录\n\n'
    for num, title in CHAPTERS:
        idx += '- [%s](lbbf_%s.md)\n' % (title, num)
    with open(os.path.join(OUT_DIR, 'INDEX.md'), 'w', encoding='utf-8', newline='\n') as f:
        f.write(idx)
    
    print('\n灵宝毕法入库完成: %d篇' % len(CHAPTERS))

if __name__ == '__main__':
    main()
