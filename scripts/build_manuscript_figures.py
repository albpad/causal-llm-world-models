#!/usr/bin/env python3
"""Build publication-grade manuscript figures from the final locked figure data."""

from __future__ import annotations

import argparse
import math
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from matplotlib.colors import LinearSegmentedColormap, ListedColormap, BoundaryNorm
from matplotlib.lines import Line2D
from matplotlib.patches import FancyArrowPatch


MODEL_ORDER = [
    "kimi-k2.5",
    "deepseek-r1",
    "qwen3-next-80b-instruct",
    "mistral-small-24b",
    "llama-3.1-8b",
]
MODEL_LABELS = {
    "kimi-k2.5": "Kimi K2.5",
    "deepseek-r1": "DeepSeek-R1",
    "qwen3-next-80b-instruct": "Qwen3-Next-80B",
    "mistral-small-24b": "Mistral-Small-24B",
    "llama-3.1-8b": "Llama 3.1-8B",
}
MODEL_COLORS = {
    "kimi-k2.5": "#0B7285",
    "deepseek-r1": "#1D3557",
    "qwen3-next-80b-instruct": "#3A7D44",
    "mistral-small-24b": "#7C5CFF",
    "llama-3.1-8b": "#B42318",
}
FIG1_STATUS_COLORS = {
    "background": "#D1D5DB",
    "soft_correct": "#4C6F8C",
    "hard_correct": "#1F3A5F",
    "wrong": "#B42318",
    "node": "#E5E7EB",
}
FAMILY_ORDER = [
    "glottic_cT2",
    "glottic_cT3",
    "supraglottic_cT3",
    "hypopharyngeal",
    "cT4a_unselected",
    "cT4a_selected",
    "cisplatin_eligibility",
    "post_ict_response",
    "elderly_frail",
    "pretreatment_function",
]
FAMILY_LABELS = {
    "glottic_cT2": "Glottic cT2",
    "glottic_cT3": "Glottic cT3",
    "supraglottic_cT3": "Supraglottic cT3",
    "hypopharyngeal": "Hypopharynx",
    "cT4a_unselected": "cT4a unselected",
    "cT4a_selected": "cT4a selected",
    "cisplatin_eligibility": "Cisplatin fitness",
    "post_ict_response": "Post-ICT response",
    "elderly_frail": "Elderly/frail",
    "pretreatment_function": "Pretreatment function",
}
FAMILY_COLORS = {
    "glottic_cT2": "#BEE3DB",
    "glottic_cT3": "#FDE68A",
    "supraglottic_cT3": "#FBCFE8",
    "hypopharyngeal": "#BFDBFE",
    "cT4a_unselected": "#FECACA",
    "cT4a_selected": "#DDD6FE",
    "cisplatin_eligibility": "#FED7AA",
    "post_ict_response": "#BBF7D0",
    "elderly_frail": "#E5E7EB",
    "pretreatment_function": "#F9A8D4",
    "cross-context": "#D6D3D1",
}
TREATMENT_ORDER = [
    "tlm",
    "tors",
    "ophl_type_i",
    "ophl_type_ii",
    "ophl_type_iib",
    "ophl_type_iii",
    "ophl_any",
    "total_laryngectomy",
    "rt_alone",
    "rt_accelerated",
    "concurrent_crt",
    "ict_rt",
    "nonsurgical_lp",
    "surgical_lp",
    "cisplatin_high_dose",
    "cetuximab_concurrent",
    "carboplatin_5fu",
]
TREATMENT_LABELS = {
    "tlm": "TLM",
    "tors": "TORS",
    "ophl_type_i": "OPHL-I",
    "ophl_type_ii": "OPHL-II",
    "ophl_type_iib": "OPHL-IIB",
    "ophl_type_iii": "OPHL-III",
    "ophl_any": "OPHL (any)",
    "total_laryngectomy": "Total laryngectomy",
    "rt_alone": "RT alone",
    "rt_accelerated": "RT accelerated",
    "concurrent_crt": "Concurrent CRT",
    "ict_rt": "ICT + RT",
    "nonsurgical_lp": "Nonsurgical LP",
    "surgical_lp": "Surgical LP",
    "cisplatin_high_dose": "High-dose cisplatin",
    "cetuximab_concurrent": "Cetuximab + RT",
    "carboplatin_5fu": "Carboplatin/5-FU",
}


