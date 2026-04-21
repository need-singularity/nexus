# Handoff Prompt — {{PROJECT}} / {{TOPIC}}

*Generated: {{TIMESTAMP}}*
*Previous session commits: {{COMMIT_COUNT}}*

---

## 1. 브랜치 + 최근 commit 상태

- 브랜치: `{{BRANCH}}` ({{PUSH_STATE}})
- 최근 commit (오래된 것 → 최신):

```
{{COMMIT_LOG}}
```

## 2. 남은 이슈 우선순위

| 우선 | 이슈 | 규모 | 현 상태 |
|---|---|---|---|
{{ISSUE_ROWS}}

## 3. 재현 / 배포 (복붙 가능)

```bash
{{REPRODUCE_COMMANDS}}
```

## 4. 세션 특수 컨벤션

{{CONVENTIONS}}

*(예: pre-commit hook 자동 stage, SSOT 수정 시 transpile 규칙, 빌드 순서 등)*

## 5. 관련 memory 포인터

{{MEMORY_POINTERS}}

*(예: `memory/user_profile.md`, `memory/project_overview.md`, `memory/feedback_*.md`)*

## 6. 권고 기본값

**{{RECOMMENDED_NEXT}}** — {{RECOMMENDED_RATIONALE}}

스코프: {{RECOMMENDED_SCOPE}}
예상 시간: {{RECOMMENDED_TIME}}

## 7. 대안

| 옵션 | 스코프 | 예상 시간 | 비고 |
|---|---|---|---|
{{ALTERNATIVE_ROWS}}

## 8. Guard

**먼저 방향 확정 후 `go` — cold start 로 큰 작업 즉시 진입 금지.**

남은 이슈 중 하나를 명시 선택하거나, 별도 방향을 제시한 후 착수할 것.

---

*R36 HANDOFF — shared/rules/common.json*
