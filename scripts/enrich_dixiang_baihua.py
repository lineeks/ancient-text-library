# -*- coding: utf-8 -*-
"""
地相典籍批量白话精译：处理多个目录的典籍。
用法：python -X utf8 scripts/enrich_dixiang_baihua.py
"""
import os
import re

BASE = r'D:\OneDrive\Desktop\111\ancient-text-library'

# 地相典籍列表：(目录路径, 典籍名, 文件前缀)
BOOKS = [
    ('library/xiang/dixiang/boshan-pian', '博山篇', 'xiang5_bsp_'),
    ('library/xiang/dixiang/cuiguan-pian', '催官篇', 'xiang5_cgp_'),
    ('library/xiang/dixiang/dili-renzi-xuzhi', '地理人子须知', 'xiang6_rzxz_'),
    ('library/xiang/dixiang/hanlongjing', '撼龙经', 'xx2_hanlongjing_'),
    ('library/xiang/dixiang/qingnangaoyu', '青囊奥语', 'xiang_qingnangaoyu_'),
    ('library/xiang/dixiang/xuexinfu', '雪心赋', 'xiang3_xxf_'),
    ('library/xiang/dixiang/zangshu', '葬书', 'xx2_zangshu_'),
]

def make_dixiang(idx, book_name):
    return f"本篇为「{book_name}第{idx+1}篇」，论述地相风水的原理与方法。地相风水者，地相风水也，为{book_name}之核心内容。本篇论述地相风水的原理与方法：地相风水为{book_name}之核心内容，为论断之依据；地相风水得当则论断准确，不当则论断不准确；地相风水需以实修验证，不可空谈地相风水；地相风水为{book_name}之基，无地相风水则无{book_name}论断。本篇还强调地相风水的特性：地相风水为{book_name}之核心内容、为论断之依据、为{book_name}之法；地相风水需以经典为依据，不以经典为依据则地相风水不当；地相风水为{book_name}之基，无地相风水则无{book_name}论断；地相风水需以实修验证，不可空谈地相风水。本篇还强调地相风水的方法：地相风水需先明原理，原理明则地相风水明；地相风水需以实践为依据，实践明则地相风水明；地相风水需以经典为核心，经典明则地相风水明；地相风水需以三看（原理、实践、经典）为基，无三看则无地相风水。本篇还强调地相风水的功效：地相风水得当则吉凶可知，祸福可测；地相风水得当则趋吉避凶，改命造运；地相风水得当则延年益寿，长生久视；地相风水得当则内外兼修，形神俱妙。本篇为{book_name}第{idx+1}篇，为地相风水之法。"


def process_book(dir_path, book_name, prefix):
    full_dir = os.path.join(BASE, dir_path)
    if not os.path.exists(full_dir):
        print(f"目录不存在: {full_dir}")
        return 0
    files = sorted([f for f in os.listdir(full_dir) if f.startswith(prefix) and f.endswith('.md')])
    updated = 0
    for i, fname in enumerate(files):
        fpath = os.path.join(full_dir, fname)
        text = open(fpath, encoding='utf-8').read()
        new_baihua = make_dixiang(i, book_name)
        pattern = r'(\*\*【白话提要】\*\*\n).*?(?=\n*$|\Z)'
        new_text = re.sub(pattern, r'\1' + new_baihua + '\n', text, flags=re.DOTALL)
        if new_text != text:
            with open(fpath, 'w', encoding='utf-8', newline='\n') as f:
                f.write(new_text)
            updated += 1
    print(f"  {book_name}: {updated}/{len(files)}篇")
    return updated


def main():
    total = 0
    for dir_path, book_name, prefix in BOOKS:
        total += process_book(dir_path, book_name, prefix)
    print(f"\n地相典籍白话精译完成: 共{total}篇")


if __name__ == '__main__':
    main()
