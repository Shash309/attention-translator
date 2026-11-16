import os
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
plt.rcParams["font.family"]="Times New Roman"
from matplotlib.patches import FancyBboxPatch, FancyArrowPatch

OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "figs")
os.makedirs(OUT, exist_ok=True)
NAVY, BLUE, TEAL, AMBER, GREY, RED = "#1f3a5f", "#dbe8f7", "#d9f0ec", "#fdebc8", "#eeeeee", "#f8d7d7"


def new(w, h):
    fig, ax = plt.subplots(figsize=(w, h), dpi=200)
    ax.set_xlim(0, w * 100); ax.set_ylim(0, h * 100); ax.axis("off")
    return fig, ax


def box(ax, x, y, w, h, text, fc=BLUE, fs=9, bold=False, ec=NAVY):
    ax.add_patch(FancyBboxPatch((x, y), w, h, boxstyle="round,pad=2,rounding_size=8", fc=fc, ec=ec, lw=1.1))
    ax.text(x + w / 2, y + h / 2, text, ha="center", va="center", fontsize=fs+0.8,
            fontweight="bold" if bold else "normal", family="Times New Roman", linespacing=1.25)


def arrow(ax, x1, y1, x2, y2, label=None, rad=0.0, fs=8):
    ax.add_patch(FancyArrowPatch((x1, y1), (x2, y2), arrowstyle="-|>", mutation_scale=11, lw=1.1, color=NAVY,
                                 connectionstyle=f"arc3,rad={rad}"))
    if label:
        ax.text((x1 + x2) / 2, (y1 + y2) / 2 + 9, label, ha="center", fontsize=fs, family="serif", style="italic")


def group(ax, x, y, w, h, title):
    ax.add_patch(FancyBboxPatch((x, y), w, h, boxstyle="round,pad=2,rounding_size=10", fc="none", ec="#888", lw=1, ls="--"))
    ax.text(x + 10, y + h - 14, title, fontsize=9, fontweight="bold", family="serif", color=NAVY, va="top")


# 1 ---- overall architecture -------------------------------------------------
fig, ax = new(8.4, 5.6)
group(ax, 15, 405, 810, 140, "DATA LAYER")
box(ax, 35, 425, 150, 70, "Multi30k EN-FR\n29,000 / 1,014 / 1,000", GREY)
box(ax, 225, 425, 150, 70, "Tokenizer\n(lowercase, regex,\nelisions)", BLUE)
box(ax, 415, 425, 150, 70, "Vocabulary\n5,979 EN / 6,486 FR\n(min freq 2)", BLUE)
box(ax, 605, 425, 190, 70, "Padded batches\n(128, masks)", BLUE)
for a, b in ((185, 225), (375, 415), (565, 605)):
    arrow(ax, a, 460, b, 460)
group(ax, 15, 235, 810, 150, "MODEL LAYER (PyTorch)")
box(ax, 35, 255, 230, 85, "Rule-based baseline\nIBM Model 1 dictionary\n+ 2 reordering rules", AMBER)
box(ax, 295, 255, 230, 85, "Seq2seq, no attention\nBi-LSTM encoder, fixed\ncontext vector, LSTM decoder", AMBER)
box(ax, 555, 255, 240, 85, "Seq2seq + Bahdanau attention\nBi-LSTM encoder, additive\nattention, LSTM decoder", TEAL, bold=True)
group(ax, 15, 85, 395, 120, "EVALUATION LAYER")
box(ax, 30, 100, 175, 62, "BLEU, n-gram precision,\nbrevity penalty", BLUE, fs=8.5)
box(ax, 220, 100, 175, 62, "By length, confusion\nmatrices, loss curves", BLUE, fs=8.5)
group(ax, 430, 85, 395, 120, "SERVING LAYER")
box(ax, 445, 100, 175, 62, "Flask API\n/api/translate", BLUE, fs=8.5)
box(ax, 635, 100, 175, 62, "Web UI: translations,\nalignment, heatmap", BLUE, fs=8.5)
arrow(ax, 420, 425, 420, 389)
arrow(ax, 420, 235, 210, 209, rad=0.0)
arrow(ax, 420, 235, 620, 209, rad=0.0)
arrow(ax, 620, 131, 635, 131)
ax.text(420, 40, "Fig. 4.1 Overall system architecture", ha="center", fontsize=1, alpha=0)
fig.savefig(os.path.join(OUT, "architecture.png"), bbox_inches="tight", pad_inches=0.05, facecolor="white")

# 2 ---- translation data flow ------------------------------------------------
fig, ax = new(8.4, 3.9)
y = 255
steps = [("English\nsentence", GREY), ("Tokenize\n+ <sos> <eos>", BLUE), ("Vocab IDs\n(unk for rare)", BLUE),
         ("Embedding\n256-d", BLUE)]
x = 15
for t, c in steps:
    box(ax, x, y, 110, 70, t, c, fs=8.5); x += 135
