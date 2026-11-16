# Viva Guide: Neural Machine Translation with Attention

**What we built:** a neural network that translates **English → French** and shows which English words it looked at for each French word.

**Results:** Rule-based **19.2** → No attention **40.7** → **With attention 56.8 BLEU**

The guide is split into **3 parts**, one per member. Each part has what to explain, the questions you'll be asked, and your role in the demo.

---

# Part 1: The problem, data & baseline

## What to explain

**1. The problem**
- Translation isn't word-for-word:
  - word order changes: "red shirt" → "t-shirt **rouge**";
  - words have gender: "**une** petite fille";
  - one phrase can become one word: "is running" → "court".

**2. Old method: rule-based**
- Look each word up in a dictionary and apply hand-written grammar rules.
- It breaks on anything the rules don't cover.

**3. Plain neural seq2seq**
- The **encoder** reads the English sentence and squeezes it into **one fixed vector**. The **decoder** writes French from that vector.
- **Problem, the "bottleneck":** a long sentence can't fit in one vector, so information is lost.

**4. Our fix: attention**
- The decoder can look back at **every English word** at every step and focus on the relevant ones.

**5. Dataset: Multi30k**
- English–French captions of Flickr images.
- **29,000 train / 1,014 validation / 1,000 test** sentence pairs, about 13 words each.

**6. Preprocessing**
1. Lowercase the text and split it into words.
2. Add `<sos>` (start) and `<eos>` (end) tokens.
3. Build the vocabulary: **5,979 English** and **6,486 French** words. Words seen only once become `<unk>`.
4. Pad sentences in a batch to the same length with `<pad>`.

**7. Our rule-based baseline**
- **IBM Model 1** learns a word dictionary automatically from the sentence pairs.
- Each word is translated using that dictionary, plus one rule: colour words go after the noun.
- Score: **19.2 BLEU**.
- Errors: "**un** fille" (wrong gender), "**est court**" (word-for-word).

## Questions you'll be asked

| Question | Answer |
|---|---|
| What problem does attention solve? | The fixed-vector bottleneck. Instead of one vector, the decoder looks at all English words for every French word. |
| Why Multi30k? | Clean, small and standard. It trains on one GPU in minutes. |
| What is `<unk>`? | A rare word not in the vocabulary. The model can't translate it. |
| Why build the vocabulary from training data only? | Using test data would be cheating and inflate the scores. |
| How does IBM Model 1 learn without labels? | Words that keep appearing together in sentence pairs get a high translation probability. It's learned with the EM algorithm. |
| Why is the rule-based system so bad? | It translates word by word, so it can't handle gender, word order or phrases unless someone writes a rule for each case. |

## Your part in the demo
- Click **"A little girl in a pink dress…"**.
- Point out the rule-based mistakes: "**un** petite fille", "herbe **vert**".
- End the demo with the scores: **19 → 41 → 57 BLEU**.

---

# Part 2: The model (encoder, attention, decoder)

## What to explain

**Model type:** an encoder–decoder (seq2seq) with **Bahdanau attention**, built in **PyTorch**, with about **16 million parameters**.

```
English → Embedding → Bi-LSTM Encoder → word vectors
                                           ↓
                                       Attention
                                           ↓
previous French word → LSTM Decoder → next French word
```

**1. Embedding**
- Each word becomes a vector of **256 numbers**, learned during training.

**2. Encoder: Bi-LSTM**
- One LSTM reads **left → right**, another **right → left**.
- Each English word gets a vector (512) that knows the words on **both sides**.
- **Why LSTM?** Its gates help it remember long sentences, avoiding the vanishing-gradient problem of plain RNNs.

**3. Attention (the main idea)**

At each French word, three steps:

| Step | Formula | Meaning |
|---|---|---|
| 1. Score | eᵢⱼ = vᵀ tanh(W·sᵢ₋₁ + U·hⱼ) | How relevant is each English word right now? |
| 2. Softmax | αᵢⱼ = softmax(eᵢⱼ) | Turn the scores into weights that add up to 1 (100%) |
| 3. Context | cᵢ = Σ αᵢⱼ · hⱼ | A weighted mix of the English word vectors |

- sᵢ₋₁ = the decoder's previous state; hⱼ = English word *j*'s vector. W, U and v are learned.
- **No one tells the model the alignments.** It learns where to look only because that reduces the translation error.

**4. Decoder: LSTM**
- **Input:** the previous French word plus the context vector.
- **Output:** probabilities over all **6,486** French words; the model picks the next word.

**5. Baseline without attention**
- The **same model**, but the decoder gets **one fixed vector** (the average of the English vectors) every step.
- Since only attention changed, the **+16 BLEU** gain comes from attention alone.

## Questions you'll be asked

