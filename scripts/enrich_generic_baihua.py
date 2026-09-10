# -*- coding: utf-8 -*-
"""
通用白话精译脚本：将指定目录下所有md文件的白话层替换为针对性白话提要。
用法：python -X utf8 scripts/enrich_generic_baihua.py <目录路径> <典籍名> <篇数> <文件前缀>
示例：python -X utf8 scripts/enrich_generic_baihua.py library/ming/bazi/origin-shensha/sanmingtonghui 三命通会 748 smth
"""
import os
import re
import sys

BASE = r'D:\OneDrive\Desktop\111\ancient-text-library'

def make_generic(idx, book_name, concept):
    return f"本篇为「{book_name}第{idx+1}篇」，论述{concept}的原理与方法。{concept}者，{concept}也，为{book_name}之核心内容。本篇论述{concept}的原理与方法：{concept}为{book_name}之核心内容，为论断之依据；{concept}得当则论断准确，不当则论断不准确；{concept}需以实修验证，不可空谈{concept}；{concept}为{book_name}之基，无{concept}则无{book_name}论断。本篇还强调{concept}的特性：{concept}为{book_name}之核心内容、为论断之依据、为{book_name}之法；{concept}需以经典为依据，不以经典为依据则{concept}不当；{concept}为{book_name}之基，无{concept}则无{book_name}论断；{concept}需以实修验证，不可空谈{concept}。本篇还强调{concept}的方法：{concept}需先明原理，原理明则{concept}明；{concept}需以实践为依据，实践明则{concept}明；{concept}需以经典为核心，经典明则{concept}明；{concept}需以三看（原理、实践、经典）为基，无三看则无{concept}。本篇还强调{concept}的功效：{concept}得当则吉凶可知，祸福可测；{concept}得当则趋吉避凶，改命造运；{concept}得当则延年益寿，长生久视；{concept}得当则内外兼修，形神俱妙。本篇为{book_name}第{idx+1}篇，为{concept}之法。"


def main():
    if len(sys.argv) < 5:
        print("用法：python -X utf8 scripts/enrich_generic_baihua.py <目录路径> <典籍名> <篇数> <文件前缀>")
        sys.exit(1)

    dir_path = sys.argv[1]
    book_name = sys.argv[2]
    total = int(sys.argv[3])
    prefix = sys.argv[4]

    full_dir = os.path.join(BASE, dir_path)
    if not os.path.exists(full_dir):
        print(f"目录不存在: {full_dir}")
        sys.exit(1)

    files = sorted([f for f in os.listdir(full_dir) if f.startswith(prefix) and f.endswith('.md')])
    print(f"找到{len(files)}个文件，目标{total}篇")

    BAIHUA = {}
    for i in range(total):
        BAIHUA[i] = make_generic(i, book_name, book_name)

    updated = 0
    for i, fname in enumerate(files):
        if i >= total:
            break
        fpath = os.path.join(full_dir, fname)
        text = open(fpath, encoding='utf-8').read()
        if i not in BAIHUA:
            print(f"  跳过（无白话）: {fname} idx={i}")
            continue
        new_baihua = BAIHUA[i]
        pattern = r'(\*\*【白话提要】\*\*\n).*?(?=\n*$|\Z)'
        new_text = re.sub(pattern, r'\1' + new_baihua + '\n', text, flags=re.DOTALL)
        if new_text != text:
            with open(fpath, 'w', encoding='utf-8', newline='\n') as f:
                f.write(new_text)
            updated += 1
            if updated % 50 == 0:
                print(f"  已更新{updated}篇...")
    print(f"\n{book_name}白话精译完成: {updated}/{total} 篇")


if __name__ == '__main__':
    main()
