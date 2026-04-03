#!/usr/bin/env python3
"""Cherry-Pick Detector — Does a formula value hit a meaningful point in a band?

Many biological hypotheses pick a specific value from a wide range
(e.g., "beta brainwave = 20 Hz" when beta is 13-30 Hz). This tool checks
whether the formula is hitting a band boundary, center, quartile, or an
arbitrary interior point.

Usage:
  python3 calc/cherry_pick_detector.py --band 13,30 --value 20 --name "beta brainwave"
  python3 calc/cherry_pick_detector.py --band 60,100 --value 72 --name "heart rate"
  python3 calc/cherry_pick_detector.py --band 12,15 --value 14.72 --name "SMR"
  python3 calc/cherry_pick_detector.py --band 12,20 --value 12 --name "respiration"
  python3 calc/cherry_pick_detector.py --builtin
  python3 calc/cherry_pick_detector.py --builtin --value 14.72
"""

import argparse
import math

# ── Built-in bands database ──────────────────────────────────────────────

BUILTIN_BANDS = [
    {"name": "Delta brainwave",          "low": 0.5,  "high": 4,      "unit": "Hz"},
    {"name": "Theta brainwave",          "low": 4,    "high": 8,      "unit": "Hz"},
    {"name": "Alpha brainwave",          "low": 8,    "high": 13,     "unit": "Hz"},
    {"name": "SMR",                      "low": 12,   "high": 15,     "unit": "Hz"},
    {"name": "Beta brainwave",           "low": 13,   "high": 30,     "unit": "Hz"},
    {"name": "Gamma brainwave",          "low": 30,   "high": 100,    "unit": "Hz"},
    {"name": "Heart rate (resting)",     "low": 60,   "high": 100,    "unit": "bpm"},
    {"name": "Respiration rate",         "low": 12,   "high": 20,     "unit": "breaths/min"},
    {"name": "Blood pressure systolic",  "low": 90,   "high": 140,    "unit": "mmHg"},
    {"name": "Human hearing",            "low": 20,   "high": 20000,  "unit": "Hz"},
    {"name": "Dolphin whistle",          "low": 2000, "high": 20000,  "unit": "Hz"},
    {"name": "Body temperature",         "low": 36.1, "high": 37.2,   "unit": "C"},
]


# ── Analysis engine ──────────────────────────────────────────────────────

def analyze_band(low, high, value, name="(unnamed)", unit="", formula_range=None):
    """Analyze where a value falls within a band.

    Returns a dict with all computed metrics.
    """
    width = high - low
    midpoint = (low + high) / 2.0

    # Position within band (0.0 = low end, 1.0 = high end)
    if width == 0:
        position_frac = 0.5
    else:
        position_frac = (value - low) / width

    in_band = low <= value <= high
    dist_from_center = abs(value - midpoint)
    dist_from_low = abs(value - low)
    dist_from_high = abs(value - high)
    dist_from_center_pct = (dist_from_center / width * 100) if width > 0 else 0

    # Quartiles
    q1 = low + width * 0.25
    q2 = midpoint
    q3 = low + width * 0.75

    # Classify position
    boundary_threshold = 0.10  # within 10% of edge
    center_threshold = 0.10    # within 10% of midpoint
    quartile_threshold = 0.05  # within 5% of quartile

    at_low_boundary = position_frac <= boundary_threshold if in_band else dist_from_low / width <= boundary_threshold
    at_high_boundary = (1 - position_frac) <= boundary_threshold if in_band else dist_from_high / width <= boundary_threshold
    at_boundary = at_low_boundary or at_high_boundary
    at_center = dist_from_center_pct <= (center_threshold * 100)

    nearest_quartile = None
    nearest_quartile_dist = float('inf')
    for label, qval in [("Q1 (25%)", q1), ("Q2 (50%)", q2), ("Q3 (75%)", q3)]:
        d = abs(value - qval)
        if d < nearest_quartile_dist:
            nearest_quartile_dist = d
            nearest_quartile = label
    near_quartile = (nearest_quartile_dist / width * 100) <= (quartile_threshold * 100) if width > 0 else False

    # Position label
    if not in_band:
        if value < low:
            position_label = f"OUTSIDE (below band by {dist_from_low:.4g})"
        else:
            position_label = f"OUTSIDE (above band by {dist_from_high:.4g})"
    elif at_low_boundary:
        position_label = "at LOW boundary"
    elif at_high_boundary:
        position_label = "at HIGH boundary"
    elif at_center:
        position_label = "at CENTER"
    else:
        position_label = "interior"

    # Random hit probability
    # Estimate formula range as 0..max(high*10, 200) unless specified
    if formula_range is None:
        fr_low = 0
        fr_high = max(high * 10, 200)
    else:
        fr_low, fr_high = formula_range
    fr_width = fr_high - fr_low
    random_hit_prob = width / fr_width if fr_width > 0 else 1.0

    # Verdict
    if not in_band:
        verdict = "NO MATCH"
        verdict_detail = "Value falls outside the band entirely."
    elif at_boundary:
        verdict = "STRONG MATCH"
        edge = "low" if at_low_boundary else "high"
        verdict_detail = (f"Value sits at the {edge} boundary -- a distinguished point. "
                          f"Random chance of landing in this band: {random_hit_prob:.1%}.")
    elif at_center:
        verdict = "STRONG MATCH"
        verdict_detail = (f"Value sits near the band center -- a distinguished point. "
                          f"Random chance of landing in this band: {random_hit_prob:.1%}.")
    elif near_quartile:
        verdict = "MODERATE MATCH"
        verdict_detail = (f"Value is near {nearest_quartile} -- a semi-distinguished point. "
                          f"Random chance of landing in this band: {random_hit_prob:.1%}.")
    else:
        verdict = "WEAK MATCH"
        verdict_detail = (f"Value is interior, not at a distinguished point. "
                          f"A random value in [{fr_low}, {fr_high}] has "
                          f"{random_hit_prob:.1%} chance of landing in this band.")

    return {
        "name": name,
        "unit": unit,
        "low": low,
        "high": high,
        "value": value,
        "width": width,
        "midpoint": midpoint,
        "position_frac": position_frac,
        "position_label": position_label,
        "in_band": in_band,
        "dist_from_center": dist_from_center,
        "dist_from_center_pct": dist_from_center_pct,
        "dist_from_low": dist_from_low,
        "dist_from_high": dist_from_high,
        "at_boundary": at_boundary,
        "at_low_boundary": at_low_boundary,
        "at_high_boundary": at_high_boundary,
        "at_center": at_center,
        "near_quartile": near_quartile,
        "nearest_quartile": nearest_quartile,
        "nearest_quartile_dist": nearest_quartile_dist,
        "q1": q1,
        "q2": q2,
        "q3": q3,
        "random_hit_prob": random_hit_prob,
        "formula_range": (fr_low, fr_high),
        "verdict": verdict,
        "verdict_detail": verdict_detail,
    }


