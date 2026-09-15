# -*- coding: utf-8 -*-
"""
医部第四批：医方集解+本草备要+小儿药证直诀 v2
"""
import urllib.request, urllib.parse, re, os, yaml

SOURCE = 'https://github.com/wenyuange/medicine'

def fetch(name):
    encoded = urllib.parse.quote(name)
    url = 'https://raw.githubusercontent.com/wenyuange/medicine/master/%s.txt' % encoded
    req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
    raw = urllib.request.urlopen(req, timeout=60).read().decode('utf-8', errors='ignore')
    lines = raw.split('\n')
    while lines and (name in lines[0] or not lines[0].strip()):
        lines.pop(0)
    return '\n'.join(lines)

def make_md(out_dir, eid, book, author, dynasty, chapter, title, body, weight=2, tags=None):
    os.makedirs(out_dir, exist_ok=True)
    fm = {
        'id': eid,
        'book': book,
        'chapter': chapter,
        'section_title': title,
        'source_version': '%s原著' % author,
        'author': author,
        'dynasty': dynasty,
        'category': 'yi',
        'subcategory': 'jingdian',
        'type': 'original',
        'conditions': {
            'day_master': [], 'month_branch': [],
            'day_pillar': [], 'hour_pillar': [],
            'ten_god': [], 'pattern': [], 'shensha': []
        },
        'keywords': [title, book],
        'weight': weight,
        'tags': tags or ['医家经典']
    }
    fm_str = yaml.dump(fm, allow_unicode=True, default_flow_style=False, sort_keys=False)
    content = '---\n' + fm_str + '---\n\n'
    content += '### %s\n\n' % title
    content += '**【原文】**\n\n%s\n\n' % body
    content += '**【白话提要】**\n\n'
    content += '本段为《%s》"%s"部分。\n' % (book, title)
    with open(os.path.join(out_dir, '%s.md' % eid), 'w', encoding='utf-8') as f:
        f.write(content)

# ========== 1. 医方集解 ==========
print('=== 医方集解 ===')
t = fetch('医方集解')
# 找"XX之剂第X"标记
ji_pat = re.compile(r'\n　　([^\n]{2,8}之剂第[一二三四五六七八九十]+)')
jm = list(ji_pat.finditer(t))
# 去重
dedup = []
seen = set()
for m in jm:
    n = m.group(1).strip()
    if n not in seen:
        dedup.append((m.start(), n))
        seen.add(n)
print('剂类:', [n for _, n in dedup])

out1 = 'library/yi/fangshu/yifangjijie'
cnt1 = 0
for i, (pos, name) in enumerate(dedup):
    end = dedup[i+1][0] if i+1 < len(dedup) else len(t)
    body = t[pos:end].strip()
    if len(body) > 500:
        cnt1 += 1
        make_md(out1, 'yfjj_%02d' % cnt1, '医方集解', '汪昂', '清', name, name, body,
                tags=['方书', '方剂学'])

# 序（第一个剂类之前）
if dedup:
    pre = t[:dedup[0][0]].strip()
    if len(pre) > 500:
        cnt1 += 1
        make_md(out1, 'yfjj_%02d' % cnt1, '医方集解', '汪昂', '清', '自序·凡例', '自序·凡例', pre,
                tags=['方书', '方剂学'])

print('医方集解: %d条' % cnt1)

# INDEX
index1 = ['# 医方集解', '', '**朝代**：清  ', '**作者**：汪昂  ', '**来源**：%s  ' % SOURCE,
          '', '## 简介', '', '《医方集解》为清代汪昂所著，按方剂治法分类（补养、发表、涌吐、攻里等），'
          '收载正方三百余首，是清代以来流传最广的方剂学入门书。', '', '## 目录', '']
for i in range(1, cnt1+1):
    eid = 'yfjj_%02d' % i
    index1.append('- [%s](./%s.md)' % (eid, eid))
with open(os.path.join(out1, 'INDEX.md'), 'w', encoding='utf-8') as f:
    f.write('\n'.join(index1))

