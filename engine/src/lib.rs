//! Aether-Cycle 瀛愬钩鍛界悊鍙ょ睄鐭ヨ瘑搴?路 妫€绱㈠紩鎿庨鏋讹紙妗嗘灦鏃犲叧锛屽彲鐩存帴琚?Tauri 澶嶇敤锛?//!
//! 鍔犺浇搴撴牴 `manifest.json`锛堢敱 `scripts/build_manifest.py` 纭畾鎬х敓鎴愶級锛?//! 渚濇嵁鎺掔洏鍐呮牳浜у嚭鐨?`Chart` 鍋氱粨鏋勫寲鍙洖銆傚尮閰?/ 鎺掑簭璇箟涓?Python 鍙傝€冨疄鐜?//! `scripts/retrieve_reference.py` 涓ユ牸涓€鑷达紝骞剁敱 `tests/recall_regression.py`
//! 鍦ㄥ悓涓€鏁版嵁涓婂仛浜ゅ弶鍥炲綊锛?//!
//! - 澶嶅悎閿€滅粍鍐?AND鈥濓細璋冨€?`day_master + month_branch`銆佹棩鏃?`day_pillar + hour_pillar`
//!   蹇呴』鍚屾椂婊¤冻锛?//! - 妫€绱㈢淮搴︹€滅粍闂?OR鈥濓細`ten_god / pattern / shensha` 浜掍负骞跺垪鍙洖鐞嗙敱锛屼换涓€鍛戒腑鍗冲彲锛?//! - 鏃犱换浣曠粨鏋勫寲纭敋鐐圭殑閫氳鏉★紙搴忋€佹硾璁恒€佺函姝岃祴锛夐粯璁や笉鍙備笌鍛界洏鍙洖锛岄伩鍏嶅櫔澹帮紝
//!   浠呭湪 `query_with(.., true)` 鏃舵暣浣撻檮鍦ㄧ簿纭潯涔嬪悗锛屾垨缁忓叧閿瘝 / 涔︾洰娴忚鑾峰彇锛?//! - 鎺掑簭锛氬懡涓簿纭害锛堝０鏄庣殑闈炵┖瀛楁鏁帮級浼樺厛锛屽叾娆″吀绫嶆潈閲?weight锛屽啀娆?path 绋冲畾銆?//!
//! 鏈?crate 涓嶄緷璧?Tauri / 鍓嶇锛岀函 std + serde_json锛屼究浜庡崟娴嬩笌鐙珛婕旇繘銆?
use serde::Deserialize;

/// 鏉＄洰缁撴瀯鍖栧尮閰嶆潯浠讹紙manifest 涓瘡鏉＄殑 conditions 瀛楁锛夈€?#[derive(Debug, Clone, Default, Deserialize)]
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

/// 涓€鏉″彜绫嶆枃鐚殑妫€绱㈠厓鏁版嵁锛堟鏂囦粛鍦?path 鎸囧悜鐨?Markdown 涓紝鎸夐渶璇诲彇锛夈€?#[derive(Debug, Clone, Deserialize)]
pub struct Entry {
    pub id: String,
    pub book: String,
    #[serde(rename = "type")]
    pub kind: String,
    pub tier: String,
    #[serde(default)]
    pub category: String,
    #[serde(default)]
    pub subcategory: String,
    pub path: String,
    pub weight: i32,
    #[serde(default)]
    pub title: String,
    #[serde(default)]
    pub chapter: String,
    pub conditions: Conditions,
}

/// manifest.json 椤跺眰缁撴瀯锛堝叾浣欏瓧娈靛拷鐣ワ級銆?#[derive(Debug, Clone, Deserialize)]
pub struct Manifest {
    #[serde(default)]
    pub schema_version: u32,
    pub total: usize,
    pub entries: Vec<Entry>,
}

/// 鎺掔洏鍐呮牳浜у嚭鐨勬煡璇㈠懡鐩橈細鍙～宸茬畻鍑虹殑缁村害锛屾湭绠楀嚭鐨勭淮搴︾暀绌恒€?#[derive(Debug, Clone, Default, Deserialize)]
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

/// 姝ｆ枃涓夊眰锛氬師鏂?/ 鍙ゆ敞锛堣瘎娉?闃愬井绛夛級 / 鐧借瘽鎻愯銆?#[derive(Debug, Clone, Default)]
pub struct Body {
    pub original: String,
    pub annotation: String,
    pub vernacular: String,
}

