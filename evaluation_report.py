"""Full evaluation of all three systems on the test set.

Translation has no class labels, so instead of a single confusion matrix this reports:
  - train/val loss and perplexity curves (from the training logs)
  - BLEU with its 1-4-gram precisions and brevity penalty
  - BLEU by source-sentence length (where attention should help most)
  - sentence-level BLEU distribution
  - confusion matrices on two word classes that matter in French:
      colour words (does "red" become "rouge"?) and article gender (un vs une)

python evaluation_report.py   ->  outputs/eval/*.png + outputs/eval/metrics.json
"""
import json
import math
import os
import re
from collections import Counter

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import torch
from nltk.translate.bleu_score import SmoothingFunction, corpus_bleu, sentence_bleu

import rule_based
from data import read_split, tokenize
from evaluate import load_checkpoint, translate

OUT = os.path.join("outputs", "eval")
SYSTEMS = [("rule", "Rule-based"), ("baseline", "No attention"), ("attention", "With attention")]
COLORS = {"rule": "#8F84AC", "baseline": "#2D1B4E", "attention": "#FF6B4A"}

# French colour words -> one label per colour (all genders / plurals)
COLOUR_FORMS = {
    "red": ["rouge", "rouges"], "blue": ["bleu", "bleue", "bleus", "bleues"],
    "white": ["blanc", "blanche", "blancs", "blanches"], "black": ["noir", "noire", "noirs", "noires"],
    "green": ["vert", "verte", "verts", "vertes"], "yellow": ["jaune", "jaunes"],
    "pink": ["rose", "roses"], "orange": ["orange", "oranges"],
}
FORM2COLOUR = {f: c for c, fs in COLOUR_FORMS.items() for f in fs}


def decode_all(en):
    """Translate every test sentence with all three systems (cached on disk)."""
    os.makedirs(OUT, exist_ok=True)
    cache = os.path.join(OUT, "predictions.json")
    if os.path.exists(cache):
        with open(cache, encoding="utf-8") as f:
            return json.load(f)
    device = "cuda" if torch.cuda.is_available() else "cpu"
    preds = {}
    for name in ("attention", "baseline"):
        model, src_vocab, tgt_vocab = load_checkpoint(os.path.join("checkpoints", f"{name}.pt"), device)
        with torch.inference_mode():
            preds[name] = [translate(model, s, src_vocab, tgt_vocab, device, beam=5)[0] for s in en]
        print(f"decoded {name}")
    import pickle
    with open(rule_based.DICT_PATH, "rb") as f:
        lexicon = pickle.load(f)
    preds["rule"] = [rule_based.translate(s, lexicon) for s in en]
    with open(cache, "w", encoding="utf-8") as f:
        json.dump(preds, f, ensure_ascii=False)
    return preds


def bleu_parts(refs, hyps):
    """Corpus BLEU split into n-gram precisions and brevity penalty (same as NLTK's corpus_bleu)."""
    p = []
    for n in range(1, 5):
        match = total = 0
        for (ref,), hyp in zip(refs, hyps):
            h = Counter(tuple(hyp[i:i + n]) for i in range(len(hyp) - n + 1))
            r = Counter(tuple(ref[i:i + n]) for i in range(len(ref) - n + 1))
            match += sum(min(c, r[g]) for g, c in h.items())
            total += max(0, len(hyp) - n + 1)
        p.append(match / total if total else 0.0)
    hyp_len = sum(len(h) for h in hyps)
    ref_len = sum(len(r[0]) for r in refs)
    bp = 1.0 if hyp_len > ref_len else math.exp(1 - ref_len / max(hyp_len, 1))
    return {"bleu": 100 * corpus_bleu(refs, hyps), "precisions": [100 * x for x in p], "brevity_penalty": bp,
            "hyp_len": hyp_len, "ref_len": ref_len}


