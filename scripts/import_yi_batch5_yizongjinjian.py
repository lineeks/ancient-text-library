# -*- coding: utf-8 -*-
"""
医宗金鉴精选入库脚本
取前5万字（凡例+原序+伤寒论注开头），按卷切分
"""
import urllib.request, urllib.parse, re, os, yaml

BOOK = '医宗金鉴'
AUTHOR = '吴谦'
DYNASTY = '清'
SOURCE = 'https://github.com/wenyuange/medicine'
OUT_DIR = 'library/yi/jingdian/yizongjinjian'
ID_PREFIX = 'yzjj'

encoded = urllib.parse.quote(BOOK)
url = 'https://raw.githubusercontent.com/wenyuange/medicine/master/%s.txt' % encoded
req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
raw = urllib.request.urlopen(req, timeout=60).read().decode('utf-8', errors='ignore')

# 清理首尾
lines = raw.split('\n')
while lines and (BOOK in lines[0] or not lines[0].strip()):
    lines.pop(0)
text = '\n'.join(lines)

# 取前5万字
text = text[:50000]

# 找卷标记
juan_pat = re.compile(r'\n　　(卷[一二三四五六七八九十]+)')
jm = list(juan_pat.finditer(text))
dedup = []
seen = set()
for m in jm:
    n = m.group(1)
    if n not in seen:
        dedup.append((m.start(), n))
        seen.add(n)
print('卷标记:', [n for _, n in dedup])

# 切分
entries = []

# 1. 凡例+原序（第一个卷之前）
if dedup:
    pre = text[:dedup[0][0]].strip()
    if len(pre) > 500:
        entries.append({
            'title': '凡例·原序',
            'body': pre,
            'section': '序跋'
        })

# 2. 各卷
for i, (pos, name) in enumerate(dedup):
    end = dedup[i+1][0] if i+1 < len(dedup) else len(text)
    body = text[pos:end].strip()
    if len(body) > 500:
        entries.append({
            'title': name,
            'body': body,
            'section': '伤寒论注'
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
        'source_version': '吴谦等编',
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
        'keywords': [title, '医宗金鉴'],
        'weight': 2,
        'tags': ['官修医书', '伤寒论注', '精选']
    }
    
    fm_str = yaml.dump(fm, allow_unicode=True, default_flow_style=False, sort_keys=False)
    
    content = '---\n' + fm_str + '---\n\n'
    content += '### %s\n\n' % title
    content += '**【原文】**\n\n%s\n\n' % body
    content += '**【白话提要】**\n\n'
    content += '本段为《%s》"%s"部分。吴谦等奉敕编撰，全书90卷，为清代官修医学教科书，本库精选前5万字凡例与伤寒论注开头。\n' % (BOOK, title)
    
    filepath = os.path.join(OUT_DIR, '%s.md' % eid)
    with open(filepath, 'w', encoding='utf-8') as f:
        f.write(content)

print('已生成 %d 个md文件' % len(entries))

# INDEX.md
index_lines = [
    '# 医宗金鉴（精选）',
    '',
    '**朝代**：清  ',
    '**作者**：%s等  ' % AUTHOR,
    '**来源**：%s  ' % SOURCE,
    '',
    '## 简介',
    '',
    '《医宗金鉴》为清代吴谦等奉敕编撰，全书90卷，是清代官修医学教科书，'
    '也是《四库全书》收录的唯一医书。本库精选前5万字凡例与伤寒论注开头，'
    '具体各科心法要诀因全书本身体量过大暂不收录。',
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
