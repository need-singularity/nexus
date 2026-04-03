# Secret Repository Reference

> 민감 정보 (계정, API 토큰)는 private 리포에 보관.
> 절대 public 리포에 토큰/비밀번호 하드코딩 금지.

## 리포

- **리포**: [need-singularity/secret](https://github.com/need-singularity/secret) (private)
- **로컬**: `~/Dev/secret/`
- **이전 이름**: `claude-code-secrets` (2026-04-01 renamed)

## 토큰 위치

| 토큰 | 위치 | 용도 |
|------|------|------|
| Zenodo | `~/Dev/TECS-L/.local/zenodo_token` | 논문 발행 (DOI) |
| OSF | `~/Dev/TECS-L/.local/osf_token` | 논문 발행 (OSF) |
| Gmail | `~/Dev/TECS-L/.local/gmail_credentials.json` | 이메일 아웃리치 |
| Gmail Token | `~/Dev/TECS-L/.local/gmail_token.json` | OAuth 토큰 |
| RunPod | `~/Dev/TECS-L/.local/runpod_api_key` | GPU 서버 |
| Zenodo Sandbox | `~/Dev/TECS-L/.local/zenodo_sandbox_token` | 테스트용 |

## 계정 정보

- `~/Dev/secret/README.md` — Claude Code 계정 + API 키 테이블

## 사용법

```bash
# Zenodo 논문 발행
ZENODO_TOKEN=$(cat ~/Dev/TECS-L/.local/zenodo_token)

# OSF 논문 발행
OSF_TOKEN=$(cat ~/Dev/TECS-L/.local/osf_token)

# Gmail 이메일
# send_emails.py가 자동으로 ~/Dev/TECS-L/.local/ 참조

# 각 리포 CLAUDE.md에서 이 파일 참조:
# "API 토큰/계정: ~/Dev/TECS-L/.shared/SECRET.md 참조"
```

## 규칙

1. **토큰은 `.local/` 디렉토리에만** — `.gitignore`에 포함됨
2. **계정 정보는 `secret` 리포에만** — private 리포
3. **public 리포에 절대 하드코딩 금지**
4. **새 토큰 추가 시 이 파일 + `secret/README.md` 동시 업데이트**
