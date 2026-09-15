# -*- coding: utf-8 -*-
"""
焦氏易林精选64卦主卦入库：从国学大师多页扫描提取。
"""
import os, re, time, urllib.request, json

BASE = r'D:\OneDrive\Desktop\111\ancient-text-library'
OUT_DIR = os.path.join(BASE, 'library/bu/yijing/jiaoshiyilin')

GUA64_SIMP = [
    '乾', '坤', '屯', '蒙', '需', '讼', '师', '比',
    '小畜', '履', '泰', '否', '同人', '大有', '谦', '豫',
    '随', '蛊', '临', '观', '噬嗑', '贲', '剥', '复',
    '无妄', '大畜', '颐', '大过', '坎', '离', '咸', '恒',
    '遯', '大壮', '晋', '明夷', '家人', '睽', '蹇', '解',
    '损', '益', '夬', '姤', '萃', '升', '困', '井',
    '革', '鼎', '震', '艮', '渐', '归妹', '丰', '旅',
    '巽', '兑', '涣', '节', '中孚', '小过', '既济', '未济'
]

GUA64_TRAD = [
    '乾', '坤', '屯', '蒙', '需', '訟', '師', '比',
    '小畜', '履', '泰', '否', '同人', '大有', '謙', '豫',
    '隨', '蠱', '臨', '觀', '噬嗑', '賁', '剝', '復',
    '无妄', '大畜', '頤', '大過', '坎', '離', '咸', '恒',
    '遯', '大壯', '晉', '明夷', '家人', '睽', '蹇', '解',
    '損', '益', '夬', '姤', '萃', '升', '困', '井',
    '革', '鼎', '震', '艮', '漸', '歸妹', '豐', '旅',
    '巽', '兑', '渙', '節', '中孚', '小過', '既濟', '未濟'
]

def fetch_page(page_id, retries=3):
    url = 'https://www.guoxuedashi.com/sikuquanshu/fanti/721r/%d.html' % page_id
    for attempt in range(retries):
        try:
            req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
            html = urllib.request.urlopen(req, timeout=20).read().decode('utf-8', errors='ignore')
            text = re.sub(r'<script[^>]*>.*?</script>', '', html, flags=re.DOTALL)
            text = re.sub(r'<style[^>]*>.*?</style>', '', text, flags=re.DOTALL)
            text = re.sub(r'<[^>]+>', '\n', text)
            text = re.sub(r'&nbsp;', ' ', text)
            text = re.sub(r'&#x[0-9A-Fa-f]+;', '', text)
            text = re.sub(r'\n\s*\n', '\n', text)
            return text
        except Exception as e:
            print('    重试 %d: %s' % (attempt+1, str(e)[:60]))
            time.sleep(3)
    return ''

def extract_from_text(text):
    """从文本中提取所有X之第N及其主卦断辞。"""
    results = {}
    # 找所有"X之第N"标记
    marks = list(re.finditer(r'([^\s\n　]{1,3})之第([一二三四五六七八九十]+)', text))
    for i, m in enumerate(marks):
        gua = m.group(1)
        # 去掉前面的"撰"等字符
        if gua not in GUA64_TRAD:
            # 取最后一个字符
            gua = gua[-1]
            if gua not in GUA64_TRAD:
                continue
        start = m.end()
        end = marks[i+1].start() if i+1 < len(marks) else len(text)
        section = text[start:end]
        
        # 主卦断辞：第一个全角空格+卦名
        first = re.search(r'[\u3000\s]+' + re.escape(gua) + r'[\u3000\s]*([^\n]+)', section)
        if first:
            duanci = first.group(1).strip()
            duanci = re.sub(r'【[^】]*】', '', duanci).strip()
            # 去掉后面的卦名
            for g in GUA64_TRAD:
                if g != gua and g in duanci:
                    duanci = duanci[:duanci.index(g)].strip()
            if duanci:
                results[gua] = duanci
    return results

