"""Regenerate the repository figures (architecture, geometry, PAC bound).

The benchmark figure (figure4) is produced by benchmark_scaling.py.
Run:  python benchmarks/generate_figures.py
"""

from __future__ import annotations

import math
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

FIG = Path(__file__).resolve().parents[1] / "figures"
FIG.mkdir(exist_ok=True)


def figure1_architecture() -> None:
    fig, ax = plt.subplots(figsize=(8.4, 3.0))
    ax.axis("off")
    boxes = [
        (0.02, "External optimiser\n(EA, solver, simulator,\nhuman engineering rule)"),
        (0.27, "Candidate x0\n+ declared certificate\n(weights, multipliers)"),
        (0.52, "cert-pareto checker\nexact | tolerance | robust\n| PAC audit"),
        (0.77, "Certificate artefact\nJSON + SHA-256\n+ typed verdict"),
    ]
    for x, text in boxes:
        ax.add_patch(plt.Rectangle((x, 0.42), 0.21, 0.42, fill=False, linewidth=1.2))
        ax.text(x + 0.105, 0.63, text, ha="center", va="center", fontsize=8.6)
    for x in (0.23, 0.48, 0.73):
        ax.annotate("", xy=(x + 0.04, 0.63), xytext=(x, 0.63),
                    arrowprops=dict(arrowstyle="->", lw=1.1))
    ax.text(0.5, 0.13,
            "The checker verifies a supplied claim and never generates the frontier;\n"
            "a failed certificate refutes the certificate, not the candidate.",
            ha="center", fontsize=9)
    ax.set_xlim(0, 1)
    ax.set_ylim(0, 1)
    fig.tight_layout()
    fig.savefig(FIG / "figure1_architecture.png", dpi=300, bbox_inches="tight")
    plt.close(fig)


def figure2_unsupported_geometry() -> None:
    """The defining picture: the supporting line through C fails.

    A and B are supported extremes on the segment f1 + f2 = 1. C = (0.6, 0.6)
    is Pareto-efficient yet strictly above that segment, so for equal weights
    the level line of the scalarisation through C (f1 + f2 = 1.2) has both A
    and B strictly below it: they are the violators every weighted-sum
    certificate for C must report. D is dominated, for contrast.
    """
    fig, ax = plt.subplots(figsize=(5.6, 4.4))
    pts = {"A": (0, 1), "B": (1, 0), "C": (0.6, 0.6), "D": (1.5, 1.5)}
    style = {"A": ("o", "supported, efficient"), "B": ("s", "supported, efficient"),
             "C": ("^", "efficient, unsupported"), "D": ("x", "dominated")}
    offsets = {"A": (8, 6), "B": (10, -4), "C": (8, 6), "D": (-10, 4)}
    for label, (x, y) in pts.items():
        marker, _ = style[label]
        ax.scatter([x], [y], marker=marker, s=75, zorder=3,
                   color="black" if label != "C" else "tab:red")
        ha = "right" if label == "D" else "left"
        ax.annotate(f"{label} {style[label][1]}", (x, y), textcoords="offset points",
                    xytext=offsets[label], fontsize=8.6, ha=ha)
    xs = [-0.1, 1.35]
    ax.plot(xs, [1 - v for v in xs], linestyle="-", linewidth=1.1, color="tab:blue",
            label="hull face through A, B:  f1 + f2 = 1")
    ax.plot(xs, [1.2 - v for v in xs], linestyle="--", linewidth=1.3, color="tab:red",
            label="certificate level at C:  f1 + f2 = 1.2")
    ax.fill_between(xs, [1 - v for v in xs], [1.2 - v for v in xs],
                    color="tab:red", alpha=0.08)
    ax.annotate("A and B lie below C's level line:\nthe certificate for C fails here",
                xy=(0.12, 0.97), xytext=(0.45, 1.40), fontsize=8.6,
                arrowprops=dict(arrowstyle="->", lw=0.9))
    ax.set_xlabel("Objective 1 (minimise)")
    ax.set_ylabel("Objective 2 (minimise)")
    ax.set_xlim(-0.12, 1.75)
    ax.set_ylim(-0.12, 1.75)
    ax.grid(True, linewidth=0.3)
    ax.legend(frameon=False, fontsize=8, loc="lower left")
    ax.set_title("Why notCertifiedByThisCertificate is not notPareto", fontsize=10)
    fig.tight_layout()
    fig.savefig(FIG / "figure2_unsupported_geometry.png", dpi=300, bbox_inches="tight")
    plt.close(fig)


def figure3_pac_bounds() -> None:
    fig, ax = plt.subplots(figsize=(5.4, 3.8))
    Ms = list(range(50, 1001, 10))
    for delta, ls in [(0.1, "-"), (0.05, "--"), (0.01, ":")]:
        ax.plot(Ms, [math.log(1 / delta) / M for M in Ms], ls, label=f"delta = {delta}")
    ax.scatter([300], [math.log(20) / 300], zorder=3, color="black", s=28)
    ax.annotate("M = 300, delta = 0.05:\nepsilon = 0.00999", (300, math.log(20) / 300),
                textcoords="offset points", xytext=(12, 14), fontsize=8.4)
    ax.set_xlabel("Audit sample size M (zero violations observed)")
    ax.set_ylabel("Certified bound on violator mass epsilon")
    ax.set_title("Zero-violation bound epsilon = ln(1/delta) / M", fontsize=10)
    ax.grid(True, linewidth=0.3)
    ax.legend(frameon=False, fontsize=8)
    fig.tight_layout()
    fig.savefig(FIG / "figure3_pac_bounds.png", dpi=300, bbox_inches="tight")
    plt.close(fig)


if __name__ == "__main__":
    figure1_architecture()
    figure2_unsupported_geometry()
    figure3_pac_bounds()
    print("figures written to", FIG)
