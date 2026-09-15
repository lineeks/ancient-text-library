# -*- coding: utf-8 -*-
"""
外台秘要精选入库脚本
取前3万字（序+正文开头），按序和卷切分
"""
import urllib.request, urllib.parse, re, os, yaml

BOOK = '外台秘要'
AUTHOR = '王焘'
DYNASTY = '唐'
SOURCE = 'https://github.com/wenyuange/medicine'
OUT_DIR = 'library/yi/fangshu/waitaimiyao'
ID_PREFIX = 'wtmy'

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

# 1. 序（第一个卷之前）
if dedup:
    pre = text[:dedup[0][0]].strip()
    if len(pre) > 500:
        entries.append({
            'title': '诸家序',
            'body': pre,
            'section': '序跋'
        })
else:
    # 没有卷标记，整个前3万字作为一条
    entries.append({
        'title': '序跋·正文辑要',
        'body': text.strip(),
        'section': '精选'
    })

# 2. 各卷
for i, (pos, name) in enumerate(dedup):
    end = dedup[i+1][0] if i+1 < len(dedup) else len(text)
    body = text[pos:end].strip()
    if len(body) > 500:
        entries.append({
            'title': name,
            'body': body,
            'section': '正文'
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
        'source_version': '王焘原著',
        'author': AUTHOR,
        'dynasty': DYNASTY,
        'category': 'yi',
        'subcategory': 'fangshu',
        'type': 'original',
        'conditions': {
            'day_master': [], 'month_branch': [],
            'day_pillar': [], 'hour_pillar': [],
            'ten_god': [], 'pattern': [], 'shensha': []
        },
        'keywords': [title, '外台秘要'],
        'weight': 2,
        'tags': ['方书', '唐代', '精选']
    }
    
    fm_str = yaml.dump(fm, allow_unicode=True, default_flow_style=False, sort_keys=False)
    
    content = '---\n' + fm_str + '---\n\n'
    content += '### %s\n\n' % title
    content += '**【原文】**\n\n%s\n\n' % body
    content += '**【白话提要】**\n\n'
    content += '本段为《%s》"%s"部分。王焘辑录唐以前医方六千余首，全书40卷，是唐代方书集大成之作。本库精选前3万字序跋与正文开头。\n' % (BOOK, title)
    
    filepath = os.path.join(OUT_DIR, '%s.md' % eid)
    with open(filepath, 'w', encoding='utf-8') as f:
        f.write(content)

print('已生成 %d 个md文件' % len(entries))

# INDEX.md
index_lines = [
    '# 外台秘要（精选）',
    '',
    '**朝代**：唐  ',
    '**作者**：%s  ' % AUTHOR,
    '**来源**：%s  ' % SOURCE,
    '',
    '## 简介',
    '',
    '《外台秘要》为唐代王焘所辑，全书40卷，录唐以前医方六千余首，'
    '是唐代方书集大成之作，保存了大量已佚古书内容。本库精选前3万字序跋与正文开头，'
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
