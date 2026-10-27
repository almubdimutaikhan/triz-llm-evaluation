#!/usr/bin/env python3
"""Render figures from results/summary.json."""
import json
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import FancyBboxPatch
from matplotlib.ticker import PercentFormatter

ROOT = Path(__file__).resolve().parents[1]
BG, INK, MUTED = "#f7f8f5", "#182d32", "#577078"
TEAL, ORANGE, PURPLE, GRID = "#087e82", "#cf6a35", "#795aa8", "#dce5e3"
plt.rcParams.update({"font.family": "DejaVu Sans", "font.size": 11,
                     "figure.facecolor": BG, "axes.facecolor": BG,
                     "text.color": INK, "axes.labelcolor": INK,
                     "xtick.color": MUTED, "ytick.color": INK,
                     "svg.fonttype": "none", "svg.hashsalt": "triz-evaluation-v1",
                     "axes.spines.top": False, "axes.spines.right": False,
                     "axes.spines.left": False, "axes.spines.bottom": False})


def save(fig, name):
    for ext in ("png", "svg"):
        options = {"metadata": {"Date": None}} if ext == "svg" else {}
        fig.savefig(ROOT / "figures" / f"{name}.{ext}", dpi=180,
                    facecolor=BG, **options)
        if ext == "svg":
            path = ROOT / "figures" / f"{name}.{ext}"
            path.write_text("\n".join(line.rstrip() for line in path.read_text().splitlines()) + "\n")
    plt.close(fig)


def heading(fig, eyebrow, title, subtitle):
    fig.text(.055, .945, eyebrow, size=10, weight="bold", color=TEAL)
    fig.text(.055, .878, title, size=23, weight="bold")
    fig.text(.055, .823, subtitle, size=11, color=MUTED)


def banner(s):
    fig = plt.figure(figsize=(12, 4.0))
    ax = fig.add_axes([0, 0, 1, 1]); ax.axis("off")
    ax.text(.055, .88, "ALMUBDI MUTAIKHAN  /  LLM EVALUATION", color=TEAL, weight="bold", size=11)
    ax.text(.055, .70, "Evaluating TRIZ prompts", weight="bold", size=35)
    ax.text(.055, .59, "Engineering solutions, prompt controls, and candidate selection", color=MUTED, size=13)
    b = s["baseline"]
    matched = next(r for r in s["contrasts"] if r["judge"] == "Gemini" and r["treatment"] == "P_L_TRIZ_ON" and r["baseline"] == "P_L_TRIZ_OFF")
    values = [("EMPTY CONTROL", f"{b['p']:.1%}", "TRIZ preferred to empty control", "45 cases · cross-family jury"),
              ("STRUCTURED CONTROL", f"{matched['p']:.1%}", "TRIZ vs structured generic prompt", "95% CI includes 50%"),
              ("CANDIDATE ORDER", "13/15 → 1/15", "Gemini repeats the same removal", "Same order → reshuffled · one problem")]
    for i, (label, value, line, note) in enumerate(values):
        x = .055 + i * .305
        ax.add_patch(FancyBboxPatch((x, .105), .28, .36, boxstyle="round,pad=0.014,rounding_size=0.018", facecolor="white", edgecolor=GRID))
        ax.text(x + .01, .414, label, size=9, color=TEAL, weight="bold")
        ax.text(x + .01, .292, value, size=25, weight="bold")
        ax.text(x + .01, .218, line, size=10)
        ax.text(x + .01, .153, note, size=9, color=MUTED)
    save(fig, "overview")


