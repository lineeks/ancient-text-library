# -*- coding: utf-8 -*-
"""
本草纲目精选入库脚本
只取前5万字序例部分（原序+凡例+百病主治药+序例），按主题切分
"""
import urllib.request, urllib.parse, re, os, yaml

BOOK = '本草纲目'
AUTHOR = '李时珍'
DYNASTY = '明'
SOURCE = 'https://github.com/wenyuange/medicine'
OUT_DIR = 'library/yi/jingdian/bencaogangmu'
ID_PREFIX = 'bcgm'

encoded = urllib.parse.quote(BOOK)
url = 'https://raw.githubusercontent.com/wenyuange/medicine/master/%s.txt' % encoded
req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
raw = urllib.request.urlopen(req, timeout=60).read().decode('utf-8', errors='ignore')

# 清理首尾
lines = raw.split('\n')
while lines and (BOOK in lines[0] or not lines[0].strip()):
    lines.pop(0)
text = '\n'.join(lines)

# 只取前5万字（序例部分）
text = text[:50000]

# 按主题切分：
# 1. 原序+进书疏（到"凡例"之前）
# 2. 凡例
# 3. 百病主治药（从"百病主治药"到"序例上"）
# 4. 序例（从"序例上"到结尾）

# 找切点
fanli_pos = text.find('《本草纲目》凡例')
bai_pos = text.find('百病主治药')
xuli_pos = text.find('序例上')

print('凡例位置:', fanli_pos)
print('百病主治药位置:', bai_pos)
print('序例上位置:', xuli_pos)

# 切分
entries = []

# 1. 原序+进书疏
if fanli_pos > 0:
    pre = text[:fanli_pos].strip()
    if len(pre) > 500:
        entries.append({
            'title': '原序·进书疏',
            'body': pre,
            'section': '序跋'
        })

# 2. 凡例
if fanli_pos > 0 and bai_pos > 0:
    fanli = text[fanli_pos:bai_pos].strip()
    if len(fanli) > 500:
        entries.append({
            'title': '凡例',
            'body': fanli,
            'section': '凡例'
        })

# 3. 百病主治药
if bai_pos > 0 and xuli_pos > 0:
    bai = text[bai_pos:xuli_pos].strip()
    if len(bai) > 500:
        entries.append({
            'title': '百病主治药',
            'body': bai,
            'section': '序例'
        })

# 4. 序例上
if xuli_pos > 0:
    xuli = text[xuli_pos:].strip()
    if len(xuli) > 500:
        entries.append({
            'title': '序例上（引经报使·药名同异）',
            'body': xuli,
            'section': '序例'
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
        'source_version': '李时珍原著',
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
        'keywords': [title, '本草纲目'],
        'weight': 2,
        'tags': ['本草', '药物学', '精选']
    }
    
    fm_str = yaml.dump(fm, allow_unicode=True, default_flow_style=False, sort_keys=False)
    
    content = '---\n' + fm_str + '---\n\n'
    content += '### %s\n\n' % title
    content += '**【原文】**\n\n%s\n\n' % body
    content += '**【白话提要】**\n\n'
    content += '本段为《%s》"%s"部分。李时珍历时三十年编成，载药1892种，是中国古代药物学集大成之作。本库精选序例部分，具体药物条目因体量过大暂不收录。\n' % (BOOK, title)
    
    filepath = os.path.join(OUT_DIR, '%s.md' % eid)
    with open(filepath, 'w', encoding='utf-8') as f:
        f.write(content)

print('已生成 %d 个md文件' % len(entries))

# INDEX.md
index_lines = [
    '# 本草纲目（精选）',
    '',
    '**朝代**：明  ',
    '**作者**：%s  ' % AUTHOR,
    '**来源**：%s  ' % SOURCE,
    '',
    '## 简介',
    '',
    '《本草纲目》为明代李时珍历时三十年编成，载药1892种，附方11096首，'
    '分16部60类，是中国古代药物学集大成之作。本库精选序例部分（原序、凡例、'
    '百病主治药、引经报使等），具体药物条目因全书190万字体量过大暂不收录。',
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
