"""Translate a sentence and save its attention heatmap.

python visualize.py "A man is riding a bike down the street."
"""
import argparse
import os

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import torch

from evaluate import load_checkpoint, translate


def plot_attention(src_tokens, out_tokens, attn, path):
    cols = ["<sos>"] + src_tokens + ["<eos>"]
    rows = out_tokens + ["<eos>"]
    fig, ax = plt.subplots(figsize=(max(5, 0.6 * len(cols)), max(4, 0.5 * len(rows))))
    ax.imshow(attn.numpy(), cmap="Blues", vmin=0, vmax=1)
    ax.set_xticks(range(len(cols)), cols, rotation=45, ha="right")
    ax.set_yticks(range(len(rows)), rows)
    ax.set_xlabel("source (EN)")
    ax.set_ylabel("generated (FR)")
    fig.tight_layout()
    fig.savefig(path, dpi=150)
    plt.close(fig)


def main():
    p = argparse.ArgumentParser()
    p.add_argument("sentence")
    p.add_argument("--ckpt", default="checkpoints/attention.pt")
    p.add_argument("--out", default="outputs/attention.png")
    p.add_argument("--beam", type=int, default=5)
    args = p.parse_args()

    device = "cuda" if torch.cuda.is_available() else "cpu"
    model, src_vocab, tgt_vocab = load_checkpoint(args.ckpt, device)
    out, src_tokens, attn = translate(model, args.sentence, src_vocab, tgt_vocab, device, args.beam)
    print("FR:", " ".join(out))
    if attn is None:
        print("checkpoint has no attention (baseline) - nothing to plot")
        return
    os.makedirs(os.path.dirname(args.out) or ".", exist_ok=True)
    plot_attention(src_tokens, out, attn, args.out)
    print("heatmap ->", args.out)


if __name__ == "__main__":
    main()
