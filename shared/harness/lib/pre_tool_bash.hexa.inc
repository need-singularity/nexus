// ═══════════════════════════════════════════════════════════
// lib/pre_tool_bash.hexa.inc — Bash PreToolUse 가드 모음
// 사용: errors.hexa.inc 패턴 — 소비자 .hexa 상단에 copy-paste.
//       (hexa stage1 native include 미지원. 본 파일은 canonical source.)
//
// 목적: pre_tool_guard.hexa 카테고리 분리 refactor (H-마커 8 혼재 해소).
// 참조 main: shared/harness/pre_tool_guard.hexa
//
// 함수 목록 (dispatch 순서):
//   check_md_to_pdf_cmd           pandoc/xelatex MD→PDF 차단          (H-MD2PDF)
//   check_external_send_cmd       gh PR/이메일/webhook 발송 차단       (H-SEND-GUARD)
//   check_blocking_cmd            read -p / wait / fg / sleep N>=10    (H-NOBLOCK)
//   check_pkill_f_cmd             pkill/pgrep -f substring 차단        (R20)
//   check_bare_interpreter_cmd    bare python3/ruby/node 차단          (R22)
//   check_no_archive_cmd          mkdir backup / cp .bak / tar.gz      (H-NOARCHIVE)
//   check_no_hook_cmd             git config core.hooksPath / claude   (H-NOHOOK)
//   check_hexa_budget             hexa 프로세스 예산 게이트            (H-NOZOMBIE)
// ═══════════════════════════════════════════════════════════

// H-MD2PDF: MD→PDF 변환은 md-to-pdf 전용. pandoc/xelatex 호출 차단.
// arg = Bash command (entry.hexa 가 argv[3] 으로 cmd 전달)
fn check_md_to_pdf_cmd(tool: str, arg: str) -> str {
    if tool != "Bash" { return "" }
    if arg.len() == 0 { return "" }
    if arg.contains("NEXUS_PDF_OK=1") { return "" }

    let has_pandoc = arg.contains("pandoc")
    let has_xelatex = arg.contains("xelatex") || arg.contains("pdflatex") || arg.contains("lualatex")
    if has_pandoc == false && has_xelatex == false { return "" }

    if has_pandoc {
        let to_pdf = arg.contains(".pdf") || arg.contains("--to=pdf") || arg.contains("-t pdf") || arg.contains("--to pdf")
        if to_pdf == false { return "" }
        return "REJECT: pandoc PDF 변환 금지 (H-MD2PDF) — `md-to-pdf <file.md>` 사용. 우회: NEXUS_PDF_OK=1 prefix"
    }

    return "REJECT: xelatex/pdflatex/lualatex 금지 (H-MD2PDF) — MD→PDF 는 `md-to-pdf` 사용. 우회: NEXUS_PDF_OK=1 prefix"
}

// H-SEND-GUARD: 외부 발송/등록 (이메일, github issue/PR, webhook) — 사용자 명시 요청 전 차단.
// 우회: NEXUS_SEND_OK=1 prefix (사용자가 직접 요청한 경우 Claude 가 명시 부여).
fn check_external_send_cmd(tool: str, arg: str) -> str {
    if tool != "Bash" { return "" }
    if arg.len() == 0 { return "" }
    if arg.contains("NEXUS_SEND_OK=1") { return "" }

    let patterns = [
        ["gh issue create", "github issue 등록"],
        ["gh issue comment", "github issue 댓글"],
        ["gh issue close", "github issue 종료"],
        ["gh issue reopen", "github issue 재오픈"],
        ["gh pr create", "github PR 생성"],
        ["gh pr comment", "github PR 댓글"],
        ["gh pr merge", "github PR 머지"],
        ["gh pr close", "github PR 종료"],
        ["gh pr review", "github PR 리뷰"],
        ["gh release create", "github release 발행"],
        ["gh gist create", "github gist 발행"],
        ["sendmail ", "이메일 발송 (sendmail)"],
        ["msmtp ", "이메일 발송 (msmtp)"],
        ["swaks ", "이메일 발송 (swaks)"],
        ["mutt -s", "이메일 발송 (mutt)"],
        ["mail -s", "이메일 발송 (mail)"],
        ["hooks.slack.com", "slack webhook"],
        ["discord.com/api/webhooks", "discord webhook"],
        ["discordapp.com/api/webhooks", "discord webhook"]
    ]
    for p in patterns {
        if arg.contains(p[0]) {
            return "REJECT: 외부 발송/등록 차단 (H-SEND-GUARD) — " + p[1] + ". 사용자 명시 요청 필요. 우회: NEXUS_SEND_OK=1 prefix"
        }
    }
    return ""
}

