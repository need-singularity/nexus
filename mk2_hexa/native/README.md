# mk2_hexa/native — HEXA-네이티브 재설계

**mk2_hexa/ 최상단 = Rust 1:1 포팅** (레거시).
**mk2_hexa/native/ = HEXA 고유 키워드 활용 재작성**.

## 사용하는 HEXA 고유 기능

| 키워드 | 용도 |
|---|---|
| `theorem` / `proof` / `invariant` | BT-344, BT-345, BT-346 n=6 정리 |
| `pure` | 수론 함수 (phi, sigma, tau, gcd) |
| `comptime` | n=6 상수 컴파일 타임 확정 |
| `effect` / `handle` / `resume` | 파일 I/O (discovery_log, custom_lenses) |
| `where` / `ensures` | 함수 전/후 조건 |
| `verify` / `optimize` | 컴파일러 자동 검증/최적화 힌트 |
| `intent` / `generate` | AI-보조 코드 생성 (향후) |
| `match` with ranges | rank 판정 |

## 파일 구성

| 파일 | 역할 | 대응 Rust(legacy) |
|---|---|---|
| `theorems.hexa` | BT-344/345/346 + 핵심 공리 | - |
| `constants.hexa` | comptime n=6 테이블 | verifier/n6_check.rs |
| `pure_math.hexa` | pure phi/sigma/tau/gcd | mk2/smooth.rs + primes.rs |
| `effects.hexa` | FileSystem / Clock / Logger | - |
| `absorb_native.hexa` | effect 기반 writeback | alien_index_cmd.rs |
| `gate_verified.hexa` | contract 있는 12-gate | gate.hexa |
