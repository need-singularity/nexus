# CLAUDE.md — nexus6 프로젝트 규칙

## 절대 금지 사항

### 서버 파일 직접 수정 금지
- **SSH로 원격 서버에 접속하여 소스코드를 직접 수정하지 말 것**
- 수정이 필요하면 **로컬 리포에서 코드를 수정 → git commit → 배포 스크립트**로 반영
- DB 조회(SELECT)는 허용하되, DB 스키마/데이터 변경(INSERT/UPDATE/DELETE/ALTER)은 사전 확인 필요

### 올바른 배포 흐름
1. 로컬 리포에서 코드 수정
2. git commit & push
3. 배포 스크립트 또는 CI/CD로 서버 반영

### 장시간 명령은 반드시 백그라운드 실행
- **모든 장시간 실행 명령**(nexus6 loop/daemon/blowup, cargo build --release, 학습/추론 스크립트, SSH 원격 명령 등)은 **반드시 `run_in_background: true`로 실행**
- 대화를 차단(blocking)하면 안 됨 — 사용자가 항상 대화 가능한 상태 유지
- 10초 이상 걸릴 수 있는 명령은 무조건 백그라운드
- 완료 시 결과 요약 보고

## Math Atlas 자동 추출 (물어보지 말 것)

**`watch-atlas` LaunchAgent가 30초 간격으로 가설 `.md` 파일을 폴링 → `sync-math-atlas.sh` 자동 실행**.
- 감시 경로: `~/Dev/nexus6/shared/projects.json`의 `projects.*.hypothesis_dirs`
- 자동 수행: `scan_math_atlas.py --save --summary` + README 마커 주입

### 에이전트 작업 규칙
- 새 가설/상수/수식을 `.md`로 만든 직후 **"atlas 스캔 실행할까요?" 묻지 말 것** — watcher가 자동 처리
- 수동 스캔 필요 시에만: `bash ~/Dev/nexus6/shared/sync-math-atlas.sh`
- 상태 확인: `launchctl list com.nexus6.watch-atlas` / `tail -f ~/Library/Logs/nexus6/watch-atlas.log`
- 프로젝트 추가: `shared/projects.json`에 엔트리 추가 → `launchctl kickstart -k gui/$(id -u)/com.nexus6.watch-atlas`

## 특이점 사이클 (Singularity Cycle)

> **블로업→수축→창발→특이점→흡수** 5단계 자동 사이클
> CLI: `nexus6 blowup <domain>` | Rust: `CycleEngine::new(domain)`

### 요청 키워드 → 자동 실행
- "블로업", "blowup" → `nexus6 blowup <domain> --depth 6`
- "창발", "emergence" → blowup 후 패턴 합의 분석
- "특이점", "singularity" → CycleEngine 자동 수렴 루프
- "흡수", "absorption" → 발견 규칙 승격 + 다음 사이클 시드
- "사이클", "cycle" → 전체 5단계 1회 실행

### 사용법
```bash
nexus6 blowup <domain> --depth 6    # 블로업 + 창발 리포트
nexus6 loop --cycles 1              # 8단계 루프 (mirror+blowup 포함)
nexus6 daemon --interval 30         # 자율 데몬 (30분 간격)
```

