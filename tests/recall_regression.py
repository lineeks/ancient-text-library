# -*- coding: utf-8 -*-
"""
Aether-Cycle 古籍知识库 · 召回回归测试（纯标准库 unittest）

验证参考检索器 scripts/retrieve_reference.py 在 manifest.json 上的匹配行为，
Rust engine/ 的匹配语义须与本测试一致。运行：
    python -X utf8 tests/recall_regression.py
或： python -m unittest tests.recall_regression -v
"""
import json
import os
import sys
import unittest

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(ROOT, "scripts"))
import retrieve_reference as rr  # noqa: E402


def ids_by(entries, book=None, **field_has):
    """按 book 与 conditions 字段包含值动态定位 id，避免在测试里硬编码易错文件名。"""
    out = []
    for e in entries:
        if book and e["book"] != book:
            continue
        ok = True
        for k, v in field_has.items():
            if v not in e["conditions"].get(k, []):
                ok = False
                break
        if ok:
            out.append(e["id"])
    return out


class RecallTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.lib = rr.Library(os.path.join(ROOT, "manifest.json"))
        cls.E = cls.lib.entries

    def hit_ids(self, chart):
        return {e["id"] for e in self.lib.structured_query(chart)}

    # 1) 穷通宝鉴：日干×月令 100% 精确锚定且 weight=10 居首
    def test_qiongtong_day_month_exact(self):
        hits = self.lib.structured_query({"day_master": ["Jia"], "month_branch": ["Yin"]})
        self.assertTrue(hits)
        self.assertEqual(hits[0]["id"], "qtbj_jia_yin")
        self.assertEqual(hits[0]["weight"], 10)
        ids = {e["id"] for e in hits}
        self.assertIn("qtbj_jia_yin", ids)
        # 换错日干不得命中该条
        self.assertNotIn("qtbj_jia_yin",
                         self.hit_ids({"day_master": ["Yi"], "month_branch": ["Yin"]}))

    # 2) 正官格：子平真诠 + 命理约言法/赋同时召回
    def test_pattern_zhengguan(self):
        ids = self.hit_ids({"pattern": ["正官格"]})
        zpzq = ids_by(self.E, book="子平真诠评注", pattern="正官格")
        self.assertTrue(zpzq, "子平真诠应存在正官格章节")
        self.assertTrue(set(zpzq) <= ids)
        self.assertIn("mlyy_fa15", ids)   # 看正官法
        self.assertIn("mlyy_fu05", ids)   # 正官赋

    # 3) 纠错：纯神煞论不得再被“七杀格”误召回；真正偏官法/赋仍在
    def test_qisha_mislabel_removed(self):
        ids = self.hit_ids({"pattern": ["七杀格"], "ten_god": ["七杀"]})
        for wrong in ("mlyy_lun15", "mlyy_lun16", "mlyy_lun18", "mlyy_lun24"):
            self.assertNotIn(wrong, ids, f"{wrong} 是神煞主题，不应被七杀格召回")
        self.assertIn("mlyy_fa16", ids)  # 看偏官法
        self.assertIn("mlyy_fu06", ids)  # 偏官赋

    # 4) 天乙贵人：三命（神煞出处）+ 五行精纪（古法源流）+ 命理约言贵人论
    def test_shensha_tianyi(self):
        ids = self.hit_ids({"shensha": ["天乙贵人"]})
        self.assertIn("smth_ss_tianyiguiren", ids)
        self.assertIn("wxjj_v13_01", ids)
        self.assertIn("wxjj_v14_01", ids)
        self.assertIn("mlyy_lun20", ids)

    # 5) 三命日时断：日柱×时柱精确命中，错时柱不命中
    def test_rishi_exact(self):
        ids = self.hit_ids({"day_pillar": ["庚子"], "hour_pillar": ["己卯"]})
        self.assertIn("smth_rs_gengzi_jimao", ids)
        bad = self.hit_ids({"day_pillar": ["庚子"], "hour_pillar": ["甲子"]})
        self.assertNotIn("smth_rs_gengzi_jimao", bad)

    # 6) 五行精纪增强：化格 / 合
    def test_wxjj_enrichment(self):
        self.assertIn("wxjj_v04_01", self.hit_ids({"pattern": ["化格"]}))
        self.assertIn("wxjj_v18_04", self.hit_ids({"shensha": ["六合"]}))
        self.assertIn("wxjj_v18_01", self.hit_ids({"ten_god": ["偏印"]}))

    # 7) 命理约言格局补全：印绶格法/赋
    def test_mlyy_pattern_completion(self):
        ids = self.hit_ids({"pattern": ["印绶格"]})
        for x in ("mlyy_fa20", "mlyy_fu07", "mlyy_fu08"):
            self.assertIn(x, ids)

    # 8) 排序契约：精确度优先（精确条整体在无约束通论之前），层内 weight 降序
    def test_ordering_specificity_then_weight(self):
        hits = self.lib.structured_query({"ten_god": ["正印"]})
        specs = [rr.Library.specificity(e["conditions"]) for e in hits]
        # 精确度序列非增：任何精确条都不落在通论条之后
        self.assertEqual(specs, sorted(specs, reverse=True))
        # 每个精确度层内部 weight 非增
        layer = {}
        for e, s in zip(hits, specs):
            layer.setdefault(s, []).append(e["weight"])
        for ws in layer.values():
            self.assertEqual(ws, sorted(ws, reverse=True))
        # 综合命盘下，精确锚定的穷通条应排在所有无约束通论之前
        top = self.lib.structured_query(
            {"day_master": ["Geng"], "month_branch": ["Zi"],
             "pattern": ["七杀格"], "shensha": ["驿马"]})
        self.assertEqual(top[0]["id"], "qtbj_geng_zi")
        self.assertGreater(rr.Library.specificity(top[0]["conditions"]), 0)

    # 9) 空命盘默认零召回（无锚点通论不制造噪声）；显式 include_general 才附带且全为通论
    def test_empty_chart_no_general_noise(self):
        self.assertEqual(self.lib.structured_query({}), [])
        gen = self.lib.structured_query({}, include_general=True)
        self.assertTrue(all(rr.Library.is_general(e["conditions"]) for e in gen))
        self.assertGreater(len(gen), 0)

    # 9b) 自召回不变量：每条“有硬锚点”的条目用自身 conditions 构造命盘必能召回自己
    def test_every_anchored_entry_self_recalls(self):
        bad = []
        for e in self.E:
            cond = e["conditions"]
            if rr.Library.is_general(cond):
                continue
            chart = {k: list(cond.get(k, [])) for k in rr.HARD_FIELDS}
            ids = self.hit_ids(chart)
            if e["id"] not in ids:
                bad.append(e["id"])
        self.assertEqual(bad, [], f"这些条目无法被自身 conditions 召回: {bad[:10]}")

    # 9c) 无锚点条目规模基线（只靠关键词/书目浏览，不进结构化召回），防止无序膨胀
    def test_unanchored_baseline(self):
        n_general = sum(rr.Library.is_general(e["conditions"]) for e in self.E)
        self.assertLessEqual(n_general, 1200, f"无锚点条目增至 {n_general}，请评估是否补 conditions")

    # 9d) 黄金对拍：Python 结果必须与 golden_expected.json 完全一致（Rust 侧同测此文件）
    def test_golden_matches_expected(self):
        cases = json.load(open(os.path.join(ROOT, "tests/golden_cases.json"),
                               encoding="utf-8"))["cases"]
        expected = json.load(open(os.path.join(ROOT, "tests/golden_expected.json"),
                                  encoding="utf-8"))
        self.assertEqual(set(cases), set(expected))
        for name, chart in cases.items():
            got = [e["id"] for e in self.lib.structured_query(chart)]
            self.assertEqual(got, expected[name], f"golden case 失配: {name}")

    # 10) 综合命盘多条件 AND：穷通条不受它书字段约束，仍按日干月令命中
    def test_combined_chart(self):
        chart = {"day_master": ["Geng"], "month_branch": ["Zi"],
                 "pattern": ["七杀格"], "shensha": ["驿马"]}
        ids = self.hit_ids(chart)
        self.assertIn("qtbj_geng_zi", ids)

    # 11) manifest 完整性：总数、id 唯一、weight 区间、path 文件真实存在
    def test_manifest_integrity(self):
        self.assertEqual(self.lib.meta["total"], 2224)
        self.assertEqual(len(self.E), 2224)
        ids = [e["id"] for e in self.E]
        self.assertEqual(len(ids), len(set(ids)))
        for e in self.E:
            self.assertGreaterEqual(e["weight"], 0)
            self.assertLessEqual(e["weight"], 10)
            self.assertTrue(os.path.isfile(os.path.join(ROOT, e["path"])),
                            f"manifest 指向不存在文件: {e['path']}")

    # 12) 关键词主题召回（非硬匹配）
    def test_keyword_query(self):
        ids = {e["id"] for e in self.lib.keyword_query("天乙")}
        self.assertIn("wxjj_v14_01", ids)


if __name__ == "__main__":
    unittest.main(verbosity=2)
