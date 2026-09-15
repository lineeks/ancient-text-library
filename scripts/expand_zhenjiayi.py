# -*- coding: utf-8 -*-
"""
针灸甲乙经扩展入库脚本
按"第X篇"切分，每篇一条
"""
import urllib.request, urllib.parse, re, os, yaml, shutil

BOOK = '针灸甲乙经'
AUTHOR = '皇甫谧'
DYNASTY = '晋'
SOURCE = 'https://github.com/wenyuange/medicine'
OUT_DIR = 'library/yi/zhenji/zhenjiujiayi'
ID_PREFIX = 'zjjy'

# 下载全文
encoded = urllib.parse.quote(BOOK)
url = 'https://raw.githubusercontent.com/wenyuange/medicine/master/%s.txt' % encoded
req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
raw = urllib.request.urlopen(req, timeout=60).read().decode('utf-8', errors='ignore')

# 清理首尾
lines = raw.split('\n')
while lines and (BOOK in lines[0] or not lines[0].strip()):
    lines.pop(0)
text = '\n'.join(lines)

# 旧文件由git删除，这里只生成新文件
os.makedirs(OUT_DIR, exist_ok=True)

# 找篇目标记：行首全角空格 + 篇名 + 第X
# 模式：　　精神五脏论第一
pian_pat = re.compile(r'\n　　([^\n]{2,15}第[一二三四五六七八九十]+)')
matches = list(pian_pat.finditer(text))

# 去重
dedup = []
seen = set()
for m in matches:
    n = m.group(1).strip()
    if n not in seen:
        dedup.append((m.start(), n))
        seen.add(n)

print('篇目数量:', len(dedup))
for pos, name in dedup[:10]:
    print(' ', name)
print('  ...')
for pos, name in dedup[-5:]:
    print(' ', name)

# 切分
entries = []

# 序（第一个篇目之前）
if dedup:
    pre = text[:dedup[0][0]].strip()
    if len(pre) > 500:
        entries.append({
            'title': '序',
            'body': pre,
            'juan': '序'
        })

# 每篇
for i, (pos, name) in enumerate(dedup):
    end = dedup[i+1][0] if i+1 < len(dedup) else len(text)
    body = text[pos:end].strip()
    if len(body) > 200:
        # 确定所属卷（在body中找"卷X"标记）
        jm = re.search(r'卷([一二三四五六七八九十]+)', body)
        juan = '卷%s' % jm.group(1) if jm else '未分卷'
        entries.append({
            'title': name,
            'body': body,
            'juan': juan
        })

print('有效条目数:', len(entries))

# 生成md
for idx, entry in enumerate(entries, 1):
    eid = '%s_%03d' % (ID_PREFIX, idx)
    title = entry['title']
    body = entry['body']
    juan = entry['juan']
    
    fm = {
        'id': eid,
        'book': BOOK,
        'chapter': juan,
        'section_title': title,
        'source_version': '皇甫谧原著',
        'author': AUTHOR,
        'dynasty': DYNASTY,
        'category': 'yi',
        'subcategory': 'zhenji',
        'type': 'original',
        'conditions': {
            'day_master': [], 'month_branch': [],
            'day_pillar': [], 'hour_pillar': [],
            'ten_god': [], 'pattern': [], 'shensha': []
        },
        'keywords': [title, juan, '针灸'],
        'weight': 2,
        'tags': ['针灸', '腧穴', '皇甫谧']
    }
    
    fm_str = yaml.dump(fm, allow_unicode=True, default_flow_style=False, sort_keys=False)
    
    content = '---\n' + fm_str + '---\n\n'
    content += '### %s\n\n' % title
    content += '**【原文】**\n\n%s\n\n' % body
    content += '**【白话提要】**\n\n'
    content += '本段为《%s》"%s"，皇甫谧辑录《素问》《针经》《明堂》三部，为针灸学经典。\n' % (BOOK, title)
    
    filepath = os.path.join(OUT_DIR, '%s.md' % eid)
    with open(filepath, 'w', encoding='utf-8') as f:
        f.write(content)

print('已生成 %d 个md文件' % len(entries))

# INDEX.md
index_lines = [
    '# 针灸甲乙经',
    '',
    '**朝代**：晋  ',
    '**作者**：%s  ' % AUTHOR,
    '**来源**：%s  ' % SOURCE,
    '',
    '## 简介',
    '',
    '《针灸甲乙经》为晋代皇甫谧所撰，辑录《素问》《针经》《明堂》三部，'
    '全书12卷，是中国现存最早的针灸学专著，系统整理了腧穴定位、刺灸法和临床治疗。',
    '',
    '## 目录',
    ''
]
for idx, entry in enumerate(entries, 1):
    eid = '%s_%03d' % (ID_PREFIX, idx)
    index_lines.append('- [%s](./%s.md) %s · %s（%d字）' % (eid, eid, entry['juan'], entry['title'], len(entry['body'])))

with open(os.path.join(OUT_DIR, 'INDEX.md'), 'w', encoding='utf-8') as f:
    f.write('\n'.join(index_lines))

print('INDEX.md已生成')