/// 杞婚噺姝ｆ枃涓夊眰鍔犺浇鍣細璇诲彇鏉＄洰 .md锛屽幓 Frontmatter锛屾寜 `**銆?..銆?*` 鏍囪鍒囧垎銆?/// 鏈嚭鐜扮殑灞傝繑鍥炵┖涓层€備笉寮曞叆姝ｅ垯渚濊禆锛岀函瀛楃涓叉煡鎵俱€?pub fn load_body(path: &str) -> std::io::Result<Body> {
    let text = std::fs::read_to_string(path)?;
    let body = if text.starts_with("---") {
        text.splitn(3, "---").nth(2).unwrap_or(&text).to_string()
    } else {
        text
    };
    let mut original = String::new();
    let mut annotation = String::new();
    let mut vernacular = String::new();
    let mut pos = 0;
    while let Some(rel) = body[pos..].find("**銆?) {
        let abs_start = pos + rel;
        if let Some(rel_key) = body[abs_start..].find("銆?*") {
            let abs_key_end = abs_start + rel_key;
            // `**銆恅 = '*'(1) + '*'(1) + '銆?(3) = 5 bytes; `銆?*` = '銆?(3) + '*' + '*' = 5 bytes
            let key = &body[abs_start + 5..abs_key_end];
            let content_start = abs_key_end + 5;
            let next = body[content_start..]
                .find("**銆?)
                .map(|p| content_start + p)
                .unwrap_or(body.len());
            let content = body[content_start..next].trim().to_string();
            match key {
                "鍘熸枃" | "缁忔枃" | "鍘熸枃路鍙ｈ瘈" | "鍘熸枃锛堝洓搴撴彁瑕侊級" => {
                    original.push_str(&content);
                    original.push('\n');
                }
                "鐧借瘽鎻愯" => {
                    vernacular.push_str(&content);
                    vernacular.push('\n');
                }
                _ => {
                    annotation.push_str(&content);
                    annotation.push('\n');
                }
            }
            pos = next;
        } else {
            break;
        }
    }
    Ok(Body {
        original: original.trim().to_string(),
        annotation: annotation.trim().to_string(),
        vernacular: vernacular.trim().to_string(),
    })
}

/// 宸插姞杞界殑鐭ヨ瘑搴擄細涓€娆℃€ц浇鍏ュ唴瀛橈紝鏌ヨ闆?IO銆?#[derive(Debug, Clone)]
pub struct Library {
    manifest: Manifest,
}

/// 涓や釜闆嗗悎鏄惁鏈変氦闆嗐€?fn intersects(declared: &[String], chart: &[String]) -> bool {
    declared.iter().any(|d| chart.contains(d))
}

/// 璇勪及涓€涓尮閰嶉敭缁勶細杩斿洖 None 琛ㄧず璇ョ粍鏈鏉＄洰澹版槑锛汼ome(hit) 琛ㄧず缁勫唴鍏ㄩ儴
/// 宸插０鏄庡瓧娈垫槸鍚﹂兘涓庡懡鐩樼浉浜わ紙缁勫唴 AND锛夈€?fn group_hit(pairs: &[(&Vec<String>, &Vec<String>)]) -> Option<bool> {
    let declared: Vec<&(&Vec<String>, &Vec<String>)> =
        pairs.iter().filter(|(d, _)| !d.is_empty()).collect();
    if declared.is_empty() {
        return None;
    }
    Some(declared.iter().all(|(d, h)| intersects(d, h)))
}

