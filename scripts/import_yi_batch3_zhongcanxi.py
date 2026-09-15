# -*- coding: utf-8 -*-
"""
医学衷中参西录入库脚本 v2
直接按"大类标题行"切分：　　一、医方　（一）治阴虚劳热方
"""
import urllib.request, urllib.parse, re, os, yaml

BOOK = '医学衷中参西录'
AUTHOR = '张锡纯'
DYNASTY = '清'
SOURCE = 'https://github.com/wenyuange/medicine'
OUT_DIR = 'library/yi/jingdian/yixuezhongcanxilu'
ID_PREFIX = 'yzcxl'

# 下载原文
encoded = urllib.parse.quote(BOOK)
url = 'https://raw.githubusercontent.com/wenyuange/medicine/master/%s.txt' % encoded
req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
raw = urllib.request.urlopen(req, timeout=60).read().decode('utf-8', errors='ignore')

# 清理首尾
lines = raw.split('\n')
while lines and (BOOK in lines[0] or not lines[0].strip()):
    lines.pop(0)
text = '\n'.join(lines)

# 找所有切点：　　X、Y　（Z）...
# 行首两个全角空格 + 中文数字、分类名 + 全角空格 + （编号）名称
marker_pattern = re.compile(r'\n　　([一二三四五六七八九十]+、[^\n　]+　（[一二三四五六七八九十]+）[^）\n]+)')
markers = list(marker_pattern.finditer(text))

# 也找没有子类的顶级分类：　　二、药物（单独一行，后面没有（）
top_only_pattern = re.compile(r'\n　　([一二三四五六七八九十]+、(?:药物|医论|医话))\n')
top_only = list(top_only_pattern.finditer(text))

# 合并所有切点，按位置排序
all_markers = []
for m in markers:
    all_markers.append((m.start(), m.group(1).strip()))
for m in top_only:
    all_markers.append((m.start(), m.group(1).strip()))
all_markers.sort()

# 去重：同一标题只保留第一次出现的位置
deduped = []
seen_titles = set()
for pos, title in all_markers:
    if title not in seen_titles:
        deduped.append((pos, title))
        seen_titles.add(title)

print('切分点数量:', len(deduped))
for pos, title in deduped[:10]:
    print(' ', title)
print('  ...')
for pos, title in deduped[-5:]:
    print(' ', title)

# 按切点切分
entries = []
for i, (pos, title) in enumerate(deduped):
    end = deduped[i+1][0] if i+1 < len(deduped) else len(text)
    body = text[pos:end].strip()
    if len(body) > 300:
        # 确定所属大类
        if '医方' in title:
            cat = '医方'
        elif '医案' in title:
            cat = '医案'
        elif '药物' in title:
            cat = '药物'
        elif '医论' in title:
            cat = '医论'
        elif '医话' in title:
            cat = '医话'
        else:
            cat = '其他'
        entries.append({
            'title': title,
            'body': body,
            'category': cat
        })

print('\n有效条目数:', len(entries))

# 生成md文件
os.makedirs(OUT_DIR, exist_ok=True)

for idx, entry in enumerate(entries, 1):
    eid = '%s_%02d' % (ID_PREFIX, idx)
    title = entry['title']
    body = entry['body']
    category = entry['category']
    
    fm = {
        'id': eid,
        'book': BOOK,
        'chapter': category,
        'section_title': title,
        'source_version': '张锡纯原著',
        'author': AUTHOR,
        'dynasty': DYNASTY,
        'category': 'yi',
        'subcategory': 'jingdian',
        'type': 'original',
        'conditions': {
            'day_master': [],
            'month_branch': [],
            'day_pillar': [],
            'hour_pillar': [],
            'ten_god': [],
            'pattern': [],
            'shensha': []
        },
        'keywords': [category, title],
        'weight': 2,
        'tags': ['医家医案', '临床方论']
    }
    
    fm_str = yaml.dump(fm, allow_unicode=True, default_flow_style=False, sort_keys=False)
    
    content = '---\n' + fm_str + '---\n\n'
    content += '### %s\n\n' % title
    content += '**【原文】**\n\n%s\n\n' % body
    content += '**【白话提要】**\n\n'
    content += '本段为《%s》"%s"部分，张锡纯结合中西医学理论，论述相关病证的辨治与方药。\n' % (BOOK, category)
    
    filepath = os.path.join(OUT_DIR, '%s.md' % eid)
    with open(filepath, 'w', encoding='utf-8') as f:
        f.write(content)

print('已生成 %d 个md文件到 %s' % (len(entries), OUT_DIR))

# INDEX.md
index_lines = [
    '# 医学衷中参西录',
    '',
    '**朝代**：清  ',
    '**作者**：%s  ' % AUTHOR,
    '**来源**：%s  ' % SOURCE,
    '',
    '## 简介',
    '',
    '《医学衷中参西录》为近代中西医汇通学派代表人物张锡纯所著。全书分医方、药物、医论、医话、医案五部分，'
    '结合中西医学理论，记载大量自创方剂与临床验案。',
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
