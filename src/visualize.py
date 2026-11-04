from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
try:
    from .process_data import load_data, summarize
except ImportError:
    from process_data import load_data, summarize

ROOT = Path(__file__).resolve().parent.parent
INPUT = ROOT / "data" / "raw" / "test_run.jsonl"
FIGURES_DIR = ROOT / "reports" / "figures"


def create_figures(show=False):
    # Load benchmark data
    df = load_data(INPUT)

    # Exclude warm-up and failed runs
    evaluation = df[
        (df["phase"] == "evaluation") &
        (df["success"] == True)
    ].copy()

    if evaluation.empty:
        raise ValueError("No successful evaluation runs found.")

    latencies = evaluation["latency_ms"].to_numpy(dtype=float)

    stats = summarize(df)
    mean_latency = stats['mean_ms']
    ci_lower, ci_upper = stats['ci95_lower_ms'], stats['ci95_upper_ms']

    FIGURES_DIR.mkdir(parents=True, exist_ok=True)

    # Figure 1: Latency across runs
    fig, ax = plt.subplots(figsize=(10, 5))

    ax.plot(
        evaluation["run_id"],
        evaluation["latency_ms"],
        marker="o",
        linestyle="-",
        color="#0072B2",
        label="Evaluation latency"
    )

    ax.axhline(
        mean_latency,
        color="#D55E00",
        linestyle="--",
        label=f"Mean: {mean_latency:.2f} ms"
    )

    ax.axhspan(
        ci_lower, ci_upper,
        color="#009E73",
        alpha=0.18,
        label="95% CI (mean)"
    )

    ax.set_title("Benchmark Execution Latency")
    ax.set_xlabel("Evaluation Run ID")
    ax.set_ylabel("Execution Time (ms)")
    ax.legend()
    ax.grid(True, alpha=0.3)

    fig.tight_layout()
    fig.savefig(
        FIGURES_DIR / "fig1_latency_runs.png",
        dpi=300
    )
    fig.savefig(
        FIGURES_DIR / "fig1_latency_runs.pdf"
    )
    if show:
        plt.show()
    plt.close(fig)

    # Figure 2: Boxplot
    fig, ax = plt.subplots(figsize=(7, 6))

    ax.boxplot(
        latencies,
        positions=[1],
        widths=0.4,
        patch_artist=True,
        boxprops=dict(facecolor="#56B4E9", alpha=0.6),
        medianprops=dict(color="#D55E00", linewidth=2)
    )

    ax.errorbar(
        1.35,
        mean_latency,
        yerr=[
            [mean_latency - ci_lower],
            [ci_upper - mean_latency]
        ],
        fmt="D",
        color="#009E73",
        capsize=6,
        label="Mean ± 95% CI"
    )

    ax.set_title("Distribution of Benchmark Execution Time")
    ax.set_ylabel("Execution Time (ms)")
    ax.set_xticks([1])
    ax.set_xticklabels([f"Evaluation Runs (n={len(latencies)})"])
    ax.set_xlabel("Measurement group (dimensionless)")
    ax.set_xlim(0.5, 1.8)
    ax.grid(axis="y", alpha=0.3)
    ax.legend()

    fig.tight_layout()
    fig.savefig(
        FIGURES_DIR / "fig2_distribution_boxplot.png",
        dpi=300
    )
    fig.savefig(
        FIGURES_DIR / "fig2_distribution_boxplot.pdf"
    )
    if show:
        plt.show()
    plt.close(fig)

    print("Scientific figures generated successfully!")
    print(f"Saved to: {FIGURES_DIR.relative_to(ROOT)}")

def create_load_comparison(show=False):
    """Plot Baseline vs Proposed latency across load sizes."""

    summary_path = (
        ROOT / "data" / "processed" /
        "method_comparison_summary.csv"
    )

    df = pd.read_csv(summary_path)
    FIGURES_DIR.mkdir(parents=True, exist_ok=True)

    fig, ax = plt.subplots(figsize=(9, 6))

    styles = {
        "Baseline": {
            "color": "#D55E00",
            "marker": "o",
            "linestyle": "-"
        },
        "Proposed": {
            "color": "#0072B2",
            "marker": "s",
            "linestyle": "--"
        }
    }

    for method, style in styles.items():
        data = df[df["method"] == method].sort_values(
            "load_size"
        )

        x = data["load_size"].to_numpy()
        y = data["mean_ms"].to_numpy()

        lower = data["ci95_lower_ms"].to_numpy()
        upper = data["ci95_upper_ms"].to_numpy()

        ax.plot(
            x, y,
            label=method,
            linewidth=2,
            markersize=7,
            **style
        )

        ax.errorbar(x, y, yerr=[y - lower, upper - y],
                    fmt='none', ecolor=style['color'], capsize=5, linewidth=1.5)

        ax.fill_between(
            x,
            lower,
            upper,
            color=style["color"],
            alpha=0.18
        )

    ax.set_xscale("log")
    ax.set_yscale("log")

    ax.set_title("Processing Latency vs Dataset Size")
    ax.set_xlabel("Dataset Size (rows)")
    ax.set_ylabel("Mean Processing Latency (ms)")

    ax.set_xticks([8, 80, 800, 8000])
    ax.set_xticklabels(["8", "80", "800", "8,000"])

    ax.grid(True, which="both", alpha=0.25)
    ax.legend()

    fig.tight_layout()

    fig.savefig(
        FIGURES_DIR / "fig1_latency_vs_load.png",
        dpi=300,
        bbox_inches="tight"
    )

    fig.savefig(
        FIGURES_DIR / "fig1_latency_vs_load.pdf",
        bbox_inches="tight"
    )

    if show:
        plt.show()
    plt.close(fig)

    print("Load comparison figure generated successfully!")

if __name__ == "__main__":
    create_figures()
    create_load_comparison()