def preference(s):
    fig = plt.figure(figsize=(12, 6.4))
    heading(fig, "PROMPT COMPARISONS", "TRIZ preference under two control designs",
            "Probability the jury prefers the treatment · 95% case-clustered bootstrap intervals")
    ax = fig.add_axes([.40, .20, .37, .54])
    rows = [("TRIZ vs empty control", "4-model jury · 45 cases", s["baseline"], TEAL)]
    for judge in ("Gemini", "Jev"):
        for r in s["contrasts"]:
            if r["judge"] == judge and r["treatment"] in ("P_L_TRIZ_ON", "P_S_TRIZ_ON") and r["baseline"] in ("P_L_TRIZ_OFF", "P_S_TRIZ_OFF"):
                name = "TRIZ vs generic / long" if r["treatment"] == "P_L_TRIZ_ON" else "TRIZ vs generic / short"
                rows.append((name, f"{judge} · {r['cases']} retained cases", r, ORANGE if judge == "Gemini" else PURPLE))
    ax.axvline(.5, color=MUTED, lw=1.2, ls=(0, (3, 4)))
    for i, (label, detail, r, color) in enumerate(rows):
        y = len(rows) - 1 - i
        ax.errorbar(r["p"], y, xerr=[[r["p"] - r["ci_low"]], [r["ci_high"] - r["p"]]],
                    fmt="o", color=color, lw=2, capsize=4, markersize=8)
        ax.text(-.10, y + .12, label, transform=ax.get_yaxis_transform(), ha="right", size=12, weight="bold")
        ax.text(-.10, y - .20, detail, transform=ax.get_yaxis_transform(), ha="right", size=10, color=MUTED)
        ax.text(1.10, y + .10, f"{r['p']:.1%}", transform=ax.get_yaxis_transform(), size=15, weight="bold", color=color)
        ax.text(1.10, y - .22, f"[{r['ci_low']:.1%}, {r['ci_high']:.1%}]", transform=ax.get_yaxis_transform(), size=10, color=MUTED)
    ax.set_xlim(.3, .8); ax.set_ylim(-.6, 4.6)
    ax.set_yticks([]); ax.set_xticks([.3, .4, .5, .6, .7, .8]); ax.xaxis.set_major_formatter(PercentFormatter(1))
    ax.grid(axis="x", color=GRID, lw=.7); ax.set_axisbelow(True)
    ax.set_xlabel("50% = no preference", labelpad=12)
    fig.text(.055, .095, "Baseline and factorial results use different comparisons and judges; problems overlap.", size=10, color=MUTED)
    fig.text(.055, .051, "Wide intervals leave the controlled TRIZ effect unresolved.", size=10, color=MUTED)
    save(fig, "preference")


def reliability(s):
    fig = plt.figure(figsize=(12, 6.3))
    heading(fig, "CANDIDATE SELECTION", "Reordering candidates changes which one is removed",
            "Ranking 41 candidates · probability of repeating the same discard · 15 slates per model")
    ax = fig.add_axes([.26, .22, .65, .51])
    models = [("google/gemini-2.5-flash", "Gemini 2.5 Flash"), ("deepseek/deepseek-chat-v3.1", "DeepSeek V3.1"),
              ("anthropic/claude-sonnet-5", "Claude Sonnet*")]
    for i, (model, name) in enumerate(models):
        r = next(r for r in s["selection"] if r["judge"] == model and r["condition"] == "rank")
        y = 2 - i
        a, b = r["same_order_agreement"], r["shuffled_agreement"]
        ax.plot([b, a], [y, y], color=GRID, lw=6, solid_capstyle="round")
        ax.scatter(a, y, s=115, color=TEAL, zorder=4)
        ax.scatter(b, y, s=115, color=ORANGE, zorder=4)
        ax.text(a, y + .20, f"{r['same_order_matches']}/15", color=TEAL, ha="center", weight="bold", size=12)
        ax.text(b, y - .30, f"{r['matches']}/15", color=ORANGE, ha="center", weight="bold", size=12)
        ax.text(-.07, y, name, transform=ax.get_yaxis_transform(), ha="right", va="center", weight="bold")
    ax.axvline(1/41, ls=(0, (3, 3)), color=MUTED, lw=1)
    ax.text(1/41, 2.55, "Uniform-choice reference: 1/41", color=MUTED, size=9)
    ax.scatter([], [], color=TEAL, s=55, label="Same order, repeat call")
    ax.scatter([], [], color=ORANGE, s=55, label="Independent shuffles")
    ax.legend(loc="lower right", frameon=False, fontsize=10)
    ax.set_xlim(-.02, 1.02); ax.set_ylim(-.65, 2.75); ax.set_yticks([])
    ax.xaxis.set_major_formatter(PercentFormatter(1)); ax.grid(axis="x", color=GRID, lw=.6); ax.set_axisbelow(True)
    fig.text(.055, .105, "Overlapping candidate sets from one Mars-boot problem. Agreement measures repeatability of removal.", size=10, color=MUTED)
    fig.text(.055, .055, "*Logged model ID: anthropic/claude-sonnet-5. GPT-4o omitted: only 2 complete shuffled pairs.", size=9, color=MUTED)
    save(fig, "reliability")