def format_result(r):
    """Format analysis result as a human-readable string."""
    u = f" {r['unit']}" if r['unit'] else ""
    lines = []
    lines.append(f"Band: {r['name']} [{r['low']}, {r['high']}]{u}")
    lines.append(f"Formula value: {r['value']}{u}")
    lines.append(f"Band width: {r['width']:.4g}{u}")
    lines.append(f"Midpoint: {r['midpoint']:.4g}{u}")
    lines.append("")

    if r['in_band']:
        lines.append(f"Position: {r['position_frac']*100:.1f}% from low end ({r['position_label']})")
    else:
        lines.append(f"Position: {r['position_label']}")
    lines.append(f"Distance from center: {r['dist_from_center']:.4g}{u} ({r['dist_from_center_pct']:.1f}% of width)")
    lines.append(f"Distance from boundaries: {r['dist_from_low']:.4g} / {r['dist_from_high']:.4g}{u}")
    lines.append("")

    # ASCII position diagram
    bar_width = 50
    lines.append(format_ascii_bar(r, bar_width))
    lines.append("")

    lines.append("Assessment:")
    lines.append(f"  At boundary?  {'YES' if r['at_boundary'] else 'NO'}"
                 f" ({'<= 10% from edge' if r['at_boundary'] else '> 10% from both edges'})")
    lines.append(f"  At center?    {'YES' if r['at_center'] else 'APPROXIMATELY' if r['dist_from_center_pct'] <= 15 else 'NO'}"
                 f" ({r['dist_from_center_pct']:.1f}% of width from midpoint)")
    lines.append(f"  At quartile?  ", )
    if r['near_quartile']:
        lines[-1] = f"  At quartile?  YES -- near {r['nearest_quartile']} ({r['nearest_quartile_dist']:.4g}{u} away)"
    else:
        lines[-1] = f"  At quartile?  Nearest: {r['nearest_quartile']} ({r['nearest_quartile_dist']:.4g}{u} away)"
    lines.append("")

    fr = r['formula_range']
    lines.append(f"Random hit probability: {r['width']:.4g}/{fr[1]-fr[0]:.4g} = {r['random_hit_prob']:.1%}"
                 f" (if formula range is [{fr[0]}, {fr[1]}])")
    lines.append("")
    lines.append(f"Verdict: {r['verdict']} -- {r['verdict_detail']}")
    return "\n".join(lines)


