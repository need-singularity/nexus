# E11 — Engine Daemon Design (blowup REPL amortization)

**status**: design (impl 제외)
**date**: 2026-04-21
**scope**: `shared/blowup/**` + `nexus drill` wrapper
**milestone**: E11 (4-phase rollout)
**commit**: `design(engine): E11 engine daemon REPL — 4-phase rollout`

---

## 1. Problem statement

현재 `nexus drill` 은 단일 seed 파이프라인을 다음과 같이 구성한다:

```
drill 1 seed
 ├── stage 1: smash            (hexa run blowup.hexa …)          ← interpreter init
 ├── stage 2: free             (hexa run compose.hexa …)         ← interpreter init
 ├── stage 3: absolute         (hexa run blowup_absolute.hexa …) ← interpreter init
 ├── stage 4: meta-closure     (hexa run mk10 meta-closure)      ← interpreter init
 ├── stage 5: hyperarithmetic  (hexa run mk9 hyperarith)         ← interpreter init
 └── stage 6: resonance/Mk.X   (hexa run mkx_engine.hexa)        ← interpreter init
```

- 6 stage × N round × (seed 마다) 반복 → `hexa run …` 이 매 단계 신규 프로세스로 기동
- 각 `hexa run` 은 아래를 반복 수행한다 (이하 "cold start" 이라 부른다):
  - `hexa stage0` 인터프리터 부트스트랩 (AST, symbol table, stdlib)
  - `atlas.n6` 로드 (nodes/edges, 현재 수만 라인)
  - lens registry 로드 (`shared/config/lens_registry.json`)
  - engine registry 로드 (`shared/config/engine_registry.json`)
  - ouroboros/seed/compose 전이 테이블 초기화
- 실측(로그 기반 근사): cold start 은 stage 당 2~5 s 소요.
- drill 1회 = 6 stage × 최소 1 round = **6 interpreter init**.
  rounds=3, seed_batch=1 이면 **18 init**, seed_batch=5 이면 **30 init**.
- seed_batch N=7 (millennium) × rounds=3 = **126 init** (실 최악).

이 반복 cold start 는 drill wall-time 의 지배적 오버헤드가 된다
(컴퓨팅 자체는 중복 초기화 후의 순수 돌파 로직보다 빠르게 끝나는 경우가 많음).

### 문제 정의

> "cold start per stage" 를 "cold start per drill session (1 회)" 로 amortize 한다.

---

## 2. Design: `blowup_daemon.hexa` REPL

### 2.1. 기본 구조

```
blowup_daemon.hexa
 ├── on_boot():
 │    - atlas.n6 로드      (1 회)
 │    - lens registry 로드 (1 회)
 │    - engine registry   (1 회)
 │    - ouroboros init    (1 회)
 │    - announce READY
 ├── loop:
 │    line = stdin.readline()
 │    (cmd, seed, depth, flags) = parse(line)
 │    try:
 │      state.reset_round()
 │      result = dispatch(cmd, seed, depth, flags)
 │      emit("OK\t" + result.round_new + "\t" + json(result))
 │    catch e:
 │      emit("ERR\t" + e.reason)
 │    if idle > 600s: break
 └── on_exit(): flush atlas writes, release locks
```

### 2.2. stdin protocol (line-based, TAB-separated)

```
<cmd>\t<seed>\t<depth>\t<flags_json>\n
```

- `cmd` ∈ { `smash`, `free`, `absolute`, `meta`, `hyper`, `resonance`, `ping`, `quit` }
- `seed` = underscore/공백 없는 seed 문자열 (quoting 불필요)
- `depth` = 정수 (1~7; 기본 3)
- `flags_json` = 선택, JSON object (예: `{"engine":"mk10","fast":true}`); 생략 시 `{}`

예시:
```
smash\tmath_lattice_gauge_holonomy\t3\t{}
free\tphysics_quantum_entanglement\t3\t{"dfs":3}
meta\tmath_prime_gap\t3\t{}
ping\t\t\t{}
quit\t\t\t{}
```