def configure_style() -> None:
    plt.rcParams.update(
        {
            "font.family": "DejaVu Serif",
            "figure.facecolor": "white",
            "axes.facecolor": "white",
            "axes.spines.top": False,
            "axes.spines.right": False,
            "axes.spines.left": False,
            "axes.spines.bottom": False,
            "axes.titleweight": "bold",
            "axes.labelcolor": "#1F2937",
            "text.color": "#1F2937",
            "xtick.color": "#374151",
            "ytick.color": "#374151",
        }
    )


def load_frames(data_dir: Path) -> tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame]:
    return (
        pd.read_csv(data_dir / "figure1_edge_overlay.csv"),
        pd.read_csv(data_dir / "figure2_edge_signal.csv"),
        pd.read_csv(data_dir / "figure3_summary.csv"),
    )


def _split_labels(raw: str | float) -> list[str]:
    if not isinstance(raw, str) or not raw.strip():
        return []
    if ";" in raw:
        return [part.strip() for part in raw.split(";") if part.strip()]
    return [part.strip() for part in raw.split(",") if part.strip()]


def build_gold_edges(df_overlay: pd.DataFrame) -> list[dict]:
    edges: list[dict] = []
    seen: set[tuple[str, str, str, str]] = set()
    for _, row in df_overlay.iterrows():
        families = _split_labels(row["families"])
        recs = _split_labels(row["gold_recommendations"])
        excs = _split_labels(row["gold_exclusions"])
        for family in families:
            for treatment in recs:
                key = (row["edge_id"], family, treatment, "positive")
                if key not in seen:
                    edges.append({"edge_id": row["edge_id"], "family": family, "treatment": treatment, "sign": "positive"})
                    seen.add(key)
            for treatment in excs:
                key = (row["edge_id"], family, treatment, "negative")
                if key not in seen:
                    edges.append({"edge_id": row["edge_id"], "family": family, "treatment": treatment, "sign": "negative"})
                    seen.add(key)
    return edges


def draw_edge(ax, start, end, *, color, lw, linestyle="-", alpha=1.0, zorder=1):
    rad = 0.18 * np.sign(end[1] - start[1])
    if abs(end[1] - start[1]) < 0.08:
        rad = 0.08
    patch = FancyArrowPatch(
        start,
        end,
        arrowstyle="-",
        linewidth=lw,
        linestyle=linestyle,
        color=color,
        alpha=alpha,
        zorder=zorder,
        connectionstyle=f"arc3,rad={rad}",
        capstyle="round",
        joinstyle="round",
    )
    ax.add_patch(patch)


