"""Reporter module -- terminal, markdown, and HTML report generation."""

from __future__ import annotations

import json
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

_RESULTS_DIR = Path(__file__).resolve().parent.parent.parent / "results"
_TEMPLATE_DIR = Path(__file__).resolve().parent.parent.parent / "templates"

GRADE_EMOJI = {
    "green": "\U0001f7e9",   # green square
    "orange": "\U0001f7e7",  # orange square
    "white": "\u26aa",       # white circle
    "black": "\u2b1b",       # black square
}

TIERS = (1, 2, 3)


def _bar(pct: float, width: int = 20) -> str:
    """Return a progress bar string like '████████░░░░░░░░░░░░'."""
    filled = round(pct / 100 * width)
    return "\u2588" * filled + "\u2591" * (width - filled)


def _tier_summary(results: list[dict[str, Any]], tier: int) -> dict[str, Any]:
    """Summarise pass/fail for a single tier."""
    subset = [r for r in results if r.get("tier") == tier]
    total = len(subset)
    passed = sum(1 for r in subset if r.get("status") == "pass")
    pct = round(passed / total * 100, 1) if total else 0.0
    return {"total": total, "passed": passed, "pct": pct}


def _grade_totals(results: list[dict[str, Any]]) -> Counter:
    """Aggregate grade_counts across all results."""
    totals: Counter = Counter()
    for r in results:
        gc = r.get("grade_counts") or {}
        for grade, count in gc.items():
            totals[grade] += count
    return totals


# ---------------------------------------------------------------------------
# find_latest_results
# ---------------------------------------------------------------------------

def find_latest_results(results_dir: Path | None = None) -> list[dict[str, Any]] | None:
    """Find the most recent ``results/*.json`` and return parsed list, or None."""
    d = results_dir or _RESULTS_DIR
    if not d.is_dir():
        return None
    candidates = sorted(d.glob("*.json"), key=lambda p: p.stat().st_mtime)
    if not candidates:
        return None
    with candidates[-1].open() as f:
        return json.load(f)


# ---------------------------------------------------------------------------
# Terminal summary
# ---------------------------------------------------------------------------

def print_terminal_summary(results: list[dict[str, Any]]) -> None:
    """Print a formatted summary to the terminal."""
    total_checks = sum(r.get("pass_count", 0) + r.get("fail_count", 0) for r in results)
    total_duration = sum(r.get("duration_seconds", 0) for r in results)
    total_scripts = len(results)
    passed_scripts = sum(1 for r in results if r.get("status") == "pass")

    # Header
    print()
    print("=" * 60)
    print("  n6-replication  --  Verification Report")
    print("=" * 60)

    # Tier breakdown
    print()
    for t in TIERS:
        ts = _tier_summary(results, t)
        if ts["total"] == 0:
            continue
        bar = _bar(ts["pct"])
        print(f"  Tier {t}:  {bar}  {ts['passed']}/{ts['total']}  ({ts['pct']}%)")

    # Overall
    print()
    overall_pct = round(passed_scripts / total_scripts * 100, 1) if total_scripts else 0
    print(f"  Overall: {_bar(overall_pct)}  {passed_scripts}/{total_scripts}  ({overall_pct}%)")

    # Grade distribution
    grades = _grade_totals(results)
    if grades:
        print()
        print("  Grade distribution:")
        for key in ("green", "orange", "white", "black"):
            if grades.get(key, 0) > 0:
                emoji = GRADE_EMOJI.get(key, key)
                print(f"    {emoji}  {key:<8} {grades[key]}")

    # Failed scripts
    failed = [r for r in results if r.get("status") != "pass"]
    if failed:
        print()
        print("  Failed scripts:")
        for r in failed:
            err = r.get("error") or "unknown"
            print(f"    - {r['id']}  ({err})")

    # Footer
    print()
    print(f"  Total checks: {total_checks}   Duration: {total_duration:.1f}s")
    print("=" * 60)
    print()


# ---------------------------------------------------------------------------
# Markdown report
# ---------------------------------------------------------------------------

def generate_markdown(results: list[dict[str, Any]]) -> str:
    """Return a markdown report string."""
    lines: list[str] = []
    now = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M UTC")

    lines.append("# n6-replication Verification Report")
    lines.append("")
    lines.append(f"Generated: {now}")
    lines.append("")

    # Tier summaries
    lines.append("## Tier Summary")
    lines.append("")
    lines.append("| Tier | Passed | Total | % |")
    lines.append("|------|--------|-------|---|")
    for t in TIERS:
        ts = _tier_summary(results, t)
        if ts["total"] == 0:
            continue
        lines.append(f"| {t} | {ts['passed']} | {ts['total']} | {ts['pct']}% |")
    lines.append("")

    # Grade distribution
    grades = _grade_totals(results)
    if grades:
        lines.append("## Grade Distribution")
        lines.append("")
        for key in ("green", "orange", "white", "black"):
            cnt = grades.get(key, 0)
            if cnt > 0:
                emoji = GRADE_EMOJI.get(key, key)
                lines.append(f"- {emoji} **{key}**: {cnt}")
        lines.append("")

    # Per-tier tables
    for t in TIERS:
        subset = [r for r in results if r.get("tier") == t]
        if not subset:
            continue
        lines.append(f"## Tier {t} Details")
        lines.append("")
        lines.append("| ID | Status | Pass | Fail | Duration |")
        lines.append("|----|--------|------|------|----------|")
        for r in subset:
            status_mark = "PASS" if r.get("status") == "pass" else "FAIL"
            lines.append(
                f"| {r['id']} | {status_mark} "
                f"| {r.get('pass_count', 0)} | {r.get('fail_count', 0)} "
                f"| {r.get('duration_seconds', 0):.1f}s |"
            )
        lines.append("")

    return "\n".join(lines)


# ---------------------------------------------------------------------------
# HTML report
# ---------------------------------------------------------------------------

def generate_html(results: list[dict[str, Any]]) -> str:
    """Render the Jinja2 HTML template and return an HTML string."""
    from jinja2 import Environment, FileSystemLoader

    env = Environment(
        loader=FileSystemLoader(str(_TEMPLATE_DIR)),
        autoescape=True,
    )
    template = env.get_template("report.html")

    tier_summary = {}
    for t in TIERS:
        ts = _tier_summary(results, t)
        if ts["total"] > 0:
            tier_summary[t] = ts

    grades = dict(_grade_totals(results))
    now = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M UTC")

    return template.render(
        results=results,
        tier_summary=tier_summary,
        grades=grades,
        generated=now,
    )


# ---------------------------------------------------------------------------
# generate_report  (save to file)
# ---------------------------------------------------------------------------

def generate_report(
    results: list[dict[str, Any]],
    fmt: str = "terminal",
    results_dir: Path | None = None,
) -> int:
    """Generate and save a report.  Returns 0 on success."""
    d = results_dir or _RESULTS_DIR
    d.mkdir(parents=True, exist_ok=True)

    if fmt == "terminal":
        print_terminal_summary(results)
        return 0

    if fmt in ("md", "markdown"):
        content = generate_markdown(results)
        out = d / "report.md"
        out.write_text(content, encoding="utf-8")
        print(f"Report saved to {out}")
        return 0

    if fmt == "html":
        content = generate_html(results)
        out = d / "report.html"
        out.write_text(content, encoding="utf-8")
        print(f"Report saved to {out}")
        return 0

    print(f"Unknown format: {fmt}")
    return 1