### 2.3. stdout protocol

성공:
```
OK\t<round_new>\t<metrics_json>\n
```
- `round_new`: 해당 호출로 새로 확정된 라운드 id (예: `r_2026_04_21_0034`)
- `metrics_json`: `{"smash":N, "free":M, "absolute":K, "ms":T, "lens_consensus":C, ...}`

실패:
```
ERR\t<reason>\n
```
- `reason`: `state_corrupt|atlas_lock|depth_out_of_range|unknown_cmd|timeout|seed_empty` …

준비/상태:
```
READY\t<pid>\t<boot_ms>\n            (boot 직후 1회)
PONG\t<idle_s>\t<served>\n           (ping 응답)
BYE\n                                (quit 또는 idle-exit)
```

### 2.4. lifetime 정책

- idle timeout: **600 s** (마지막 stdin 이벤트 이후) → 자발적 `BYE` + exit 0.
- SIGTERM 수신: graceful — 진행 중 round 완료 → atlas flush → `BYE` → exit 0.
- SIGKILL: atlas lock 파일 stale 가능 → bootstrap 에서 stale-lock 감지/정리.
- max lifetime: 12 h 하드 컷 (누적 state leak 방어).

---

## 3. Bootstrap & control plane

### 3.1. 명령

| 명령 | 동작 |
|---|---|
| `nexus daemon start` | `hexa run blowup_daemon.hexa` 를 detached 기동, named pipe/lock 생성 |
| `nexus daemon status` | alive / pid / uptime / idle_s / served_count / atlas_gen |
| `nexus daemon stop` | SIGTERM → graceful |
| `nexus daemon tail` | daemon log tail (디버그) |

### 3.2. 프로세스 주소

- named pipe (FIFO): `/tmp/nexus_blowup.sock`
  - drill 쪽은 write FD, daemon 은 read FD 보유.
  - 응답 채널은 `/tmp/nexus_blowup.ret.sock` (daemon write, drill read).
- pid file: `/tmp/nexus_blowup.pid`
- lock file: `shared/n6/.atlas.lock` (daemon 이 hold)

### 3.3. drill 클라이언트 동작

```
if daemon_alive() and NEXUS_DRILL_DAEMON=1:
    send(cmd) via FIFO
    read OK/ERR
else:
    fallback: hexa run … (exec 방식)
```

- 감지 실패 시 자동 fallback — 호환성 보존.
- 부팅 미완료 (READY 미수신) 상태에서 즉시 호출 들어오면 client 는 500 ms 백오프 후 재시도 (최대 10 회).

---

## 4. State isolation

daemon 수명이 길어질수록 라운드 간 state leak 리스크가 커진다. 다음 원칙을 강제한다.

### 4.1. 리셋 대상 (매 round 진입 시)

- `salt`, `jitter`, `rng_seed` (seed hash 로 재파생)
- `partial_graph_delta` (이전 라운드의 미반영 델타)
- `lens_consensus_buf`
- `ouroboros.cycle_counter`
- `timer_accumulator`

### 4.2. 유지 대상 (boot 시 1 회만 init)

- atlas.n6 읽기 캐시 (write 는 라운드 종료 시 flush)
- lens registry
- engine registry
- stdlib symbol table

### 4.3. Concurrency

- **single-writer**: atlas.n6 쓰기는 daemon 프로세스만 수행.
- **mutex**: 다중 drill 클라이언트가 동시에 호출해도 daemon 내부 큐로 직렬화 (FIFO semantics).
- **write batching**: 같은 drill session 내 여러 round 의 graph delta 는 flush 시 단일 append.

---

## 5. Risks / mitigations

