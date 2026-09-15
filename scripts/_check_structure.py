# -*- coding: utf-8 -*-
"""检查候选书的章节结构"""
import urllib.request, urllib.parse, re

for name in ['医学心悟', '血证论', '医林改错', '温热论', '湿热病篇']:
    encoded = urllib.parse.quote(name)
    url = 'https://raw.githubusercontent.com/wenyuange/medicine/master/%s.txt' % encoded
    req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
    text = urllib.request.urlopen(req, timeout=20).read().decode('utf-8', errors='ignore')
    
    # 找常见章节标记
    marks = []
    for pattern in [r'卷[上中下一二三四五六七八九十]+', r'[一二三四五六七八九十]+、', r'[第][一二三四五六七八九十]+[章篇]']:
        matches = re.findall(pattern, text[:5000])
        if matches:
            marks.append(pattern + ': ' + str(matches[:10]))
    
    print('\n=== %s (%d字) ===' % (name, len(text)))
    print('前300字:', text[:300].replace('\n', '|'))
    for m in marks:
        print('  章节标记:', m)
