"""Train the attention model (default) or the no-attention baseline (--no-attention)."""
import argparse
import math
import os
import time

import torch
import torch.nn as nn

from data import make_loaders
from evaluate import bleu_on_loader
from model import Seq2Seq


def run_epoch(model, loader, criterion, device, optimizer=None, clip=1.0, tf=1.0):
    model.train(optimizer is not None)
    total, n_tok = 0.0, 0
    with torch.set_grad_enabled(optimizer is not None):
        for src, src_lens, tgt in loader:
            src, src_lens, tgt = src.to(device), src_lens.to(device), tgt.to(device)
            logits = model(src, src_lens, tgt, teacher_forcing=tf if optimizer else 1.0)
            gold = tgt[:, 1:]
            loss = criterion(logits.reshape(-1, logits.size(-1)), gold.reshape(-1))
            if optimizer:
                optimizer.zero_grad()
                loss.backward()
                nn.utils.clip_grad_norm_(model.parameters(), clip)
                optimizer.step()
            k = (gold != 0).sum().item()
            total += loss.item() * k
            n_tok += k
    return total / n_tok


def main():
    p = argparse.ArgumentParser()
    p.add_argument("--epochs", type=int, default=15)
    p.add_argument("--batch-size", type=int, default=128)
    p.add_argument("--lr", type=float, default=1e-3)
    p.add_argument("--teacher-forcing", type=float, default=1.0)
    p.add_argument("--no-attention", action="store_true")
    p.add_argument("--out", default=None)
    p.add_argument("--limit-batches", type=int, default=0, help="debug: stop each epoch early")
    args = p.parse_args()

    torch.manual_seed(0)
    device = "cuda" if torch.cuda.is_available() else "cpu"
    loaders, src_vocab, tgt_vocab = make_loaders(args.batch_size)
    print(f"device={device} src_vocab={len(src_vocab)} tgt_vocab={len(tgt_vocab)} "
          f"train={len(loaders['train'].dataset)}")

    model = Seq2Seq(len(src_vocab), len(tgt_vocab), use_attention=not args.no_attention).to(device)
    print(f"params: {sum(p.numel() for p in model.parameters()) / 1e6:.1f}M  attention={not args.no_attention}")
    optimizer = torch.optim.Adam(model.parameters(), lr=args.lr)
    scheduler = torch.optim.lr_scheduler.ReduceLROnPlateau(optimizer, factor=0.5, patience=1)
    criterion = nn.CrossEntropyLoss(ignore_index=0, label_smoothing=0.1)

    if args.limit_batches:
        from itertools import islice
        for k in ("train", "val"):
            loaders[k] = list(islice(loaders[k], args.limit_batches))

    out = args.out or os.path.join("checkpoints", "baseline.pt" if args.no_attention else "attention.pt")
    os.makedirs(os.path.dirname(out), exist_ok=True)
    best = math.inf
    for epoch in range(1, args.epochs + 1):
        t0 = time.time()
        tr = run_epoch(model, loaders["train"], criterion, device, optimizer, tf=args.teacher_forcing)
        va = run_epoch(model, loaders["val"], criterion, device)
        scheduler.step(va)
        bleu = bleu_on_loader(model, loaders["val"], tgt_vocab, device)
        print(f"epoch {epoch:2d} | train {tr:.3f} | val {va:.3f} (ppl {math.exp(va):.1f}) | "
              f"val BLEU {bleu:.2f} | lr {optimizer.param_groups[0]['lr']:.1e} | {time.time() - t0:.0f}s")
        if va < best:
            best = va
            torch.save({"model": model.state_dict(), "config": model.config,
                        "src_itos": src_vocab.itos, "tgt_itos": tgt_vocab.itos}, out)
    print(f"best val loss {best:.3f} -> {out}")


if __name__ == "__main__":
    main()
