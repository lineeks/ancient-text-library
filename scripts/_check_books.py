# -*- coding: utf-8 -*-
"""检查wenyuange/medicine仓库中几本候选书的体量"""
import urllib.request, urllib.parse

CANDIDATES = [
    '医学心悟', '医学入门', '医学正传', '景岳全书',
    '本草纲目', '医宗金鉴', '医学三字经', '濒湖脉学',
    '温病条辨', '伤寒论', '金匮要略', '神农本草经',
    '黄帝内经素问', '灵枢经', '难经',
    '脉经', '针灸甲乙经', '千金方', '外台秘要',
    '丹溪心法', '脾胃论', '兰室秘藏',
    '汤头歌诀', '药性赋',
    '医学衷中参西录', '血证论', '医林改错',
    '温病条辨', '温热论', '湿热病篇',
]

for name in CANDIDATES:
    encoded = urllib.parse.quote(name)
    url = 'https://raw.githubusercontent.com/wenyuange/medicine/master/%s.txt' % encoded
    try:
        req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
        data = urllib.request.urlopen(req, timeout=10).read()
        text = data.decode('utf-8', errors='ignore')
        print('%-12s %8d字' % (name, len(text)))
    except Exception as e:
        print('%-12s 错误: %s' % (name, str(e)[:40]))