// H-NOBLOCK: 세션 채팅 블로킹 금지 — 사용자 입력 채널을 막는 동기 대기 명령 차단.
// 대상: read -p / read -r / wait (PID/%N) / fg / sleep N (N>=10) / while sleep ... do done
// 우회: NEXUS_BLOCK_OK=1 prefix (정당한 사유 — 예: long-poll 의도 명시).
// 구현: arg 를 임시파일로 쓰고 awk 매칭 — hexa-real char 비교/$expansion 함정 우회.
fn check_blocking_cmd(tool: str, arg: str) -> str {
    if tool != "Bash" { return "" }
    if arg.len() == 0 { return "" }
    if arg.contains("NEXUS_BLOCK_OK=1") { return "" }
    if arg.contains("@allow-block") { return "" }

    if arg.contains("read -p ") || arg.contains("read -rp ") || arg.contains("read -sp ") {
        return "REJECT: read -p/-rp/-sp 입력 대기 금지 (H-NOBLOCK) — 세션 블로킹. 우회: NEXUS_BLOCK_OK=1 prefix"
    }
    if arg.contains(" fg ") || arg.starts_with("fg ") || arg == "fg" || arg.contains(";fg") || arg.contains("&& fg") {
        return "REJECT: fg 포그라운드 복귀 금지 (H-NOBLOCK) — 세션 블로킹. 우회: NEXUS_BLOCK_OK=1"
    }
    if (arg.contains("while ") || arg.contains("until ")) && arg.contains("sleep ") && arg.contains("done") {
        return "REJECT: while/until + sleep 폴링 루프 금지 (H-NOBLOCK) — Monitor 또는 run_in_background 사용. 우회: NEXUS_BLOCK_OK=1"
    }

    // wait + sleep N>=10 → awk 로 검사 (arg 임시파일 경유, $expansion 회피)
    let tmp = "/tmp/h_noblock_arg." + to_string(exec("date +%s%N")).trim()
    let _ = exec("cat > " + tmp + " <<'NOBLOCK_EOF'\n" + arg + "\nNOBLOCK_EOF")

    let wait_hits = to_string(exec("awk '/wait[[:space:]]+(\\$|%|[0-9])/{c++} END{print c+0}' " + tmp + " 2>/dev/null")).trim()
    if wait_hits != "0" && wait_hits != "" {
        let _ = exec("rm -f " + tmp)
        return "REJECT: wait PID/%/숫자 합류 대기 금지 (H-NOBLOCK) — run_in_background + Monitor 사용. 우회: NEXUS_BLOCK_OK=1"
    }

    let sl_hits = to_string(exec("awk '/sleep[[:space:]]+([1-9][0-9]+|[1-9][0-9][0-9]+)/{c++} END{print c+0}' " + tmp + " 2>/dev/null")).trim()
    if sl_hits != "0" && sl_hits != "" {
        let _ = exec("rm -f " + tmp)
        return "REJECT: sleep N>=10s 장시간 대기 금지 (H-NOBLOCK) — ScheduleWakeup/Monitor 사용. 우회: NEXUS_BLOCK_OK=1"
    }

    let _ = exec("rm -f " + tmp)
    return ""
}

