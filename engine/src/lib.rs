//! Aether-Cycle 子平命理古籍知识库 · 检索引擎骨架（框架无关，可直接被 Tauri 复用）
//!
//! 加载库根 `manifest.json`（由 `scripts/build_manifest.py` 确定性生成），
//! 依据排盘内核产出的 `Chart` 做结构化召回。匹配 / 排序语义与 Python 参考实现
//! `scripts/retrieve_reference.py` 严格一致，并由 `tests/recall_regression.py`
//! 在同一数据上做交叉回归：
//!
//! - 复合键“组内 AND”：调候 `day_master + month_branch`、日时 `day_pillar + hour_pillar`
//!   必须同时满足；
//! - 检索维度“组间 OR”：`ten_god / pattern / shensha` 互为并列召回理由，任一命中即可；
//! - 无任何结构化硬锚点的通论条（序、泛论、纯歌赋）默认不参与命盘召回，避免噪声，
//!   仅在 `query_with(.., true)` 时整体附在精确条之后，或经关键词 / 书目浏览获取；
//! - 排序：命中精确度（声明的非空字段数）优先，其次典籍权重 weight，再次 path 稳定。
//!
//! 本 crate 不依赖 Tauri / 前端，纯 std + serde_json，便于单测与独立演进。

use serde::Deserialize;

/// 条目结构化匹配条件（manifest 中每条的 conditions 字段）。
#[derive(Debug, Clone, Default, Deserialize)]
pub struct Conditions {
    #[serde(default)]
    pub day_master: Vec<String>,
    #[serde(default)]
    pub month_branch: Vec<String>,
    #[serde(default)]
    pub day_pillar: Vec<String>,
    #[serde(default)]
    pub hour_pillar: Vec<String>,
    #[serde(default)]
    pub ten_god: Vec<String>,
    #[serde(default)]
    pub pattern: Vec<String>,
    #[serde(default)]
    pub shensha: Vec<String>,
    #[serde(default)]
    pub keywords: Vec<String>,
}

/// 一条古籍文献的检索元数据（正文仍在 path 指向的 Markdown 中，按需读取）。
#[derive(Debug, Clone, Deserialize)]
pub struct Entry {
    pub id: String,
    pub book: String,
    #[serde(rename = "type")]
    pub kind: String,
    pub tier: String,
    pub path: String,
    pub weight: i32,
    #[serde(default)]
    pub title: String,
    #[serde(default)]
    pub chapter: String,
    pub conditions: Conditions,
}

/// manifest.json 顶层结构（其余字段忽略）。
#[derive(Debug, Clone, Deserialize)]
pub struct Manifest {
    #[serde(default)]
    pub schema_version: u32,
    pub total: usize,
    pub entries: Vec<Entry>,
}

/// 排盘内核产出的查询命盘：只填已算出的维度，未算出的维度留空。
#[derive(Debug, Clone, Default, Deserialize)]
pub struct Chart {
    #[serde(default)]
    pub day_master: Vec<String>,
    #[serde(default)]
    pub month_branch: Vec<String>,
    #[serde(default)]
    pub day_pillar: Vec<String>,
    #[serde(default)]
    pub hour_pillar: Vec<String>,
    #[serde(default)]
    pub ten_god: Vec<String>,
    #[serde(default)]
    pub pattern: Vec<String>,
    #[serde(default)]
    pub shensha: Vec<String>,
}

impl Chart {
    pub fn new() -> Self {
        Self::default()
    }
    pub fn day_master(mut self, v: &[&str]) -> Self {
        self.day_master = v.iter().map(|s| s.to_string()).collect();
        self
    }
    pub fn month_branch(mut self, v: &[&str]) -> Self {
        self.month_branch = v.iter().map(|s| s.to_string()).collect();
        self
    }
    pub fn day_pillar(mut self, v: &[&str]) -> Self {
        self.day_pillar = v.iter().map(|s| s.to_string()).collect();
        self
    }
    pub fn hour_pillar(mut self, v: &[&str]) -> Self {
        self.hour_pillar = v.iter().map(|s| s.to_string()).collect();
        self
    }
    pub fn ten_god(mut self, v: &[&str]) -> Self {
        self.ten_god = v.iter().map(|s| s.to_string()).collect();
        self
    }
    pub fn pattern(mut self, v: &[&str]) -> Self {
        self.pattern = v.iter().map(|s| s.to_string()).collect();
        self
    }
    pub fn shensha(mut self, v: &[&str]) -> Self {
        self.shensha = v.iter().map(|s| s.to_string()).collect();
        self
    }
}