def build_figure1(df_overlay: pd.DataFrame, df_summary: pd.DataFrame, outdir: Path) -> None:
    gold_edges = build_gold_edges(df_overlay)
    figure, axes = plt.subplots(2, 3, figsize=(20, 13))
    figure.subplots_adjust(left=0.035, right=0.985, top=0.90, bottom=0.10, wspace=0.12, hspace=0.14)
    axes = axes.flatten()

    family_positions = {
        family: (0.14, 0.88 - idx * (0.72 / (len(FAMILY_ORDER) - 1)))
        for idx, family in enumerate(FAMILY_ORDER)
    }
    treatment_positions = {
        treatment: (0.86, 0.90 - idx * (0.76 / (len(TREATMENT_ORDER) - 1)))
        for idx, treatment in enumerate(TREATMENT_ORDER)
    }

    panels = [("gold", "Gold-standard KG1")] + [(model, MODEL_LABELS[model]) for model in MODEL_ORDER]
    summary_map = {row["model"]: row for _, row in df_summary.iterrows()}
    overlay_map = {row["edge_id"]: row for _, row in df_overlay.iterrows()}

    for ax, (model_key, title) in zip(axes, panels):
        ax.set_xlim(0, 1)
        ax.set_ylim(0, 1)
        ax.axis("off")
        ax.text(0.02, 0.985, title, ha="left", va="top", fontsize=13, fontweight="bold")
        if model_key == "gold":
            ax.text(0.02, 0.94, "58 evaluation edges from 60 statement-linked rules", ha="left", va="top", fontsize=9, color="#4B5563")
        else:
            stats = summary_map[model_key]
            ax.text(
                0.02,
                0.94,
                f"Soft recall {float(stats['soft_recall'])*100:.1f}%   SNR {float(stats['snr']):.2f}",
                ha="left",
                va="top",
                fontsize=9,
                color="#4B5563",
            )

        for family, (x, y) in family_positions.items():
            ax.scatter([x], [y], s=250, color=FIG1_STATUS_COLORS["node"], edgecolor="#9CA3AF", linewidth=0.8, zorder=5)
            label = FAMILY_LABELS[family]
            if family == "cT4a_unselected":
                label = f"{label}*"
            ax.text(x - 0.018, y, label, ha="right", va="center", fontsize=8.2)
        for treatment, (x, y) in treatment_positions.items():
            ax.scatter([x], [y], s=250, color="#F9FAFB", edgecolor="#9CA3AF", linewidth=0.8, zorder=5)
            ax.text(x + 0.018, y, TREATMENT_LABELS.get(treatment, treatment), ha="left", va="center", fontsize=7.9)

        for edge in gold_edges:
            start = family_positions[edge["family"]]
            end = treatment_positions[edge["treatment"]]
            draw_edge(
                ax,
                start,
                end,
                color=FIG1_STATUS_COLORS["background"],
                lw=0.9,
                linestyle="--" if edge["sign"] == "negative" else "-",
                alpha=0.8,
                zorder=1,
            )

        if model_key != "gold":
            for edge in gold_edges:
                row = overlay_map[edge["edge_id"]]
                soft = str(row[f"{model_key}_soft_detected"]).lower() == "true"
                hard = str(row[f"{model_key}_hard_detected"]).lower() == "true"
                direction = str(row[f"{model_key}_direction_correct"]).lower() == "true"
                if not soft and not hard:
                    continue
                if direction:
                    color = FIG1_STATUS_COLORS["hard_correct"] if hard else FIG1_STATUS_COLORS["soft_correct"]
                else:
                    color = FIG1_STATUS_COLORS["wrong"]
                lw = 2.2 if hard else 1.6
                alpha = 0.95 if hard else 0.8
                draw_edge(
                    ax,
                    family_positions[edge["family"]],
                    treatment_positions[edge["treatment"]],
                    color=color,
                    lw=lw,
                    linestyle="--" if edge["sign"] == "negative" else "-",
                    alpha=alpha,
                    zorder=3,
                )

    legend_items = [
        Line2D([0], [0], color=FIG1_STATUS_COLORS["background"], lw=1.2, label="Gold-standard edge (background)"),
        Line2D([0], [0], color=FIG1_STATUS_COLORS["soft_correct"], lw=1.6, label="Soft detected, directionally consistent"),
        Line2D([0], [0], color=FIG1_STATUS_COLORS["hard_correct"], lw=2.2, label="Hard detected, directionally consistent"),
        Line2D([0], [0], color=FIG1_STATUS_COLORS["wrong"], lw=2.0, label="Detected, wrong direction"),
        Line2D([0], [0], color="#6B7280", lw=1.2, linestyle="--", label="Dashed = contraindication / exclusion edge"),
    ]
    figure.legend(handles=legend_items, loc="lower center", ncol=3, frameon=False, fontsize=9, bbox_to_anchor=(0.5, 0.03))
    figure.text(
        0.035,
        0.018,
        "* cT4a unselected is retained as baseline/null-control context only; the final benchmark does not include a directional perturbation edge for this family.",
        ha="left",
        va="bottom",
        fontsize=8.3,
        color="#4B5563",
    )
    figure.suptitle("Figure 1. Shared-layout recovery of the gold-standard graph across five models", fontsize=15.5, fontweight="bold", y=0.965)
    figure.savefig(outdir / "figure1_kg_overlay.svg", bbox_inches="tight")
    figure.savefig(outdir / "figure1_kg_overlay.png", dpi=300, bbox_inches="tight")
    plt.close(figure)