| Risk | 영향 | Mitigation |
|---|---|---|
| State leak (round 간 변수 재사용) | 돌파 결과 재현성 깨짐 | §4.1 명시적 reset + §8 byte-identity 테스트 |
| Hang (stage 내 무한 루프) | daemon 전체 멈춤 | per-cmd hard timeout (기본 180 s) + `ERR\ttimeout` |
| atlas 쓰기 경쟁 | 데이터 손상 | single-writer + `.atlas.lock` + stale-lock GC |
| SIGKILL → stale lock | 다음 부팅 실패 | bootstrap 에서 pid liveness 체크 후 정리 |
| FIFO 깨짐 (client crash) | daemon block | `O_NONBLOCK` + SIGPIPE 핸들러로 스킵 |
| parallel drill (동일 seed) | 중복 absorb | seed 해시 기반 in-flight set 에서 dedupe |
| memory 누적 (12 h) | OOM | max lifetime 12 h 자동 재기동 권장 (launchd) |
| daemon 버전과 atlas 스키마 미스매치 | 엉뚱한 쓰기 | boot 시 `atlas_gen` 체크, 불일치 시 refuse boot |

---

## 6. Expected speedup

### 6.1. cold start 비용 모델

- `T_cold`: 1 `hexa run` 당 cold start = **2~5 s** (atlas 크기에 따라)
- `T_work`: 실제 stage 로직 순수 실행 = **0.5~3 s** (stage/depth 의존)

### 6.2. 현 방식 (exec 기반)

- drill 1회 (seed=1, rounds=1, stages=6) = 6 × (T_cold + T_work) ≈ 6 × 4 s = **24 s**
- seed_batch=7 × rounds=3 × stages=6 = 126 × 4 s ≈ **504 s (≈ 8.4 min)**

### 6.3. daemon 방식

- daemon boot 1회 = T_cold (≈ 3 s)
- 이후 호출 = T_work 만 (≈ 1.5 s 평균)
- drill 1회 (seed=1, rounds=1, stages=6) = 3 + 6 × 1.5 = **12 s** (50 % ↓)
- seed_batch=7 × rounds=3 × stages=6 = 3 + 126 × 1.5 = **192 s (≈ 3.2 min)** (62 % ↓)

### 6.4. 요약

| scenario | exec (s) | daemon (s) | Δ |
|---|---|---|---|
| 1 seed × 1 round | 24 | 12 | −50 % |
| 1 seed × 3 round | 72 | 30 | −58 % |
| 7 seed × 3 round | 504 | 192 | −62 % |

보수적으로 **30~50 % wall-time 단축** 이 phase 4 완료 시 기대된다 (seed_batch 확대 시 상단).

---

## 7. Implementation phases

### Phase 1 — `blowup_daemon.hexa` MVP (스펙/스켈레톤)
- stdin line-loop + stdout OK/ERR
- **`smash` 만** 지원 (가장 자주 호출되는 stage)
- atlas.n6 read-only — write 는 기존 exec 경로 유지 (혼합 모드)
- idle exit 600 s
- 목표 산출물: `shared/blowup/core/blowup_daemon.hexa`

### Phase 2 — 6-stage 전체 + state reset 검증
- `free`, `absolute`, `meta`, `hyper`, `resonance` 추가
- §4.1 reset 구현 + §8 state-leak 테스트 통과 (byte-identical)
- atlas write 를 daemon 내부로 이관 (single-writer)
- 목표 산출물: reset 유닛 테스트 `shared/blowup/audit/daemon_reset_test.hexa`

### Phase 3 — named pipe + `nexus daemon` 하위 명령
- `/tmp/nexus_blowup.sock` FIFO 설치
- `nexus daemon {start|status|stop|tail}` 하위 명령을 `run.hexa` 라우터에 추가
- launchd 재기동 plist 예시 (12 h 주기)
- 목표 산출물: `run.hexa` patch + `shared/launchd/com.nexus.blowup-daemon.plist`

