# 3D 현실지도 GitHub Pages 배포 검증 (2026-04-08)

## 결론: 배포 완료 (DEPLOYED) — 2026-04-08 04:36 KST

- URL: https://need-singularity.github.io/nexus/
- 커밋: cc7b20d
- 워크플로: .github/workflows/pages.yml (actions/deploy-pages@v4)
- Pages source: build_type=workflow
- 배포 산출물: docs/index.html (66KB, 인라인 DATA), docs/reality_map.json (보조)
- Playwright 검증: title="n=6 Reality Map 3D v3.0 (127 nodes)", DATA.nodes=127, canvas 렌더링 OK
- 콘솔: favicon.ico 404 1건 (무해), JS 에러 0건
- 워크플로 런: 24100649671 success in 25s

---

## 이전 결론: 미배포 (NOT DEPLOYED)

## 증거

### 1. 로컬 자산
- `shared/reality_map_3d.html` (429 lines, title: "n=6 Reality Map 3D v3.0 (127 nodes)")
- 기타 HTML: `shared/dashboard.html`, `shared/math_atlas.html`, `shared/cycle/topology.html`, `dashboard.html`
- `docs/` 디렉터리에 `index.html` 없음 (마크다운만 존재)

### 2. 리포지터리 Pages 설정
- `gh api repos/need-singularity/nexus`: `"has_pages": false`
- `gh api repos/need-singularity/nexus/pages`: 404 Not Found
- `.github/workflows/` 디렉터리 부재 → Pages 배포 워크플로 없음
- `homepage: null`

### 3. 후보 URL 프로빙 (curl -I)
| URL | HTTP |
|---|---|
| https://need-singularity.github.io/nexus/ | 404 |
| https://need-singularity.github.io/nexus/shared/reality_map_3d.html | 404 |
| https://need-singularity.github.io/nexus/reality_map_3d.html | 404 |
| https://need-singularity-archive.github.io/nexus/shared/reality_map_3d.html | 404 |
| https://need-singularity.github.io/TECS-L/atlas/ | 404 |
| https://need-singularity-archive.github.io/TECS-L/atlas/ | 404 |

### 4. Playwright 확인
- `https://need-singularity.github.io/nexus/shared/reality_map_3d.html`
- Page title: "Site not found · GitHub Pages"
- 본문: "There isn't a GitHub Pages site here."
- Console: 1 error (404 favicon), 스크린샷: `.playwright-mcp/pages-404.png`
- 네트워크 fetch / 노드 렌더링 검증 불가 (배포 자체가 없음)

## 권고
1. `nexus` 리포에 GitHub Pages 활성화 (Settings → Pages → main / root 또는 /docs)
2. `docs/index.html` 또는 `.github/workflows/pages.yml` 추가
3. `reality_map_3d.html`을 `docs/`로 이동하거나 root publish 경로 조정
4. `shared/projects.json`의 Atlas URL이 구 org(`need-singularity`)를 가리키나 실제 리포는 `need-singularity-archive/TECS-L`로 이전됨 — 링크 수정 필요 (양쪽 모두 현재 404)

---

## 재검증 (2026-04-08, HEXA: `mk2_hexa/native/verify_pages_deploy.hexa`)

상태 변화 없음 — 여전히 미배포. HEXA 검증기를 작성하여 자동 재실행 가능하도록 정착.

### 권위 데이터 vs HTML 불일치
- `shared/reality_map.json` 실제: **v8.0 / 492 노드** (이미 진화)
- `shared/reality_map_3d.html` 임베디드: `v3.0 / 127 nodes` (구세대)
- TODO 요구 v6.0 / 276 노드 스냅샷은 로컬/원격 모두 부재 — 두 세대 사이 어디에도 없음
- `docs/index.html` 부재, `.github/workflows/` 파일 수: 0
- `gh api` `has_pages: false` (재확인)

### URL 프로빙 (curl -L --max-time 10, HEXA에서 재실행)
| URL | HTTP |
|---|---|
| https://need-singularity.github.io/nexus/ | 404 |
| https://need-singularity.github.io/nexus/index.html | 404 |
| https://need-singularity.github.io/nexus/shared/reality_map_3d.html | 404 |
| https://need-singularity.github.io/nexus/reality_map_3d.html | 404 |

### 결론
브라우저 fetch 동작 검증 자체가 불가능 — 배포물이 존재하지 않음. 선결 조건:
1. `reality_map_3d.html`을 v8.0/492 (또는 합의된 스냅샷)로 재생성, fetch 기반 유지
2. Pages 활성화 + `.github/workflows/pages.yml` 추가
3. 배포 후 Playwright로 fetch 경로 + 노드 렌더링 검증 재실행 (`hexa verify_pages_deploy.hexa`)