def prepare_figure2_data(df_signal: pd.DataFrame, df_overlay: pd.DataFrame) -> tuple[pd.DataFrame, list[dict]]:
    df_signal = df_signal.copy()
    df_signal["mean_jsd"] = df_signal["mean_jsd"].astype(float)
    df_signal["hard_detected"] = df_signal["hard_detected"].astype(str).str.lower() == "true"
    df_signal["soft_detected"] = df_signal["soft_detected"].astype(str).str.lower() == "true"
    df_signal["direction_correct"] = df_signal["direction_correct"].astype(str).str.lower() == "true"

    family_by_edge = {}
    for _, row in df_overlay.iterrows():
        families = _split_labels(row["families"])
        family_by_edge[row["edge_id"]] = families[0] if len(families) == 1 else "cross-context"

    df_signal["family"] = df_signal["edge_id"].map(family_by_edge)
    ordered_families = [family for family in FAMILY_ORDER + ["cross-context"] if (df_signal["family"] == family).any()]
    family_heat = (
        df_signal.groupby(["family", "model"], as_index=False)["mean_jsd"]
        .mean()
        .pivot(index="family", columns="model", values="mean_jsd")
        .reindex(index=ordered_families, columns=MODEL_ORDER)
    )

    recovery_counts = []
    for model in MODEL_ORDER:
        sub = df_signal[df_signal["model"] == model]
        hard_correct = int((sub["hard_detected"] & sub["direction_correct"]).sum())
        soft_correct = int((sub["soft_detected"] & ~sub["hard_detected"] & sub["direction_correct"]).sum())
        wrong = int(((sub["soft_detected"] | sub["hard_detected"]) & ~sub["direction_correct"]).sum())
        not_detected = int((~sub["soft_detected"] & ~sub["hard_detected"]).sum())
        recovery_counts.append({"model": model, "hard_correct": hard_correct, "soft_correct": soft_correct, "wrong": wrong, "not_detected": not_detected})

    return family_heat, recovery_counts


