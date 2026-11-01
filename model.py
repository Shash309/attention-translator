"""Bi-LSTM encoder + Bahdanau (additive) attention + LSTM decoder.

Set use_attention=False to get the plain seq2seq baseline (fixed context vector).
"""
import torch
import torch.nn as nn
import torch.nn.functional as F
from torch.nn.utils.rnn import pack_padded_sequence, pad_packed_sequence


class Encoder(nn.Module):
    def __init__(self, vocab_size, emb_dim, hid_dim, dec_hid_dim, dropout):
        super().__init__()
        self.embedding = nn.Embedding(vocab_size, emb_dim, padding_idx=0)
        self.rnn = nn.LSTM(emb_dim, hid_dim, batch_first=True, bidirectional=True)
        self.fc_h = nn.Linear(2 * hid_dim, dec_hid_dim)
        self.fc_c = nn.Linear(2 * hid_dim, dec_hid_dim)
        self.dropout = nn.Dropout(dropout)

    def forward(self, src, src_lens):
        emb = self.dropout(self.embedding(src))
        packed = pack_padded_sequence(emb, src_lens.cpu(), batch_first=True, enforce_sorted=False)
        out, (h, c) = self.rnn(packed)
        out, _ = pad_packed_sequence(out, batch_first=True, total_length=src.size(1))  # [B, S, 2H]
        # Merge forward/backward final states into the decoder's initial state.
        h = torch.tanh(self.fc_h(torch.cat([h[0], h[1]], dim=1)))
        c = torch.tanh(self.fc_c(torch.cat([c[0], c[1]], dim=1)))
        return out, (h, c)


class BahdanauAttention(nn.Module):
    """e_ij = v^T tanh(W s_{i-1} + U h_j);  a_ij = softmax_j(e_ij);  c_i = sum_j a_ij h_j"""

    def __init__(self, enc_dim, dec_hid_dim, attn_dim):
        super().__init__()
        self.W = nn.Linear(dec_hid_dim, attn_dim, bias=False)
        self.U = nn.Linear(enc_dim, attn_dim)
        self.v = nn.Linear(attn_dim, 1, bias=False)

    def forward(self, dec_hidden, enc_proj, enc_out, mask):
        scores = self.v(torch.tanh(self.W(dec_hidden).unsqueeze(1) + enc_proj)).squeeze(2)  # [B, S]
        scores = scores.masked_fill(~mask, float("-inf"))
        alpha = F.softmax(scores, dim=1)
        context = torch.bmm(alpha.unsqueeze(1), enc_out).squeeze(1)  # [B, enc_dim]
        return context, alpha


class Decoder(nn.Module):
    def __init__(self, vocab_size, emb_dim, enc_dim, hid_dim, attn_dim, dropout, use_attention):
        super().__init__()
        self.use_attention = use_attention
        self.embedding = nn.Embedding(vocab_size, emb_dim, padding_idx=0)
        self.attention = BahdanauAttention(enc_dim, hid_dim, attn_dim) if use_attention else None
        self.rnn = nn.LSTMCell(emb_dim + enc_dim, hid_dim)
        self.out = nn.Linear(hid_dim + enc_dim + emb_dim, vocab_size)
        self.dropout = nn.Dropout(dropout)

    def step(self, tok, state, enc_proj, enc_out, mask, fixed_context):
        emb = self.dropout(self.embedding(tok))
        h, c = state
        if self.use_attention:
            context, alpha = self.attention(h, enc_proj, enc_out, mask)
        else:
            context, alpha = fixed_context, None
        h, c = self.rnn(torch.cat([emb, context], dim=1), (h, c))
        logits = self.out(self.dropout(torch.cat([h, context, emb], dim=1)))
        return logits, (h, c), alpha


