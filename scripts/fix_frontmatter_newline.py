# -*- coding: utf-8 -*-
"""
修复 frontmatter 结束标记前缺换行的问题（v3）。

元数据增强脚本 bug：new_fm 末尾无 trailing newline，导致结束标记 ---
被直接附加到 frontmatter 最后一行末尾（如 tags: [...]---），
使 YAML 解析失败（scan 返回只有 _file 字段的条目）。

修复：全文件搜索非行首的 ---（即前面不是换行的 ---），在其前插入换行。
仅修复 frontmatter 区域内（开头 --- 到第一个 \n\n# 或 \n\n**【）。

用法：python -X utf8 scripts/fix_frontmatter_newline.py
"""
import os
import re
import glob

BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def fix_file(path):
    with open(path, encoding="utf-8") as f:
        content = f.read()
    if not content.startswith("---"):
        return False

    # 找到 frontmatter 区域结束位置：第一个 \n\n# 或 \n\n**【
    body_match = re.search(r"\n\n(?:#|\*\*【)", content)
    if not body_match:
        return False
    fm_end = body_match.start() + 2  # 包含 \n\n

    # 在 fm_region 内搜索：--- 前面不是换行（即被附加到前一行末尾）
    fm_region = content[:fm_end]
    # 找所有 --- 的位置
    modified = False
    # 从后往前修复，避免位置偏移
    for m in reversed(list(re.finditer(r"---", fm_region))):
        pos = m.start()
        if pos == 0:
            continue  # 开头的 ---
        if content[pos - 1] != "\n":
            # 损坏：--- 前面不是换行
            content = content[:pos] + "\n" + content[pos:]
            modified = True

    if modified:
        with open(path, "w", encoding="utf-8", newline="\n") as f:
            f.write(content)
    return modified


def main():
    total = 0
    fixed = 0
    for path in glob.glob(os.path.join(BASE, "library", "**", "*.md"), recursive=True):
        if path.endswith("INDEX.md"):
            continue
        total += 1
        if fix_file(path):
            fixed += 1
    print(f"扫描 {total} 个文件，修复 {fixed} 个")


if __name__ == "__main__":
    main()