def build_figure2(df_signal: pd.DataFrame, df_overlay: pd.DataFrame, outdir: Path) -> None:
    family_heat, _ = prepare_figure2_data(df_signal, df_overlay)
    ordered_families = list(family_heat.index)

    cmap = LinearSegmentedColormap.from_list("jsd_teal", ["#F8FAFC", "#D9F0F2", "#7CC6CD", "#0B7285", "#073B4C"])
    fig, ax_heat = plt.subplots(figsize=(10.4, 7.2))

    im = ax_heat.imshow(
        family_heat.values,
        aspect="auto",
        cmap=cmap,
        vmin=0,
        vmax=max(0.32, float(np.nanmax(family_heat.values))),
    )
    ax_heat.set_title("Clinical family", fontsize=13, fontweight="bold", loc="left", pad=12)
    ax_heat.set_xticks(range(len(MODEL_ORDER)))
    ax_heat.set_xticklabels(["Kimi\nK2.5", "DeepSeek\nR1", "Qwen3-\nNext 80B", "Mistral-\nSmall 24B", "Llama\n3.1-8B"], fontsize=10)
    ax_heat.set_yticks(range(len(ordered_families)))
    ax_heat.set_yticklabels([FAMILY_LABELS.get(family, "Cross-context") for family in ordered_families], fontsize=10)
    for x in range(len(MODEL_ORDER) + 1):
        ax_heat.axvline(x - 0.5, color="white", lw=1.2, alpha=0.9)
    for y in range(len(ordered_families) + 1):
        ax_heat.axhline(y - 0.5, color="white", lw=1.2, alpha=0.9)
    for yi, family in enumerate(ordered_families):
        for xi, model in enumerate(MODEL_ORDER):
            value = family_heat.loc[family, model]
            text_color = "#FFFFFF" if value >= 0.18 else "#1F2937"
            ax_heat.text(xi, yi, f"{value:.2f}", ha="center", va="center", fontsize=9.2, color=text_color, fontweight="bold")

    cbar = fig.colorbar(im, ax=ax_heat, fraction=0.046, pad=0.03)
    cbar.ax.set_ylabel("Mean edge JSD", rotation=270, labelpad=18, fontsize=10)
    fig.suptitle(
        "Figure 2. Family-level causal signal across the clinical benchmark",
        fontsize=15,
        fontweight="bold",
        y=0.985,
    )
    fig.savefig(outdir / "figure2_family_signal.svg", bbox_inches="tight")
    fig.savefig(outdir / "figure2_family_signal.png", dpi=300, bbox_inches="tight")
    plt.close(fig)


def build_figure3(df_signal: pd.DataFrame, df_overlay: pd.DataFrame, outdir: Path) -> None:
    _, recovery_counts = prepare_figure2_data(df_signal, df_overlay)
    fig, ax_status = plt.subplots(figsize=(11.2, 6.8))
    status_colors = {
        "hard_correct": "#1F3A5F",
        "soft_correct": "#9EBFD6",
        "wrong": "#D95D5D",
        "not_detected": "#ECEFF3",
    }
    ypos = np.arange(len(MODEL_ORDER))
    left = np.zeros(len(MODEL_ORDER))
    for key in ["hard_correct", "soft_correct", "wrong", "not_detected"]:
        widths = np.array([row[key] for row in recovery_counts], dtype=float)
        ax_status.barh(ypos, widths, left=left, color=status_colors[key], edgecolor="white", height=0.68)
        left += widths

    ax_status.set_title("Recovery status across 58 gold-standard evaluation edges", fontsize=13, fontweight="bold", loc="left", pad=12)
    ax_status.set_xlim(0, 73)
    ax_status.set_yticks(ypos)
    ax_status.set_yticklabels(["Kimi", "DeepSeek", "Qwen3-Next", "Mistral", "Llama"], fontsize=10.5)
    ax_status.invert_yaxis()
    ax_status.grid(axis="x", color="#E5E7EB", linewidth=0.8)
    ax_status.set_xlabel("Number of evaluation edges", fontsize=10, color="#4B5563")
    for idx, row in enumerate(recovery_counts):
        correct = row["hard_correct"] + row["soft_correct"]
        ax_status.text(
            60.8,
            idx,
            f"{correct} correct\n{row['wrong']} wrong, {row['not_detected']} missed",
            va="center",
            ha="left",
            fontsize=9.0,
            color="#374151",
        )

    legend_items = [
        Line2D([0], [0], marker="s", color=status_colors["hard_correct"], markerfacecolor=status_colors["hard_correct"], markersize=8, linestyle="None", label="Hard detected, directionally consistent"),
        Line2D([0], [0], marker="s", color=status_colors["soft_correct"], markerfacecolor=status_colors["soft_correct"], markersize=8, linestyle="None", label="Soft detected, directionally consistent"),
        Line2D([0], [0], marker="s", color=status_colors["wrong"], markerfacecolor=status_colors["wrong"], markersize=8, linestyle="None", label="Detected, wrong direction"),
        Line2D([0], [0], marker="s", color=status_colors["not_detected"], markeredgecolor="#CBD5E1", markerfacecolor=status_colors["not_detected"], markersize=8, linestyle="None", label="Not detected"),
    ]
    fig.legend(handles=legend_items, loc="lower center", bbox_to_anchor=(0.5, 0.01), ncol=4, frameon=False, fontsize=9)
    fig.suptitle("Figure 3. Recovery profile across 58 evaluation edges", fontsize=15, fontweight="bold", y=0.98)
    fig.savefig(outdir / "figure3_recovery_profile.svg", bbox_inches="tight")
    fig.savefig(outdir / "figure3_recovery_profile.png", dpi=300, bbox_inches="tight")
    plt.close(fig)