def read_log(path):
    with open(path, encoding="utf-8") as f:
        txt = f.read()
    rows = re.findall(r"epoch\s+(\d+) \| train ([\d.]+) \| val ([\d.]+) \(ppl ([\d.]+)\) \| val BLEU ([\d.]+)", txt)
    return {k: [float(r[i]) for r in rows] for i, k in enumerate(["epoch", "train_loss", "val_loss", "val_ppl", "val_bleu"])}


def first_article(tokens):
    for t in tokens[:3]:
        if t in ("un", "une"):
            return t
    return "other"


def confusion(pairs, labels):
    m = np.zeros((len(labels), len(labels)), dtype=int)
    for ref, hyp in pairs:
        m[labels.index(ref), labels.index(hyp)] += 1
    return m


def plot_confusion(ax, m, labels, title, cmap):
    norm = m / np.maximum(m.sum(1, keepdims=True), 1)
    ax.imshow(norm, cmap=cmap, vmin=0, vmax=1)
    ax.set_xticks(range(len(labels)), labels, rotation=45, ha="right")
    ax.set_yticks(range(len(labels)), labels)
    for i in range(len(labels)):
        for j in range(len(labels)):
            if m[i, j]:
                ax.text(j, i, m[i, j], ha="center", va="center", fontsize=9,
                        color="white" if norm[i, j] > 0.55 else "#1A1425")
    ax.set_xlabel("predicted")
    ax.set_ylabel("reference")
    ax.set_title(title, fontsize=11)


