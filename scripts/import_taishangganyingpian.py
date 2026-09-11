# -*- coding: utf-8 -*-
"""
太上感应篇入库脚本：从劝学网获取全文，生成标准Markdown。
用法：python -X utf8 scripts/import_taishangganyingpian.py
"""
import os
import re
import urllib.request

BASE = r'D:\OneDrive\Desktop\111\ancient-text-library'
OUT_DIR = os.path.join(BASE, 'library/shan/shanshu/taishangganyingpian')
os.makedirs(OUT_DIR, exist_ok=True)

def fetch_text():
    url = 'https://www.quanxue.cn/ct_daojia/ganying/ganying01.html'
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

def clean_text(text):
    idx = text.find('太上感应篇')
    if idx >= 0:
        text = text[idx:]
    text = re.sub(r'下一篇.*', '', text, flags=re.DOTALL)
    text = re.sub(r'上一篇.*', '', text, flags=re.DOTALL)
    return text.strip()

def main():
    print('获取太上感应篇全文...')
    raw = fetch_text()
    body = clean_text(raw)
    print('全文长度: %d字' % len(body))
    
    baihua = ('本篇为《太上感应篇》，道教善书经典，全文一篇。'
              '太上感应篇为道教劝善书，相传为太上老君所传，宋代李昌龄传，为道教善书之首。'
              '本篇论述善恶报应的原理：祸福无门，唯人自召；善恶之报，如影随形；'
              '天地有司过之神，依人所犯轻重，以夺人算；算减则贫耗，多逢忧患；算尽则死。'
              '本篇列举善行：不履邪径，不欺暗室；积德累功，慈心于物；忠孝友悌，正己化人；'
              '矜孤恤寡，敬老怀幼；昆虫草木，犹不可伤；宜悯人之凶，乐人之善；济人之急，救人之危。'
              '本篇列举恶行：虚诬诈伪，攻讦宗亲；刚强不仁，狠戾自用；是非不当，向背乖宜；'
              '虐下取功，谄上希旨；受恩不感，念怨不休；轻蔑天民，扰乱国政；赏及非义，刑及无辜。'
              '本篇强调：所谓善人，人皆敬之，天道佑之，福禄随之，众邪远之，神灵卫之；'
              '所作必成，神仙可冀。欲求天仙者，当立一千三百善；欲求地仙者，当立三百善。'
              '本篇为道教善书经典，为劝善惩恶之法。')
    
    content = '''---
id: "tsgyp_01"
book: "太上感应篇"
chapter: "全文"
section_title: "太上感应篇"
source_version: "劝学网繁体竖排本"
author: "李昌龄"
dynasty: "宋"
category: "shan"
subcategory: "shanshu"
type: "quanshan"
conditions:
  day_master: []
  month_branch: []
  day_pillar: []
  hour_pillar: []
  ten_god: []
  pattern: []
  shensha: []
  keywords: ["感应篇", "善书", "劝善", "道教", "善恶报应"]
weight: 4
tags: ["太上感应篇", "道教善书", "劝善惩恶"]
---

### 太上感应篇

**【原文】**
%s

**【注解】**
《太上感应篇》，道教善书经典，相传为太上老君所传，宋代李昌龄传。全文一卷，为道教善书之首，对后世影响深远。其说以善恶报应为主，强调"祸福无门，唯人自召；善恶之报，如影随形"。

**【白话提要】**
%s
''' % (body, baihua)
    
    fpath = os.path.join(OUT_DIR, 'tsgyp_01.md')
    with open(fpath, 'w', encoding='utf-8', newline='\n') as f:
        f.write(content)
    print('已保存: tsgyp_01.md (%d字)' % len(body))
    
    # 生成INDEX
    idx = '# 太上感应篇\n\n道教善书经典，相传为太上老君所传，宋代李昌龄传。全文一卷，为道教善书之首，强调"祸福无门，唯人自召；善恶之报，如影随形"。\n\n来源：劝学网（繁体竖排本）\n\n## 目录\n\n- [太上感应篇](tsgyp_01.md)\n'
    with open(os.path.join(OUT_DIR, 'INDEX.md'), 'w', encoding='utf-8', newline='\n') as f:
        f.write(idx)
    
    print('\n太上感应篇入库完成: 1篇')

if __name__ == '__main__':
    main()
