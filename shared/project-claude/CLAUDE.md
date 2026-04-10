# project-claude/ — 프로젝트 CLAUDE.md 마스터

각 프로젝트의 CLAUDE.md SSOT — 이 폴더의 파일이 원본.

**심링크 폐기** (`07e314c6`, 2026-04-11): GitHub 렌더링을 위해 심링크 → 실제 파일로 전환됨.
동기화는 `shared/hooks/auto-sync.hexa` PostToolUse 훅이 담당 —
`project-claude/*.md` 편집 시 해당 프로젝트 루트의 CLAUDE.md로 `cp` + `sync_claude_md.hexa` 실행.

## 동기화 매핑 (auto-sync 대상)

```
nexus.md        → /Users/ghost/Dev/nexus/CLAUDE.md
anima.md        → /Users/ghost/Dev/anima/CLAUDE.md
n6-architecture.md → /Users/ghost/Dev/n6-architecture/CLAUDE.md
papers.md       → /Users/ghost/Dev/papers/CLAUDE.md
hexa-lang.md    → /Users/ghost/Dev/hexa-lang/CLAUDE.md
void.md         → /Users/ghost/Dev/void/CLAUDE.md
airgenome.md    → /Users/ghost/Dev/airgenome/CLAUDE.md
contact.md      → /Users/ghost/Dev/contact/CLAUDE.md
```

## 편집 규칙

- **편집 위치**: project-claude/*.md 또는 프로젝트 루트 CLAUDE.md 둘 중 하나
- **주의**: project-claude 편집 시 auto-sync가 프로젝트 루트를 덮어씀 → 루트의 미동기화 내용 유실 가능
- **권장**: 새 내용은 항상 project-claude 쪽부터 편집, 루트는 auto-sync에 맡김

parent: ../CLAUDE.md
