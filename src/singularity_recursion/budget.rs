//! Budget tracking for infinite singularity recursion.

use serde::{Deserialize, Serialize};

#[derive(Debug, Clone, Serialize, Deserialize, PartialEq)]
pub struct Budget {
    pub tick_count: u64,
    pub cpu_sec_used: u64,
    pub total_points: u64,
    // Limits
    pub max_total_points: u64,
    pub global_cpu_sec_budget: u64,
}

impl Default for Budget {
    fn default() -> Self {
        Self {
            tick_count: 0,
            cpu_sec_used: 0,
            total_points: 0,
            max_total_points: 50_000,
            global_cpu_sec_budget: 86_400,
        }
    }
}

#[derive(Debug, Clone, PartialEq)]
pub enum BudgetStatus {
    Allowed,
    ExhaustedPoints,
    ExhaustedCpu,
}

impl Budget {
    pub fn check(&self) -> BudgetStatus {
        if self.total_points >= self.max_total_points {
            return BudgetStatus::ExhaustedPoints;
        }
        if self.cpu_sec_used >= self.global_cpu_sec_budget {
            return BudgetStatus::ExhaustedCpu;
        }
        BudgetStatus::Allowed
    }

    pub fn commit_tick(&mut self, cpu_sec: u64, new_points: u64) {
        self.tick_count += 1;
        self.cpu_sec_used += cpu_sec;
        self.total_points += new_points;
    }
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn default_is_allowed() {
        let b = Budget::default();
        assert_eq!(b.check(), BudgetStatus::Allowed);
    }

    #[test]
    fn exhausted_points() {
        let mut b = Budget::default();
        b.total_points = 50_000;
        assert_eq!(b.check(), BudgetStatus::ExhaustedPoints);
    }

    #[test]
    fn exhausted_cpu() {
        let mut b = Budget::default();
        b.cpu_sec_used = 86_400;
        assert_eq!(b.check(), BudgetStatus::ExhaustedCpu);
    }

    #[test]
    fn commit_updates_all_counters() {
        let mut b = Budget::default();
        b.commit_tick(30, 1);
        assert_eq!(b.tick_count, 1);
        assert_eq!(b.cpu_sec_used, 30);
        assert_eq!(b.total_points, 1);
    }

    #[test]
    fn serde_roundtrip() {
        let b = Budget { tick_count: 5, cpu_sec_used: 100, total_points: 3, ..Default::default() };
        let json = serde_json::to_string(&b).unwrap();
        let decoded: Budget = serde_json::from_str(&json).unwrap();
        assert_eq!(b, decoded);
    }
}
