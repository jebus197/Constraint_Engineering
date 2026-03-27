"""
Decay curve analysis for CDSFL bench test results.

Fits geometric and Duane (NHPP power-law) models to per-round finding counts.
Computes the D metric (inverse half-life) for the capability fingerprint.
Duane gamma < 1 = convergent (genuine analysis). gamma >= 1 = churn.

Usage:
    python3 bench/decay_analysis.py                    # analyse current results
    python3 bench/decay_analysis.py --results-dir DIR  # analyse specific dir
"""

import json
import sys
import numpy as np
from pathlib import Path
from scipy.optimize import curve_fit
from scipy.special import gammaln

REVIEWERS = ("cc", "deepseek", "cx", "gemini", "chatgpt")

def _geometric(n, A, lam):
    """Geometric decay: f(n) = A * exp(-lam * n)"""
    return A * np.exp(-lam * n)

def _duane_cumulative(n, alpha, gamma):
    """Duane cumulative: N(n) = alpha * n^gamma"""
    return alpha * np.power(n, gamma)

def _aic(k, sse, n):
    """AIC from sum of squared errors. k=params, n=data points."""
    if sse <= 0 or n <= k:
        return float('inf')
    return n * np.log(sse / n) + 2 * k

def _aicc(k, sse, n):
    """AICc (corrected AIC for small samples)."""
    aic = _aic(k, sse, n)
    if n - k - 1 <= 0:
        return aic  # fallback to plain AIC
    return aic + (2 * k * (k + 1)) / (n - k - 1)

def fit_geometric(rounds_data):
    """Fit geometric decay to per-round finding counts."""
    # rounds_data = [5, 3, 2, 1, 0]
    n = len(rounds_data)
    if n < 2:
        return {"model": "geometric", "params": {}, "sse": float('inf'), "aicc": float('inf'), "status": "insufficient_data"}

    x = np.arange(1, n + 1, dtype=float)
    y = np.array(rounds_data, dtype=float)

    try:
        popt, _ = curve_fit(_geometric, x, y, p0=[max(y.max(), 1), 0.5],
                           bounds=([0, 0], [1000, 10]), maxfev=5000)
        A, lam = popt
        y_pred = _geometric(x, A, lam)
        sse = np.sum((y - y_pred) ** 2)
        aicc = _aicc(2, sse, n)
        half_life = np.log(2) / lam if lam > 0.001 else float('inf')
        return {
            "model": "geometric",
            "params": {"A": round(float(A), 4), "lambda": round(float(lam), 4)},
            "half_life": round(float(half_life), 2),
            "sse": round(float(sse), 4),
            "aicc": round(float(aicc), 4),
            "status": "ok"
        }
    except Exception as e:
        return {"model": "geometric", "params": {}, "sse": float('inf'), "aicc": float('inf'), "status": f"fit_failed: {e}"}

def fit_duane(rounds_data):
    """Fit Duane NHPP power-law to cumulative finding counts."""
    n = len(rounds_data)
    if n < 2:
        return {"model": "duane", "params": {}, "sse": float('inf'), "aicc": float('inf'), "status": "insufficient_data"}

    # Convert per-round to cumulative
    cumulative = np.cumsum(rounds_data).astype(float)
    x = np.arange(1, n + 1, dtype=float)

    if cumulative[-1] == 0:
        return {"model": "duane", "params": {"alpha": 0, "gamma": 0}, "sse": 0, "aicc": float('inf'), "status": "no_findings"}

    try:
        popt, _ = curve_fit(_duane_cumulative, x, cumulative,
                           p0=[cumulative[-1], 0.5],
                           bounds=([0, 0.01], [10000, 5]),
                           maxfev=5000)
        alpha, gamma = popt
        y_pred = _duane_cumulative(x, alpha, gamma)
        sse = np.sum((cumulative - y_pred) ** 2)
        aicc = _aicc(2, sse, n)

        # Interpretation
        if gamma < 1:
            interpretation = "convergent"
        elif gamma > 1.1:
            interpretation = "churn"
        else:
            interpretation = "borderline"

        return {
            "model": "duane",
            "params": {"alpha": round(float(alpha), 4), "gamma": round(float(gamma), 4)},
            "gamma_interpretation": interpretation,
            "sse": round(float(sse), 4),
            "aicc": round(float(aicc), 4),
            "status": "ok"
        }
    except Exception as e:
        return {"model": "duane", "params": {}, "sse": float('inf'), "aicc": float('inf'), "status": f"fit_failed: {e}"}

