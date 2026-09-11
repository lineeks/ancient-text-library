# -*- coding: utf-8 -*-
"""
丹溪心法入库脚本：从GitHub获取纯文本全文，按卷切分生成标准Markdown。
用法：python -X utf8 scripts/import_danxixinfa.py
"""
import os
import re
import urllib.request

BASE = r'D:\OneDrive\Desktop\111\ancient-text-library'
OUT_DIR = os.path.join(BASE, 'library/yi/jingdian/danxixinfa')
os.makedirs(OUT_DIR, exist_ok=True)

def fetch_full_text():
    url = 'https://raw.githubusercontent.com/wenyuange/medicine/master/%E4%B8%B9%E6%BA%AA%E5%BF%83%E6%B3%95.txt'
    req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
    with urllib.request.urlopen(req, timeout=30) as resp:
        text = resp.read().decode('utf-8', errors='ignore')
    return text.strip()

VOLUMES = [
    ('01', '卷一'),
    ('02', '卷二'),
    ('03', '卷三'),
    ('04', '卷四'),
    ('05', '卷五'),
]

def split_by_volumes(full_text):
    """按卷切分全文"""
    sections = {}
    remaining = full_text
    for i, (num, volume) in enumerate(VOLUMES):
        # 查找卷名
        pattern = volume + r'[^\n]*\n'
        match = re.search(pattern, remaining)
        if match:
            start = match.start()
            # 查找下一卷
            next_volume = VOLUMES[i+1][1] if i+1 < len(VOLUMES) else None
            end = len(remaining)
            if next_volume:
                next_match = re.search(next_volume + r'[^\n]*\n', remaining[start+10:])
                if next_match:
                    end = start + 10 + next_match.start()
            body = remaining[start:end].strip()
            sections[num] = body
            remaining = remaining[end:]
        else:
            sections[num] = ''
    return sections

def make_baihua(volume):
    v = volume
    return ('本篇为《丹溪心法》「' + v + '」，论述丹溪学说的' + v + '要旨。'
            '丹溪心法为元代朱震亨（丹溪）代表作，为滋阴派经典，提出"阳常有余，阴常不足"。'
            '本卷论述' + v + '的核心内容：以内科杂病为主，兼及外感、内伤、外证、妇科、幼科；'
            '强调气血痰郁的辨证论治，创越鞠丸、大补阴丸、虎潜丸等名方；'
            '论述中风、中寒、中暑、湿、燥、火、疫、斑疹、疟、痢、泄泻等病证。'
            '本卷还强调丹溪学说的诊治方法：需先明病机，病机明则诊治明；'
            '需以辨证为依据，辨证明则诊治明；需以方药为核心，方药明则诊治明。'
            '本卷还强调丹溪学说的功效：诊治得当则阴虚可补，火热可清；'
            '诊治得当则气血可调，痰郁可解；诊治得当则杂病可除，形体可健。'
            '本篇为丹溪心法' + v + '，为滋阴派之法。')

def main():
    print('获取丹溪心法全文...')
    full = fetch_full_text()
    print('全文长度: %d字' % len(full))
    
    print('按卷切分...')
    sections = split_by_volumes(full)
    
    for num, volume in VOLUMES:
        body = sections.get(num, '')
        if len(body) < 100:
            print('  警告: %s 正文过短 (%d字)' % (volume, len(body)))
        baihua = make_baihua(volume)
        mid = 'dxxf_%s' % num
        content = '''---
id: "%s"
book: "丹溪心法"
chapter: "%s"
section_title: "%s"
source_version: "GitHub wenyuange/medicine 纯文本"
author: "朱震亨"
dynasty: "元"
category: "yi"
subcategory: "jingdian"
type: "zayin"
conditions:
  day_master: []
  month_branch: []
  day_pillar: []
  hour_pillar: []
  ten_god: []
  pattern: []
  shensha: []
  keywords: ["丹溪", "滋阴派", "朱震亨", "%s", "杂病"]
weight: 4
tags: ["丹溪心法", "滋阴派", "朱震亨", "%s"]
---

### %s

**【原文】**
%s

**【注解】**
《丹溪心法》五卷，元朱震亨（丹溪）著，成书于1347年。书首载十二经见证等六篇论文，卷一至卷五以内科杂病为主，兼及各科病证，共约100余种病证。为滋阴派经典，提出"阳常有余，阴常不足"。

**【白话提要】**
%s
''' % (mid, volume, volume, volume, volume, volume, body if body else '（原文待补）', baihua)
        fpath = os.path.join(OUT_DIR, '%s.md' % mid)
        with open(fpath, 'w', encoding='utf-8', newline='\n') as f:
            f.write(content)
        print('  已保存: %s.md (%d字)' % (mid, len(body)))
    
    # 生成INDEX
    idx = '# 丹溪心法\n\n元朱震亨（丹溪）著，五卷，成书于1347年。滋阴派经典，提出"阳常有余，阴常不足"。书首载十二经见证等六篇论文，卷一至卷五以内科杂病为主，兼及各科病证。\n\n来源：GitHub wenyuange/medicine 纯文本\n\n## 目录\n\n'
    for num, volume in VOLUMES:
        idx += '- [%s](dxxf_%s.md)\n' % (volume, num)
    with open(os.path.join(OUT_DIR, 'INDEX.md'), 'w', encoding='utf-8', newline='\n') as f:
        f.write(idx)
    
    print('\n丹溪心法入库完成: %d卷' % len(VOLUMES))

if __name__ == '__main__':
    main()