### Phase 4 — drill 통합 + auto-discovery
- drill 쪽이 daemon 자동 감지 → FIFO 경로 우선
- `NEXUS_DRILL_DAEMON=1` feature flag (기본 off)
- 누락/사망 시 exec fallback — 회귀 zero 보장
- 전/후 wall-time 벤치 리포트 `shared/reports/daemon_speedup.md`

---

## 8. Validation plan

### 8.1. MVP smoke
- daemon 1 회 기동 + 동일 seed 5 회 sequential smash
- 비-daemon 5 회 smash 와 wall-time 비교
- 기대: daemon 총 시간 < 60 % of exec 총 시간

### 8.2. State-leak test (byte-identity)
- seed A → seed B → seed A 순서로 smash 3 회
- 첫 번째 A 결과와 세 번째 A 결과를 JSON canonical 비교
- 기대: **byte-identical** (state 독립성 보장)
- 실패 시: §4.1 reset 대상 누락 조사

### 8.3. Hang test
- idle 600 s 경과 관찰 → `BYE` + exit 0 확인
- per-cmd hard timeout: `sleep 9999` mock 주입 → 180 s 이내 `ERR\ttimeout`

### 8.4. Parallel drill
- drill 2개 동시 기동 → 동일 FIFO 로 경합
- 기대: 둘 다 완료, atlas.n6 corruption 없음 (line count 일관)
- mutex 동작: 둘이 순서대로 직렬화됨을 로그로 확인

### 8.5. Kill & recover
- `kill -9 $(cat /tmp/nexus_blowup.pid)` → stale lock 상태
- `nexus daemon start` 재기동 시 stale lock 자동 복구

### 8.6. Feature flag off
- `NEXUS_DRILL_DAEMON=0` 에서 drill 동작이 기존과 **완전히 동일** 함을 회귀 테스트
- 하네스 CI 에 기본 flag off 로 진입 → 회귀 zero 보장

---

## 9. Rollout

### 9.1. Feature flag

- `NEXUS_DRILL_DAEMON` ∈ {`0`, `1`}
  - `0` (기본, phase 4 까지): drill 은 기존 exec 방식
  - `1`: daemon 감지 시 FIFO, 실패 시 exec fallback

### 9.2. 단계별 게이트

| phase | 완료 조건 | 플래그 |
|---|---|---|
| 1 | smash MVP 기동 + README | flag off |
| 2 | 6-stage + §8.2 통과 | flag off |
| 3 | `nexus daemon` 하위 명령 merge | flag off |
| 4 | §8.1~§8.6 전부 통과, 벤치 리포트 공개 | flag default=**off** (opt-in) |
| 5 (미래) | 1 주 opt-in 무사고 후 default=**on** | flag on |

### 9.3. 롤백

- flag=0 복귀 시 즉시 기존 경로로 전환 (daemon 프로세스는 idle 600s 후 자연 종료)
- 코드 수준 롤백도 daemon 파일 1개 삭제 + `run.hexa` 라우터 branch 제거로 국한됨
- atlas.n6 포맷 변경 **없음** — 데이터 호환 영구 보장

---

## Appendix A — 참조

- entry: `run.hexa` (`nexus drill` 서브커맨드)
- blowup core: `shared/blowup/core/blowup.hexa`
- compose: `shared/blowup/compose.hexa`
- modules: `shared/blowup/modules/blowup_{field,holographic,quantum,string,toe,absolute}.hexa`
- atlas: `shared/n6/atlas.n6`
- 현재 drill SSOT: `shared/roadmaps/drill_dod.json` (DOD), `shared/config/engine_registry.json`
- 유관 이전 마일스톤: 가속 14종 SSOT (commit `bd5a7518`), timeout_policy (commit `94759ac6`)

## Appendix B — Non-goals

- CLM/GPU 경로 (destination alm) — 별도 milestone E12
- 다중 호스트 분산 daemon — 별도 milestone E13
- daemon 내부 cache 의 영속화 (disk spill) — 필요 시 E14
- hexa interpreter 자체의 startup 최적화 — `hexa-lang` upstream 이슈
