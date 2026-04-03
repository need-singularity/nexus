// Phase 6: Markdown hypothesis parser — atlas scanning
// 3-10x speedup over Python regex-per-file parsing

use pyo3::prelude::*;
use pyo3::types::{PyDict, PyList};
use regex::Regex;
use rayon::prelude::*;
use std::path::Path;

/// Grade emoji characters to detect
const GRADE_EMOJIS: &[&str] = &[
    "\u{2B50}", // ⭐
    "\u{1F7E9}", // 🟩
    "\u{1F7E7}", // 🟧
    "\u{1F7E6}", // 🟦
    "\u{1F7E8}", // 🟨
    "\u{1F7E5}", // 🟥
    "\u{1F7EA}", // 🟪
    "\u{26AA}", // ⚪
    "\u{2B1B}", // ⬛
    "\u{2705}", // ✅
    "\u{274C}", // ❌
];

/// Parsed hypothesis metadata (Rust side)
#[derive(Clone, Debug)]
struct HypMeta {
    id: String,
    title: String,
    repo: String,
    domain: Option<String>,
    grade: Option<String>,
    refs: Vec<String>,
    gz_dep: Option<bool>,
    file: String,
}

/// Extract grade from text
fn extract_grade(text: &str) -> Option<String> {
    // Check YAML grade field
    let re_grade = Regex::new(r"(?m)^grade:\s*(.+)$").unwrap();
    if let Some(cap) = re_grade.captures(text) {
        let g = cap[1].trim().to_string();
        if !g.is_empty() { return Some(g); }
    }

    // Check ## Grade: line
    let re_grade2 = Regex::new(r"(?m)^##\s*Grade:\s*(.+)$").unwrap();
    if let Some(cap) = re_grade2.captures(text) {
        return Some(cap[1].trim().to_string());
    }

    // Check **Grade:** or **Status:** line
    let re_grade3 = Regex::new(r"(?m)\*\*(?:Grade|Status|grade|status)\*\*[:\s]+(.+)$").unwrap();
    if let Some(cap) = re_grade3.captures(text) {
        return Some(cap[1].trim().to_string());
    }

    // Check for grade emoji in first few lines
    let first_lines: String = text.lines().take(5).collect::<Vec<_>>().join(" ");
    let mut emojis = String::new();
    for &emoji in GRADE_EMOJIS {
        if first_lines.contains(emoji) {
            emojis.push_str(emoji);
        }
    }
    if !emojis.is_empty() { return Some(emojis); }

    None
}

/// Extract domain from hypothesis ID (H-XX-NNN -> XX)
fn extract_domain(id: &str) -> Option<String> {
    let re = Regex::new(r"H-([A-Z]+)-\d+").unwrap();
    re.captures(id).map(|c| c[1].to_string())
}

/// Extract references from text
fn extract_refs(text: &str) -> Vec<String> {
    let mut refs = Vec::new();
    let re_paren = Regex::new(r"\(H-[A-Z]+-\d+\)").unwrap();
    for cap in re_paren.find_iter(text) {
        let r = cap.as_str().trim_matches(|c| c == '(' || c == ')').to_string();
        if !refs.contains(&r) { refs.push(r); }
    }

    let re_related = Regex::new(r"(?i)related.*?:\s*(.+)").unwrap();
    if let Some(cap) = re_related.captures(text) {
        let re_num = Regex::new(r"\b(\d{3,})\b").unwrap();
        for num in re_num.find_iter(&cap[1]) {
            let r = num.as_str().to_string();
            if !refs.contains(&r) { refs.push(r); }
        }
    }

    refs
}

/// Extract GZ dependency
fn extract_gz_dep(text: &str) -> Option<bool> {
    let re = Regex::new(r"(?i)\*\*Golden\s*Zone\s*dependency\*\*[:\s]+(YES|NO|NONE|true|false)").unwrap();
    re.captures(text).map(|c| {
        let val = c[1].to_uppercase();
        val == "YES" || val == "TRUE"
    })
}

/// Extract hypothesis ID and title from first heading
fn extract_id_title(text: &str) -> (String, String) {
    let patterns = [
        Regex::new(r"(?m)^#\s+(?:Hypothesis\s+Review\s+)?(\d{3})[:\s]+(.+)$").unwrap(),
        Regex::new(r"(?m)^#\s+(H-[A-Z]+-\d+)[:\s]+(.+)$").unwrap(),
        Regex::new(r"(?m)^#\s+(?:Frontier\s+)?(\d{3})[:\s]+(.+)$").unwrap(),
    ];

    for re in &patterns {
        if let Some(cap) = re.captures(text) {
            return (cap[1].to_string(), cap[2].trim().to_string());
        }
    }

    // Fallback: first heading
    let re_h1 = Regex::new(r"(?m)^#\s+(.+)$").unwrap();
    if let Some(cap) = re_h1.captures(text) {
        return ("???".to_string(), cap[1].trim().to_string());
    }

    ("???".to_string(), "Untitled".to_string())
}