class Seq2Seq(nn.Module):
    def __init__(self, src_vocab_size, tgt_vocab_size, emb_dim=256, enc_hid=256, dec_hid=512,
                 attn_dim=256, dropout=0.3, use_attention=True):
        super().__init__()
        self.config = dict(src_vocab_size=src_vocab_size, tgt_vocab_size=tgt_vocab_size, emb_dim=emb_dim,
                           enc_hid=enc_hid, dec_hid=dec_hid, attn_dim=attn_dim, dropout=dropout,
                           use_attention=use_attention)
        self.encoder = Encoder(src_vocab_size, emb_dim, enc_hid, dec_hid, dropout)
        self.decoder = Decoder(tgt_vocab_size, emb_dim, 2 * enc_hid, dec_hid, attn_dim, dropout, use_attention)

    def encode(self, src, src_lens):
        enc_out, state = self.encoder(src, src_lens)
        mask = src != 0
        enc_proj = self.decoder.attention.U(enc_out) if self.decoder.use_attention else None
        # Baseline context: mean of encoder states (one fixed vector for the whole sentence).
        fixed = (enc_out * mask.unsqueeze(2)).sum(1) / mask.sum(1, keepdim=True)
        return enc_out, enc_proj, mask, fixed, state

    def forward(self, src, src_lens, tgt, teacher_forcing=1.0):
        enc_out, enc_proj, mask, fixed, state = self.encode(src, src_lens)
        tok = tgt[:, 0]
        logits_all = []
        for t in range(1, tgt.size(1)):
            logits, state, _ = self.decoder.step(tok, state, enc_proj, enc_out, mask, fixed)
            logits_all.append(logits)
            if teacher_forcing >= 1.0 or torch.rand(1).item() < teacher_forcing:
                tok = tgt[:, t]
            else:
                tok = logits.argmax(1)
        return torch.stack(logits_all, dim=1)  # [B, T-1, V]

    @torch.no_grad()
    def greedy(self, src, src_lens, sos, eos, max_len=60):
        enc_out, enc_proj, mask, fixed, state = self.encode(src, src_lens)
        B = src.size(0)
        tok = torch.full((B,), sos, dtype=torch.long, device=src.device)
        outs, done = [], torch.zeros(B, dtype=torch.bool, device=src.device)
        for _ in range(max_len):
            logits, state, _ = self.decoder.step(tok, state, enc_proj, enc_out, mask, fixed)
            tok = logits.argmax(1)
            outs.append(tok)
            done |= tok == eos
            if done.all():
                break
        return torch.stack(outs, dim=1)

    @torch.no_grad()
    def beam_search(self, src, src_len, sos, eos, beam=5, max_len=60, len_alpha=0.7):
        """Single sentence. Returns (token ids, attention matrix [T, S] or None)."""
        enc_out, enc_proj, mask, fixed, state = self.encode(src, src_len)
        beams = [(0.0, [sos], state, [])]  # (logprob, tokens, state, alphas)
        finished = []
        for _ in range(max_len):
            candidates = []
            for score, toks, st, alphas in beams:
                tok = torch.tensor([toks[-1]], device=src.device)
                logits, new_st, alpha = self.decoder.step(tok, st, enc_proj, enc_out, mask, fixed)
                logp = F.log_softmax(logits, dim=1).squeeze(0)
                top = logp.topk(beam)
                for lp, idx in zip(top.values.tolist(), top.indices.tolist()):
                    a = alphas + ([alpha.squeeze(0).cpu()] if alpha is not None else [])
                    candidates.append((score + lp, toks + [idx], new_st, a))
            candidates.sort(key=lambda x: x[0], reverse=True)
            beams = []
            for cand in candidates:
                (finished if cand[1][-1] == eos else beams).append(cand)
                if len(beams) == beam:
                    break
            if len(finished) >= beam or not beams:
                break
        pool = finished or beams
        best = max(pool, key=lambda x: x[0] / ((len(x[1]) - 1) ** len_alpha))
        attn = torch.stack(best[3]) if best[3] else None
        return best[1][1:], attn
