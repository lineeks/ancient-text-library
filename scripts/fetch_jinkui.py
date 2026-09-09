# -*- coding: utf-8 -*-
"""获取金匮要略25篇全文（中华典藏网译注本 + 古诗文网补第十四篇）"""
import urllib.request, re, time, os

BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT = os.path.join(BASE, "raw/jinkui-yaolue.txt")

# 25篇标题
CHAPTERS = [
    "脏腑经络先后病脉证第一",
    "痉湿暍病脉证治第二",
    "百合狐惑阴阳毒病脉证治第三",
    "疟病脉证并治第四",
    "中风历节病脉证并治第五",
    "血痹虚劳病脉证并治第六",
    "肺痿肺痈咳嗽上气病脉证治第七",
    "奔豚气病脉证治第八",
    "胸痹心痛短气病脉证治第九",
    "腹满寒疝宿食病脉证治第十",
    "五脏风寒积聚病脉证并治第十一",
    "痰饮咳嗽病脉证并治第十二",
    "消渴小便不利淋病脉证并治第十三",
    "水气病脉证并治第十四",
    "黄疸病脉证并治第十五",
    "惊悸吐血下血胸满瘀血病脉证治第十六",
    "呕吐哕下利病脉证治第十七",
    "疮痈肠痈浸淫病脉证并治第十八",
    "趺蹶手指臂肿转筋阴狐疝蛔虫病脉证治第十九",
    "妇人妊娠病脉证并治第二十",
    "妇人产后病脉证治第二十一",
    "妇人杂病脉证并治第二十二",
    "杂疗方第二十三",
    "禽兽鱼虫禁忌并治第二十四",
    "果实菜谷禁忌并治第二十五",
]

def fetch(url, timeout=20):
    req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
    return urllib.request.urlopen(req, timeout=timeout).read().decode('utf-8', errors='ignore')

def clean(html):
    text = re.sub(r'<[^>]+>', '', html)
    text = re.sub(r'&nbsp;', ' ', text)
    text = re.sub(r'&[a-z]+;', '', text)
    text = re.sub(r'\s+', ' ', text)
    return text.strip()

all_text = []
# 篇1-13: ID 324874-324886
for i in range(13):
    pid = 324874 + i
    url = f'https://www.diancang.xyz/xuanxuewushu/16877/{pid}.html'
    try:
        html = fetch(url)
        text = clean(html)
        # 提取正文
        start = max(text.find('问曰'), text.find('师曰'), text.find('金匮'))
        if start > 0:
            text = text[start:]
        end = min([x for x in [text.find('上一篇'), text.find('下一篇'), text.find('目录')] if x > 0] + [len(text)])
        text = text[:end].strip()
        all_text.append(f'=== {CHAPTERS[i]} ===\n{text}')
        print(f'  篇{i+1}: {len(text)} 字符')
        time.sleep(0.3)
    except Exception as e:
        print(f'  篇{i+1}: 错误 {e}')

# 篇14: 古诗文网
try:
    url = 'https://m.gushiwen.cn/guwen/bookv_944b026f6e13.aspx'
    html = fetch(url)
    text = clean(html)
    start = text.find('师曰')
    if start > 0:
        text = text[start:]
    end = min([x for x in [text.find('上一篇'), text.find('下一篇'), text.find('古诗文')] if x > 0] + [len(text)])
    text = text[:end].strip()
    all_text.append(f'=== {CHAPTERS[13]} ===\n{text}')
    print(f'  篇14: {len(text)} 字符 (古诗文网)')
except Exception as e:
    print(f'  篇14: 错误 {e}')

# 篇15-25: ID 324887-324897
for i in range(11):
    pid = 324887 + i
    url = f'https://www.diancang.xyz/xuanxuewushu/16877/{pid}.html'
    try:
        html = fetch(url)
        text = clean(html)
        start = max(text.find('问曰'), text.find('师曰'), text.find('金匮'), text.find('黄疸'))
        if start > 0:
            text = text[start:]
        end = min([x for x in [text.find('上一篇'), text.find('下一篇'), text.find('目录')] if x > 0] + [len(text)])
        text = text[:end].strip()
        all_text.append(f'=== {CHAPTERS[14+i]} ===\n{text}')
        print(f'  篇{15+i}: {len(text)} 字符')
        time.sleep(0.3)
    except Exception as e:
        print(f'  篇{15+i}: 错误 {e}')

full = '\n\n'.join(all_text)
with open(OUT, 'w', encoding='utf-8') as f:
    f.write(full)
print(f'\n金匮要略保存: {len(full)} 字符, {len(all_text)} 篇 → {OUT}')