// R20: pkill/pgrep -f substring 금지 — -xf 정확매칭 또는 PID 파일 기반만 허용
// 우회: @allow-pkill-f 토큰 명시
fn check_pkill_f_cmd(tool: str, arg: str) -> str {
    if tool != "Bash" { return "" }
    if arg.len() == 0 { return "" }
    if arg.contains("@allow-pkill-f") { return "" }
    if arg.contains("-xf") { return "" }

    let has_pkill_f = arg.contains("pkill -f") || arg.contains("pgrep -f")
    if has_pkill_f == false { return "" }
    return "REJECT: pkill/pgrep -f substring 금지 (R20) — 무고한 프로세스 silent kill 위험. -xf 정확매칭 / PID 파일 / pgrep -x <basename> 사용. 우회: @allow-pkill-f 주석"
}

// R22: 스크립트 인터프리터 절대경로 강제 — bare python3/ruby/node 금지
// 우회: NEXUS_INTERP_OK=1 prefix (일회성 ad-hoc)
fn check_bare_interpreter_cmd(tool: str, arg: str) -> str {
    if tool != "Bash" { return "" }
    if arg.len() == 0 { return "" }
    if arg.contains("NEXUS_INTERP_OK=1") { return "" }

    let patterns = [
        ["python3 ", "python3 (R22) — /usr/bin/python3 절대경로 필수 (hetzner 라우팅 회피)"],
        ["ruby ", "ruby (R22) — 절대경로 필수"],
        ["node ", "node (R22) — 절대경로 필수"]
    ]
    for p in patterns {
        let idx = arg.index_of(p[0])
        if idx < 0 { continue }
        if idx > 0 {
            let prev = arg.substring(idx - 1, idx)
            if prev == "/" { continue }
            if prev == "=" { continue }
        }
        return "REJECT: bare interpreter 호출 금지 — " + p[1] + ". 우회: NEXUS_INTERP_OK=1 prefix"
    }
    return ""
}

// H-NOARCHIVE Bash: mkdir archive/backup, cp/mv/rsync to .bak/.backup/.old, tar.gz 백업 생성 차단.
fn check_no_archive_cmd(tool: str, arg: str) -> str {
    if tool != "Bash" { return "" }
    if arg.len() == 0 { return "" }
    if arg.contains("NEXUS_ARCHIVE_OK=1") { return "" }
    if arg.contains("@allow-archive") { return "" }

    // 격리 공간 안에서의 작업은 통과
    let in_safe_zone = arg.contains("shared/backups/") || arg.contains("shared/archive/") || arg.contains("shared/discovery/archive/") || arg.contains("archive/deprecated_json/")

    let mkdir_patterns = [
        "mkdir backup", "mkdir backups", "mkdir archive", "mkdir archives",
        "mkdir -p backup", "mkdir -p backups", "mkdir -p archive", "mkdir -p archives",
        "mkdir .backup", "mkdir .archive", "mkdir _backup", "mkdir _archive"
    ]
    if in_safe_zone { return "" }

    for p in mkdir_patterns {
        if arg.contains(p) {
            return "REJECT: '" + p + "' 신규 폴더 생성 금지 (H-NOARCHIVE). archive 는 git commit/branch/tag 로. 격리 예외: shared/backups/, shared/archive/. 우회: NEXUS_ARCHIVE_OK=1"
        }
    }

    let starts_cp_mv = arg.contains("cp ") || arg.contains("mv ") || arg.contains("rsync ")
    if starts_cp_mv {
        let sfx_patterns = [".bak ", ".bak'", ".bak\"", ".backup ", ".backup'", ".backup\"", ".old ", ".old'", ".old\"", ".orig ", ".orig'", ".orig\""]
        for s in sfx_patterns {
            if arg.contains(s) {
                return "REJECT: cp/mv/rsync → '*" + s.trim() + "' 백업 사본 금지 (H-NOARCHIVE). git stash/commit 으로 보존. 우회: NEXUS_ARCHIVE_OK=1"
            }
        }
        let end_patterns = [".bak", ".backup", ".old", ".orig"]
        for s in end_patterns {
            if arg.ends_with(s) {
                return "REJECT: cp/mv/rsync → '*" + s + "' 백업 사본 금지 (H-NOARCHIVE). git stash/commit 으로 보존. 우회: NEXUS_ARCHIVE_OK=1"
            }
        }
    }

    let tar_patterns = ["backup.tar", "backup.tgz", "backup.zip", "_backup.tar", "_backup.zip", "archive.tar", "archive.tgz", "archive.zip"]
    for t in tar_patterns {
        if arg.contains(t) {
            return "REJECT: '" + t + "' 백업 아카이브 생성 금지 (H-NOARCHIVE). git bundle/tag 사용. 우회: NEXUS_ARCHIVE_OK=1"
        }
    }

    return ""
}

