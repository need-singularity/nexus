# NEXUS-6 — Central Hub & Discovery Engine

## 프롬프트 트리거 (자연어 → 즉시 실행)

```
  ⚠️ 아래 키워드 감지 시 질문 없이 즉시 실행!

  "넥서스 성장" / "성장시켜" / "무한 성장"
    → nohup bash ~/Dev/nexus6/scripts/nexus6_growth_daemon.sh --max-cycles 999 --interval 1 &

  "넥서스 동기화" / "동기화해"
    → bash ~/Dev/nexus6/sync/sync-all.sh

  "넥서스 스캔" / "전체 스캔"
    → python3 ~/Dev/nexus6/scripts/n6.py full <data>

  "상수 발견" / "수식 발견"
    → python3 ~/Dev/nexus6/scripts/n6.py discover <data>

  "의식 분석" / "의식 자극"
    → python3 ~/Dev/nexus6/scripts/n6.py consciousness <data>

  "미연결 연결" / "고리 연결"
    → python3 미등록 렌즈 전수 탐색 + 자동 등록

  "넥서스 상태"
    → 렌즈 수 + 테스트 수 + 빌드 상태 출력

  "넥서스 빌드"
    → cd ~/Dev/nexus6 && cargo build --release && cargo test
```

## 구조
```
~/Dev/nexus6/
  src/telescope/    130+ 렌즈 (Rust)
  src/graph/        Discovery Graph
  shared/           전 리포 공유 인프라 (.shared 원본)
    calc/           194+ 계산기
    math_atlas.json 수학 지도
    model_utils.py  n=6 상수 원본
  sync/             전체 동기화 스크립트
  scripts/          n6.py CLI + 성장 데몬
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