/// 已加载的知识库：一次性载入内存，查询零 IO。
#[derive(Debug, Clone)]
pub struct Library {
    manifest: Manifest,
}

/// 两个集合是否有交集。
fn intersects(declared: &[String], chart: &[String]) -> bool {
    declared.iter().any(|d| chart.contains(d))
}

/// 评估一个匹配键组：返回 None 表示该组未被条目声明；Some(hit) 表示组内全部
/// 已声明字段是否都与命盘相交（组内 AND）。
fn group_hit(pairs: &[(&Vec<String>, &Vec<String>)]) -> Option<bool> {
    let declared: Vec<&(&Vec<String>, &Vec<String>)> =
        pairs.iter().filter(|(d, _)| !d.is_empty()).collect();
    if declared.is_empty() {
        return None;
    }
    Some(declared.iter().all(|(d, h)| intersects(d, h)))
}

impl Library {
    /// 从 manifest.json 文本解析加载。
    pub fn from_json(text: &str) -> Result<Self, serde_json::Error> {
        let manifest: Manifest = serde_json::from_str(text)?;
        Ok(Self { manifest })
    }

    pub fn total(&self) -> usize {
        self.manifest.total
    }

    pub fn entries(&self) -> &[Entry] {
        &self.manifest.entries
    }

    /// 命中精确度：条目声明了几个非空结构化硬字段（0 = 无约束通论条）。
    pub fn specificity(c: &Conditions) -> usize {
        [
            !c.day_master.is_empty(),
            !c.month_branch.is_empty(),
            !c.day_pillar.is_empty(),
            !c.hour_pillar.is_empty(),
            !c.ten_god.is_empty(),
            !c.pattern.is_empty(),
            !c.shensha.is_empty(),
        ]
        .iter()
        .filter(|x| **x)
        .count()
    }

    /// 无任何结构化硬锚点（序、泛论、纯歌赋/口诀）：不参与结构化命盘召回，
    /// 只通过关键词或书目浏览获取，避免大量通论条在每一命盘下恒命中、稀释精确结果。
    pub fn is_general(c: &Conditions) -> bool {
        c.day_master.is_empty() && c.month_branch.is_empty() && c.day_pillar.is_empty()
            && c.hour_pillar.is_empty() && c.ten_god.is_empty() && c.pattern.is_empty()
            && c.shensha.is_empty()
    }

    /// 单条严格匹配：至少一个已声明匹配组整体命中（组内 AND、组间 OR）；
    /// 无硬锚点的通论条返回 false，不混入结构化召回。
    pub fn matches_entry(e: &Entry, chart: &Chart) -> bool {
        let c = &e.conditions;
        let groups: [Vec<(&Vec<String>, &Vec<String>)>; 5] = [
            vec![(&c.day_master, &chart.day_master), (&c.month_branch, &chart.month_branch)],
            vec![(&c.day_pillar, &chart.day_pillar), (&c.hour_pillar, &chart.hour_pillar)],
            vec![(&c.ten_god, &chart.ten_god)],
            vec![(&c.pattern, &chart.pattern)],
            vec![(&c.shensha, &chart.shensha)],
        ];
        groups
            .iter()
            .any(|g| matches!(group_hit(g), Some(true)))
    }

    /// 结构化召回（严格，默认）：只返回至少一个硬维度命中的精确条。
    pub fn query<'a>(&'a self, chart: &Chart) -> Vec<&'a Entry> {
        self.query_with(chart, false)
    }

    /// 结构化召回；`include_general=true` 时把无锚点通论条（按 weight↓, path↑）
    /// 整体附在精确条之后。
    pub fn query_with<'a>(&'a self, chart: &Chart, include_general: bool) -> Vec<&'a Entry> {
        let mut precise: Vec<&Entry> = Vec::new();
        let mut general: Vec<&Entry> = Vec::new();
        for e in self.manifest.entries.iter() {
            if Self::is_general(&e.conditions) {
                general.push(e);
            } else if Self::matches_entry(e, chart) {
                precise.push(e);
            }
        }
        precise.sort_by(|a, b| {
            let sa = Self::specificity(&a.conditions);
            let sb = Self::specificity(&b.conditions);
            sb.cmp(&sa)
                .then_with(|| b.weight.cmp(&a.weight))
                .then_with(|| a.path.cmp(&b.path))
        });
        if include_general {
            general.sort_by(|a, b| {
                b.weight
                    .cmp(&a.weight)
                    .then_with(|| a.path.cmp(&b.path))
            });
            precise.extend(general);
        }
        precise
    }
}