def build_figure4(df_summary: pd.DataFrame, outdir: Path) -> None:
    df = df_summary.copy()
    df = df.set_index("model").loc[MODEL_ORDER].reset_index()
    df["fidelity_bar"] = 1 - df["sid_normalised"].astype(float)
    df["direction_accuracy"] = df["direction_accuracy"].astype(float)
    df["soft_recall"] = df["soft_recall"].astype(float)
    df["snr"] = df["snr"].astype(float)
    df["detection_power"] = df["detection_power"].astype(float)
    df["snr_norm"] = df["snr"].clip(upper=3.0) / 3.0

    fig, axes = plt.subplots(1, 3, figsize=(15, 6.6), sharey=True)
    fig.subplots_adjust(left=0.12, right=0.98, top=0.84, bottom=0.14, wspace=0.08)
    y = np.arange(len(df))
    labels = [MODEL_LABELS[m] for m in df["model"]]

    panels = [
        ("Coverage", "soft_recall", None, "Bar = soft recall"),
        ("Fidelity", "fidelity_bar", "direction_accuracy", "Bar = 1 - normalized SID; dot = soft-edge direction accuracy"),
        ("Discriminability", "snr_norm", "detection_power", "Bar = SNR normalized to threshold 3.0; dot = detection power"),
    ]

    for ax, (title, bar_col, marker_col, subtitle) in zip(axes, panels):
        for idx, row in df.iterrows():
            color = MODEL_COLORS[row["model"]]
            ax.barh(idx, row[bar_col], color=color, alpha=0.85, height=0.56)
            if marker_col:
                ax.scatter(row[marker_col], idx, s=48, color="#111827", zorder=3)
        ax.set_title(title, fontsize=14, fontweight="bold")
        ax.set_xlim(0, 1.02)
        ax.set_ylim(-0.7, len(df) - 0.3)
        ax.grid(axis="x", color="#E5E7EB", linewidth=0.8)
        ax.set_xlabel(subtitle, fontsize=9, color="#4B5563")
        ax.invert_yaxis()
        ax.set_yticks(y)
        ax.set_yticklabels(labels, fontsize=10)
        for idx, row in df.iterrows():
            ax.text(min(row[bar_col] + 0.02, 0.98), idx, f"{row[bar_col]:.2f}", va="center", ha="left", fontsize=8.5, color="#374151")

    axes[0].set_ylabel("")
    fig.suptitle("Figure 4. Three-domain summary of model performance", fontsize=15.5, fontweight="bold", y=0.94)
    fig.savefig(outdir / "figure4_three_domain_summary.svg", bbox_inches="tight")
    fig.savefig(outdir / "figure4_three_domain_summary.png", dpi=300, bbox_inches="tight")
    plt.close(fig)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("--data-dir", type=Path, default=Path("manuscript/figure_data"))
    parser.add_argument("--outdir", type=Path, default=Path("manuscript/figures/final"))
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    configure_style()
    args.outdir.mkdir(parents=True, exist_ok=True)
    df_overlay, df_signal, df_summary = load_frames(args.data_dir)
    build_figure1(df_overlay, df_summary, args.outdir)
    build_figure2(df_signal, df_overlay, args.outdir)
    build_figure3(df_signal, df_overlay, args.outdir)
    build_figure4(df_summary, args.outdir)
    print(f"Wrote figures to {args.outdir}")


if __name__ == "__main__":
    main()
