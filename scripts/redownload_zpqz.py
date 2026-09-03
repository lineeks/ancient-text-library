# -*- coding: utf-8 -*-
"""重新下载《子平真诠评注》，保存原始字节并尝试多种编码解码。"""
import os
import urllib.request

RAW_DIR = r"D:\OneDrive\Desktop\111\ancient-text-library\raw"
url = "https://raw.githubusercontent.com/bho1668/yibook/main/" \
      "%E5%AD%90%E5%B9%B3%E7%9C%9F%E8%AF%A0%E8%AF%84%E6%B3%A8-%E6%B8%85-%E6%B2%88%E5%AD%9D%E7%9E%BB.txt"
ua = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 Chrome/120.0 Safari/537.36"}

req = urllib.request.Request(url, headers=ua)
with urllib.request.urlopen(req, timeout=60) as resp:
    data = resp.read()
print("bytes:", len(data))
raw_path = os.path.join(RAW_DIR, "zipingzhenquan.raw.bin")
with open(raw_path, "wb") as f:
    f.write(data)

# 尝试多种编码
for enc in ("utf-8", "gb18030", "gbk", "big5", "big5hkscs"):
    try:
        text = data.decode(enc)
        print(f"[OK] {enc}: {len(text)} chars, 前20字符: {text[:20]!r}")
    except Exception as e:
        print(f"[FAIL] {enc}: {e}")
