//! Topology graph: points (singularities) + edges (proximity).
//!
//! topology.jsonl and edges.jsonl are append-only, source of truth.

use std::fs::OpenOptions;
use std::io::{BufRead, BufReader, Write};
use std::path::Path;

use serde::{Deserialize, Serialize};

use super::embedding::{distance, simhash, to_vector};

#[derive(Debug, Clone, Serialize, Deserialize, PartialEq)]
pub struct Singularity {
    pub invariant: String,
    pub confidence: f64,
    pub novelty: f64,
    pub depth_reached: usize,
}

#[derive(Debug, Clone, Serialize, Deserialize, PartialEq)]
pub struct Point {
    pub id: String,
    pub domain: String,
    pub seed_from: Option<String>,
    pub simhash: String,         // 32-char hex of u128
    pub embedding: [f32; 16],
    pub singularity: Singularity,
    pub discovered_at_tick: u64,
    pub ts: String,
}

#[derive(Debug, Clone, Serialize, Deserialize, PartialEq)]
pub struct Edge {
    pub from: String,
    pub to: String,
    pub distance: f32,
    pub ts: String,
}

pub struct Topology {
    pub points: Vec<Point>,
    pub edges: Vec<Edge>,
    pub eps: f32,
}

impl Topology {
    pub fn new(eps: f32) -> Self {
        Self { points: Vec::new(), edges: Vec::new(), eps }
    }

    pub fn next_id(&self) -> String {
        format!("p_{:06}", self.points.len())
    }

    /// Create a Point from a Singularity, computing embedding.
    pub fn make_point(
        &self,
        domain: &str,
        seed_from: Option<String>,
        sing: Singularity,
        tick: u64,
        ts: &str,
    ) -> Point {
        let h = simhash(&sing.invariant);
        Point {
            id: self.next_id(),
            domain: domain.to_string(),
            seed_from,
            simhash: format!("{:032x}", h),
            embedding: to_vector(h),
            singularity: sing,
            discovered_at_tick: tick,
            ts: ts.to_string(),
        }
    }

    /// Append point to in-memory state and compute edges to existing points.
    pub fn insert_point(&mut self, p: Point, ts: &str) -> Vec<Edge> {
        let h_new = u128::from_str_radix(&p.simhash, 16).unwrap_or(0);
        let mut new_edges = Vec::new();
        for existing in &self.points {
            let h_ex = u128::from_str_radix(&existing.simhash, 16).unwrap_or(0);
            let d = distance(h_new, h_ex);
            if d <= self.eps {
                new_edges.push(Edge {
                    from: p.id.clone(),
                    to: existing.id.clone(),
                    distance: d,
                    ts: ts.to_string(),
                });
            }
        }
        self.edges.extend(new_edges.iter().cloned());
        self.points.push(p);
        new_edges
    }

    /// Neighbors of a point id (symmetric edge lookup).
    pub fn neighbors(&self, id: &str) -> Vec<&str> {
        self.edges.iter()
            .filter_map(|e| {
                if e.from == id { Some(e.to.as_str()) }
                else if e.to == id { Some(e.from.as_str()) }
                else { None }
            })
            .collect()
    }
}

/// Append a point to topology.jsonl with fsync.
pub fn append_point(path: &Path, p: &Point) -> std::io::Result<()> {
    let mut f = OpenOptions::new().create(true).append(true).open(path)?;
    let line = serde_json::to_string(p)
        .map_err(|e| std::io::Error::new(std::io::ErrorKind::InvalidData, e))?;
    writeln!(f, "{}", line)?;
    f.sync_all()?;
    Ok(())
}

/// Append an edge with fsync.
pub fn append_edge(path: &Path, e: &Edge) -> std::io::Result<()> {
    let mut f = OpenOptions::new().create(true).append(true).open(path)?;
    let line = serde_json::to_string(e)
        .map_err(|err| std::io::Error::new(std::io::ErrorKind::InvalidData, err))?;
    writeln!(f, "{}", line)?;
    f.sync_all()?;
    Ok(())
}

