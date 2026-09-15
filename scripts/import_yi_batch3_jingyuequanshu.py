# -*- coding: utf-8 -*-
"""
景岳全书精选入库脚本
取前3万字序+传忠录理论部分
"""
import urllib.request, urllib.parse, re, os, yaml

BOOK = '景岳全书'
AUTHOR = '张介宾'
DYNASTY = '明'
SOURCE = 'https://github.com/wenyuange/medicine'
OUT_DIR = 'library/yi/jingdian/jingyuequanshu'
ID_PREFIX = 'jyqs'

encoded = urllib.parse.quote(BOOK)
url = 'https://raw.githubusercontent.com/wenyuange/medicine/master/%s.txt' % encoded
req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
raw = urllib.request.urlopen(req, timeout=60).read().decode('utf-8', errors='ignore')

# 清理首尾
lines = raw.split('\n')
while lines and (BOOK in lines[0] or not lines[0].strip()):
    lines.pop(0)
text = '\n'.join(lines)

# 取前3万字
text = text[:30000]

# 按序和理论篇章切分
# 找序的结尾和传忠录的开始
# 模式：贾序、范序、查序... 然后是正文

# 找"传忠录"位置
chuanzhong = text.find('传忠录')
print('传忠录位置:', chuanzhong)

# 切分
entries = []

# 1. 序（所有序）
if chuanzhong > 0:
    preface = text[:chuanzhong].strip()
    if len(preface) > 500:
        entries.append({
            'title': '诸家序',
            'body': preface,
            'section': '序跋'
        })

# 2. 传忠录（理论部分）
if chuanzhong > 0:
    theory = text[chuanzhong:].strip()
    if len(theory) > 500:
        entries.append({
            'title': '传忠录（理论辑要）',
            'body': theory,
            'section': '理论'
        })

print('有效条目数:', len(entries))
for e in entries:
    print(' ', e['title'], '%d字' % len(e['body']))

# 生成md
os.makedirs(OUT_DIR, exist_ok=True)

for idx, entry in enumerate(entries, 1):
    eid = '%s_%02d' % (ID_PREFIX, idx)
    title = entry['title']
    body = entry['body']
    
    fm = {
        'id': eid,
        'book': BOOK,
        'chapter': entry['section'],
        'section_title': title,
        'source_version': '张介宾原著',
        'author': AUTHOR,
        'dynasty': DYNASTY,
        'category': 'yi',
        'subcategory': 'jingdian',
        'type': 'original',
        'conditions': {
            'day_master': [], 'month_branch': [],
            'day_pillar': [], 'hour_pillar': [],
            'ten_god': [], 'pattern': [], 'shensha': []
        },
        'keywords': [title, '景岳全书'],
        'weight': 2,
        'tags': ['温补派', '医论', '精选']
    }
    
    fm_str = yaml.dump(fm, allow_unicode=True, default_flow_style=False, sort_keys=False)
    
    content = '---\n' + fm_str + '---\n\n'
    content += '### %s\n\n' % title
    content += '**【原文】**\n\n%s\n\n' % body
    content += '**【白话提要】**\n\n'
    content += '本段为《%s》"%s"部分。张介宾（景岳）为明代温补派代表，主张阳非有余、真阴不足，全书64卷，本库精选序跋与传忠录理论部分。\n' % (BOOK, title)
    
    filepath = os.path.join(OUT_DIR, '%s.md' % eid)
    with open(filepath, 'w', encoding='utf-8') as f:
        f.write(content)

print('已生成 %d 个md文件' % len(entries))

# INDEX.md
index_lines = [
    '# 景岳全书（精选）',
    '',
    '**朝代**：明  ',
    '**作者**：%s  ' % AUTHOR,
    '**来源**：%s  ' % SOURCE,
    '',
    '## 简介',
    '',
    '《景岳全书》为明代张介宾（景岳）所著，全书64卷，为温补派代表作。'
    '张氏主张"阳非有余、真阴不足"，创左右归丸等名方。本库精选序跋与传忠录理论部分，'
    '具体方论因全书本身体量过大暂不收录。',
    '',
    '## 目录',
    ''
]
for idx, entry in enumerate(entries, 1):
    eid = '%s_%02d' % (ID_PREFIX, idx)
    index_lines.append('- [%s](./%s.md) %s（%d字）' % (eid, eid, entry['title'], len(entry['body'])))

with open(os.path.join(OUT_DIR, 'INDEX.md'), 'w', encoding='utf-8') as f:
    f.write('\n'.join(index_lines))

print('INDEX.md已生成')
