# -*- coding: utf-8 -*-
"""
Aether-Cycle 古籍知识库 · 一键重建脚本（跨平台，纯标准库）

按依赖顺序执行：
  1. build_index.py     — 生成人类可读 INDEX.md（各书子索引 + 根索引）
  2. build_manifest.py  — 生成机器索引 manifest.json（确定性，无时间戳）
  3. validate_library.py — 交付前质量门（Frontmatter / id / 枚举 / 正文分层）
  4. tests/recall_regression.py — Python 召回回归 + golden 对拍 + 自召回

用法：
  python -X utf8 scripts/rebuild_all.py
  python -X utf8 scripts/rebuild_all.py --skip-tests   # 只重建+校验，不跑测试
  python -X utf8 scripts/rebuild_all.py --manifest-only # 只重建 manifest
"""
import argparse
import subprocess
import sys
import os

BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PY = sys.executable


def run(script, desc):
    print(f"\n{'='*60}")
    print(f"▶ {desc}: {script}")
    print('='*60)
    r = subprocess.run([PY, "-X", "utf8", os.path.join(BASE, script)],
                       cwd=BASE, env={**os.environ, "PYTHONIOENCODING": "utf-8"})
    if r.returncode != 0:
        print(f"\n❌ {desc} 失败（exit {r.returncode}），终止重建。")
        sys.exit(r.returncode)
    print(f"✅ {desc} 通过")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--skip-tests", action="store_true", help="跳过 Python 召回测试")
    ap.add_argument("--manifest-only", action="store_true", help="只重建 manifest（跳过 index/validate/tests）")
    args = ap.parse_args()

    if args.manifest_only:
        run("scripts/build_manifest.py", "重建 manifest.json")
        print("\n✅ manifest-only 重建完成")
        return

    run("scripts/build_index.py", "重建 INDEX.md（各书子索引 + 根索引）")
    run("scripts/build_manifest.py", "重建 manifest.json（机器索引）")
    run("scripts/validate_library.py", "质量门校验")

    if not args.skip_tests:
        run("tests/recall_regression.py", "Python 召回回归 + golden 对拍 + 自召回")
        # Rust 测试（如果有 cargo）
        cargo = shutil_which("cargo")
        if cargo:
            print(f"\n{'='*60}")
            print("▶ Rust engine 测试: cargo test")
            print('='*60)
            r = subprocess.run([cargo, "test"], cwd=os.path.join(BASE, "engine"))
            if r.returncode != 0:
                print(f"\n❌ Rust 测试失败（exit {r.returncode}）")
                sys.exit(r.returncode)
            print("✅ Rust 测试通过")
        else:
            print("\n⚠️  未找到 cargo，跳过 Rust 测试（可本地手动运行 cargo test）")

    print(f"\n{'='*60}")
    print("🎉 全部重建完成：INDEX + manifest + validate + tests 全部通过")
    print('='*60)


def shutil_which(cmd):
    """shutil.which 的轻量替代（避免 import shutil 仅用一次）。"""
    from shutil import which
    return which(cmd)


if __name__ == "__main__":
    main()