def main():
    os.makedirs(OUT_DIR, exist_ok=True)
    
    all_duanci = {}
    for page_id in range(7155, 7172):
        print('扫描 page=%d...' % page_id)
        text = fetch_page(page_id)
        if not text or len(text) < 1000:
            print('  跳过(空或太短)')
            continue
        results = extract_from_text(text)
        for gua, duanci in results.items():
            if gua not in all_duanci:
                all_duanci[gua] = duanci
                print('  +%s: %s' % (gua, duanci[:25]))
        time.sleep(1.5)
    
    print('\n共提取%d卦' % len(all_duanci))
    
    # 保存
    with open(os.path.join(BASE, 'scripts', '_yilin_all.json'), 'w', encoding='utf-8') as f:
        json.dump(all_duanci, f, ensure_ascii=False, indent=2)
    
    # 生成Markdown
    success = 0
    for i, (gua_simp, gua_trad) in enumerate(zip(GUA64_SIMP, GUA64_TRAD)):
        duanci = all_duanci.get(gua_trad, '')
        if not duanci:
            continue
        
        baihua = ('本卦为《焦氏易林》「%s之%s」主卦断辞。焦氏易林为西汉焦赣（延寿）所撰，'
                  '以64卦各变64卦，共4096则四言韵语，为古代占筮参考。'
                  '本则为%s卦之%s卦（主卦不变）的占辞："%s"。'
                  '此断辞以四言韵语形式描述占筮所得之吉凶意象，'
                  '传统上用于占问某事时参考其象义。'
                  '传统释读强调：占筮得此卦时，宜结合所占之事具体参详，'
                  '不可执一辞而断万事。焦氏易林为古代占筮参考书籍，'
                  '其断辞仅作文献研究与传统文化参考。'
                  % (gua_simp, gua_simp, gua_simp, gua_simp, duanci[:30]))
        
        mid = 'jsyl_%02d' % (i+1)
        content = '''---
id: "%s"
book: "焦氏易林"
chapter: "%s之%s"
section_title: "%s之%s"
source_version: "国学大师·四库全书本"
author: "焦赣"
dynasty: "西汉"
category: "bu"
subcategory: "yijing"
type: "zhanji"
conditions:
  day_master: []
  month_branch: []
  day_pillar: []
  hour_pillar: []
  ten_god: []
  pattern: []
  shensha: []
  keywords: ["焦氏易林", "%s", "%s之%s", "占筮", "主卦"]
weight: 3
tags: ["焦氏易林", "%s", "占筮", "主卦"]
---

### %s之%s

**【原文】**
%s

**【注解】**
《焦氏易林》，西汉焦赣（字延寿）撰。以64卦各变64卦，共4096则四言韵语，为古代占筮参考。本则为%s卦之%s卦（主卦不变）断辞。

**【白话提要】**
%s
''' % (mid, gua_simp, gua_simp, gua_simp, gua_simp,
       gua_simp, gua_simp, gua_simp, gua_simp,
       gua_simp, gua_simp, duanci,
       gua_simp, gua_simp, baihua)
        
        fpath = os.path.join(OUT_DIR, '%s.md' % mid)
        with open(fpath, 'w', encoding='utf-8', newline='\n') as f:
            f.write(content)
        success += 1
    
    # INDEX
    idx = '# 焦氏易林（精选64卦主卦）\n\n西汉·焦赣撰。四库全书本。精选64卦主卦断辞。\n\n## 目录\n\n'
    for i, gua in enumerate(GUA64_SIMP):
        idx += '- [%s之%s](jsyl_%02d.md)\n' % (gua, gua, i+1)
    with open(os.path.join(OUT_DIR, 'INDEX.md'), 'w', encoding='utf-8', newline='\n') as f:
        f.write(idx)
    
    print('焦氏易林精选入库: %d/64卦' % success)

if __name__ == '__main__':
    main()
