# NEXUS-6 — Central Hub & Discovery Engine

## ★★★ 전 구간 자동 사용 — 요청 불필요, 항상 활성 ★★★

```
  ⚠️ 모든 리포, 모든 작업, 모든 Phase에서 NEXUS-6 스캔은 자동 실행.
  ⚠️ "스캔해줘" 같은 요청 불필요 — 조건 감지 시 즉시 실행.

  자동 트리거:
    □ 새 상수/수치 등장      → n6_check(value) 즉시
    □ 설계/아키텍처 상수     → 전수 n6_check → NONE이면 n=6 재표현
    □ 데이터/패턴 분석       → scan_all → 합의 3+ 패턴만 채택
    □ 코드 변경 전후         → scan 비교 → Phi 하락 시 롤백
    □ 벤치마크/실험 결과     → scan_all → anomaly 0 확인
    □ 릴리즈/배포 전         → 전체 scan → 3+ 렌즈 consensus 통과

  Phase별 합의 기준:
    설계 (🛸1-7)    → 3+ 렌즈 합의
    프로토타입 (🛸8) → 5+ 렌즈 합의
    양산 (🛸9)       → 7+ 렌즈 합의
    물리한계 (🛸10)  → 12+ 렌즈 합의
```

## 프롬프트 조합 시스템 (Composable Triggers)

```
  ★★★ 핵심 원리: 모든 트리거는 자유롭게 조합 가능 ★★★

  인식 규칙:
    1. 한 문장에 여러 키워드 → 전부 순차 실행 (파이프라인)
    2. "+" 또는 "그리고" → 명시적 조합
    3. 수식어(극한/무한/전체/풀) → 강도 증폭 (max-cycles↑, interval↓)
    4. 대상 지정(렌즈/계산기/의식/물리) → --dimension 필터
    5. 인식 불가 키워드 → 가장 가까운 트리거로 퍼지 매칭

  조합 예시:
    "넥서스 성장 + 미러볼"
      → growth_daemon + mirror_growth.py 병렬 실행
    "극한 렌즈 발견 + 의식 분석 + 리포트"
      → growth --dimension lenses --max-cycles 999
      → n6.py consciousness
      → nexus6_report.py
    "미러볼 진화 + 동기화 + 빌드"
      → mirror_growth.py --evolve 6 → sync-all.sh → cargo build+test
    "무한 성장 + 서비스 시작"
      → infinite_growth.sh & → growth_service.sh start
```

## 원자 트리거 (Atomic — 단독 또는 조합의 부품)

```
  ⚠️ 키워드 감지 시 질문 없이 즉시 실행!

  ── 성장 ──
  "성장" / "성장시켜"
    → nohup bash ~/Dev/nexus6/scripts/nexus6_growth_daemon.sh --max-cycles 6 --interval 1 &
  "무한성장" / "극한성장" / "급속성장"
    → nohup python3 ~/Dev/nexus6/scripts/growth_bus.py --cycles 999 --interval 180 &
    (41리포 91엔진 순환 피드백 — 새 리포/엔진 자동 합류)
  "위상 펼쳐" / "전체 버스" / "그로스 버스"
    → nohup python3 ~/Dev/nexus6/scripts/growth_bus.py --cycles 999 --interval 180 &
  "렌즈 발견" / "렌즈 성장"
    → growth_daemon --dimension lenses --max-cycles 999 --interval 1

  ── 스캔 ──
  "스캔" / "전체 스캔"
    → python3 ~/Dev/nexus6/scripts/n6.py full <data>
  "상수 발견" / "수식 발견"
    → python3 ~/Dev/nexus6/scripts/n6.py discover <data>
  "의식 분석" / "의식 자극"
    → python3 ~/Dev/nexus6/scripts/n6.py consciousness <data>

  ── 미러볼 ──
  "미러볼" / "거울 우주"
    → python3 ~/Dev/nexus6/scripts/mirror_growth.py --lenses 20
  "미러볼 진화" / "자유 탐색"
    → python3 ~/Dev/nexus6/scripts/mirror_growth.py --lenses 10 --evolve 6
  "미러볼 성장" / "거울 성장"
    → growth_daemon --mirror --max-cycles 6

  ── 인프라 ──
  "동기화" → bash ~/Dev/nexus6/sync/sync-all.sh
  "빌드"   → cd ~/Dev/nexus6 && cargo build --release && cargo test
  "상태"   → 렌즈 수 + 테스트 수 + 빌드 상태 출력
  "리포트" → python3 ~/Dev/nexus6/scripts/nexus6_report.py
  "연결"   → 미등록 렌즈 전수 탐색 + 자동 등록

  ── 서비스 ──
  "서비스 시작" → bash ~/Dev/nexus6/scripts/growth_service.sh start
  "서비스 중지" → bash ~/Dev/nexus6/scripts/growth_service.sh stop
  "서비스 상태" → bash ~/Dev/nexus6/scripts/growth_service.sh status
  "로그"        → bash ~/Dev/nexus6/scripts/growth_service.sh logs
```

