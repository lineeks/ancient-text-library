# -*- coding: utf-8 -*-
"""
生成双端检索黄金期望：用 Python 参考检索器跑 tests/golden_cases.json 中的命盘，
把每个 case 的有序命中 id 序列写入 tests/golden_expected.json。

Rust engine 的对拍测试与 Python 回归测试都以该文件为期望，从而保证两端
匹配 / 排序语义在同一夹具上完全一致。仅在有意改动数据或匹配语义后重跑；
输出确定性（无时间戳、按 case 名排序）。

用法：python -X utf8 scripts/dump_golden.py
"""
import json
import os
import sys

BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(BASE, "scripts"))
import retrieve_reference as rr  # noqa: E402

CASES = os.path.join(BASE, "tests", "golden_cases.json")
OUT = os.path.join(BASE, "tests", "golden_expected.json")


def main():
    cases = json.load(open(CASES, encoding="utf-8"))["cases"]
    lib = rr.Library(os.path.join(BASE, "manifest.json"))
    expected = {}
    for name in sorted(cases):
        chart = cases[name]
        expected[name] = [e["id"] for e in lib.structured_query(chart)]
    with open(OUT, "w", encoding="utf-8", newline="\n") as f:
        json.dump(expected, f, ensure_ascii=False, indent=2)
        f.write("\n")
    total = sum(len(v) for v in expected.values())
    print(f"golden 期望已写出 {len(expected)} 个 case、共 {total} 条有序命中 -> {OUT}")


if __name__ == "__main__":
    main()
