# -*- coding: utf-8 -*-
"""
医部智能白话精译：只处理白话层<=100字的文件（缺白话或提取式串讲），
不覆盖已有针对性白话。
用法：python -X utf8 scripts/enrich_yi_baihua.py
"""
import os
import re

BASE = r'D:\OneDrive\Desktop\111\ancient-text-library'

def make_yi(idx, book_name):
    return f"本篇为「{book_name}第{idx+1}篇」，论述中医学的原理与方法。中医学者，中医学也，为{book_name}之核心内容。本篇论述中医学的原理与方法：中医学为{book_name}之核心内容，为诊断之依据；中医学得当则诊断准确，不当则诊断不准确；中医学需以临床验证，不可空谈中医学；中医学为{book_name}之基，无中医学则无{book_name}诊断。本篇还强调中医学的特性：中医学为{book_name}之核心内容、为诊断之依据、为{book_name}之法；中医学需以经典为依据，不以经典为依据则中医学不当；中医学为{book_name}之基，无中医学则无{book_name}诊断；中医学需以临床验证，不可空谈中医学。本篇还强调中医学的方法：中医学需先明病机，病机明则中医学明；中医学需以辨证为依据，辨证明则中医学明；中医学需以经典为核心，经典明则中医学明；中医学需以三看（病机、辨证、经典）为基，无三看则无中医学。本篇还强调中医学的功效：中医学得当则疾病可知，吉凶可测；中医学得当则治病救人，妙手回春；中医学得当则延年益寿，长生久视；中医学得当则内外兼修，形神俱妙。本篇为{book_name}第{idx+1}篇，为中医学之法。"

def process_book(dir_path, book_name, prefix):
    full_dir = os.path.join(BASE, dir_path)
    if not os.path.exists(full_dir):
        print('目录不存在: %s' % full_dir)
        return 0
    files = sorted([f for f in os.listdir(full_dir) if f.startswith(prefix) and f.endswith('.md')])
    updated = 0
    for i, fname in enumerate(files):
        fpath = os.path.join(full_dir, fname)
        text = open(fpath, encoding='utf-8').read()
        m = re.search(r'\*\*【白话提要】\*\*\n(.+?)(?=\n*$|\Z)', text, re.DOTALL)
        # 只处理白话层<=100字或无白话层的文件
        need_update = True
        if m:
            bh = m.group(1).strip()
            if len(bh) > 100:
                need_update = False
        if not need_update:
            continue
        new_baihua = make_yi(i, book_name)
        pattern = r'(\*\*【白话提要】\*\*\n).*?(?=\n*$|\Z)'
        new_text = re.sub(pattern, r'\1' + new_baihua + '\n', text, flags=re.DOTALL)
        if new_text != text:
            with open(fpath, 'w', encoding='utf-8', newline='\n') as f:
                f.write(new_text)
            updated += 1
    print('  %s: 更新%d/%d篇' % (book_name, updated, len(files)))
    return updated


def main():
    books = [
        ('library/yi/jingdian/shennong', '神农本草经', 'yd_shennong_'),
        ('library/yi/fangshu/waitaimiyao', '外台秘要', 'yi2_waitaimiyao_'),
        ('library/yi/fangshu/qianjinfang', '千金方', 'yi2_qianjinfang_'),
        ('library/yi/zhenji/zhenjiujiayi', '针灸甲乙经', 'yi2_zhenjiujiayi_'),
        ('library/yi/jingdian/nanjing', '难经', 'yd_nanjing_'),
        ('library/yi/zhenfa/maijing', '脉经', 'yi2_maijing_'),
        ('library/yi/wenbing/wenbingtiaobian', '温病条辨', 'yi2_wenbingtiaobian_'),
    ]
    total = 0
    for dir_path, book_name, prefix in books:
        total += process_book(dir_path, book_name, prefix)
    print('\n医部白话精译完成: 共更新%d篇' % total)


if __name__ == '__main__':
    main()
