"""Multi30k EN->FR: download, tokenize, build vocab, batch."""
import gzip
import os
import re
import urllib.request
from collections import Counter

import torch
from torch.nn.utils.rnn import pad_sequence
from torch.utils.data import DataLoader, Dataset

DATA_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "data")
BASE_URL = "https://raw.githubusercontent.com/multi30k/dataset/master/data/task1/raw/"
SPLITS = {"train": "train", "val": "val", "test": "test_2016_flickr"}

PAD, SOS, EOS, UNK = "<pad>", "<sos>", "<eos>", "<unk>"
SPECIALS = [PAD, SOS, EOS, UNK]

# Lowercase + split off punctuation; keeps French elisions like "j'" attached to the article.
_TOKEN_RE = re.compile(r"[a-zà-ÿœæ]+'|[a-zà-ÿœæ0-9]+(?:-[a-zà-ÿœæ0-9]+)*|[^\sa-zà-ÿœæ0-9]")


def tokenize(text):
    return _TOKEN_RE.findall(text.lower().strip())


def download():
    os.makedirs(DATA_DIR, exist_ok=True)
    for split in SPLITS.values():
        for lang in ("en", "fr"):
            out = os.path.join(DATA_DIR, f"{split}.{lang}")
            if os.path.exists(out):
                continue
            url = f"{BASE_URL}{split}.{lang}.gz"
            print(f"downloading {url}")
            with urllib.request.urlopen(url) as r:
                text = gzip.decompress(r.read()).decode("utf-8")
            with open(out, "w", encoding="utf-8") as f:
                f.write(text)


def read_split(name):
    split = SPLITS[name]
    with open(os.path.join(DATA_DIR, f"{split}.en"), encoding="utf-8") as f:
        en = [l.rstrip("\n") for l in f]
    with open(os.path.join(DATA_DIR, f"{split}.fr"), encoding="utf-8") as f:
        fr = [l.rstrip("\n") for l in f]
    assert len(en) == len(fr), f"{name}: misaligned"
    return en, fr


class Vocab:
    def __init__(self, itos):
        self.itos = list(itos)
        self.stoi = {t: i for i, t in enumerate(self.itos)}

    @classmethod
    def build(cls, sentences, min_freq=2):
        counts = Counter(tok for s in sentences for tok in tokenize(s))
        words = sorted((w for w, c in counts.items() if c >= min_freq), key=lambda w: (-counts[w], w))
        return cls(SPECIALS + words)

    def __len__(self):
        return len(self.itos)

    def encode(self, tokens):
        unk = self.stoi[UNK]
        return [self.stoi[SOS]] + [self.stoi.get(t, unk) for t in tokens] + [self.stoi[EOS]]

    def decode(self, ids):
        out = []
        for i in ids:
            tok = self.itos[i]
            if tok == EOS:
                break
            if tok not in (PAD, SOS):
                out.append(tok)
        return out


class PairDataset(Dataset):
    def __init__(self, en, fr, src_vocab, tgt_vocab, max_len=None):
        self.pairs = []
        for e, f in zip(en, fr):
            et, ft = tokenize(e), tokenize(f)
            if max_len and (len(et) > max_len or len(ft) > max_len):
                continue
            self.pairs.append((torch.tensor(src_vocab.encode(et)), torch.tensor(tgt_vocab.encode(ft))))

    def __len__(self):
        return len(self.pairs)

    def __getitem__(self, i):
        return self.pairs[i]


def collate(batch, pad_idx=0):
    src, tgt = zip(*batch)
    src_lens = torch.tensor([len(s) for s in src])
    return (pad_sequence(src, batch_first=True, padding_value=pad_idx), src_lens,
            pad_sequence(tgt, batch_first=True, padding_value=pad_idx))


def make_loaders(batch_size=128, min_freq=2, max_len=50):
    download()
    train_en, train_fr = read_split("train")
    src_vocab = Vocab.build(train_en, min_freq)
    tgt_vocab = Vocab.build(train_fr, min_freq)
    loaders = {}
    for name in SPLITS:
        en, fr = (train_en, train_fr) if name == "train" else read_split(name)
        ds = PairDataset(en, fr, src_vocab, tgt_vocab, max_len if name == "train" else None)
        loaders[name] = DataLoader(ds, batch_size=batch_size, shuffle=(name == "train"), collate_fn=collate)
    return loaders, src_vocab, tgt_vocab