/// Load topology from jsonl files (source of truth).
pub fn load(points_path: &Path, edges_path: &Path, eps: f32) -> std::io::Result<Topology> {
    let mut t = Topology::new(eps);
    if points_path.exists() {
        let f = std::fs::File::open(points_path)?;
        for line in BufReader::new(f).lines() {
            let line = line?;
            if line.trim().is_empty() { continue; }
            if let Ok(p) = serde_json::from_str::<Point>(&line) {
                t.points.push(p);
            }
        }
    }
    if edges_path.exists() {
        let f = std::fs::File::open(edges_path)?;
        for line in BufReader::new(f).lines() {
            let line = line?;
            if line.trim().is_empty() { continue; }
            if let Ok(e) = serde_json::from_str::<Edge>(&line) {
                t.edges.push(e);
            }
        }
    }
    Ok(t)
}

#[cfg(test)]
mod tests {
    use super::*;
    use std::env::temp_dir;

    fn tmp_dir(name: &str) -> std::path::PathBuf {
        let mut p = temp_dir();
        p.push(format!("nexus6_topo_{}_{}", name, std::process::id()));
        let _ = std::fs::remove_dir_all(&p);
        std::fs::create_dir_all(&p).unwrap();
        p
    }

    fn sing(s: &str) -> Singularity {
        Singularity { invariant: s.into(), confidence: 0.5, novelty: 0.7, depth_reached: 3 }
    }

    #[test]
    fn make_point_populates_embedding() {
        let t = Topology::new(0.3);
        let p = t.make_point("arch", None, sing("a b c"), 1, "t");
        assert_eq!(p.id, "p_000000");
        assert_eq!(p.simhash.len(), 32);
    }

    #[test]
    fn insert_creates_edges_for_similar_points() {
        let mut t = Topology::new(0.5);
        let p1 = t.make_point("arch", None, sing("alpha bravo charlie"), 1, "t");
        t.insert_point(p1, "t");
        let p2 = t.make_point("arch", Some("p_000000".into()), sing("alpha bravo delta"), 2, "t");
        let edges = t.insert_point(p2, "t");
        assert!(!edges.is_empty(), "expected edge between similar points");
    }

    #[test]
    fn insert_no_edges_for_different() {
        let mut t = Topology::new(0.1);
        let p1 = t.make_point("arch", None, sing("banana quantum"), 1, "t");
        t.insert_point(p1, "t");
        let p2 = t.make_point("arch", None, sing("fourier transform lock"), 2, "t");
        let edges = t.insert_point(p2, "t");
        assert!(edges.is_empty(), "expected no edges for distant points");
    }

    #[test]
    fn append_and_load_roundtrip() {
        let d = tmp_dir("roundtrip");
        let points_path = d.join("topology.jsonl");
        let edges_path = d.join("edges.jsonl");
        let mut t = Topology::new(0.5);
        let p1 = t.make_point("arch", None, sing("alpha bravo"), 1, "t");
        let p1c = p1.clone();
        t.insert_point(p1, "t");
        append_point(&points_path, &p1c).unwrap();
        let loaded = load(&points_path, &edges_path, 0.5).unwrap();
        assert_eq!(loaded.points.len(), 1);
        assert_eq!(loaded.points[0].id, "p_000000");
        std::fs::remove_dir_all(&d).ok();
    }

    #[test]
    fn neighbors_symmetric() {
        let mut t = Topology::new(0.5);
        let p1 = t.make_point("arch", None, sing("alpha bravo charlie"), 1, "t");
        t.insert_point(p1, "t");
        let p2 = t.make_point("arch", None, sing("alpha bravo delta"), 2, "t");
        t.insert_point(p2, "t");
        let n1 = t.neighbors("p_000000");
        let n2 = t.neighbors("p_000001");
        assert!(n1.contains(&"p_000001"));
        assert!(n2.contains(&"p_000000"));
    }
}
