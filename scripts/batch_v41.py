# -*- coding: utf-8 -*-
"""
补充：易隐卷首张星元总断 + 道法会元卷十一至卷二十
"""
import os, yaml, urllib.request, urllib.parse, re

# 1. 易隐卷首补充：张星元先生总断
OUT_DIR1 = 'library/bu/liuyao/yiyin'
entries = [
    {
        'id': 'yy_008',
        'title': '张星元先生总断',
        'body': '''吉凶由八卦变通，须察吉变凶而凶变吉。飞伏在二仪交换，定然隔伏阴而阴伏阳。爻爻有伏有飞，伏无不用。卦卦有动有静，动无不之。变出他宫，但取金木水火土，还归本卦，配成兄父子财官。水化金，则坎增其势。火化土，则离减其威。亥变子日进神，水得生而火被制。戌变未云退度，金不助而水无伤。卦之墓绝非宜，还究伪真之辩。爻变生扶最利，更详喜忌之分。爻有伏吟不吉，卦有反吟最凶。归妹变随为例，小畜之姤皆同。但识六爻占克，那知二卦交冲。变能生克于动爻，动不制于变象。静受动伤，静难制动。柔遭刚克，柔岂伐刚。日月善会克爻神，爻神谁敢伤日月。日为君主，旺衰之象尽能伤。月乃提纲，动静之爻皆可克。本卦为贞为始，之卦为悔为终。亲官云出现之爻，远年可取。他卦曰伏藏之象，近日堪推。内为己，外为人，喜生喜合。应为宾，世为主，兼克兼冲。我生人而半吉，人克我以全凶。世应齐空，两下目前退悔。主宾皆动，二边日后更张。两间之爻，动则起居多阻。一身之位，空则祸福咸虚。凡欲久长，用宜安静。如求脱卸，主利交重。用木金来，从吉而不吉。用土火到，虽凶而不凶。元神却要生扶，忌客最宜伏制。用神旺相，事必亨通。主象休囚，理当愁闷。''',
        'intro': '《易隐》卷首张星元先生总断，续刘伯温总断之后，论八卦变通、飞伏交换、变爻生克、日月旺衰、世应主宾、元神忌神等，为六爻断法纲领。',
        'keywords': ['张星元', '总断', '飞伏', '世应'],
    },
]

for entry in entries:
    fm = {
        'id': entry['id'],
        'book': '易隐',
        'chapter': '卷首',
        'section_title': entry['title'],
        'source_version': '清曹九锡辑·曹璿演',
        'author': '曹九锡',
        'dynasty': '清',
        'category': 'bu',
        'subcategory': 'liuyao',
        'type': 'original',
        'conditions': {
            'day_master': [], 'month_branch': [],
            'day_pillar': [], 'hour_pillar': [],
            'ten_god': [], 'pattern': [], 'shensha': []
        },
        'keywords': entry['keywords'],
        'weight': 6,
        'tags': ['卜部', '六爻', '易隐']
    }
    fm_str = yaml.dump(fm, allow_unicode=True, default_flow_style=False, sort_keys=False)
    content = '---\n' + fm_str + '---\n\n'
    content += '### %s\n\n' % entry['title']
    content += '**【原文】**\n\n%s\n\n' % entry['body']
    content += '**【白话提要】**\n\n'
    content += '%s\n' % entry['intro']
    with open(os.path.join(OUT_DIR1, '%s.md' % entry['id']), 'w', encoding='utf-8') as f:
        f.write(content)
    print('%s: %d字' % (entry['id'], len(entry['body'])))

# 2. 道法会元卷十一至卷二十
print('\n=== 道法会元卷十一至卷二十 ===')
BASE_URL = 'https://raw.githubusercontent.com/lhw828/GuWen/master/%E9%81%93%E8%97%8F/%E6%AD%A3%E7%BB%9F%E9%81%93%E8%97%8F%E6%AD%A3%E4%B8%80%E9%83%A8/'

def fetch_text(html_name):
    url = BASE_URL + urllib.parse.quote(html_name)
    req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
    with urllib.request.urlopen(req, timeout=30) as resp:
        html = resp.read().decode('utf-8', errors='replace')
    html = re.sub(r'<style[^>]*>.*?</style>', '', html, flags=re.S)
    html = re.sub(r'<script[^>]*>.*?</script>', '', html, flags=re.S)
    text = re.sub(r'<[^>]+>', '', html)
    start = text.find('经名：')
    if start < 0:
        start = text.find('道法')
    text = text[start:]
    lines = [l.strip() for l in text.split('\n') if l.strip()]
    return '\n'.join(lines)

all_text = ''
for i in range(11, 21):
    p = '道法会元_page%d.html' % i
    try:
        t = fetch_text(p)
        print('  %s: %d字' % (p, len(t)))
        all_text += t + '\n\n'
    except Exception as e:
        print('  %s: 失败 %s' % (p, e))

print('  总计: %d字' % len(all_text))

OUT_DIR2 = 'library/shan/fuzhou/daohuihuiyuan'
fm2 = {
    'id': 'dwhy_03',
    'book': '道法会元',
    'chapter': '卷十一至卷二十',
    'section_title': '道法会元精选（卷十一至卷二十）',
    'source_version': '正统道藏正一部',
    'author': '清微派编集',
    'dynasty': '宋',
    'category': 'shan',
    'subcategory': 'fuzhou',
    'type': 'original',
    'conditions': {
        'day_master': [], 'month_branch': [],
        'day_pillar': [], 'hour_pillar': [],
        'ten_god': [], 'pattern': [], 'shensha': []
    },
    'keywords': ['道法会元', '雷法', '符咒', '清微派'],
    'weight': 2,
    'tags': ['山部', '符咒', '道法会元']
}
fm_str2 = yaml.dump(fm2, allow_unicode=True, default_flow_style=False, sort_keys=False)
content2 = '---\n' + fm_str2 + '---\n\n'
content2 += '### 道法会元精选（卷十一至卷二十）\n\n'
content2 += '**【原文】**\n\n%s\n\n' % all_text[:15000]
content2 += '**【白话提要】**\n\n'
content2 += '《道法会元》卷十一至卷二十，续收雷法、符咒、斋醮科仪等内容。'
with open(os.path.join(OUT_DIR2, 'dwhy_03.md'), 'w', encoding='utf-8') as f:
    f.write(content2)
print('  保存: dwhy_03.md')

print('\n全部完成')