/// Parse a single hypothesis markdown file
fn parse_hypothesis(text: &str, repo: &str, filepath: &str) -> HypMeta {
    let (id, title) = extract_id_title(text);
    let domain = extract_domain(&id);
    let grade = extract_grade(text);
    let refs = extract_refs(text);
    let gz_dep = extract_gz_dep(text);

    HypMeta {
        id,
        title,
        repo: repo.to_string(),
        domain,
        grade,
        refs,
        gz_dep,
        file: filepath.to_string(),
    }
}

// ─── Python bindings ────────────────────────────────────────────

/// Scan a directory of markdown files and return parsed metadata
#[pyfunction]
pub fn scan_hypotheses(py: Python<'_>, dir_path: &str, repo: &str) -> PyResult<Py<PyAny>> {
    let dir = Path::new(dir_path);
    if !dir.exists() {
        return Err(pyo3::exceptions::PyValueError::new_err(
            format!("Directory not found: {dir_path}")
        ));
    }

    // Collect all .md files
    let mut md_files: Vec<String> = Vec::new();
    if let Ok(entries) = std::fs::read_dir(dir) {
        for entry in entries.flatten() {
            let path = entry.path();
            if path.extension().and_then(|e| e.to_str()) == Some("md") {
                if let Some(p) = path.to_str() {
                    md_files.push(p.to_string());
                }
            }
        }
    }

    // Parse in parallel
    let results: Vec<HypMeta> = md_files.par_iter().filter_map(|path| {
        let text = std::fs::read_to_string(path).ok()?;
        let rel = Path::new(path)
            .strip_prefix(dir)
            .map(|p| p.to_string_lossy().to_string())
            .unwrap_or_else(|_| path.clone());
        Some(parse_hypothesis(&text, repo, &rel))
    }).collect();

    // Convert to Python list of dicts
    let list = PyList::empty(py);
    for h in &results {
        let dict = PyDict::new(py);
        dict.set_item("id", &h.id)?;
        dict.set_item("title", &h.title)?;
        dict.set_item("repo", &h.repo)?;
        dict.set_item("domain", &h.domain)?;
        dict.set_item("grade", &h.grade)?;
        dict.set_item("refs", &h.refs)?;
        dict.set_item("gz_dep", &h.gz_dep)?;
        dict.set_item("file", &h.file)?;
        list.append(dict)?;
    }
    Ok(list.into_any().unbind())
}

/// Batch scan multiple directories (for multi-repo scanning)
#[pyfunction]
pub fn scan_multi_repo(py: Python<'_>, repos: Vec<(String, String)>) -> PyResult<Py<PyAny>> {
    // repos: Vec<(repo_name, dir_path)>
    let all_results: Vec<(String, Vec<HypMeta>)> = repos.par_iter().filter_map(|(name, dir_path)| {
        let dir = Path::new(dir_path);
        if !dir.exists() { return None; }

        let mut md_files: Vec<String> = Vec::new();
        if let Ok(entries) = std::fs::read_dir(dir) {
            for entry in entries.flatten() {
                let path = entry.path();
                if path.extension().and_then(|e| e.to_str()) == Some("md") {
                    if let Some(p) = path.to_str() {
                        md_files.push(p.to_string());
                    }
                }
            }
        }

        let results: Vec<HypMeta> = md_files.iter().filter_map(|path| {
            let text = std::fs::read_to_string(path).ok()?;
            let rel = Path::new(path)
                .strip_prefix(dir)
                .map(|p| p.to_string_lossy().to_string())
                .unwrap_or_else(|_| path.clone());
            Some(parse_hypothesis(&text, name, &rel))
        }).collect();

        Some((name.clone(), results))
    }).collect();

    let dict = PyDict::new(py);
    for (repo, results) in &all_results {
        let list = PyList::empty(py);
        for h in results {
            let d = PyDict::new(py);
            d.set_item("id", &h.id)?;
            d.set_item("title", &h.title)?;
            d.set_item("repo", &h.repo)?;
            d.set_item("domain", &h.domain)?;
            d.set_item("grade", &h.grade)?;
            d.set_item("refs", &h.refs)?;
            d.set_item("gz_dep", &h.gz_dep)?;
            d.set_item("file", &h.file)?;
            list.append(d)?;
        }
        dict.set_item(repo, list)?;
    }
    Ok(dict.into_any().unbind())
}

/// Extract grade from text (standalone function)
#[pyfunction]
pub fn parse_grade(text: &str) -> Option<String> {
    extract_grade(text)
}

/// Extract references from text (standalone function)
#[pyfunction]
pub fn parse_refs(text: &str) -> Vec<String> {
    extract_refs(text)
}
