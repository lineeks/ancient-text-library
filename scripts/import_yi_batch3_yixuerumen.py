# -*- coding: utf-8 -*-
"""
医学入门入库脚本
按卷切分：卷首+卷一~卷七+卷二三
"""
import urllib.request, urllib.parse, re, os, yaml

BOOK = '医学入门'
AUTHOR = '李梴'
DYNASTY = '明'
SOURCE = 'https://github.com/wenyuange/medicine'
OUT_DIR = 'library/yi/jingdian/yixuerumen'
ID_PREFIX = 'yxrm'

encoded = urllib.parse.quote(BOOK)
url = 'https://raw.githubusercontent.com/wenyuange/medicine/master/%s.txt' % encoded
req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
raw = urllib.request.urlopen(req, timeout=60).read().decode('utf-8', errors='ignore')

# 清理首尾
lines = raw.split('\n')
while lines and (BOOK in lines[0] or not lines[0].strip()):
    lines.pop(0)
text = '\n'.join(lines)

# 找卷标记：内集·卷一　经络 或 卷首
# 模式：全角空格 + [内外]集·卷X　名称
juan_pattern = re.compile(r'\n　　([内外]集·卷[一二三四五六七八九十]+　[^\n]+)')
juan_matches = list(juan_pattern.finditer(text))

# 也找卷首
juan_shou = re.search(r'\n　　(卷首[^\n]*)', text)
if juan_shou:
    juan_matches.insert(0, juan_shou)

# 去重：同一卷名只保留第一次
deduped = []
seen = set()
for m in juan_matches:
    name = m.group(1)
    if name not in seen:
        deduped.append((m.start(), name))
        seen.add(name)

print('卷标记:', [name for _, name in deduped])

# 切分
entries = []
for i, (pos, name) in enumerate(deduped):
    end = deduped[i+1][0] if i+1 < len(deduped) else len(text)
    body = text[pos:end].strip()
    if len(body) > 500:
        entries.append({
            'title': name,
            'body': body,
            'juan': name
        })

print('有效卷数:', len(entries))
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
        'chapter': title,
        'section_title': title,
        'source_version': '李梴原著',
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
        'keywords': [title, '医学入门'],
        'weight': 2,
        'tags': ['医学入门', '综合教材']
    }
    
    fm_str = yaml.dump(fm, allow_unicode=True, default_flow_style=False, sort_keys=False)
    
    content = '---\n' + fm_str + '---\n\n'
    content += '### %s\n\n' % title
    content += '**【原文】**\n\n%s\n\n' % body
    content += '**【白话提要】**\n\n'
    content += '本段为《%s》"%s"部分，李梴汇编历代医论、脉法、方药，为明代医学入门综合教材。\n' % (BOOK, title)
    
    filepath = os.path.join(OUT_DIR, '%s.md' % eid)
    with open(filepath, 'w', encoding='utf-8') as f:
        f.write(content)

print('已生成 %d 个md文件' % len(entries))

# INDEX.md
index_lines = [
    '# 医学入门',
    '',
    '**朝代**：明  ',
    '**作者**：%s  ' % AUTHOR,
    '**来源**：%s  ' % SOURCE,
    '',
    '## 简介',
    '',
    '《医学入门》为明代李梴所著，是一部综合性医学入门教材。'
    '全书分内外集，自谓"医能知此入门，医道可毕"，内容涵盖医学源流、经络脏腑、诊法方药等。',
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