def fit_best(rounds_data):
    """Run both fits, compare AICc, return the better model."""
    geo = fit_geometric(rounds_data)
    duane = fit_duane(rounds_data)

    if len(rounds_data) < 3:
        return {
            "best": "insufficient_data",
            "geometric": geo,
            "duane": duane,
            "aicc_diff": 0,
            "interpretation": "insufficient_data",
            "rounds_data": rounds_data,
        }

    aicc_diff = geo["aicc"] - duane["aicc"]  # positive = Duane better

    if duane["aicc"] < geo["aicc"]:
        best = "duane"
    else:
        best = "geometric"

    # Overall interpretation from best model
    if best == "duane":
        interpretation = duane.get("gamma_interpretation", "unknown")
    else:
        lam = geo.get("params", {}).get("lambda", 0)
        if lam > 0.1:
            interpretation = "convergent"
        elif lam < 0.02:
            interpretation = "churn"
        else:
            interpretation = "borderline"

    return {
        "best": best,
        "geometric": geo,
        "duane": duane,
        "aicc_diff": round(float(aicc_diff), 4),
        "interpretation": interpretation,
        "rounds_data": rounds_data,
    }

def compute_d_score(rounds_data):
    """Compute D metric: inverse half-life from best-fitting model. Higher = steeper decay."""
    result = fit_best(rounds_data)

    if result["interpretation"] == "churn":
        return 0.0
    if result["interpretation"] == "insufficient_data":
        return -1.0  # sentinel

    if result["best"] == "geometric":
        hl = result["geometric"].get("half_life", float('inf'))
        return round(1.0 / hl, 4) if hl > 0 and hl != float('inf') else 0.0
    else:
        # For Duane, approximate half-life from gamma
        gamma = result["duane"]["params"].get("gamma", 1)
        alpha = result["duane"]["params"].get("alpha", 0)
        if gamma >= 1 or alpha == 0:
            return 0.0
        # Half-life approximation: round where intensity drops to 50% of round 1
        # lambda(n) = alpha*gamma*n^(gamma-1). lambda(n)/lambda(1) = n^(gamma-1) = 0.5
        # n = 0.5^(1/(gamma-1))
        try:
            hl = 0.5 ** (1.0 / (gamma - 1))
            return round(1.0 / hl, 4) if hl > 0 else 0.0
        except:
            return 0.0

def analyse_task_results(result_path):
    """Analyse a single task result JSON file."""
    data = json.loads(Path(result_path).read_text())

    task_id = data.get("task_id", "unknown")
    condition = data.get("condition", "unknown")
    rounds = data.get("rounds", [])

    if not rounds:
        return {"task_id": task_id, "condition": condition, "status": "no_rounds"}

    # Extract per-model per-round finding counts
    model_curves = {}
    for reviewer in REVIEWERS:
        curve = []
        for rd in rounds:
            rd_data = rd.get(reviewer, {})
            if rd.get("round_type") == "blind" or rd.get("round_type") == "self-iterate":
                count = len(rd_data.get("findings", []))
            else:  # confer
                count = len(rd_data.get("confer_response", {}).get("new_findings", []))
            curve.append(count)
        if any(c > 0 for c in curve):  # skip models that found nothing
            model_curves[reviewer] = curve

    # Fit each model
    model_analysis = {}
    for model, curve in model_curves.items():
        fit = fit_best(curve)
        fit["d_score"] = compute_d_score(curve)
        model_analysis[model] = fit

    # Aggregate gamma across models (domain characterisation)
    gammas = [
        ma["duane"]["params"].get("gamma", 1.0)
        for ma in model_analysis.values()
        if ma["duane"].get("status") == "ok"
    ]

    return {
        "task_id": task_id,
        "condition": condition,
        "models": model_analysis,
        "aggregate_gamma": round(float(np.mean(gammas)), 4) if gammas else None,
        "convergent_models": sum(1 for ma in model_analysis.values() if ma.get("interpretation") == "convergent"),
        "churn_models": sum(1 for ma in model_analysis.values() if ma.get("interpretation") == "churn"),
        "total_models_with_data": len(model_analysis),
    }

