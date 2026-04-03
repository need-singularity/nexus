# Calculator Development Rules (All Repos)

> 이 파일은 TECS-L family 전체 리포에서 공유하는 계산기 개발 규칙입니다.
> 모든 리포의 CLAUDE.md에서 이 파일을 참조하세요.
> 소스 경로: `~/Dev/TECS-L/.shared/CALCULATOR_RULES.md`

---

## 언어 우선순위 (Language Priority)

### 1순위: Rust — 성능 문제 예상시 반드시 Rust 우선

적용 기준:
- 반복 > 10,000회
- 실행 시간 > 10초 예상
- 조합 공간 > 10^6
- Monte Carlo 샘플 > 100,000
- Grid scan, brute-force search, 행렬 연산
- 대규모 데이터 파싱/변환

Rust 프로젝트 구조 (리포별):
```
  TECS-L:           tecsrs/src/*.rs + Cargo.toml (cargo build --release)
  n6-architecture:  tools/<name>/main.rs (rustc main.rs -o <name>)
  anima:            tools/<name>/main.rs (rustc)
  SEDI:             rust/<name>/main.rs (rustc)
```

빌드 규칙:
```
  # Cargo 프로젝트 (TECS-L)
  cd tecsrs && cargo build --release && cargo run --release -- <args>

  # 단일 파일 (n6-architecture 등)
  rustc tools/<name>/main.rs -o tools/<name>/<name>
  # rustc 경로: ~/.cargo/bin/rustc
```

### 2순위: Python — 단순 검증, 시각화, 프로토타입

적용 기준:
- 단일 공식 평가, 오차 계산, 테이블 출력
- 외부 데이터 fetch, API 호출
- NumPy/SciPy로 충분한 경우
- 빠른 프로토타입 (이후 Rust 포팅 고려)
- 시각화/matplotlib 필요시

---

## 판단 플로우차트

```
  새 계산기 필요?
    ├─ 반복 > 10K or 실행 > 10s or 조합 > 10^6?
    │   └─ YES → Rust 우선 개발
    │         ├─ TECS-L: tecsrs/ (cargo)
    │         └─ 기타 리포: tools/<name>/main.rs (rustc)
    └─ NO → Python 개발
          ├─ TECS-L: calc/<name>.py
          ├─ n6-architecture: tools/<name>.py
          └─ 기타: tools/<name>.py
```

---

## 계산기 레지스트리 동기화

모든 계산기는 자동 스캔됩니다:
```bash
  cd ~/Dev/TECS-L
  python3 .shared/scan-calculators.py          # 스캔 (JSON 출력)
  bash .shared/sync-calculators.sh             # README 동기화
```

지원 파일 형식:
- `*.py` — Python 계산기 (docstring에서 설명 추출)
- `**/main.rs` — Rust 계산기 (`///` doc 주석에서 설명 추출)

Rust `main.rs` 파일은 부모 디렉토리명이 계산기 이름이 됩니다:
```
  tools/gpu-arch-calc/main.rs  →  이름: "gpu-arch-calc"
  tools/energy-calc/main.rs    →  이름: "energy-calc"
```

---

## Rust 계산기 작성 템플릿

```rust
/// Calculator Name — One-line description for registry
/// ====================================================
/// Detailed description here.
///
/// Build: rustc main.rs -o <name>
/// Usage: ./<name> [--flag1] [--flag2] [--all]

use std::env;

fn main() {
    let args: Vec<String> = env::args().collect();
    // ... implementation
}
```

## Python 계산기 작성 템플릿

```python
#!/usr/bin/env python3
"""Calculator Name — One-line description for registry.

Usage:
  python tools/<name>.py [--flag1] [--flag2]
"""
```

---

## 현재 Rust 계산기 목록 (2026-03-31)

| 리포 | 이름 | 설명 |
|------|------|------|
| TECS-L | tecsrs/ (cargo) | 통합 Rust 엔진 (search, monte_carlo, grid, sieves) |
| n6-architecture | gpu-arch-calc | GPU/HBM 아키텍처 검증 + Rubin 예측 |
| n6-architecture | energy-calc | 태양전지/배터리/수소/IEEE519 에너지 검증 |
| n6-architecture | fusion-calc | KSTAR/ITER/SPARC 핵융합 파라미터 |
| n6-architecture | tokamak-shape | 토카막 형상 최적화 + N6 스코어 |
| n6-architecture | optics-calc | 렌즈/망원경/토카막 진단 광학 |
| n6-architecture | gut-calc-rust | GUT 통합이론 파라미터 brute-force |