impl Library {
    /// 浠?manifest.json 鏂囨湰瑙ｆ瀽鍔犺浇銆?    pub fn from_json(text: &str) -> Result<Self, serde_json::Error> {
        let manifest: Manifest = serde_json::from_str(text)?;
        Ok(Self { manifest })
    }

    pub fn total(&self) -> usize {
        self.manifest.total
    }

    pub fn entries(&self) -> &[Entry] {
        &self.manifest.entries
    }

    /// 鍛戒腑绮剧‘搴︼細鏉＄洰澹版槑浜嗗嚑涓潪绌虹粨鏋勫寲纭瓧娈碉紙0 = 鏃犵害鏉熼€氳鏉★級銆?    pub fn specificity(c: &Conditions) -> usize {
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

    /// 鏃犱换浣曠粨鏋勫寲纭敋鐐癸紙搴忋€佹硾璁恒€佺函姝岃祴/鍙ｈ瘈锛夛細涓嶅弬涓庣粨鏋勫寲鍛界洏鍙洖锛?    /// 鍙€氳繃鍏抽敭璇嶆垨涔︾洰娴忚鑾峰彇锛岄伩鍏嶅ぇ閲忛€氳鏉″湪姣忎竴鍛界洏涓嬫亽鍛戒腑銆佺█閲婄簿纭粨鏋溿€?    pub fn is_general(c: &Conditions) -> bool {
        c.day_master.is_empty() && c.month_branch.is_empty() && c.day_pillar.is_empty()
            && c.hour_pillar.is_empty() && c.ten_god.is_empty() && c.pattern.is_empty()
            && c.shensha.is_empty()
    }

    /// 鍗曟潯涓ユ牸鍖归厤锛氳嚦灏戜竴涓凡澹版槑鍖归厤缁勬暣浣撳懡涓紙缁勫唴 AND銆佺粍闂?OR锛夛紱
    /// 鏃犵‖閿氱偣鐨勯€氳鏉¤繑鍥?false锛屼笉娣峰叆缁撴瀯鍖栧彫鍥炪€?    pub fn matches_entry(e: &Entry, chart: &Chart) -> bool {
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

    /// 缁撴瀯鍖栧彫鍥烇紙涓ユ牸锛岄粯璁わ級锛氬彧杩斿洖鑷冲皯涓€涓‖缁村害鍛戒腑鐨勭簿纭潯銆?    pub fn query<'a>(&'a self, chart: &Chart) -> Vec<&'a Entry> {
        self.query_with(chart, false)
    }

    /// 缁撴瀯鍖栧彫鍥烇紱`include_general=true` 鏃舵妸鏃犻敋鐐归€氳鏉★紙鎸?weight鈫? path鈫戯級
    /// 鏁翠綋闄勫湪绮剧‘鏉′箣鍚庛€?    pub fn query_with<'a>(&'a self, chart: &Chart, include_general: bool) -> Vec<&'a Entry> {
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
            {"id":"qtbj_jia_yin","book":"绌烽€氬疂閴?,"type":"monthly","tier":"core",
             "path":"core/qiongtongbj/qtbj_jia_yin.md","weight":10,"title":"姝ｆ湀鐢叉湪","chapter":"鐢叉湪路瀵呮湀",
             "conditions":{"day_master":["Jia"],"month_branch":["Yin"],"day_pillar":[],"hour_pillar":[],
               "ten_god":[],"pattern":[],"shensha":[],"keywords":["璋冨€?]}},
            {"id":"zpzq_zhengguan","book":"瀛愬钩鐪熻癄璇勬敞","type":"pattern","tier":"core",
             "path":"core/zipingzhenquan/zpzq_zhengguan.md","weight":10,"title":"璁烘瀹?,"chapter":"",
             "conditions":{"day_master":[],"month_branch":[],"day_pillar":[],"hour_pillar":[],
               "ten_god":["姝ｅ畼"],"pattern":["姝ｅ畼鏍?],"shensha":[],"keywords":[]}},
            {"id":"wxjj_hua","book":"浜旇绮剧邯","type":"general","tier":"extended",
             "path":"extended/wuxingjingji/wxjj_hua.md","weight":3,"title":"璁哄悎鍖?,"chapter":"",
             "conditions":{"day_master":[],"month_branch":[],"day_pillar":[],"hour_pillar":[],
               "ten_god":[],"pattern":["鍖栨牸"],"shensha":["鍗佸共鍚?],"keywords":[]}},
            {"id":"smth_rs","book":"涓夊懡閫氫細","type":"rishi","tier":"origin-shensha",
             "path":"origin-shensha/sanmingtonghui/smth_rs.md","weight":6,"title":"搴氬瓙鏃ュ繁鍗椂","chapter":"",
             "conditions":{"day_master":[],"month_branch":[],"day_pillar":["搴氬瓙"],"hour_pillar":["宸卞嵂"],
               "ten_god":[],"pattern":[],"shensha":[],"keywords":[]}},
            {"id":"general_lun","book":"瀛愬钩鐪熻癄璇勬敞","type":"general","tier":"core",
             "path":"core/zipingzhenquan/general_lun.md","weight":10,"title":"璁虹敤绁?,"chapter":"",
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
        // 鏃ュ共瀵广€佹湀浠ら敊锛氬鍚堥敭缁勫唴 AND锛屼笉鍛戒腑
        let bad = ids(&Chart::new().day_master(&["Jia"]).month_branch(&["Mao"]));
        assert!(!bad.contains(&"qtbj_jia_yin".to_string()));
    }

    #[test]
    fn independent_dimensions_or_across_groups() {
        // 鍙粰 pattern 鍖栨牸锛屾潯鐩彟甯?shensha 鍗佸共鍚堬紝缁勯棿 OR 浠嶅簲鍛戒腑
        let hit = ids(&Chart::new().pattern(&["鍖栨牸"]));
        assert!(hit.contains(&"wxjj_hua".to_string()));
        // 鍙粰 shensha 涔熷簲鍛戒腑
        let hit2 = ids(&Chart::new().shensha(&["鍗佸共鍚?]));
        assert!(hit2.contains(&"wxjj_hua".to_string()));
    }

    #[test]
    fn rishi_composite_key() {
        let ok = ids(&Chart::new().day_pillar(&["搴氬瓙"]).hour_pillar(&["宸卞嵂"]));
        assert!(ok.contains(&"smth_rs".to_string()));
        let bad = ids(&Chart::new().day_pillar(&["搴氬瓙"]).hour_pillar(&["鐢插瓙"]));
        assert!(!bad.contains(&"smth_rs".to_string()));
    }

    #[test]
    fn general_entry_excluded_by_default_appended_when_asked() {
        let chart = Chart::new().pattern(&["姝ｅ畼鏍?]).ten_god(&["姝ｅ畼"]);
        // 榛樿涓ユ牸鍙洖锛氭棤閿氱偣閫氳涓嶅埗閫犲櫔澹?        let strict = ids(&chart);
        assert!(!strict.contains(&"general_lun".to_string()));
        assert_eq!(strict[0], "zpzq_zhengguan"); // 绮剧‘鏉′粛鍦ㄦ渶鍓?        // 鏄惧紡闄勫甫閫氳鏃讹紝閫氳鏁翠綋娌夊簳
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
        // 鐢叉棩瀵呮湀 + 姝ｅ畼鏍硷細璋冨€欐潯(绮剧‘搴?) 搴斿湪鍗曠淮鏍煎眬鏉?绮剧‘搴?) 涔嬪墠
        let l = lib();
        let r = l.query(
            &Chart::new()
                .day_master(&["Jia"])
                .month_branch(&["Yin"])
                .pattern(&["姝ｅ畼鏍?]),
        );
        let order: Vec<&str> = r.iter().map(|e| e.id.as_str()).collect();
        assert_eq!(order[0], "qtbj_jia_yin");
    }

    #[test]
    fn loads_real_manifest() {
        // 鐪熷疄搴撴竻鍗曪細engine/ 鐨勪笂涓€绾у嵆搴撴牴
        let path = concat!(env!("CARGO_MANIFEST_DIR"), "/../manifest.json");
        let text = std::fs::read_to_string(path).expect("manifest.json 搴斿瓨鍦ㄤ簬搴撴牴");
        let l = Library::from_json(&text).unwrap();
        assert_eq!(l.total(), 4724);
        assert_eq!(l.entries().len(), 4724);
        // 鐢叉棩瀵呮湀棣栨潯鍗崇┓閫氱簿纭敋瀹?        let r = l.query(&Chart::new().day_master(&["Jia"]).month_branch(&["Yin"]));
        assert_eq!(r[0].id, "qtbj_jia_yin");
    }

    fn read_root(rel: &str) -> String {
        let path = concat!(env!("CARGO_MANIFEST_DIR"), "/../");
        std::fs::read_to_string(format!("{path}{rel}")).expect("golden 鏂囦欢搴斿瓨鍦?)
    }

    /// 姝ｆ枃涓夊眰鍔犺浇鍣細璇荤湡瀹炴潯鐩紝楠岃瘉鍘熸枃/鐧借瘽闈炵┖銆?    #[test]
    fn load_body_splits_three_layers() {
        let path = concat!(env!("CARGO_MANIFEST_DIR"),
            "/../library/ming/bazi/core/qiongtongbj/qtbj_jia_yin.md");
        let b = load_body(path).expect("qtbj_jia_yin.md 搴斿瓨鍦?);
        assert!(!b.original.is_empty(), "鍘熸枃灞備笉搴斾负绌?);
        assert!(!b.vernacular.is_empty(), "鐧借瘽灞備笉搴斾负绌?);
        assert!(b.original.contains("姝ｆ湀鐢叉湪"));
    }

    /// 鑷彫鍥炰笉鍙橀噺锛氭瘡鏉℃湁纭敋鐐圭殑鏉＄洰鐢ㄨ嚜韬?conditions 鏋勯€犲懡鐩樺繀鑳藉彫鍥炶嚜宸便€?    #[test]
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
        assert!(missing.is_empty(), "鏃犳硶鑷彫鍥炵殑鏉＄洰: {missing:?}");
    }

    /// 榛勯噾瀵规媿锛歊ust 缁撴灉搴忓垪蹇呴』涓?Python 鐢熸垚鐨?golden_expected.json 瀹屽叏涓€鑷淬€?    #[test]
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
            "golden case 闆嗗悎涓嶄竴鑷?
        );
        let text = std::fs::read_to_string(
            concat!(env!("CARGO_MANIFEST_DIR"), "/../manifest.json")).unwrap();
        let l = Library::from_json(&text).unwrap();
        for (name, chart) in &cases.cases {
            let got: Vec<String> = l.query(chart).iter().map(|e| e.id.clone()).collect();
            let want = expected.get(name).unwrap();
            if &got != want {
                eprintln!("CASE {name}\n rust={got:?}\n py  ={want:?}");
                panic!("golden case 澶遍厤: {name}");
            }
        }
    }
}