def analyse_full_bench(results_dir):
    """Analyse all task result files in a directory."""
    results_dir = Path(results_dir)
    all_results = []

    for f in sorted(results_dir.glob("*_result.json")):
        try:
            analysis = analyse_task_results(f)
            all_results.append(analysis)
        except Exception as e:
            all_results.append({"file": str(f), "error": str(e)})

    # Aggregate by condition
    condition_stats = {}
    for r in all_results:
        cond = r.get("condition", "unknown")
        if cond not in condition_stats:
            condition_stats[cond] = {"runs": 0, "convergent": 0, "churn": 0, "gammas": [], "d_scores": []}
        stats = condition_stats[cond]
        stats["runs"] += 1
        stats["convergent"] += r.get("convergent_models", 0)
        stats["churn"] += r.get("churn_models", 0)
        if r.get("aggregate_gamma") is not None:
            stats["gammas"].append(r["aggregate_gamma"])
        for model_data in r.get("models", {}).values():
            d = model_data.get("d_score", -1)
            if d >= 0:
                stats["d_scores"].append(d)

    # Compute condition averages
    for cond, stats in condition_stats.items():
        stats["avg_gamma"] = round(float(np.mean(stats["gammas"])), 4) if stats["gammas"] else None
        stats["avg_d_score"] = round(float(np.mean(stats["d_scores"])), 4) if stats["d_scores"] else None
        stats["convergence_rate"] = round(stats["convergent"] / max(stats["convergent"] + stats["churn"], 1), 4)

    return {
        "total_runs": len(all_results),
        "per_condition": condition_stats,
        "per_task": all_results,
    }

if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(description="CDSFL Decay Curve Analysis")
    parser.add_argument("--results-dir", type=str,
                       default="bench/results/round_robin_phase2",
                       help="Directory containing result JSON files")
    args = parser.parse_args()

    print(f"Analysing results in: {args.results_dir}")
    results = analyse_full_bench(args.results_dir)

    # Summary table
    print(f"\n{'='*70}")
    print(f"  DECAY CURVE ANALYSIS — {results['total_runs']} runs")
    print(f"{'='*70}")
    print(f"{'Condition':15s} | {'Runs':4s} | {'Avg γ':7s} | {'Avg D':7s} | {'Conv%':6s}")
    print(f"{'-'*50}")
    for cond in ['control', 'hil', 'cdsfl', 'cdsfl_hil']:
        stats = results['per_condition'].get(cond, {})
        if stats:
            gamma = f"{stats['avg_gamma']:.3f}" if stats.get('avg_gamma') is not None else "n/a"
            d = f"{stats['avg_d_score']:.3f}" if stats.get('avg_d_score') is not None else "n/a"
            conv = f"{stats['convergence_rate']*100:.0f}%" if stats.get('convergence_rate') is not None else "n/a"
            print(f"{cond:15s} | {stats['runs']:4d} | {gamma:>7s} | {d:>7s} | {conv:>6s}")

    # Save detailed JSON
    out_path = Path(args.results_dir) / "decay_analysis.json"
    out_path.write_text(json.dumps(results, indent=2, default=str) + "\n")
    print(f"\nDetailed analysis saved to: {out_path}")
