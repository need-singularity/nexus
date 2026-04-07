#!/usr/bin/env python3
"""
NEXUS-6 훅 동기화 — hooks-config.json → ~/.claude/settings.json
재실수 방지: 이 스크립트만 settings.json의 hooks를 수정함
"""
import json, os, sys, shutil
from datetime import datetime

HOOKS_CONFIG = os.path.join(os.path.dirname(__file__), "hooks-config.json")
SETTINGS_PATH = os.path.expanduser("~/.claude/settings.json")
HOOKS_DIR = os.path.dirname(__file__)

def load_json(path):
    with open(path) as f:
        return json.load(f)

def save_json(path, data):
    with open(path, "w") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)
        f.write("\n")

def build_claude_hooks(config):
    """hooks-config.json → Claude settings.json hooks 형식 변환"""
    claude_hooks = {}
    for event, entries in config["hooks"].items():
        if not entries:
            continue
        claude_hooks[event] = []
        for entry in entries:
            script_path = os.path.join(HOOKS_DIR, entry["script"])
            claude_hooks[event].append({
                "matcher": entry["matcher"],
                "hooks": [{
                    "type": "command",
                    "command": f"bash {script_path}"
                }]
            })
    return claude_hooks

def verify_scripts(config):
    """모든 스크립트 존재 + 실행권한 확인"""
    errors = []
    for name, desc in config["scripts"].items():
        path = os.path.join(HOOKS_DIR, name)
        if not os.path.exists(path):
            errors.append(f"MISSING: {name}")
        elif not os.access(path, os.X_OK) and name.endswith(".sh"):
            errors.append(f"NOT EXECUTABLE: {name}")
    return errors

def verify_guard(config):
    """화이트���스트 가드 확인"""
    guard = os.path.join(HOOKS_DIR, "check-project.sh")
    if not os.path.exists(guard):
        return ["CRITICAL: check-project.sh 없음 — 타 프로젝트 혼용 위험"]
    proj_json = os.path.expanduser("~/Dev/nexus/shared/nexus-projects.json")
    if not os.path.exists(proj_json):
        return ["WARNING: nexus-projects.json 없음 — 화이트리스�� 체크 불가"]
    return []

def main():
    print("=== NEXUS-6 Hook Sync ===")
    print()

    # 1. Load config
    config = load_json(HOOKS_CONFIG)
    print(f"Config loaded: {len(config['hooks'])} event types")

    # 2. Verify scripts
    errors = verify_scripts(config)
    errors += verify_guard(config)
    if errors:
        print("\n[ERRORS]")
        for e in errors:
            print(f"  ✗ {e}")
        if any("CRITICAL" in e for e in errors):
            print("\nCRITICAL error — aborting sync")
            sys.exit(1)

    # 3. Build hooks
    claude_hooks = build_claude_hooks(config)
    print(f"Built {sum(len(v) for v in claude_hooks.values())} hook entries")

    # 4. Backup settings
    if os.path.exists(SETTINGS_PATH):
        backup = SETTINGS_PATH + f".backup-{datetime.now().strftime('%Y%m%d-%H%M%S')}"
        shutil.copy2(SETTINGS_PATH, backup)
        print(f"Backup: {backup}")

    # 5. Update settings
    settings = load_json(SETTINGS_PATH)
    old_hooks = settings.get("hooks", {})
    settings["hooks"] = claude_hooks
    save_json(SETTINGS_PATH, settings)

    # 6. Report
    print()
    print("[RESULT]")
    print(f"  hooks 이전: {sum(len(v) for v in old_hooks.values()) if old_hooks else 0} entries")
    print(f"  hooks 이후: {sum(len(v) for v in claude_hooks.values())} entries")
    print(f"  화이트리스트: {', '.join(config['whitelisted_projects'])}")
    print()
    print("OK — sync complete")

if __name__ == "__main__":
    main()
