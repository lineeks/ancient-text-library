# -*- coding: utf-8 -*-
"""
医学正传入库脚本
按"或问："问答体切分，前半部分序/凡例作为总述
"""
import urllib.request, urllib.parse, re, os, yaml

BOOK = '医学正传'
AUTHOR = '虞抟'
DYNASTY = '明'
SOURCE = 'https://github.com/wenyuange/medicine'
OUT_DIR = 'library/yi/jingdian/yixuezhengzhuan'
ID_PREFIX = 'yxzz'

encoded = urllib.parse.quote(BOOK)
url = 'https://raw.githubusercontent.com/wenyuange/medicine/master/%s.txt' % encoded
req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
raw = urllib.request.urlopen(req, timeout=60).read().decode('utf-8', errors='ignore')

# 清理首尾书名
lines = raw.split('\n')
while lines and (BOOK in lines[0] or not lines[0].strip()):
    lines.pop(0)
text = '\n'.join(lines)

# 找所有"或问："位置
qa_pattern = re.compile(r'或问：')
qa_matches = list(qa_pattern.finditer(text))

print('问答数量:', len(qa_matches))

# 切分
entries = []

# 第一个问答之前的内容（序+凡例）
if qa_matches:
    pre = text[:qa_matches[0].start()].strip()
    if len(pre) > 200:
        entries.append({
            'title': '序·凡例',
            'body': pre,
            'section': '序·凡例'
        })

# 每个问答
for i, m in enumerate(qa_matches):
    start = m.start()
    end = qa_matches[i+1].start() if i+1 < len(qa_matches) else len(text)
    body = text[start:end].strip()
    
    # 提取问题标题（前20字）
    first_line = body.split('\n')[0].replace('或问：', '').strip()
    title = '问：' + first_line[:30]
    
    if len(body) > 200:
        entries.append({
            'title': title,
            'body': body,
            'section': '问答'
        })

print('有效条目数:', len(entries))

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
        'source_version': '虞抟原著',
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
        'keywords': [entry['section'], title],
        'weight': 2,
        'tags': ['医家问答', '理论阐微']
    }
    
    fm_str = yaml.dump(fm, allow_unicode=True, default_flow_style=False, sort_keys=False)
    
    content = '---\n' + fm_str + '---\n\n'
    content += '### %s\n\n' % title
    content += '**【原文】**\n\n%s\n\n' % body
    content += '**【白话提要】**\n\n'
    content += '本段为《%s》虞抟以问答体论述医学理论与临床辨治之要。\n' % BOOK
    
    filepath = os.path.join(OUT_DIR, '%s.md' % eid)
    with open(filepath, 'w', encoding='utf-8') as f:
        f.write(content)

print('已生成 %d 个md文件' % len(entries))

# INDEX.md
index_lines = [
    '# 医学正传',
    '',
    '**朝代**：明  ',
    '**作者**：%s  ' % AUTHOR,
    '**来源**：%s  ' % SOURCE,
    '',
    '## 简介',
    '',
    '《医学正传》为明代虞抟所著，以问答体阐述医学理论、诊断辨证与临床方药，'
    '上承《内经》《难经》，下采朱丹溪等诸家学说，是明代重要医学入门书。',
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