def main():
    plt.rcParams.update({"font.family": "Calibri", "font.size": 11, "axes.spines.top": False, "axes.spines.right": False})
    en, fr = read_split("test")
    refs = [[tokenize(f)] for f in fr]
    preds = decode_all(en)
    metrics = {}

    # ---- 1. BLEU + n-gram precisions ----
    for k, _ in SYSTEMS:
        metrics[k] = bleu_parts(refs, preds[k])
        print(k, f"BLEU {metrics[k]['bleu']:.2f}", [round(x, 1) for x in metrics[k]["precisions"]], f"BP {metrics[k]['brevity_penalty']:.3f}")

    # ---- 2. BLEU by source length ----
    buckets = [(1, 8), (9, 12), (13, 16), (17, 20), (21, 60)]
    names = ["≤8", "9–12", "13–16", "17–20", "21+"]
    src_len = [len(tokenize(e)) for e in en]
    metrics["by_length"] = {"buckets": names, "count": []}
    for k, _ in SYSTEMS:
        metrics["by_length"][k] = []
    for lo, hi in buckets:
        idx = [i for i, n in enumerate(src_len) if lo <= n <= hi]
        metrics["by_length"]["count"].append(len(idx))
        for k, _ in SYSTEMS:
            metrics["by_length"][k].append(100 * corpus_bleu([refs[i] for i in idx], [preds[k][i] for i in idx]))

    # ---- 3. sentence-level BLEU distribution ----
    sm = SmoothingFunction().method1
    edges = [0, 10, 20, 30, 40, 50, 60, 70, 80, 90, 100.01]
    metrics["sentence_bleu_hist"] = {"bins": ["0–10", "10–20", "20–30", "30–40", "40–50", "50–60", "60–70", "70–80", "80–90", "90–100"]}
    for k, _ in SYSTEMS:
        s = [100 * sentence_bleu(r, h, smoothing_function=sm) for r, h in zip(refs, preds[k])]
        metrics["sentence_bleu_hist"][k] = np.histogram(s, bins=edges)[0].tolist()
        metrics[k]["exact_match"] = sum(h == r[0] for r, h in zip(refs, preds[k]))
        metrics[k]["median_sentence_bleu"] = float(np.median(s))

    # ---- 4. confusion matrices ----
    colour_labels = list(COLOUR_FORMS) + ["none"]
    art_labels = ["un", "une", "other"]
    metrics["confusion"] = {}
    for k, _ in SYSTEMS:
        pairs = []
        for (ref,), hyp in zip(refs, preds[k]):
            rc = {FORM2COLOUR[t] for t in ref if t in FORM2COLOUR}
            if len(rc) != 1:
                continue  # only sentences with exactly one colour in the reference
            hc = [FORM2COLOUR[t] for t in hyp if t in FORM2COLOUR]
            pairs.append((rc.pop(), hc[0] if hc else "none"))
        cm = confusion(pairs, colour_labels)
        ga = [(first_article(r[0]), first_article(h)) for r, h in zip(refs, preds[k]) if first_article(r[0]) != "other"]
        gm = confusion(ga, art_labels)
        metrics["confusion"][k] = {"colour": cm.tolist(), "colour_acc": float(np.trace(cm) / max(cm.sum(), 1)),
                                   "colour_n": int(cm.sum()), "article": gm.tolist(),
                                   "article_acc": float(np.trace(gm) / max(gm.sum(), 1)), "article_n": int(gm.sum())}
    metrics["confusion"]["colour_labels"] = colour_labels
    metrics["confusion"]["article_labels"] = art_labels

    # ---- training curves ----
    metrics["curves"] = {"attention": read_log("train_attention.log"), "baseline": read_log("train_baseline.log")}

    # ---------------- figures ----------------
    fig, axes = plt.subplots(1, 3, figsize=(13, 4.2))
    for ax, k in zip(axes, ["rule", "baseline", "attention"]):
        c = metrics["confusion"][k]
        plot_confusion(ax, np.array(c["colour"]), colour_labels,
                       f"{dict(SYSTEMS)[k]}: {100 * c['colour_acc']:.0f}% correct", "Oranges" if k == "attention" else "Purples")
    fig.suptitle("Colour-word confusion matrix (test sentences with one colour in the reference)", fontsize=12)
    fig.tight_layout()
    fig.savefig(os.path.join(OUT, "confusion_colour.png"), dpi=170)
    plt.close(fig)

    fig, axes = plt.subplots(1, 3, figsize=(10, 3.4))
    for ax, k in zip(axes, ["rule", "baseline", "attention"]):
        c = metrics["confusion"][k]
        plot_confusion(ax, np.array(c["article"]), art_labels,
                       f"{dict(SYSTEMS)[k]}: {100 * c['article_acc']:.0f}% correct", "Oranges" if k == "attention" else "Purples")
    fig.suptitle("Article-gender confusion matrix (un / une at sentence start)", fontsize=12)
    fig.tight_layout()
    fig.savefig(os.path.join(OUT, "confusion_article.png"), dpi=170)
    plt.close(fig)

    fig, axes = plt.subplots(1, 2, figsize=(11, 4))
    for k, lbl in [("attention", "With attention"), ("baseline", "No attention")]:
        cv = metrics["curves"][k]
        axes[0].plot(cv["epoch"], cv["train_loss"], "--", color=COLORS[k], label=f"{lbl}: train")
        axes[0].plot(cv["epoch"], cv["val_loss"], "-o", ms=3, color=COLORS[k], label=f"{lbl}: val")
        axes[1].plot(cv["epoch"], cv["val_ppl"], "-o", ms=3, color=COLORS[k], label=lbl)
    axes[0].set(title="Cross-entropy loss", xlabel="epoch", ylabel="loss")
    axes[1].set(title="Validation perplexity", xlabel="epoch", ylabel="perplexity")
    for ax in axes:
        ax.grid(alpha=.3)
        ax.legend(fontsize=9)
    fig.tight_layout()
    fig.savefig(os.path.join(OUT, "loss_curves.png"), dpi=170)
    plt.close(fig)

    with open(os.path.join(OUT, "metrics.json"), "w", encoding="utf-8") as f:
        json.dump(metrics, f, ensure_ascii=False, indent=1)
    print(json.dumps({k: {x: metrics[k][x] for x in ("bleu", "brevity_penalty", "exact_match", "median_sentence_bleu")} for k, _ in SYSTEMS}, indent=1))
    print("by length", metrics["by_length"])
    for k, _ in SYSTEMS:
        c = metrics["confusion"][k]
        print(k, "colour acc", round(c["colour_acc"], 3), "n", c["colour_n"], "| article acc", round(c["article_acc"], 3), "n", c["article_n"])
    print("->", OUT)


if __name__ == "__main__":
    main()
