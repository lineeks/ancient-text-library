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
//! - 条目未声明任何结构化硬条件时视为无约束通论条，恒可召回；
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
#[derive(Debug, Clone, Default)]
pub struct Chart {
    pub day_master: Vec<String>,
    pub month_branch: Vec<String>,
    pub day_pillar: Vec<String>,
    pub hour_pillar: Vec<String>,
    pub ten_god: Vec<String>,
    pub pattern: Vec<String>,
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

    /// 单条匹配：组内 AND、组间 OR；未声明任何硬字段的通论条恒命中。
    pub fn matches_entry(e: &Entry, chart: &Chart) -> bool {
        let c = &e.conditions;
        let mut declared_any = false;
        let mut any_group_hit = false;

        let groups: [Vec<(&Vec<String>, &Vec<String>)>; 5] = [
            vec![(&c.day_master, &chart.day_master), (&c.month_branch, &chart.month_branch)],
            vec![(&c.day_pillar, &chart.day_pillar), (&c.hour_pillar, &chart.hour_pillar)],
            vec![(&c.ten_god, &chart.ten_god)],
            vec![(&c.pattern, &chart.pattern)],
            vec![(&c.shensha, &chart.shensha)],
        ];
        for g in groups.iter() {
            if let Some(hit) = group_hit(g) {
                declared_any = true;
                if hit {
                    any_group_hit = true;
                }
            }
        }
        !declared_any || any_group_hit
    }

    /// 结构化召回，返回按（精确度↓, weight↓, path↑）排序的命中条目引用。
    pub fn query<'a>(&'a self, chart: &Chart) -> Vec<&'a Entry> {
        let mut hits: Vec<&Entry> = self
            .manifest
            .entries
            .iter()
            .filter(|e| Self::matches_entry(e, chart))
            .collect();
        hits.sort_by(|a, b| {
            let sa = Self::specificity(&a.conditions);
            let sb = Self::specificity(&b.conditions);
            sb.cmp(&sa)
                .then_with(|| b.weight.cmp(&a.weight))
                .then_with(|| a.path.cmp(&b.path))
        });
        hits
    }
}

#[cfg(test)]
mod tests {
    use super::*;

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
    fn general_entry_always_recalled_but_sinks() {
        let r = ids(&Chart::new().pattern(&["正官格"]).ten_god(&["正官"]));
        assert!(r.contains(&"general_lun".to_string())); // 无约束通论恒召回
        assert_eq!(r[0], "zpzq_zhengguan"); // 精确条在通论之前
        assert_eq!(r[r.len() - 1], "general_lun"); // 通论沉底
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
}
