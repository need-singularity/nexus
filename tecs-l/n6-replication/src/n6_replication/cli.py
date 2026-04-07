"""CLI for n6-replication -- run/fetch/report/list subcommands."""

import argparse
import sys
from pathlib import Path

from n6_replication import __version__


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def find_repo_root() -> Path:
    """Walk up from __file__ (then cwd) looking for a verify/ directory."""
    candidates = [Path(__file__).resolve().parent, Path.cwd()]
    for start in candidates:
        cur = start
        while cur != cur.parent:
            if (cur / "verify").is_dir():
                return cur
            cur = cur.parent
    # Fallback: return cwd even if verify/ not found
    return Path.cwd()


def _check_gpu() -> bool:
    """Return True if torch is importable (GPU available)."""
    try:
        import torch  # noqa: F401
        return True
    except ImportError:
        return False


# ---------------------------------------------------------------------------
# Subcommand handlers
# ---------------------------------------------------------------------------

def cmd_run(args: argparse.Namespace) -> int:
    """Run verification scripts for the requested tiers."""
    from n6_replication.runner import run_tier1, run_tier2_3, save_results
    from n6_replication.reporter import print_terminal_summary

    gpu = (not args.no_gpu) and _check_gpu()
    if args.verbose:
        print(f"[n6] repo root : {find_repo_root()}")
        print(f"[n6] tiers     : {args.tier}")
        print(f"[n6] parallel  : {args.parallel}")
        print(f"[n6] gpu       : {gpu}")

    all_results = []

    if 1 in args.tier:
        results_t1 = run_tier1(verbose=args.verbose)
        all_results.extend(results_t1)

    remaining = [t for t in args.tier if t in (2, 3)]
    if remaining:
        root = find_repo_root()
        results_t23 = run_tier2_3(
            tiers=remaining,
            repo_root=root,
            parallel=args.parallel,
            gpu=gpu,
            verbose=args.verbose,
        )
        all_results.extend(results_t23)

    save_results(all_results)
    print_terminal_summary(all_results)

    if args.format:
        from n6_replication.reporter import generate_report
        generate_report(all_results, fmt=args.format)

    failed = sum(1 for r in all_results if r.get("status") == "fail")
    return 1 if failed else 0


def cmd_fetch(args: argparse.Namespace) -> int:
    """Fetch (or update) Tier 3 external repos."""
    from n6_replication.fetcher import fetch_all, update_all

    if args.update:
        update_all(verbose=True)
    else:
        fetch_all(verbose=True)
    return 0


def cmd_report(args: argparse.Namespace) -> int:
    """Generate a report from the most recent results."""
    from n6_replication.reporter import generate_report, find_latest_results

    results = find_latest_results()
    if results is None:
        print("No previous results found. Run 'n6-replicate run' first.",
              file=sys.stderr)
        return 1

    generate_report(results, fmt=args.format)
    return 0


def cmd_list(args: argparse.Namespace) -> int:
    """List registered verification scripts."""
    from n6_replication.registry import load_all

    scripts = load_all(tiers=args.tier)
    if not scripts:
        print("No scripts registered for the requested tiers.")
        return 0

    # Header
    print(f"{'ID':<45} {'Tier':<6} {'GPU':<5} {'Timeout'}")
    print("-" * 70)
    for s in scripts:
        gpu_flag = "yes" if s.get("requires_gpu") else ""
        timeout = s.get("timeout", "")
        print(f"{s['id']:<45} {s.get('tier', '?'):<6} {gpu_flag:<5} {timeout}")

    print(f"\nTotal: {len(scripts)} scripts")
    return 0


# ---------------------------------------------------------------------------
# Argument parser
# ---------------------------------------------------------------------------

def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="n6-replicate",
        description=f"n6-replication v{__version__} -- "
                    "Independent replication of perfect-number-6 mathematics",
    )
    parser.add_argument(
        "--version", action="version", version=f"%(prog)s {__version__}",
    )

    sub = parser.add_subparsers(dest="command")
    sub.required = True  # compatible with Python 3.9

    # ---- run ----
    p_run = sub.add_parser("run", help="Run verification scripts")
    p_run.add_argument(
        "--tier", type=int, nargs="+", default=[1, 2],
        choices=[1, 2, 3],
        help="Tiers to run (default: 1 2)",
    )
    p_run.add_argument(
        "--parallel", type=int, default=1,
        help="Number of parallel workers (default: 1)",
    )
    p_run.add_argument(
        "--format", choices=["md", "html"], default=None,
        help="Also generate a report in this format",
    )
    p_run.add_argument(
        "--no-gpu", action="store_true",
        help="Skip scripts that require GPU",
    )
    p_run.add_argument(
        "-v", "--verbose", action="store_true",
        help="Verbose output",
    )
    p_run.set_defaults(func=cmd_run)

    # ---- fetch ----
    p_fetch = sub.add_parser("fetch", help="Fetch Tier 3 external repos")
    p_fetch.add_argument(
        "--update", action="store_true",
        help="Update already-fetched repos",
    )
    p_fetch.set_defaults(func=cmd_fetch)

    # ---- report ----
    p_report = sub.add_parser("report", help="Generate report from last run")
    p_report.add_argument(
        "--format", choices=["md", "html"], default="md",
        help="Report format (default: md)",
    )
    p_report.set_defaults(func=cmd_report)

    # ---- list ----
    p_list = sub.add_parser("list", help="List registered verification scripts")
    p_list.add_argument(
        "--tier", type=int, nargs="+", default=None,
        choices=[1, 2, 3],
        help="Filter by tier(s)",
    )
    p_list.set_defaults(func=cmd_list)

    return parser


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    return args.func(args)


if __name__ == "__main__":
    raise SystemExit(main())
