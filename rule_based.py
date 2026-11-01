"""Rule-based baseline: word-by-word dictionary translation + a few hand-written reordering rules.

The bilingual dictionary is extracted from the training pairs with IBM Model 1 (a few EM steps),
then each English word is looked up independently - no context, no learned word order.
Rules: colour adjectives move after their noun; "'s" possessives are dropped.
"""
import argparse
import os
import pickle

import numpy as np
from nltk.translate.bleu_score import corpus_bleu

from data import Vocab, download, read_split, tokenize

COLOURS = {"red", "blue", "green", "white", "black", "yellow", "orange", "pink", "purple", "brown",
           "gray", "grey"}
DICT_PATH = os.path.join("checkpoints", "rule_dict.pkl")


def train_dictionary(en, fr, iters=5, min_freq=2):
    src_vocab, tgt_vocab = Vocab.build(en, min_freq), Vocab.build(fr, min_freq)
    pairs = [([0] + [src_vocab.stoi.get(w, 3) for w in tokenize(e)],  # 0 = NULL word
              [tgt_vocab.stoi.get(w, 3) for w in tokenize(f)]) for e, f in zip(en, fr)]
    t = np.full((len(src_vocab), len(tgt_vocab)), 1.0 / len(tgt_vocab), dtype=np.float32)  # t(f|e)
    for it in range(iters):
        counts = np.zeros_like(t)
        for e_ids, f_ids in pairs:
            sub = t[np.ix_(e_ids, f_ids)]                     # [E, F]
            post = sub / sub.sum(0, keepdims=True)            # P(alignment e | f)
            np.add.at(counts, (np.array(e_ids)[:, None], np.array(f_ids)[None, :]), post)
        t = counts / np.maximum(counts.sum(1, keepdims=True), 1e-9)
        print(f"IBM1 EM iteration {it + 1}/{iters}")
    best = t.argmax(1)
    lexicon = {}
    for i, w in enumerate(src_vocab.itos[4:], start=4):
        f = tgt_vocab.itos[best[i]]
        if f not in ("<pad>", "<sos>", "<eos>", "<unk>"):
            lexicon[w] = f
    return lexicon


def translate(sentence, lexicon):
    tokens = tokenize(sentence)
    # Rule 1: English "colour noun" -> French "noun colour".
    i = 0
    while i < len(tokens) - 1:
        if tokens[i] in COLOURS and tokens[i + 1] not in COLOURS and tokens[i + 1].isalpha():
            tokens[i], tokens[i + 1] = tokens[i + 1], tokens[i]
            i += 2
        else:
            i += 1
    out = []
    for w in tokens:
        if w == "'s":  # Rule 2: drop possessive marker
            continue
        out.append(lexicon.get(w, w if not w.isalpha() else "<unk>"))
    return out


def main():
    p = argparse.ArgumentParser()
    p.add_argument("--split", default="test")
    p.add_argument("--samples", type=int, default=5)
    args = p.parse_args()

    download()
    if os.path.exists(DICT_PATH):
        with open(DICT_PATH, "rb") as f:
            lexicon = pickle.load(f)
    else:
        lexicon = train_dictionary(*read_split("train"))
        os.makedirs("checkpoints", exist_ok=True)
        with open(DICT_PATH, "wb") as f:
            pickle.dump(lexicon, f)
    print(f"dictionary: {len(lexicon)} entries")

    en, fr = read_split(args.split)
    hyps = [translate(e, lexicon) for e in en]
    refs = [[tokenize(f)] for f in fr]
    for e, f, h in list(zip(en, fr, hyps))[: args.samples]:
        print(f"EN  : {e}\nREF : {f}\nPRED: {' '.join(h)}\n")
    print(f"{args.split} BLEU (rule-based word-by-word): {100 * corpus_bleu(refs, hyps):.2f}")


if __name__ == "__main__":
    main()