def format_ascii_bar(r, bar_width=50):
    """Draw an ASCII bar showing value position within band."""
    low, high, value = r['low'], r['high'], r['value']
    width = high - low
    if width == 0:
        return "  [=== zero-width band ===]"

    # Determine display range (extend slightly beyond band)
    margin = width * 0.15
    disp_low = low - margin
    disp_high = high + margin
    disp_width = disp_high - disp_low

    def to_pos(v):
        frac = (v - disp_low) / disp_width
        return max(0, min(bar_width - 1, int(frac * (bar_width - 1))))

    band_start = to_pos(low)
    band_end = to_pos(high)
    mid_pos = to_pos((low + high) / 2)
    val_pos = to_pos(value)

    # Build bar
    bar = [' '] * bar_width
    for i in range(band_start, band_end + 1):
        bar[i] = '-'
    bar[band_start] = '['
    bar[band_end] = ']'
    if band_start < mid_pos < band_end:
        bar[mid_pos] = '|'

    # Value marker on separate line
    marker_line = [' '] * bar_width
    if 0 <= val_pos < bar_width:
        marker_line[val_pos] = '^'

    lines = []
    lines.append("  " + "".join(bar))
    lines.append("  " + "".join(marker_line))

    # Labels
    label_line = [' '] * bar_width
    low_s = f"{low:.4g}"
    high_s = f"{high:.4g}"
    val_s = f"{value:.4g}"

    # Place low label
    for i, c in enumerate(low_s):
        pos = band_start + i
        if 0 <= pos < bar_width:
            label_line[pos] = c
    # Place high label
    start = max(0, band_end - len(high_s) + 1)
    for i, c in enumerate(high_s):
        pos = start + i
        if 0 <= pos < bar_width:
            label_line[pos] = c

    lines.append("  " + "".join(label_line))

    return "\n".join(lines)


# ── Summary table for --builtin ──────────────────────────────────────────

def format_summary_table(results):
    """Format a compact summary table for multiple band analyses."""
    lines = []
    lines.append("")
    lines.append("=" * 78)
    lines.append("  SUMMARY TABLE")
    lines.append("=" * 78)
    lines.append("")

    hdr = f"{'Band':<28} {'Value':>8} {'Band':>12} {'Pos%':>6} {'Verdict':<16}"
    lines.append(hdr)
    lines.append("-" * 78)

    for r in results:
        band_str = f"[{r['low']:.4g},{r['high']:.4g}]"
        pos_str = f"{r['position_frac']*100:.1f}%" if r['in_band'] else "OUT"
        lines.append(f"{r['name']:<28} {r['value']:>8.4g} {band_str:>12} {pos_str:>6} {r['verdict']:<16}")

    lines.append("-" * 78)

    # Counts
    strong = sum(1 for r in results if r['verdict'] == "STRONG MATCH")
    moderate = sum(1 for r in results if r['verdict'] == "MODERATE MATCH")
    weak = sum(1 for r in results if r['verdict'] == "WEAK MATCH")
    no_match = sum(1 for r in results if r['verdict'] == "NO MATCH")
    lines.append(f"  STRONG: {strong}  MODERATE: {moderate}  WEAK: {weak}  NO MATCH: {no_match}")
    lines.append("")

    return "\n".join(lines)


# ── Main ─────────────────────────────────────────────────────────────────

def main():
    parser = argparse.ArgumentParser(
        description="Cherry-Pick Detector: checks if a formula value hits a "
                    "meaningful point within a band, or is cherry-picked."
    )
    parser.add_argument("--band", type=str, default=None,
                        help="Band as low,high (e.g., '13,30')")
    parser.add_argument("--value", type=float, default=None,
                        help="Formula value to test")
    parser.add_argument("--name", type=str, default="(unnamed)",
                        help="Name/label for the band")
    parser.add_argument("--unit", type=str, default="",
                        help="Unit label (e.g., Hz, bpm)")
    parser.add_argument("--formula-range", type=str, default=None,
                        help="Range of possible formula outputs as low,high (default: auto)")
    parser.add_argument("--builtin", action="store_true",
                        help="Test value against all built-in bands")

    args = parser.parse_args()

    formula_range = None
    if args.formula_range:
        parts = args.formula_range.split(",")
        formula_range = (float(parts[0]), float(parts[1]))

    if args.builtin:
        # Test against all built-in bands
        if args.value is None:
            print("=" * 60)
            print("  Cherry-Pick Detector -- Built-in Bands Database")
            print("=" * 60)
            print()
            for b in BUILTIN_BANDS:
                print(f"  {b['name']:<28} [{b['low']:>8.4g}, {b['high']:>8.4g}] {b['unit']}")
            print()
            print("Provide --value to test against all bands.")
            print("Example: python3 calc/cherry_pick_detector.py --builtin --value 14.72")
            return

        print("=" * 60)
        print(f"  Cherry-Pick Detector -- Testing value {args.value}")
        print(f"  against all built-in bands")
        print("=" * 60)

        results = []
        for b in BUILTIN_BANDS:
            r = analyze_band(b["low"], b["high"], args.value,
                             name=b["name"], unit=b["unit"],
                             formula_range=formula_range)
            results.append(r)
            print()
            print("-" * 60)
            print(format_result(r))

        print(format_summary_table(results))
        return

    # Single band mode
    if args.band is None or args.value is None:
        parser.print_help()
        print("\nError: --band and --value are required (or use --builtin).")
        return

    parts = args.band.split(",")
    low, high = float(parts[0]), float(parts[1])

    r = analyze_band(low, high, args.value,
                     name=args.name, unit=args.unit,
                     formula_range=formula_range)

    print()
    print("=" * 60)
    print("  Cherry-Pick Detector")
    print("=" * 60)
    print()
    print(format_result(r))
    print()


if __name__ == "__main__":
    main()
