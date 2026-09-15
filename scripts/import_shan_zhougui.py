# -*- coding: utf-8 -*-
"""
山部符咒经典入库：太上正一咒鬼经
从 lhw828/GuWen GitHub仓库获取HTML，去标签后入库
"""
import urllib.request, urllib.parse, re, os, yaml

SOURCE = 'https://github.com/lhw828/GuWen'
OUT_DIR = 'library/shan/fuzhou/zhougui'
ID_PREFIX = 'zj'

# 获取HTML
path = '道藏/正统道藏正一部/太上正一咒鬼经.html'
url = 'https://raw.githubusercontent.com/lhw828/GuWen/master/' + urllib.parse.quote(path)
req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
html = urllib.request.urlopen(req, timeout=30).read().decode('utf-8', errors='ignore')

# 去HTML标签，提取正文
text = re.sub(r'<style[^>]*>.*?</style>', '', html, flags=re.DOTALL)
text = re.sub(r'<script[^>]*>.*?</script>', '', text, flags=re.DOTALL)
text = re.sub(r'<[^>]+>', '\n', text)
text = re.sub(r'\n+', '\n', text)
text = re.sub(r'[ \t]+', ' ', text)

# 找到正文起始（"经名：太上正一咒鬼经"之后）
start = text.find('经名：太上正一咒鬼经')
if start < 0:
    start = text.find('太上正一咒鬼经\n　　天师曰')
body = text[start:].strip() if start >= 0 else text.strip()

# 去掉尾部导航
end = body.find('🏯')
if end > 0:
    body = body[:end].strip()

print('正文长度:', len(body))

# 生成md
os.makedirs(OUT_DIR, exist_ok=True)

eid = '%s_01' % ID_PREFIX
fm = {
    'id': eid,
    'book': '太上正一咒鬼经',
    'chapter': '正一部',
    'section_title': '太上正一咒鬼经',
    'source_version': '正统道藏正一部',
    'author': '撰人不详',
    'dynasty': '南北朝',
    'category': 'shan',
    'subcategory': 'fuzhou',
    'type': 'original',
    'conditions': {
        'day_master': [], 'month_branch': [],
        'day_pillar': [], 'hour_pillar': [],
        'ten_god': [], 'pattern': [], 'shensha': []
    },
    'keywords': ['咒鬼', '正一', '神咒', '驱邪'],
    'weight': 2,
    'tags': ['符咒', '正一', '驱鬼']
}

fm_str = yaml.dump(fm, allow_unicode=True, default_flow_style=False, sort_keys=False)

content = '---\n' + fm_str + '---\n\n'
content += '### 太上正一咒鬼经\n\n'
content += '**【原文】**\n\n%s\n\n' % body
content += '**【白话提要】**\n\n'
content += '此经假托正一真人张陵告诸祭酒弟子，述太上正一咒鬼驱邪之法。'
content += '经中载天师神咒，以"急急如律令"为结，为正一道符咒驱邪类经典。\n'

filepath = os.path.join(OUT_DIR, '%s.md' % eid)
with open(filepath, 'w', encoding='utf-8') as f:
    f.write(content)

print('已生成:', filepath)

# INDEX.md
index = [
    '# 太上正一咒鬼经',
    '',
    '**朝代**：南北朝  ',
    '**作者**：撰人不详  ',
    '**来源**：%s  ' % SOURCE,
    '',
    '## 简介',
    '',
    '《太上正一咒鬼经》假托正一真人张陵告诸祭酒弟子，一卷，'
    '出自《正统道藏》正一部。经中载天师神咒，述正一道驱邪咒鬼之法，'
    '以"急急如律令"为结，是正一符咒类经典。',
    '',
    '## 目录',
    '',
    '- [%s_01](./%s_01.md) 太上正一咒鬼经' % (ID_PREFIX, ID_PREFIX),
    ''
]
with open(os.path.join(OUT_DIR, 'INDEX.md'), 'w', encoding='utf-8') as f:
    f.write('\n'.join(index))
print('INDEX.md已生成')
