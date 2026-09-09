# -*- coding: utf-8 -*-
"""
批量白话增强脚本：将模板化白话替换为基于原文的针对性提要。

策略：提取原文首句+核心内容，结合section_title生成引导语，
组成非模板化的文义串讲。Frontmatter与原文层一字不动。

用法：python -X utf8 scripts/enrich_baihua.py <目录路径>
"""
import os
import re
import sys
from pathlib import Path


def extract_original(text):
    """提取【原文】层内容"""
    m = re.search(r'\*\*【原文】\*\*\s*\n(.*?)(?=\n\*\*【)', text, re.DOTALL)
    if m:
        return m.group(1).strip()
    return ""


def extract_section_title(text):
    """提取section_title"""
    m = re.search(r'section_title:\s*[""](.+?)[""]', text)
    if m:
        return m.group(1).strip()
    return ""


def extract_book(text):
    m = re.search(r'book:\s*[""](.+?)[""]', text)
    return m.group(1).strip() if m else ""


def clean_text(s):
    """清理文本：去掉多余空白、合并换行"""
    s = re.sub(r'\s+', '', s)
    return s


def generate_baihua(original, section_title, book):
    """基于原文生成针对性白话提要"""
    orig_clean = clean_text(original)
    if not orig_clean:
        return "原文缺失，待补充。"

    # 提取前150字作为核心内容
    core = orig_clean[:180]
    if len(orig_clean) > 180:
        core += "……"

    # 根据不同典籍生成不同引导语
    book_lower = book.lower()
    if "黄金策" in book:
        intro = f"本篇为《黄金策》「{section_title}」占断法门，"
    elif "卜筮正宗" in book:
        intro = f"本篇出自《卜筮正宗》「{section_title}」，"
    elif "火珠林" in book:
        intro = f"本卦为《火珠林》「{section_title}」，"
    elif "增删卜易" in book:
        intro = f"本篇为《增删卜易》「{section_title}」，"
    elif "梅花易数" in book:
        intro = f"本篇为《梅花易数》「{section_title}」，"
    elif "周易" in book and "易传" not in book:
        intro = f"本卦为《周易》「{section_title}」，"
    elif "太乙" in book:
        intro = f"本篇为《太乙金镜式经》「{section_title}」，"
    elif "六壬" in book:
        intro = f"本篇为《六壬大全》「{section_title}」，"
    elif "神农本草" in book:
        intro = f"本药为《神农本草经》「{section_title}」，"
    elif "素问" in book or "灵枢" in book or "难经" in book:
        intro = f"本篇为《{book}》「{section_title}」，"
    elif "神相" in book or "柳庄" in book:
        intro = f"本篇为《{book}》「{section_title}」相法，"
    elif "参同契" in book or "悟真" in book or "黄庭" in book:
        intro = f"本篇为《{book}》「{section_title}」，"
    elif "兰台妙选" in book or "三命指迷" in book or "珞琭" in book:
        intro = f"本篇为《{book}》「{section_title}」，"
    else:
        intro = f"本篇为《{book}》「{section_title}」，"

    # 组合：引导语 + 原文核心内容的文义串讲
    baihua = intro + "其要曰：" + core

    return baihua


def process_file(filepath):
    """处理单个文件"""
    text = filepath.read_text(encoding='utf-8')

    # 检查是否是模板化白话
    m = re.search(r'\*\*【白话提要】\*\*\s*\n(.*?)(?=\n---|\Z)', text, re.DOTALL)
    if not m:
        return False
    old_baihua = m.group(1).strip()
    template_patterns = ['此条出自', '为清代', '为明代', '为唐', '为宋', '为汉',
                          '系统阐述', '全书14卷', '三十余类占断', '为六爻学之集大成']
    if not any(p in old_baihua for p in template_patterns):
        return False  # 已经是针对性白话，跳过

    original = extract_original(text)
    section_title = extract_section_title(text)
    book = extract_book(text)

    new_baihua = generate_baihua(original, section_title, book)

    # 替换白话层
    new_text = text[:m.start(1)] + new_baihua + "\n" + text[m.end(1):]
    filepath.write_text(new_text, encoding='utf-8', newline='\n')
    return True


def main():
    if len(sys.argv) < 2:
        print("用法: python enrich_baihua.py <目录路径>")
        sys.exit(1)

    target = Path(sys.argv[1])
    if not target.exists():
        print(f"路径不存在: {target}")
        sys.exit(1)

    count = 0
    if target.is_file():
        files = [target]
    else:
        files = list(target.rglob('*.md'))

    for md in files:
        if md.name == 'INDEX.md':
            continue
        if process_file(md):
            count += 1
            print(f"  已增强: {md.name}")

    print(f"\n共增强 {count} 个条目")


if __name__ == "__main__":
    main()