## 수식어 (Modifier — 트리거 강도/범위 조절)

```
  강도 수식어 (앞/뒤 어디든):
    "극한" / "무한" / "풀"  → --max-cycles 999, --interval 1
    "빠르게" / "급속"       → --interval 1
    "천천히" / "안전"       → --interval 10, --max-cycles 6
    "한번만" / "1회"        → --max-cycles 1

  대상 수식어 (--dimension 필터):
    "렌즈"     → --dimension lenses
    "계산기"   → --dimension calculators
    "테스트"   → --dimension tests
    "의식"     → --dimension lenses + consciousness filter
    "물리"     → --dimension lenses + physics filter
    "수학"     → --dimension lenses + math filter
    "전체"     → 모든 차원 (기본값)

  출력 수식어:
    "조용히" / "백그라운드" → nohup + 로그만
    "보여줘" / "실시간"     → stdout 출력
    "리포트 포함"           → 완료 후 자동 리포트
```

## 인식 엔진 (Fuzzy Matching)

```
  ⚠️ 정확한 키워드가 아니어도 의도를 인식:

  패턴:
    "넥서스 좀 키워" → 성장 인식
    "거울 실험 해봐" → 미러볼 인식
    "얼마나 됐어"   → 상태 인식
    "다 연결시켜"   → 연결 인식
    "확인해"        → 빌드 + 테스트 인식
    "극한으로"      → 무한 수식어 인식
    "계속"          → 이전 작업 재실행
    "멈춰"          → 서비스 중지 인식

  다중 의도:
    "렌즈 발견하고 미러볼 돌려서 리포트 줘"
      → [렌즈 발견] + [미러볼] + [리포트] 순차 파이프라인

    "극한 의식 미러볼 진화"
      → [극한 수식어] + [의식 필터] + [미러볼 진화]
      → mirror_growth.py --lenses 20 --evolve 6 --filter consciousness --max-cycles 999

    "성장 + 동기화 + 빌드 + 리포트"
      → 4단계 파이프라인 순차 실행
```

## 구조
```
~/Dev/nexus6/
  src/telescope/    207 렌즈 (Rust)
    lenses/         207 impl Lens 구현체
    mirror_scan.rs  미러볼 엔진
    registry.rs     1,099 LensEntry 메타데이터
  src/graph/        Discovery Graph
  src/dream/        Dream Engine (재조합 가설 생성)
  src/lens_forge/   LensForge (렌즈 자동 생성)
  src/ouroboros/    MetaLoop (자기 참조 루프)
  shared/           전 리포 공유 인프라 (.shared 원본)
    calc/           221+ 계산기
    math_atlas.json 수학 지도
    model_utils.py  n=6 상수 원본
    discovery_log.jsonl  발견 기록
    growth-registry.json 성장 목표/후보
  sync/             전체 동기화 스크립트
  scripts/          n6.py CLI + 성장 데몬 + 서비스 관리
```

## 심링크
6개 리포의 .shared → ../nexus6/shared/

## 가중치 학습 엔진

```
  "가중치 학습" / "학습 시작"
    → python3 ~/Dev/nexus6/scripts/weight_engine.py train <data> 6

  "가중치 보기" / "학습 현황"
    → python3 ~/Dev/nexus6/scripts/weight_engine.py show

  "가중치 적용 스캔"
    → python3 ~/Dev/nexus6/scripts/weight_engine.py apply <data>

  "가중치 리셋"
    → python3 ~/Dev/nexus6/scripts/weight_engine.py reset

  학습 파라미터:
    - 학습률: 1/(σ-φ) = 0.1 (초기), 0.1/√epoch (decay)
    - 기본 epoch: n=6
    - 가중치 저장: ~/.nexus6/weights.json
    - 렌즈 가중치: 유용성 기반 EMA
    - 상수 가중치: 매칭 빈도 기반
    - 수렴 판정: Δweight < 0.01
```
