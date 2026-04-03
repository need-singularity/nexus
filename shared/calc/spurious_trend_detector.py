#!/usr/bin/env python3
"""
spurious_trend_detector.py -- Detects spurious correlations from shared monotonic trends.

When two quantities both increase over training epochs, high correlation is
expected BY CONSTRUCTION. This tool detrends and tests for genuine association.

Usage:
  python3 calc/spurious_trend_detector.py --file experiment_data.json
  python3 calc/spurious_trend_detector.py --x "1,2,3,4,5" --y "0.8,0.85,0.9,0.93,0.95" --epochs "1,2,3,4,5"
"""
import argparse
import numpy as np
from scipy import stats


def detrend_linear(series):
    """Remove linear trend from a time series."""
    n = len(series)
    x = np.arange(n)
    slope, intercept, _, _, _ = stats.linregress(x, series)
    return series - (slope * x + intercept), slope


def detect_spurious(x, y, epochs=None, label=""):
    """Test whether correlation between x and y is spurious due to shared trend."""
    x, y = np.array(x, dtype=float), np.array(y, dtype=float)
    n = len(x)
    if epochs is None:
        epochs = np.arange(n)
    else:
        epochs = np.array(epochs, dtype=float)

    print(f"{'='*65}")
    print(f"Spurious Trend Detector")
    print(f"{'='*65}")
    if label:
        print(f"Label: {label}")
    print(f"n = {n} data points")
    print()

    # 1. Raw correlation
    r_raw, p_raw = stats.spearmanr(x, y)
    print(f"[1] Raw Spearman:       r = {r_raw:.4f},  p = {p_raw:.6f}")

    # 2. Monotonicity check
    x_mono = all(x[i] <= x[i+1] for i in range(n-1)) or all(x[i] >= x[i+1] for i in range(n-1))
    y_mono = all(y[i] <= y[i+1] for i in range(n-1)) or all(y[i] >= y[i+1] for i in range(n-1))
    print(f"\n[2] Monotonicity check:")
    print(f"    x is monotonic: {x_mono}")
    print(f"    y is monotonic: {y_mono}")
    if x_mono and y_mono:
        print(f"    WARNING: Both series monotonic -> high correlation EXPECTED by construction")

    # 3. Trend strength
    r_x_epoch, _ = stats.spearmanr(epochs, x)
    r_y_epoch, _ = stats.spearmanr(epochs, y)
    print(f"\n[3] Trend with time:")
    print(f"    x vs epoch: r = {r_x_epoch:.4f}")
    print(f"    y vs epoch: r = {r_y_epoch:.4f}")
    trend_strength = abs(r_x_epoch) * abs(r_y_epoch)
    print(f"    Shared trend strength: {trend_strength:.4f}")
    if trend_strength > 0.5:
        print(f"    WARNING: Strong shared trend (>{0.5:.1f}) -> spurious correlation likely")

    # 4. Detrended correlation (remove linear epoch trend)
    x_dt, x_slope = detrend_linear(x)
    y_dt, y_slope = detrend_linear(y)
    r_dt, p_dt = stats.spearmanr(x_dt, y_dt)
    print(f"\n[4] Detrended Spearman:  r = {r_dt:.4f},  p = {p_dt:.6f}")
    print(f"    x trend removed: slope = {x_slope:.6f}")
    print(f"    y trend removed: slope = {y_slope:.6f}")

    drop = abs(r_raw) - abs(r_dt)
    print(f"    Correlation drop after detrending: {drop:.4f}")
    if drop > 0.3:
        print(f"    ALERT: Large drop ({drop:.2f}) -> raw correlation was trend-inflated")

    # 5. First-difference correlation (dx[i] = x[i+1] - x[i])
    if n > 3:
        dx = np.diff(x)
        dy = np.diff(y)
        r_diff, p_diff = stats.spearmanr(dx, dy)
        print(f"\n[5] First-difference:    r = {r_diff:.4f},  p = {p_diff:.6f}")
        print(f"    Tests: do CHANGES in x associate with CHANGES in y?")
        if abs(r_diff) < 0.3:
            print(f"    NOTE: Weak first-difference correlation -> changes are NOT associated")
    else:
        r_diff, p_diff = 0, 1
        print(f"\n[5] First-difference: n={n} too small for meaningful diff analysis")

    # 6. Autocorrelation (Durbin-Watson proxy)
    if n > 4:
        resid_x = x_dt
        dw_x = np.sum(np.diff(resid_x)**2) / np.sum(resid_x**2) if np.sum(resid_x**2) > 0 else 2
        resid_y = y_dt
        dw_y = np.sum(np.diff(resid_y)**2) / np.sum(resid_y**2) if np.sum(resid_y**2) > 0 else 2
        print(f"\n[6] Autocorrelation (Durbin-Watson, ideal=2.0):")
        print(f"    DW(x residuals) = {dw_x:.3f}")
        print(f"    DW(y residuals) = {dw_y:.3f}")
        if dw_x < 1.0 or dw_y < 1.0:
            print(f"    WARNING: Strong positive autocorrelation -> observations NOT independent")
    print()

    # Verdict
    print("VERDICT:")
    spurious = False
    reasons = []
    if x_mono and y_mono:
        reasons.append("both series monotonic")
        spurious = True
    if trend_strength > 0.5 and drop > 0.3:
        reasons.append(f"shared trend inflates r by {drop:.2f}")
        spurious = True
    if abs(r_diff) < 0.3 and n > 3:
        reasons.append("first-differences not correlated")
        spurious = True

    if spurious:
        print(f"  LIKELY SPURIOUS — {'; '.join(reasons)}")
        print(f"  Raw r={r_raw:.3f} is inflated. Detrended r={r_dt:.3f} is more reliable.")
        print(f"  Recommendation: detrend, use first-differences, or test across independent runs")
    else:
        print(f"  LIKELY GENUINE — raw r={r_raw:.3f}, detrended r={r_dt:.3f}")
        print(f"  Correlation survives detrending")
    print(f"{'='*65}")

    return {
        "r_raw": r_raw, "p_raw": p_raw,
        "r_detrended": r_dt, "p_detrended": p_dt,
        "r_firstdiff": r_diff, "p_firstdiff": p_diff,
        "likely_spurious": spurious, "reasons": reasons
    }


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Spurious Trend Detector")
    parser.add_argument("--x", type=str, help="Comma-separated x values (e.g., tension_mean per epoch)")
    parser.add_argument("--y", type=str, help="Comma-separated y values (e.g., accuracy per epoch)")
    parser.add_argument("--epochs", type=str, help="Comma-separated epoch numbers (optional)")
    parser.add_argument("--label", type=str, default="", help="Label for output")
    parser.add_argument("--demo", action="store_true", help="Run demo with synthetic monotonic data")
    args = parser.parse_args()

    if args.demo:
        print("DEMO: Two independent monotonic series (should detect spurious)\n")
        np.random.seed(42)
        epochs = np.arange(20)
        x = 0.5 + 0.1 * epochs + np.random.normal(0, 0.05, 20)  # monotonic + noise
        y = 0.3 + 0.03 * epochs + np.random.normal(0, 0.02, 20)  # monotonic + noise
        detect_spurious(x, y, epochs, "Synthetic monotonic (expect: SPURIOUS)")
    elif args.x and args.y:
        x = [float(v) for v in args.x.split(",")]
        y = [float(v) for v in args.y.split(",")]
        epochs = [float(v) for v in args.epochs.split(",")] if args.epochs else None
        detect_spurious(x, y, epochs, args.label)
    else:
        parser.print_help()
