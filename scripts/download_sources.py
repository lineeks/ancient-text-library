# -*- coding: utf-8 -*-
"""
Aether-Cycle 古籍源文下载脚本
下载《穷通宝鉴》《子平真诠评注》的 GitHub 纯文本源文，统一保存为 UTF-8。
"""
import os
import sys
import urllib.request
import urllib.parse

BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
RAW_DIR = os.path.join(BASE, "raw")
os.makedirs(RAW_DIR, exist_ok=True)

SOURCES = [
    {
        "name": "qiongtongbaojian",
        "label": "《穷通宝鉴》（余春台辑本）",
        "url": "https://raw.githubusercontent.com/garychowcmu/daizhigev20/master/"
               "%E6%98%93%E8%97%8F/%E6%9C%AF%E6%95%B0/%E7%A9%B7%E9%80%9A%E5%AE%9D%E9%89%B4.txt",
    },
    {
        "name": "zipingzhenquan",
        "label": "《子平真诠评注》（徐乐吾评注本）",
        "url": "https://raw.githubusercontent.com/bho1668/yibook/main/"
               "%E5%AD%90%E5%B9%B3%E7%9C%9F%E8%AF%A0%E8%AF%84%E6%B3%A8-%E6%B8%85-%E6%B2%88%E5%AD%9D%E7%9E%BB.txt",
    },
]

UA = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
                  "(KHTML, like Gecko) Chrome/120.0 Safari/537.36"
}


def decode_auto(data: bytes):
    """依次尝试常见编码，返回 (text, encoding)。"""
    for enc in ("utf-8-sig", "utf-8", "gb18030", "big5"):
        try:
            return data.decode(enc), enc
        except (UnicodeDecodeError, LookupError):
            continue
    return data.decode("utf-8", errors="replace"), "utf-8(replace)"


def main():
    ok = True
    for src in SOURCES:
        out_path = os.path.join(RAW_DIR, src["name"] + ".txt")
        print(f"==> 下载 {src['label']}")
        print(f"    {src['url']}")
        try:
            req = urllib.request.Request(src["url"], headers=UA)
            with urllib.request.urlopen(req, timeout=60) as resp:
                data = resp.read()
            text, enc = decode_auto(data)
            with open(out_path, "w", encoding="utf-8") as f:
                f.write(text)
            print(f"    OK: {len(data)} bytes, 检测编码={enc}, 字符数={len(text)}")
            print(f"    保存: {out_path}")
        except Exception as e:
            ok = False
            print(f"    FAIL: {type(e).__name__}: {e}")
    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(main())
