"""Plot validation BLEU per epoch for attention vs baseline from the training logs."""
import re

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt


def read_bleu(path):
    with open(path, encoding="utf-8") as f:
        return [float(m) for m in re.findall(r"val BLEU ([\d.]+)", f.read())]


def main():
    fig, ax = plt.subplots(figsize=(6, 4))
    for path, label, color in [("train_attention.log", "with attention", "#1f5fa8"),
                               ("train_baseline.log", "no attention (baseline)", "#999999")]:
        bleu = read_bleu(path)
        ax.plot(range(1, len(bleu) + 1), bleu, marker="o", ms=3, label=label, color=color)
    ax.set_xlabel("epoch")
    ax.set_ylabel("validation BLEU (greedy)")
    ax.set_title("Multi30k EN→FR: attention vs baseline")
    ax.grid(alpha=0.3)
    ax.legend()
    fig.tight_layout()
    fig.savefig("outputs/bleu_curves.png", dpi=150)
    print("-> outputs/bleu_curves.png")


if __name__ == "__main__":
    main()