#[cfg(test)]
mod tests {
    use super::*;
    use std::collections::{HashMap, HashSet};

    fn sample_manifest() -> String {
        r#"{
          "schema_version": 1, "total": 5,
          "entries": [
            {"id":"qtbj_jia_yin","book":"穷通宝鉴","type":"monthly","tier":"core",
             "path":"core/qiongtongbj/qtbj_jia_yin.md","weight":10,"title":"正月甲木","chapter":"甲木·寅月",
             "conditions":{"day_master":["Jia"],"month_branch":["Yin"],"day_pillar":[],"hour_pillar":[],
               "ten_god":[],"pattern":[],"shensha":[],"keywords":["调候"]}},
            {"id":"zpzq_zhengguan","book":"子平真诠评注","type":"pattern","tier":"core",
             "path":"core/zipingzhenquan/zpzq_zhengguan.md","weight":10,"title":"论正官","chapter":"",
             "conditions":{"day_master":[],"month_branch":[],"day_pillar":[],"hour_pillar":[],
               "ten_god":["正官"],"pattern":["正官格"],"shensha":[],"keywords":[]}},
            {"id":"wxjj_hua","book":"五行精纪","type":"general","tier":"extended",
             "path":"extended/wuxingjingji/wxjj_hua.md","weight":3,"title":"论合化","chapter":"",
             "conditions":{"day_master":[],"month_branch":[],"day_pillar":[],"hour_pillar":[],
               "ten_god":[],"pattern":["化格"],"shensha":["十干合"],"keywords":[]}},
            {"id":"smth_rs","book":"三命通会","type":"rishi","tier":"origin-shensha",
             "path":"origin-shensha/sanmingtonghui/smth_rs.md","weight":6,"title":"庚子日己卯时","chapter":"",
             "conditions":{"day_master":[],"month_branch":[],"day_pillar":["庚子"],"hour_pillar":["己卯"],
               "ten_god":[],"pattern":[],"shensha":[],"keywords":[]}},
            {"id":"general_lun","book":"子平真诠评注","type":"general","tier":"core",
             "path":"core/zipingzhenquan/general_lun.md","weight":10,"title":"论用神","chapter":"",
             "conditions":{"day_master":[],"month_branch":[],"day_pillar":[],"hour_pillar":[],
               "ten_god":[],"pattern":[],"shensha":[],"keywords":[]}}
          ]
        }"#.to_string()
    }

    fn lib() -> Library {
        Library::from_json(&sample_manifest()).unwrap()
    }

    fn ids(chart: &Chart) -> Vec<String> {
        lib().query(chart).into_iter().map(|e| e.id.clone()).collect()
    }

    #[test]
    fn tiaohou_composite_key_requires_both() {
        let ok = ids(&Chart::new().day_master(&["Jia"]).month_branch(&["Yin"]));
        assert!(ok.contains(&"qtbj_jia_yin".to_string()));
        // 日干对、月令错：复合键组内 AND，不命中
        let bad = ids(&Chart::new().day_master(&["Jia"]).month_branch(&["Mao"]));
        assert!(!bad.contains(&"qtbj_jia_yin".to_string()));
    }

    #[test]
    fn independent_dimensions_or_across_groups() {
        // 只给 pattern 化格，条目另带 shensha 十干合，组间 OR 仍应命中
        let hit = ids(&Chart::new().pattern(&["化格"]));
        assert!(hit.contains(&"wxjj_hua".to_string()));
        // 只给 shensha 也应命中
        let hit2 = ids(&Chart::new().shensha(&["十干合"]));
        assert!(hit2.contains(&"wxjj_hua".to_string()));
    }

    #[test]
    fn rishi_composite_key() {
        let ok = ids(&Chart::new().day_pillar(&["庚子"]).hour_pillar(&["己卯"]));
        assert!(ok.contains(&"smth_rs".to_string()));
        let bad = ids(&Chart::new().day_pillar(&["庚子"]).hour_pillar(&["甲子"]));
        assert!(!bad.contains(&"smth_rs".to_string()));
    }

    #[test]
    fn general_entry_excluded_by_default_appended_when_asked() {
        let chart = Chart::new().pattern(&["正官格"]).ten_god(&["正官"]);
        // 默认严格召回：无锚点通论不制造噪声
        let strict = ids(&chart);
        assert!(!strict.contains(&"general_lun".to_string()));
        assert_eq!(strict[0], "zpzq_zhengguan"); // 精确条仍在最前
        // 显式附带通论时，通论整体沉底
        let with = lib().query_with(&chart, true).into_iter()
            .map(|e| e.id.clone()).collect::<Vec<_>>();
        assert!(with.contains(&"general_lun".to_string()));
        assert_eq!(with[0], "zpzq_zhengguan");
        assert_eq!(with[with.len() - 1], "general_lun");
    }

    #[test]
    fn empty_chart_is_silent() {
        assert!(ids(&Chart::new()).is_empty());
    }

    #[test]
    fn ordering_specificity_then_weight() {
        // 甲日寅月 + 正官格：调候条(精确度2) 应在单维格局条(精确度1) 之前
        let l = lib();
        let r = l.query(
            &Chart::new()
                .day_master(&["Jia"])
                .month_branch(&["Yin"])
                .pattern(&["正官格"]),
        );
        let order: Vec<&str> = r.iter().map(|e| e.id.as_str()).collect();
        assert_eq!(order[0], "qtbj_jia_yin");
    }

    #[test]
    fn loads_real_manifest() {
        // 真实库清单：engine/ 的上一级即库根
        let path = concat!(env!("CARGO_MANIFEST_DIR"), "/../manifest.json");
        let text = std::fs::read_to_string(path).expect("manifest.json 应存在于库根");
        let l = Library::from_json(&text).unwrap();
        assert_eq!(l.total(), 1547);
        assert_eq!(l.entries().len(), 1547);
        // 甲日寅月首条即穷通精确锚定
        let r = l.query(&Chart::new().day_master(&["Jia"]).month_branch(&["Yin"]));
        assert_eq!(r[0].id, "qtbj_jia_yin");
    }

    fn read_root(rel: &str) -> String {
        let path = concat!(env!("CARGO_MANIFEST_DIR"), "/../");
        std::fs::read_to_string(format!("{path}{rel}")).expect("golden 文件应存在")
    }

    /// 自召回不变量：每条有硬锚点的条目用自身 conditions 构造命盘必能召回自己。
    #[test]
    fn every_anchored_entry_self_recalls() {
        let text = std::fs::read_to_string(
            concat!(env!("CARGO_MANIFEST_DIR"), "/../manifest.json")).unwrap();
        let l = Library::from_json(&text).unwrap();
        let mut missing = Vec::new();
        for e in l.entries() {
            if Library::is_general(&e.conditions) {
                continue;
            }
            let c = &e.conditions;
            let chart = Chart {
                day_master: c.day_master.clone(),
                month_branch: c.month_branch.clone(),
                day_pillar: c.day_pillar.clone(),
                hour_pillar: c.hour_pillar.clone(),
                ten_god: c.ten_god.clone(),
                pattern: c.pattern.clone(),
                shensha: c.shensha.clone(),
            };
            let got: Vec<&str> = l.query(&chart).iter().map(|x| x.id.as_str()).collect();
            if !got.contains(&e.id.as_str()) {
                missing.push(e.id.clone());
            }
        }
        assert!(missing.is_empty(), "无法自召回的条目: {missing:?}");
    }

    /// 黄金对拍：Rust 结果序列必须与 Python 生成的 golden_expected.json 完全一致。
    #[test]
    fn golden_parity_with_python() {
        #[derive(Deserialize)]
        struct GoldenCases {
            cases: HashMap<String, Chart>,
        }
        let cases: GoldenCases =
            serde_json::from_str(&read_root("tests/golden_cases.json")).unwrap();
        let expected: HashMap<String, Vec<String>> =
            serde_json::from_str(&read_root("tests/golden_expected.json")).unwrap();
        assert_eq!(
            cases.cases.keys().collect::<HashSet<_>>(),
            expected.keys().collect::<HashSet<_>>(),
            "golden case 集合不一致"
        );
        let text = std::fs::read_to_string(
            concat!(env!("CARGO_MANIFEST_DIR"), "/../manifest.json")).unwrap();
        let l = Library::from_json(&text).unwrap();
        for (name, chart) in &cases.cases {
            let got: Vec<String> = l.query(chart).iter().map(|e| e.id.clone()).collect();
            let want = expected.get(name).unwrap();
            if &got != want {
                eprintln!("CASE {name}\n rust={got:?}\n py  ={want:?}");
                panic!("golden case 失配: {name}");
            }
        }
    }
}