# ========== 2. 本草备要 ==========
print('\n=== 本草备要 ===')
t2 = fetch('本草备要')
# 找部类标记
bu_pat = re.compile(r'\n　　([^\n　]{2,6}部)')
bm = list(bu_pat.finditer(t2))
dedup2 = []
seen2 = set()
for m in bm:
    n = m.group(1).strip()
    if n not in seen2 and len(n) <= 6:
        dedup2.append((m.start(), n))
        seen2.add(n)
print('部类:', [n for _, n in dedup2[:15]])

out2 = 'library/yi/jingdian/bencaobeiyao'
cnt2 = 0
for i, (pos, name) in enumerate(dedup2):
    end = dedup2[i+1][0] if i+1 < len(dedup2) else len(t2)
    body = t2[pos:end].strip()
    if len(body) > 500:
        cnt2 += 1
        make_md(out2, 'bcby_%02d' % cnt2, '本草备要', '汪昂', '清', name, name, body,
                tags=['本草', '药物学'])

if dedup2:
    pre = t2[:dedup2[0][0]].strip()
    if len(pre) > 500:
        cnt2 += 1
        make_md(out2, 'bcby_%02d' % cnt2, '本草备要', '汪昂', '清', '诸家序', '诸家序', pre,
                tags=['本草', '药物学'])

print('本草备要: %d条' % cnt2)

index2 = ['# 本草备要', '', '**朝代**：清  ', '**作者**：汪昂  ', '**来源**：%s  ' % SOURCE,
          '', '## 简介', '', '《本草备要》为清代汪昂所著，择要辑录四百余味常用中药的性味、主治、禁忌，简明扼要。',
          '', '## 目录', '']
for i in range(1, cnt2+1):
    eid = 'bcby_%02d' % i
    index2.append('- [%s](./%s.md)' % (eid, eid))
with open(os.path.join(out2, 'INDEX.md'), 'w', encoding='utf-8') as f:
    f.write('\n'.join(index2))

# ========== 3. 小儿药证直诀 ==========
print('\n=== 小儿药证直诀 ===')
t3 = fetch('小儿药证直诀')
# 找上中下卷
vol_pat = re.compile(r'\n　　(上卷|中卷|下卷|卷上|卷中|卷下)')
vm = list(vol_pat.finditer(t3))
dedup3 = []
seen3 = set()
for m in vm:
    n = m.group(1)
    if n not in seen3:
        dedup3.append((m.start(), n))
        seen3.add(n)
print('卷标记:', [n for _, n in dedup3])

out3 = 'library/yi/jingdian/xiaoeryaozheng'
cnt3 = 0
for i, (pos, name) in enumerate(dedup3):
    end = dedup3[i+1][0] if i+1 < len(dedup3) else len(t3)
    body = t3[pos:end].strip()
    if len(body) > 500:
        cnt3 += 1
        make_md(out3, 'eyzz_%02d' % cnt3, '小儿药证直诀', '钱乙', '宋', name, name, body,
                tags=['儿科', '钱乙'])

if dedup3:
    pre = t3[:dedup3[0][0]].strip()
    if len(pre) > 500:
        cnt3 += 1
        make_md(out3, 'eyzz_%02d' % cnt3, '小儿药证直诀', '钱乙', '宋', '原序', '原序', pre,
                tags=['儿科', '钱乙'])

print('小儿药证直诀: %d条' % cnt3)

index3 = ['# 小儿药证直诀', '', '**朝代**：宋  ', '**作者**：钱乙  ', '**来源**：%s  ' % SOURCE,
          '', '## 简介', '', '《小儿药证直诀》为宋代钱乙所著，是中国现存最早的儿科专著。'
          '钱乙被尊为"儿科之圣"，创立儿科五脏辨证体系，创制六味地黄丸等名方。',
          '', '## 目录', '']
for i in range(1, cnt3+1):
    eid = 'eyzz_%02d' % i
    index3.append('- [%s](./%s.md)' % (eid, eid))
with open(os.path.join(out3, 'INDEX.md'), 'w', encoding='utf-8') as f:
    f.write('\n'.join(index3))

print('\n合计: %d + %d + %d = %d条' % (cnt1, cnt2, cnt3, cnt1+cnt2+cnt3))