def cost(s):
    fig = plt.figure(figsize=(12, 5.5))
    heading(fig, "TOKEN USAGE", "TRIZ prompts use more tokens",
            "640 cached generations · 40 cases × 4 generator models × 4 conditions")
    ax = fig.add_axes([.32, .22, .57, .51])
    lookup = {r["mode"]: r for r in s["cost"]}
    modes = ["P_S_TRIZ_OFF", "P_S_TRIZ_ON", "P_L_TRIZ_OFF", "P_L_TRIZ_ON"]
    labels = ["Short / generic", "Short / TRIZ", "Long / generic", "Long / TRIZ"]
    for i, (mode, label) in enumerate(zip(modes, labels)):
        value = lookup[mode]["mean_tokens"]; y = 3 - i
        color = TEAL if mode.endswith("OFF") else ORANGE
        ax.barh(y, value, height=.55, color=color)
        ax.text(value + 25, y, f"{value:,.0f}", va="center", weight="bold")
        ax.text(-.04, y, label, transform=ax.get_yaxis_transform(), ha="right", va="center", size=12)
    ax.set_xlim(0, 1600); ax.set_yticks([]); ax.grid(axis="x", color=GRID, lw=.7); ax.set_axisbelow(True)
    ax.set_xlabel("Mean input + output tokens per generation (cl100k_base)", labelpad=10)
    fig.text(.055, .095, "All text counted with cl100k_base; provider-billed usage may differ.", size=10, color=MUTED)
    fig.text(.055, .048, "Counts use the same generations as the controlled prompt comparisons.", size=10, color=MUTED)
    save(fig, "tokens")


def protocol():
    fig = plt.figure(figsize=(12, 3.6))
    ax = fig.add_axes([0, 0, 1, 1]); ax.axis("off")
    ax.text(.055, .89, "HOW THE COMPARISON WORKS", color=TEAL, weight="bold", size=11)
    boxes = [("1. CONTROL", "Same problem + task\nSystem prompt varies"),
             ("2. BLIND", "Final solution only\nBoth A/B orders"),
             ("3. FILTER", "Different model family\nSame pick both orders"),
             ("4. ESTIMATE", "One retained vote per pair\nBootstrap whole cases")]
    for i, (title, body) in enumerate(boxes):
        x = .055 + .235 * i
        ax.add_patch(FancyBboxPatch((x, .29), .205, .42, boxstyle="round,pad=.012,rounding_size=.018", facecolor="white", edgecolor=GRID))
        ax.text(x + .013, .605, title, weight="bold", color=TEAL, size=11)
        ax.text(x + .013, .43, body, size=11, linespacing=1.8)
        if i < 3:
            ax.annotate("", (x + .231, .50), (x + .21, .50), arrowprops={"arrowstyle": "->", "color": MUTED})
    ax.text(.055, .13, "Gold answers stay out of generation prompts. More votes do not create more independent cases.", size=11, color=MUTED)
    save(fig, "protocol")


if __name__ == "__main__":
    s = json.loads((ROOT / "results/summary.json").read_text())
    banner(s); preference(s); reliability(s); cost(s); protocol()
    print("Rendered five figures as PNG and SVG.")