arrow(ax, 125, y + 35, 150, y + 35); arrow(ax, 260, y + 35, 285, y + 35); arrow(ax, 395, y + 35, 420, y + 35)
box(ax, 570, y, 250, 70, "Bi-LSTM encoder\n2 x 256 -> h_j (512-d)", TEAL, fs=9, bold=True)
arrow(ax, 530, y + 35, 570, y + 35)
box(ax, 570, 120, 250, 70, "Bahdanau attention\nscore - softmax - context c_i", TEAL, fs=9, bold=True)
arrow(ax, 695, y, 695, 190, "h_1 ... h_n")
box(ax, 285, 120, 250, 70, "LSTM decoder (512)\nstep i -> word distribution", TEAL, fs=9, bold=True)
arrow(ax, 570, 155, 535, 155, "c_i")
arrow(ax, 535, 140, 570, 140)
ax.text(552, 128, "s_(i-1)", ha="center", fontsize=7, family="serif", style="italic")
box(ax, 15, 120, 220, 70, "Beam search (width 5)\nlength-normalised", BLUE, fs=9)
arrow(ax, 285, 155, 235, 155)
box(ax, 15, 25, 220, 60, "French translation\n(detokenised)", GREY, fs=9)
arrow(ax, 125, 120, 125, 85)
box(ax, 285, 25, 250, 60, "Attention weights alpha_ij\n-> heatmap / alignment view", AMBER, fs=9)
arrow(ax, 695, 120, 535, 70, rad=0.0)
fig.savefig(os.path.join(OUT, "dataflow.png"), bbox_inches="tight", pad_inches=0.05, facecolor="white")

# 3 ---- attention mechanism --------------------------------------------------
fig, ax = new(8.4, 4.8)
ax.text(15, 462, "Encoder states h_j (source words)", fontsize=10, family="Times New Roman", fontweight="bold", color=NAVY)
ax.text(15, 440, "score  e_ij = v^T tanh(W s_(i-1) + U h_j)   ->   softmax over j   ->   weights a_ij (sum to 1)", fontsize=9.5, family="Times New Roman", style="italic")
srcs = ["<sos>", "a", "man", "in", "a", "red", "shirt", "..."]
wts = [0.02, 0.03, 0.05, 0.04, 0.03, 0.78, 0.04, 0.01]
for k, w in enumerate(srcs):
    box(ax, 15 + k * 100, 345, 80, 45, f"h{k}\n{w}", BLUE, fs=8)
    arrow(ax, 55 + k * 100, 345, 55 + k * 100, 290)
    box(ax, 15 + k * 100, 255, 80, 35, f"a = {wts[k]:.2f}", AMBER if wts[k] < 0.5 else "#f6c26b", fs=8)
    arrow(ax, 55 + k * 100, 255, 400, 195)
box(ax, 245, 150, 310, 50, "context  c_i = sum_j a_ij h_j", TEAL, fs=9, bold=True)
box(ax, 20, 40, 230, 60, "previous decoder state\ns_(i-1)  (the query)", GREY, fs=8.5)
arrow(ax, 135, 100, 300, 150, "query")
box(ax, 330, 40, 330, 60, "LSTM decoder step -> French word\n(\"rouge\" attends to \"red\")", TEAL, fs=8.5, bold=True)
arrow(ax, 400, 150, 470, 102)
fig.savefig(os.path.join(OUT, "attention.png"), bbox_inches="tight", pad_inches=0.05, facecolor="white")

# 4 ---- bottleneck vs attention ---------------------------------------------
fig, ax = new(8.4, 3.2)
ax.text(210, 295, "Without attention", ha="center", fontsize=10, fontweight="bold", family="Times New Roman", color=NAVY)
ax.text(630, 295, "With attention", ha="center", fontsize=10, fontweight="bold", family="Times New Roman", color=NAVY)
for k in range(5):
    box(ax, 15 + k * 62, 215, 52, 34, f"h{k+1}", BLUE, fs=8)
    box(ax, 535 + k * 62, 215, 52, 34, f"h{k+1}", BLUE, fs=8)
box(ax, 120, 120, 170, 45, "ONE fixed vector\n(mean of h)", RED, fs=9)
for k in range(5):
    arrow(ax, 41 + k * 62, 215, 205, 167)
box(ax, 120, 25, 170, 45, "Decoder (all steps)", AMBER, fs=9)
arrow(ax, 205, 120, 205, 72)
box(ax, 560, 120, 260, 45, "different c_i at every step i", TEAL, fs=9)
for k in range(5):
    arrow(ax, 561 + k * 62, 215, 690, 167)
box(ax, 560, 25, 260, 45, "Decoder step i (looks at all h_j)", AMBER, fs=9)
arrow(ax, 690, 120, 690, 72)
fig.savefig(os.path.join(OUT, "bottleneck.png"), bbox_inches="tight", pad_inches=0.05, facecolor="white")
print("ok")
