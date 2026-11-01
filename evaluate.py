"""BLEU on the Multi30k test set (greedy or beam search) + sample translations."""
import argparse

import torch
from nltk.translate.bleu_score import corpus_bleu

from data import EOS, SOS, Vocab, make_loaders, read_split, tokenize
from model import Seq2Seq


def load_checkpoint(path, device):
    # Load on CPU first (works without a GPU), then move the model.
    ckpt = torch.load(path, map_location=lambda storage, loc: storage)
    model = Seq2Seq(**ckpt["config"]).to(device)
    model.load_state_dict(ckpt["model"])
    model.eval()
    return model, Vocab(ckpt["src_itos"]), Vocab(ckpt["tgt_itos"])


def bleu_on_loader(model, loader, tgt_vocab, device):
    """Fast greedy corpus BLEU (0-100) used for per-epoch monitoring."""
    model.eval()
    hyps, refs = [], []
    sos, eos = tgt_vocab.stoi[SOS], tgt_vocab.stoi[EOS]
    for src, src_lens, tgt in loader:
        out = model.greedy(src.to(device), src_lens.to(device), sos, eos)
        for h, r in zip(out.tolist(), tgt.tolist()):
            hyps.append(tgt_vocab.decode(h))
            refs.append([tgt_vocab.decode(r)])
    return 100 * corpus_bleu(refs, hyps)


def translate(model, sentence, src_vocab, tgt_vocab, device, beam=5):
    tokens = tokenize(sentence)
    src = torch.tensor([src_vocab.encode(tokens)], device=device)
    ids, attn = model.beam_search(src, torch.tensor([src.size(1)]), tgt_vocab.stoi[SOS],
                                  tgt_vocab.stoi[EOS], beam=beam)
    out = tgt_vocab.decode(ids)
    if attn is not None:
        # rows: generated tokens (+ <eos>); cols: <sos> src <eos>
        attn = attn[: len(out) + 1]
    return out, tokens, attn


def main():
    p = argparse.ArgumentParser()
    p.add_argument("--ckpt", default="checkpoints/attention.pt")
    p.add_argument("--beam", type=int, default=5)
    p.add_argument("--split", default="test")
    p.add_argument("--samples", type=int, default=10)
    args = p.parse_args()

    device = "cuda" if torch.cuda.is_available() else "cpu"
    model, src_vocab, tgt_vocab = load_checkpoint(args.ckpt, device)
    en, fr = read_split(args.split)
    hyps, refs = [], []
    for i, (e, f) in enumerate(zip(en, fr)):
        out, _, _ = translate(model, e, src_vocab, tgt_vocab, device, beam=args.beam)
        hyps.append(out)
        refs.append([tokenize(f)])
        if i < args.samples:
            print(f"EN  : {e}\nREF : {f}\nPRED: {' '.join(out)}\n")
    print(f"{args.split} BLEU (beam={args.beam}): {100 * corpus_bleu(refs, hyps):.2f}  [{args.ckpt}]")


if __name__ == "__main__":
    main()