// H-NOHOOK Bash: git config core.hooksPath 변경 / chmod +x 새 hook 활성화 / 새 .git/hooks 파일 생성 차단.
fn check_no_hook_cmd(tool: str, arg: str) -> str {
    if tool != "Bash" { return "" }
    if arg.len() == 0 { return "" }
    if arg.contains("NEXUS_HOOK_OK=1") { return "" }
    if arg.contains("@allow-hook") { return "" }

    if arg.contains("git config core.hooksPath") || arg.contains("git config --global core.hooksPath") {
        return "REJECT: git config core.hooksPath 변경 금지 (H-NOHOOK) — H-COMMIT .githooks/ 가 SSOT. 우회: NEXUS_HOOK_OK=1"
    }
    if arg.contains("claude hooks add") || arg.contains("claude config hooks") {
        return "REJECT: claude hooks add 금지 (H-NOHOOK) — settings.json hooks={} SSOT. harness/entry.hexa 자율 호출로 대체. 우회: NEXUS_HOOK_OK=1"
    }
    return ""
}

// H-NOZOMBIE: hexa 프로세스 예산 게이트 — 동시 활성 hexa N개 초과 시 BLOCK.
// Why: nexus 에서 .hexa 프로세스가 30+ 누적 → Mac load 220 사고. 사후 청소 외 사전 차단 필수.
// 우회: NEXUS_BUDGET_OK=1 prefix 또는 cmd 내 @allow-many-hexa 토큰.
// host 별 임계치: mac=8, hetzner/ubu/vast=32, 기타=12 (CPU 코어 기준 추정).
fn check_hexa_budget(tool: str, arg: str) -> str {
    if tool != "Bash" { return "" }
    if arg.len() == 0 { return "" }
    if arg.contains("NEXUS_BUDGET_OK=1") { return "" }
    if arg.contains("@allow-many-hexa") { return "" }
    if arg.contains("hexa") == false { return "" }

    let host = to_string(exec("hostname -s 2>/dev/null || echo unknown")).trim()
    let mut budget = 12
    if host == "Mac" || host == "mac" { budget = 8 }
    else if host.contains("hetzner") || host.contains("ubu") || host.contains("vast") { budget = 32 }

    let count_str = to_string(exec(
        "ps -axo command 2>/dev/null | " +
        "awk '/\\/hexa[[:space:]]run|hexa\\.real/ && !/awk/ && !/\\/bin\\/zsh/ && !/pre_tool_guard\\.hexa/{n++} END{print n+0}'"
    )).trim()
    let count = to_int(count_str)
    if count < budget { return "" }

    return "REJECT: hexa 프로세스 예산 초과 (활성=" + count_str + "/임계=" + to_string(budget) +
           " host=" + host + ") H-NOZOMBIE — 잠시 후 재시도. 우회: NEXUS_BUDGET_OK=1 prefix 또는 @allow-many-hexa 주석"
}