| Question | Answer |
|---|---|
| What is attention, in one line? | A weighted average of all English word vectors, recomputed for every French word. |
| Explain the three formulas. | Score each English word, softmax the scores into weights, then take the weighted sum as the context. |
| Why softmax? | The weights become positive and sum to 1, and it's differentiable, so it can be trained. |
| How does it learn alignments without labels? | From the translation loss alone. Good attention gives lower loss, so backpropagation learns it. |
| Why a bidirectional encoder? | A word's meaning depends on the words before and after it. |
| Why is the decoder not bidirectional? | French is generated left to right; future words don't exist yet. |
| LSTM vs RNN? | LSTM has gates and a memory cell, so it remembers long-range information. A plain RNN forgets (vanishing gradient). |
| Bahdanau vs Luong attention? | Bahdanau adds and uses a small network (ours). Luong uses a dot product: simpler and faster. |
| How is this related to Transformers? | Transformers drop the LSTM and use only attention (self-attention). Our attention is their ancestor. |
| Why mask padding? | So the model never pays attention to empty `<pad>` tokens. |

## Your part in the demo
- In the **Alignment** view, show the **crossing lines**: "pink dress → robe rose".
- Hover over **"rose"** to show it looks at **"pink"**, which proves the model learned word order.
- In the console, point at the trace: "rose ← pink 9x%".

---

# Part 3: Training, results & demo

## What to explain

**1. Training settings**

| Setting | Value | Why (one line) |
|---|---|---|
| Loss | Cross-entropy | Standard for predicting the next word |
| Optimizer | Adam, learning rate 0.001 | Adjusts the learning rate per parameter automatically |
| Epochs / batch size | 15 / 128 | |
| Gradient clipping | 1.0 | Stops gradients from exploding in LSTMs |
| Dropout | 0.3 | Prevents overfitting |
| Label smoothing | 0.1 | Stops the model being over-confident |
| GPU | RTX 4060 | ~1 minute per epoch |

**2. Teacher forcing**
- During training, the decoder is given the **correct** previous word, not its own guess. This makes training faster.
- **Downside:** at test time it uses its own guesses, so mistakes can pile up ("exposure bias").

**3. Beam search (width 5)**
- Instead of picking only the single best word each step, the model keeps the **top 5 sentences** and picks the best at the end.
- **Length normalization** stops it from preferring sentences that are too short.

**4. Results**

| System | Test BLEU |
|---|---|
| Rule-based | 19.2 |
| Seq2seq, no attention | 40.7 |
| **Seq2seq + attention** | **56.8** |

- **BLEU** = how many words and short phrases match a human translation (0–100).
- Attention was ahead at **every** epoch of training (`outputs/bleu_curves.png`).
- **Honest note:** our BLEU is computed on lowercased text, which scores a bit higher than the standard research version (sacreBLEU). Say this before they ask.

**5. Heatmap proof**
- "red shirt" → "t-shirt **rouge**": the "rouge" row lights up on "red".
- The model learned to swap word order **by itself**.

**6. Web demo**
- A **Flask** server runs all 3 models.
- The webpage shows the translations, alignment lines, the heatmap, and a live console showing what happens inside the model.
- It handles wrong input safely: empty text, text that's too long, and non-English text.

**7. Limitations & future work**
- Unknown words become `<unk>`. **Fix:** subword tokenization (BPE).
- Only trained on image captions, so it fails on other kinds of text.
- Slower than no attention (~270 ms vs 34 ms).
- **Next steps:** compare against a Transformer, and use a bigger dataset.

## Questions you'll be asked

| Question | Answer |
|---|---|
| What is teacher forcing? | Giving the correct previous word during training. The downside is that errors can pile up at test time. |
| Why gradient clipping? | LSTM gradients can explode; clipping limits their size. |
| Greedy vs beam search? | Greedy picks the best word each step. Beam keeps the top 5 sentences, so it gives better results. |
| What is BLEU? | Word and phrase overlap with a human translation. Its weakness: it penalizes correct synonyms. |
| BLEU is 56.8, but the target was 22–28. Why? | We score lowercased text and the dataset is easy. What matters is the gain: 19 → 41 → 57. |
| Is the comparison fair? | Yes. Same model, data and settings; only attention was removed. |
| Why is attention slower? | It re-checks every English word for every French word. |
| What would you improve? | Subword tokens (to fix `<unk>`), a Transformer, a bigger dataset. |

## Your part in the demo
- Start the app (`python app.py`) and show the console's **model summary**.
- Switch to the **Heatmap** tab, then click **Random test sentence** to compare with the human translation.
- Type something in French to show the **"Is the sentence in English?"** warning.

---

## Key numbers (everyone)

| | |
|---|---|
| Data | 29,000 train / 1,014 val / 1,000 test |
| Vocabulary | 5,979 English / 6,486 French |
| Parameters | ~16 million |
| BLEU | 19.2 / 40.7 / **56.8** |
