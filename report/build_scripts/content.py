"""Report body (Chapters 1-8 + Appendix A) for the NMT-with-attention project."""
import json
from lib import LEFT
import os

REPO = r"E:\CODING\attention-translator"
FIG = os.path.join(os.path.dirname(os.path.abspath(__file__)), "figs")
M = json.load(open(os.path.join(REPO, "outputs", "eval", "metrics.json"), encoding="utf8"))
OUT = os.path.join(REPO, "outputs")


def src(name, start=None, end=None):
    lines = open(os.path.join(REPO, name), encoding="utf8").read().split("\n")
    return "\n".join(lines[(start or 1) - 1:end])


def write_body(w):
    A, B, R = M["attention"], M["baseline"], M["rule"]

    # ======================= CHAPTER 1 =======================
    w.chapter(1, "INTRODUCTION")
    w.h1("1.1 Introduction to Project")
    w.para("Language is still one of the largest barriers to sharing information. More than 7,100 languages are "
           "spoken in the world, and roughly 5.5 billion people do not have English as their first language. "
           "Healthcare, education, travel, emergency response, trade and diplomacy all depend on text being "
           "carried correctly from one language to another. Machine translation (MT) is the branch of natural "
           "language processing that automates this task.")
    w.para("Early MT systems translated word by word with dictionaries and hand-written grammar rules. Such systems "
           "cannot agree gender, cannot reorder words unless a rule exists for the exact case, and ignore the "
           "meaning of the whole sentence. Neural machine translation (NMT) replaced them: a single neural network "
           "reads the source sentence and writes the target sentence, learning vocabulary, word order and "
           "agreement directly from parallel text. The first NMT models squeezed the whole source sentence into one "
           "fixed-size vector, which loses information on long sentences. Bahdanau et al. (2015) removed this "
           "bottleneck with an //attention// mechanism that lets the decoder look back at every source word while it "
           "writes each target word.")
    w.para("This project builds an English-to-French neural translator with Bahdanau additive attention, trains it on "
           "the Multi30k image-caption corpus, and compares it with two baselines: a plain sequence-to-sequence "
           "model without attention, and a rule-based word-by-word dictionary translator. Beyond translation "
           "quality, the project exposes the attention weights as heatmaps and alignment lines, so that a user can "
           "see which English words each French word was generated from. A Flask web application demonstrates all "
           "three systems side by side.")

    w.h1("1.2 Problem Statement")
    w.para("Translating text between languages with software faces three key challenges:", keep_next=True)
    w.numbered(["Translation is not word-for-word. Word order changes (\"a red shirt\" becomes \"un t-shirt "
                "rouge\"), words carry gender (\"a little girl\" becomes \"une petite fille\"), and a phrase can "
                "collapse into one word (\"is running\" becomes \"court\").",
                "Dictionary and rule-based systems do not scale to real sentences, because every exception needs "
                "a new hand-written rule and the system has no sense of context.",
                "A plain encoder-decoder network compresses a sentence of any length into one fixed vector. Long "
                "sentences lose information, and the model is a black box that gives no hint of why a word was "
                "chosen."])
    w.para("What is needed is a translation model that learns from data, keeps access to the whole source sentence "
           "at every step, and makes its decisions visible. The project therefore asks: //how much does additive "
           "attention improve English-to-French translation over a no-attention network and a rule-based system, "
           "and can the learned attention weights be shown as interpretable word alignments?//")

    w.h1("1.3 Motivation")
    w.para("Attention is the core idea behind modern language technology, including the Transformer and the large "
           "language models built on it. Implementing it from scratch on a small, clean problem is the most direct "
           "way to understand why it works. Multi30k is small enough (29,000 training pairs) to train on a single "
           "laptop GPU in about ten minutes per model, yet rich enough to show word reordering, gender "
           "agreement and long-sentence effects.")
    w.para("The project is also motivated by explainability. Attention weights form a matrix that can be drawn as a "
           "heatmap, giving a rare look inside a neural model. Showing that the network learned to place "
           "\"rouge\" after \"t-shirt\" by attending to \"red\", without any alignment labels, turns an abstract "
           "equation into something a viewer can verify. The objectives are therefore threefold: //learn// an "
           "encoder-decoder end to end on real sentence pairs, //attend// with a Bahdanau-style additive "
           "mechanism, and //reveal// the attention matrix as an interpretable visual.")

    w.h1("1.4 Sustainable Development Goal of the Project")
    w.para("The project supports three United Nations Sustainable Development Goals. **SDG 4 (Quality Education):** "
           "machine translation lowers the language barrier to learning material, and the interactive heatmaps and "
           "demo make the workings of neural translation easy to teach. **SDG 9 (Industry, Innovation and "
           "Infrastructure):** the project builds and evaluates a complete NLP pipeline, from data to a deployed "
           "web service, on modest hardware. **SDG 10 (Reduced Inequalities):** translation technology widens "
           "access to information, health advice and public services for people who do not speak the dominant "
           "language of a region.")

    # ======================= CHAPTER 2 =======================
    w.chapter(2, "LITERATURE SURVEY")
    w.h1("2.1 Overview of the Research Area")
    w.para("Machine translation has moved through three eras: rule-based systems built from dictionaries and "
           "grammar rules, statistical MT that learned phrase tables from parallel corpora, and neural MT that "
           "learns a single end-to-end model. Statistical word alignment models such as the IBM models "
           "(Brown et al., 1993) remain important because they learn bilingual dictionaries automatically from "
           "sentence pairs, and our rule-based baseline uses IBM Model 1 for exactly this reason.")
    w.para("Neural MT began with recurrent encoder-decoder networks (Cho et al., 2014; Sutskever et al., 2014). "
           "Their weakness, a fixed-length sentence vector, was removed by the attention mechanism of Bahdanau et "
           "al. (2015) and its simplification by Luong et al. (2015). The Transformer (Vaswani et al., 2017) later "
           "replaced recurrence by self-attention alone, and today's multilingual systems such as NLLB cover more "
           "than 200 languages. This project implements the recurrent attention model that sits at the centre of "
           "this history, and is the direct ancestor of the Transformer.")
    w.para("Table 2.1 lists the six studies that frame this project. The first two are the methods we implement; "
           "the other four are recent work on attention, multilinguality and interpretability.", keep_next=True)
    w.table(["Author (Year) & Venue", "Methodology", "Advantages", "Limitations"],
            [["Sutskever, Vinyals & Le (2014), NeurIPS",
              "Deep LSTM encoder-decoder; the whole source sentence is encoded into one fixed vector",
              "First strong end-to-end NMT; no hand-made features or phrase tables",
              "Fixed-vector bottleneck; quality drops on long sentences"],
             ["Bahdanau, Cho & Bengio (2015), ICLR",
              "Bidirectional RNN encoder with additive attention (soft alignment) over all source states",
              "Removes the bottleneck; learns alignments; better on long sentences",
              "Sequential decoding is slow; rare words become unknown tokens"],
             ["NLLB Team, Meta AI (2022/2024), Nature",
              "Large multilingual Transformer MT covering 200+ languages",
              "Brings attention-based MT to many low-resource languages",
              "Very large and compute-heavy; hard to inspect or retrain"],
             ["Bhadauria et al. (2024), Springer TCCE",
              "Attention-based NMT applied to multilingual communication",
              "Shows attention is still effective in applied translation settings",
              "Task-specific results, not directly comparable with Multi30k"],
             ["Pang et al. (2025), TACL",
              "Revisits classic NMT challenges (rare words, long sentences, alignment, beam search) in the "
              "LLM era",
              "Shows these challenges are still open; motivates studying alignment",
              "Focuses on large language models, not small recurrent models"],
             ["Nourbakhsh, Lamsiyah & Schommer (2025), RANLP",
              "Studies attribution maps for encoder-decoder translation models",
              "Supports reading attention as a faithful explanation of the model",
              "Faithfulness depends on model and language pair"]],
            [2100, 2800, 2300, 2100], caption="Research Area", size=10)

    w.h1("2.2 Rule-Based and Statistical Translation")
    w.para("Rule-based MT translates through bilingual dictionaries and hand-coded reordering rules. It is "
           "predictable and cheap, but every grammatical phenomenon needs its own rule, and word choice ignores "
           "context. Statistical MT replaced hand-written knowledge with probabilities learned from parallel text. "
           "IBM Model 1 (Brown et al., 1993) estimates a word-translation table t(f|e) with the "
           "Expectation-Maximisation (EM) algorithm: words that repeatedly appear together in aligned sentence "
           "pairs receive a high translation probability, with no labelled alignments needed. Model 1 ignores word "
           "order, which is why a system built on it still needs separate reordering rules.")

    w.h1("2.3 Recurrent Neural Sequence-to-Sequence Models")
    w.para("A sequence-to-sequence model has an encoder that reads the source sentence and a decoder that writes the "
           "target. Long Short-Term Memory (LSTM) cells (Hochreiter and Schmidhuber, 1997) are the usual building "
           "block, because their gates and memory cell avoid the vanishing-gradient problem of plain recurrent "
           "networks. Sutskever et al. (2014) showed that a deep LSTM encoder-decoder can match phrase-based "
           "systems on English-French translation. Bidirectional encoders (Schuster and Paliwal, 1997) read the "
           "sentence in both directions so that every word vector carries left and right context.")
    w.para("The limitation is the bottleneck: whatever the sentence length, the decoder only sees one fixed-size "
           "vector. Figure 4.4 in Chapter 4 illustrates this, and Section 6.3 measures its effect on long "
           "sentences.")

    w.h1("2.4 Attention Mechanisms")
    w.para("Bahdanau et al. (2015) let the decoder compute a fresh context vector at every output step, as a "
           "weighted average of all encoder states. The weights come from a small feed-forward network that scores "
           "the previous decoder state against each encoder state (additive attention), so the model //softly "
           "aligns// each target word to the source words that matter. Luong et al. (2015) proposed multiplicative "
           "(dot-product) variants and global and local attention. Vaswani et al. (2017) generalised the idea into "
           "scaled dot-product self-attention and removed recurrence completely. Because the attention weights "
           "form a probability distribution over source words, they can be plotted directly, which is the basis "
           "of the heatmaps in this project.")

    w.h1("2.5 Scale, Interpretability and Open Challenges")
    w.para("NLLB Team (2024) shows that attention-based translation scales to more than 200 languages, including "
           "many low-resource ones. Bhadauria et al. (2024) apply attention-based NMT to multilingual "
           "communication. Pang et al. (2025) argue that classic NMT challenges, namely rare-word prediction, long "
           "sentences, word alignment and sub-optimal beam search, remain open even in the era of large language "
           "models. Nourbakhsh et al. (2025) examine attribution maps in encoder-decoder translation and "
           "support using attention as an explanation. Word-level vocabularies suffer from unknown words; "
           "subword units learned with byte-pair encoding (Sennrich et al., 2016) are the standard remedy.")

    w.h1("2.6 Challenges and Research Gaps")
    w.bullets(["**Fixed-vector bottleneck:** quality of a plain encoder-decoder falls steadily with sentence length.",
               "**Opaque decisions:** neural translators rarely show why a word was chosen; attention maps give a "
               "partial answer that needs to be shown, not just claimed.",
               "**Unknown words:** word-level vocabularies map rare words to a single unknown token.",
               "**Exposure bias:** models are trained on true previous words but decode with their own guesses.",
               "**Fair comparison:** many reports compare systems with different data and settings. A controlled "
               "comparison, same network and data with only attention removed, isolates the contribution of "
               "attention."])

    w.h1("2.7 Summary")
    w.para("The literature shows a clear path from rule-based and statistical systems to recurrent encoder-decoders, "
           "to attention, and then to the Transformer. This project fills a small but useful gap: a controlled, "
           "reproducible comparison of rule-based, no-attention and attention models on the same data, with "
           "the attention weights exposed as interactive heatmaps in a working web application.")

    # ======================= CHAPTER 3 =======================
    w.chapter(3, "SPRINT PLANNING AND EXECUTION METHODOLOGY")
    w.para("The project was developed with an Agile Scrum approach: the work was split into three short sprints, "
           "each ending in a working, testable increment (a data pipeline and baselines, trained models and "
           "evaluation, then the demo application and documentation). The four team members took ownership of "
           "distinct parts of the system in each sprint, as shown below.")
    w.table(["Member", "Registration No.", "Primary responsibility"],
            [["Ankam Sai Anirudh", "RA2311026010087", "Dataset pipeline, tokenizer, vocabulary; rule-based baseline"],
             ["Atharva Bhutada", "RA2311026010089", "Model architecture: encoder, attention, decoder, beam search"],
             ["Vansh Agrawal", "RA2311026010120", "Training, baseline comparison, evaluation and visualisation"],
             ["Shashwat Sharma", "RA2311026010121", "Web demo, presentation deck, viva guide and report"]],
            [2300, 2000, 4900], caption="Team Roles")

    w.h1("3.1 Sprint I: Data Pipeline, Baseline and Model Architecture")
    w.h2("3.1.1 Objectives with User Stories of Sprint I")
    w.table(["ID", "USER STORY", "OBJECTIVE"],
            [["1", "As a researcher, I want English-French sentence pairs cleaned and tokenised so that models can "
                   "be trained on them.", "Data pipeline"],
             ["2", "As a researcher, I want a dictionary-based translator so that I have a classical baseline to "
                   "beat.", "Rule-based baseline"],
             ["3", "As a researcher, I want an encoder-decoder with Bahdanau attention (and a switch to turn "
                   "attention off) so that the effect of attention can be isolated.", "Model architecture"]],
            [600, 6300, 2300], caption="Sprint I", align=["c", "l", "l"])
    w.h2("3.1.2 Functional Document")
    w.bullets(["**Data acquisition:** Multi30k Task 1 English-French files (train, val, test 2016 Flickr) are "
               "downloaded from the official repository by `data.py`.",
               "**Preprocessing:** lowercase, regex tokenizer that splits punctuation and keeps French elisions "
               "such as `l'`; `<sos>`, `<eos>`, `<pad>`, `<unk>` special tokens; vocabulary built from the "
               "training split only with minimum frequency 2; training pairs longer than 50 tokens dropped.",
               "**Rule-based baseline (`rule_based.py`):** IBM Model 1 dictionary learned with 5 EM iterations, "
               "plus two rules (colour adjectives move after the noun, the possessive 's is dropped).",
               "**Model (`model.py`):** Bi-LSTM encoder, additive attention, LSTM decoder, greedy and beam search, "
               "and a `use_attention=False` mode that gives the fixed-context baseline."])
    w.h2("3.1.3 Architecture Document")
    w.para("Sprint I produced the data layer and the model layer of the system architecture (Figure 4.1): raw text "
           "-> tokenizer -> vocabulary -> padded batches feed three interchangeable translators. Data flow: "
           "Multi30k files -> tokenise -> vocabulary -> batches -> model.")
    w.h2("3.1.4 Outcome of Objectives / Result Analysis")
    w.bullets(["Vocabularies of 5,979 English and 6,486 French words built from 29,000 training pairs.",
               f"Rule-based translator working end to end with a 5,764-word dictionary and a test BLEU of "
               f"{R['bleu']:.2f}.",
               "Attention and no-attention models implemented in one class, so the comparison changes only one "
               "component."])
    w.h2("3.1.5 Sprint Retrospective")
    w.para("**What went well:** a single `Seq2Seq` class with an attention switch made the later comparison fair "
           "by construction; building the vocabulary from training data only avoided any test leakage.",
           before=4)
    w.para("**Areas for improvement:** the proposal planned spaCy tokenisation and about 10,000 subword units; "
           "a custom regex tokenizer and a word-level vocabulary were used instead, which leaves rare words as "
           "unknown tokens.", before=4)

    w.h1("3.2 Sprint II: Training, Evaluation and Visualisation")
    w.h2("3.2.1 Objectives with User Stories of Sprint II")
    w.table(["ID", "USER STORY", "OBJECTIVE"],
            [["1", "As a researcher, I want both neural models trained with identical settings so that the "
                   "comparison is fair.", "Training"],
             ["2", "As a reviewer, I want BLEU, n-gram precision, results by sentence length and error analysis "
                   "so that I can see where attention helps.", "Evaluation"],
             ["3", "As a learner, I want attention heatmaps for any sentence so that I can see what the model "
                   "looked at.", "Visualisation"]],
            [600, 6300, 2300], caption="Sprint II", align=["c", "l", "l"])
    w.h2("3.2.2 Functional Document")
    w.bullets(["**Training (`train.py`):** teacher forcing, cross-entropy with label smoothing 0.1, Adam "
               "(learning rate 1e-3) with ReduceLROnPlateau, gradient clipping at 1.0, 15 epochs, batch size 128, "
               "best-validation-loss checkpointing, per-epoch validation BLEU.",
               "**Evaluation (`evaluate.py`, `evaluation_report.py`):** beam-search BLEU on the 1,000-sentence "
               "test set, 1-4-gram precision, brevity penalty, exact matches, BLEU by sentence length, and "
               "confusion matrices for the un/une articles and for colour words.",
               "**Visualisation (`visualize.py`, `plot_curves.py`):** heatmap of the attention matrix for any "
               "sentence, and validation-BLEU curves for both models."])
    w.h2("3.2.3 Architecture Document")
    w.para("The evaluation layer consumes the checkpoints written by the training loop and the rule-based "
           "dictionary, decodes the test set with each system, and writes charts and `metrics.json` to "
           "`outputs/eval/`.")
    w.h2("3.2.4 Outcome of Objectives / Result Analysis")
    w.bullets([f"Attention model: test BLEU {A['bleu']:.2f}; no-attention baseline: {B['bleu']:.2f}; "
               f"rule-based: {R['bleu']:.2f}.",
               "Attention was ahead of the baseline at every training epoch.",
               "Heatmaps show learned word reordering, for example \"red shirt\" -> \"t-shirt rouge\"."])
    w.h2("3.2.5 Sprint Retrospective")
    w.para("**What went well:** the controlled comparison produced a clean +16.1 BLEU result, and the extra "
           "evaluation (by length, confusion matrices) explained //why// attention wins.", before=4)
    w.para("**Areas for improvement:** two training jobs sharing a laptop GPU crashed with a cuBLAS error, so "
           "jobs had to be run one at a time; attention rows sometimes sit one word to the left of the source "
           "word, a known trait of Bahdanau attention, which uses the decoder state from before the current "
           "word.", before=4)

    w.h1("3.3 Sprint III: Web Demo, Documentation and Review")
    w.h2("3.3.1 Objectives with User Stories of Sprint III")
    w.table(["ID", "USER STORY", "OBJECTIVE"],
            [["1", "As a user, I want to type an English sentence and see all three translations side by side so "
                   "that I can compare them.", "Web demo"],
             ["2", "As a user, I want bad input (empty, too long, non-English) to give a clear message instead of "
                   "a crash.", "Robustness"],
             ["3", "As a team, we want a presentation, a viva guide and a project report so that the work can be "
                   "assessed.", "Documentation"]],
            [600, 6300, 2300], caption="Sprint III", align=["c", "l", "l"])
    w.h2("3.3.2 Functional Document")
    w.bullets(["**Flask application (`app.py`):** loads the attention, no-attention and rule-based models once, "
               "serialises inference with a lock, and exposes `/api/translate`, `/api/example` and `/api/health`.",
               "**Single-page frontend (`web/index.html`):** three translation cards with test BLEU, an "
               "alignment view and a heatmap view, a random test-sentence button and an under-the-hood console.",
               "**Documents:** a 26-slide deck (`NMT_Attention_Project_v3.pptx`), `VIVA_GUIDE.md`, a demo "
               "notebook and this report."])
    w.h2("3.3.3 Architecture Document")
    w.para("The serving layer wraps the same model code used for evaluation, so the numbers shown in the web page "
           "come from the trained checkpoints and not from a separate implementation.")
    w.h2("3.3.4 Outcome of Objectives / Result Analysis")
    w.bullets(["A responsive demo that was tested in a desktop browser and at phone width (375 px).",
               "Input validation for empty text, no letters, over 300 characters or 60 words, a non-numeric "
               "beam, malformed requests and missing checkpoints.",
               "Complete documentation set: deck, viva guide, README and report."])
    w.h2("3.3.5 Sprint Retrospective")
    w.para("**What went well:** reusing the evaluation code in the server kept the demo consistent with the "
           "reported results.", before=4)
    w.para("**Areas for improvement:** beam-search attention inference is slower than no attention (about 270 ms "
           "against 34 ms per sentence); the demo covers short image-caption style sentences only.", before=4)

    w.h1("3.4 Sprint Review and Testing")
    w.bullets(["**Model testing:** validation loss, perplexity and BLEU after every epoch; final test BLEU with beam "
               "search.",
               "**Functional testing:** the API validation cases in Section 5.7.",
               "**Integration testing:** the web page calls the Flask API, which calls the same `translate()` "
               "function used by `evaluate.py`.",
               "**Usability testing:** desktop and 375 px phone-width layouts."])

    w.h1("3.5 Final Sprint Outcome and Summary")
    w.para("The three sprints together delivered a data pipeline, three translators, a full evaluation suite and an "
           "interactive web application, which validates the Agile approach for a research-style project.",
           keep_next=True)
    w.table(["Sprint", "Owners", "Modules completed"],
            [["I", "Anirudh, Atharva", "data.py, rule_based.py, model.py"],
             ["II", "Vansh (with Atharva)", "train.py, evaluate.py, evaluation_report.py, visualize.py, plot_curves.py"],
             ["III", "Shashwat (with all)", "app.py, web/index.html, deck, viva guide, report"]],
            [1200, 2600, 5400], caption="Sprint Summary Table")

    # ======================= CHAPTER 4 =======================
    w.chapter(4, "SYSTEM DESIGN AND METHODOLOGY")
    w.h1("4.1 Introduction")
    w.para("The system is a small, modular NLP stack written in Python with PyTorch. It has four layers: a data "
           "layer that turns raw sentence pairs into padded batches; a model layer with three interchangeable "
           "translators; an evaluation layer that measures them on a held-out test set; and a serving layer that "
           "shows their output in a browser. The layered design keeps each part independently testable.")

    w.h1("4.2 Overall System Architecture")
    w.figure(os.path.join(FIG, "architecture.png"), 6.0, "Overall System Architecture")

    w.h1("4.3 Module Description")
    w.h2("4.3.1 Data Layer")
    w.para("`data.py` downloads Multi30k, tokenises, builds the vocabularies and creates batches. Technologies: "
           "Python `re`, `urllib`, PyTorch `Dataset`/`DataLoader` with a padding collate function. Padding index 0 "
           "is masked in the loss and in attention.")
    w.h2("4.3.2 Model Layer")
    w.para("`model.py` defines `Encoder`, `BahdanauAttention`, `Decoder` and `Seq2Seq`. `rule_based.py` defines "
           "the dictionary baseline. All three translators expose the same `translate` function so they can be "
           "evaluated and served uniformly.")
    w.h2("4.3.3 Evaluation Layer")
    w.para("`evaluate.py`, `evaluation_report.py` and `plot_curves.py` compute corpus BLEU with NLTK on lowercased "
           "tokens, n-gram precisions, brevity penalty, exact-match counts, sentence-level BLEU, BLEU by "
           "length bucket, confusion matrices, and training curves.")
    w.h2("4.3.4 Serving Layer")
    w.para("`app.py` is a Flask server with a thread lock around inference, a 16 KB request limit, JSON error "
           "responses and start-up checkpoint checks. `web/index.html` is a single-page frontend that draws "
           "translations, the alignment view, the heatmap and the inference console.")

    w.h1("4.4 Data Flow Diagram")
    w.para("A sentence travels through the system as follows: it is tokenised and converted to IDs, embedded, "
           "encoded by the Bi-LSTM, then decoded one word at a time. At every decoding step the attention module "
           "reads all encoder states and the previous decoder state and returns a context vector together with "
           "the attention weights. Beam search keeps the five best partial translations. The weights are returned "
           "with the translation so that the interface can draw them.", keep_next=True)
    w.figure(os.path.join(FIG, "dataflow.png"), 6.1, "Data Flow Diagram")

    w.h1("4.5 Machine Learning Methodology")
    w.h2("4.5.1 Embedding and Bidirectional LSTM Encoder")
    w.para("Each source word ID is mapped to a learned 256-dimensional embedding (dropout 0.3). A bidirectional LSTM "
           "with 256 hidden units per direction reads the sentence left-to-right and right-to-left; the two "
           "directions are concatenated so every source word j gets a 512-dimensional state h_{j} that knows the "
           "words on both sides. The final forward and backward states are merged by a linear layer and a tanh "
           "to form the decoder's initial hidden and cell state. Padded positions are packed away with "
           "`pack_padded_sequence`.")
    w.h2("4.5.2 Bahdanau Additive Attention")
    w.para("At decoding step i the attention module scores every source word against the previous decoder state "
           "s_{i-1}, turns the scores into weights with a softmax (padding masked to zero probability) and "
           "builds the context vector as the weighted sum of encoder states:", keep_next=True)
    w.eq("e_{ij} = v^{T} tanh( W s_{i-1} + U h_{j} )", "4.1")
    w.eq("α_{ij} = exp(e_{ij}) / Σ_{k} exp(e_{ik})", "4.2")
    w.eq("c_{i} = Σ_{j} α_{ij} h_{j}", "4.3")
    w.para("W (512 -> 256), U (512 -> 256) and v (256 -> 1) are learned, with attention dimension 256. U h_{j} does "
           "not depend on the decoder, so it is computed once per sentence and reused at every step. The "
           "attention module adds only about 0.26 million parameters (15.7M -> 16.0M). No alignment labels are "
           "used; the weights are learned purely because they lower the translation loss.", keep_next=True)
    w.figure(os.path.join(FIG, "attention.png"), 6.0, "Attention step for one French word "
             "(weights shown are illustrative)")
    w.h2("4.5.3 LSTM Decoder and Output Layer")
    w.para("The decoder is an LSTM cell with 512 hidden units. Its input is the previous word embedding (256) "
           "concatenated with the context vector (512), a 768-dimensional vector. The next-word scores come from a "
           "\"deep output\" layer that sees the decoder state, the context vector and the previous word "
           "embedding together (512 + 512 + 256 = 1,280 inputs) and projects to the 6,486 French words:",
           keep_next=True)
    w.eq("s_{i} = LSTM( [E(y_{i-1}) ; c_{i}], s_{i-1} )", "4.4")
    w.eq("P( y_{i} | y_{<i}, x ) = softmax( W_{o} [ s_{i} ; c_{i} ; E(y_{i-1}) ] )", "4.5")
    w.h2("4.5.4 No-Attention Baseline")
    w.para("The baseline is the same network with one change: the decoder receives a single fixed context vector, "
           "the mean of the encoder states, at every step instead of a fresh attention context. Because "
           "everything else (data, layers, hyper-parameters, seed) is identical, any difference in score is "
           "caused by attention alone.", keep_next=True)
    w.figure(os.path.join(FIG, "bottleneck.png"), 6.0, "Fixed-Vector Bottleneck versus Attention")
    w.h2("4.5.5 Rule-Based Baseline")
    w.para("The classical system learns a dictionary from the training pairs with IBM Model 1 (five EM "
           "iterations, a NULL source word, and the most probable French word kept for each English word, giving "
           "5,764 entries). At translation time each English word is looked up independently. Two hand-written "
           "rules are applied: a colour adjective placed before a noun is moved after it, and the possessive 's is "
           "dropped. It cannot choose gender, cannot translate phrases such as \"is running\" and keeps English "
           "word order elsewhere.")
    w.h2("4.5.6 Training Procedure")
    w.para("Models are trained with teacher forcing: the decoder is fed the true previous word, which makes "
           "training faster and more stable, at the cost of exposure bias at test time. The loss is "
           "cross-entropy over the target words with padding ignored and label smoothing of 0.1 (Szegedy et "
           "al., 2016), optimised with Adam (Kingma and Ba, 2015). Table 4.1 lists the settings.",
           keep_next=True)
    w.table(["Setting", "Value", "Purpose"],
            [["Embedding size", "256 (source and target)", "Dense word representation"],
             ["Encoder", "Bi-LSTM, 2 x 256 -> 512", "Context from both directions"],
             ["Decoder / attention size", "LSTM 512 / 256", "Generation and alignment scoring"],
             ["Dropout", "0.3", "Regularisation"],
             ["Loss", "Cross-entropy, label smoothing 0.1", "Prevents over-confidence"],
             ["Optimiser", "Adam, learning rate 1e-3, ReduceLROnPlateau (factor 0.5, patience 1)",
              "Adaptive learning rate"],
             ["Gradient clipping", "Norm 1.0", "Stops exploding gradients"],
             ["Epochs / batch size", "15 / 128", "Keep best validation loss"],
             ["Teacher forcing", "1.0", "Feed the true previous word"],
             ["Seed / hardware", "0 / NVIDIA RTX 4060 laptop GPU", "About 10 minutes per model"]],
            [2400, 3800, 3000], caption="Model and Training Configuration", size=10)
    w.h2("4.5.7 Inference: Beam Search")
    w.para("At test time the decoder cannot use the true previous word. Greedy decoding picks the most likely word "
           "at each step, so one early mistake is permanent. Beam search (width 5) instead keeps the five best "
           "partial sentences at every step and expands each of them, stopping at `<eos>` or 60 words. Finished "
           "hypotheses are ranked with length normalisation, score = log P(y) / |y|^0.7, because without it the "
           "search prefers sentences that are too short.")

    w.h1("4.6 Dataset Design")
    w.para("The dataset is Multi30k Task 1 (Elliott et al., 2016): English image captions from Flickr with French "
           "translations. It is the same corpus as the Kaggle mirror `shahadhamza/multi30k-dataset`. Captions are "
           "short (about 13 words on average) and concern everyday scenes, which makes the task clean and "
           "quick to train.", keep_next=True)
    w.table(["Item", "Value"],
            [["Training pairs", "29,000"], ["Validation pairs", "1,014"],
             ["Test pairs (test 2016 Flickr)", "1,000"], ["Average sentence length", "about 13 words"],
             ["English vocabulary", "5,979 words (frequency >= 2, plus 4 special tokens)"],
             ["French vocabulary", "6,486 words"],
             ["Special tokens", "<pad> = 0, <sos>, <eos>, <unk>"]],
            [3600, 5600], caption="Multi30k Dataset Summary", size=10.5)
    w.h2("4.6.1 Preprocessing")
    w.numbered(["**Tokenise:** lowercase, split punctuation, keep French elisions (j'aime -> j' + aime).",
                "**Boundaries:** add `<sos>` and `<eos>`.",
                "**Vocabulary:** map words to IDs, words seen once become `<unk>`; built from the training split only.",
                "**Pad and batch:** pad to equal length per batch of 128 and mask the padding.",
                "**Filter:** drop training pairs longer than 50 tokens."])
    w.h1("4.7 Evaluation Methodology")
    w.para("The main metric is corpus BLEU (Papineni et al., 2002): the geometric mean of modified 1-4-gram "
           "precisions multiplied by a brevity penalty BP = min(1, exp(1 - r/c)), where r is the reference length "
           "and c the hypothesis length. BLEU is computed with NLTK on lowercased, tokenised text, so it reads "
           "higher than detokenised sacreBLEU; the relative differences between systems are the meaningful result. "
           "Because translation has no fixed class set (each step is a 6,486-way choice), confusion matrices are "
           "built on two small word groups: the articles un/une (gender agreement) and nine colour classes "
           "(including \"none\" for a dropped colour). Training progress is tracked with validation loss, "
           "perplexity and greedy validation BLEU.")
    w.h1("4.8 User Interface Design")
    w.bullets(["**Translation cards:** attention, no-attention and rule-based outputs side by side with their test BLEU.",
               "**Alignment view:** lines join each French word to the English words it attended to; line "
               "thickness is the attention weight and hovering a French word highlights its sources.",
               "**Heatmap view:** the full attention matrix with exact weights on hover.",
               "**Under-the-hood console:** tokens, vocabulary IDs, tensor shapes, per-step attention peak and latency.",
               "**Helpers:** random test-sentence button (shows the human reference), unknown-word list, and a "
               "warning when the input does not look like English."])
    w.h1("4.9 Robustness and Security Considerations")
    w.bullets(["Request bodies above 16 KB are rejected early; text is whitespace-normalised.",
               "Length limits of 300 characters and 60 words protect the server; the beam width is clamped to 1-10.",
               "Inference is serialised with a lock because the models are not thread-safe.",
               "Every error returns a JSON message with a suitable HTTP status; unexpected exceptions are logged and "
               "reported generically.",
               "Missing or corrupt checkpoints are reported with the command needed to fix them."])
    w.h1("4.10 Advantages of the System Design")
    w.bullets(["Controlled comparison: one network, a single attention switch.",
               "Modular files, each with one responsibility, and the same code for evaluation and serving.",
               "Explainable output through attention heatmaps and alignment lines.",
               "Runs on a single laptop GPU and is reproducible with a fixed seed."])

    # ======================= CHAPTER 5 =======================
    w.chapter(5, "IMPLEMENTATION AND TESTING")
    w.h1("5.1 Introduction")
    w.para("The design of Chapter 4 was implemented in Python 3 with PyTorch, NLTK, NumPy, Matplotlib and Flask. "
           "The implementation emphasises clarity, a fair comparison and reproducibility. All results in this "
           "report were produced by the scripts in the project repository.")
    w.h1("5.2 Project Structure")
    w.table(["File", "Purpose"],
            [["`data.py`", "Downloads Multi30k, tokenises, builds vocabularies, pads and batches"],
             ["`model.py`", "Encoder (Bi-LSTM), BahdanauAttention, Decoder, Seq2Seq with greedy and beam search"],
             ["`train.py`", "Teacher forcing, label-smoothed cross-entropy, Adam, scheduler, clipping, validation BLEU"],
             ["`evaluate.py`", "Test-set BLEU with beam search and sample translations"],
             ["`visualize.py`", "Translates one sentence and saves its attention heatmap"],
             ["`rule_based.py`", "IBM Model 1 dictionary and reordering rules; test BLEU"],
             ["`evaluation_report.py`", "BLEU parts, BLEU by length, confusion matrices, loss curves"],
             ["`plot_curves.py`", "Validation-BLEU curves of both models"],
             ["`app.py`, `web/index.html`", "Flask API and single-page demo"],
             ["`demo.ipynb`", "Notebook with heatmaps and test samples"],
             ["`VIVA_GUIDE.md`, deck", "Viva guide and 26-slide presentation"]],
            [3000, 6200], caption="Project Files", size=10)
    w.h1("5.3 Data Pipeline Implementation")
    w.para("The tokenizer is one regular expression that lowercases, keeps French elisions attached to the article, "
           "keeps hyphenated words together and splits punctuation:", keep_next=True)
    w.code(src("data.py", 19, 24))
    w.para("The `Vocab` class is built from the training split only and maps words that occur fewer than twice to "
           "`<unk>`. A `collate` function pads each batch and returns the source lengths needed to pack the "
           "encoder input.")
    w.h1("5.4 Model Implementation")
    w.para("The attention module is a direct transcription of Equations 4.1-4.3. Padding positions are masked "
           "with minus infinity before the softmax so that they receive exactly zero weight:", keep_next=True)
    w.code(src("model.py", 31, 46))
    w.para("In the decoder, the context vector from attention is concatenated with the word embedding to feed the "
           "LSTM cell, and the output layer sees state, context and embedding together. Setting "
           "`use_attention=False` swaps the attention call for the fixed mean context, which is how the baseline "
           "is produced from the same class.")
    w.h1("5.5 Training Implementation")
    w.para("`train.py` runs 15 epochs. After every epoch it computes validation loss, perplexity and greedy "
           "validation BLEU, steps the learning-rate scheduler, and saves the checkpoint whenever validation loss "
           "improves. Commands to reproduce all results:", keep_next=True)
    w.code("pip install -r requirements.txt\n"
           "python train.py                     # attention model  -> checkpoints/attention.pt\n"
           "python train.py --no-attention      # baseline         -> checkpoints/baseline.pt\n"
           "python evaluate.py --ckpt checkpoints/attention.pt\n"
           "python rule_based.py                # rule-based baseline\n"
           "python evaluation_report.py         # charts and metrics -> outputs/eval/\n"
           "python app.py                       # demo at http://127.0.0.1:5000", size=9)
    w.h1("5.6 Web Application Implementation")
    w.para("`app.py` loads the checkpoints once at start-up and runs a warm-up translation so that the first real "
           "request does not pay the GPU initialisation cost. Table 5.2 lists the API endpoints.",
           keep_next=True)
    w.table(["Method", "Endpoint", "Purpose"],
            [["GET", "/", "Serves the single-page frontend"],
             ["GET", "/api/health", "Device, model status, parameter counts, vocabulary sizes"],
             ["GET", "/api/example", "Random test sentence with its human reference"],
             ["POST", "/api/translate", "Translations from all three systems, latency and attention matrix"]],
            [1300, 2700, 5200], caption="API Endpoints")
    w.para("A request to `/api/translate` carries `{\"text\": \"...\", \"beam\": 5}`. The server validates the "
           "input, tokenises it, translates with the attention and no-attention models under a lock, runs the "
           "rule-based translator, and returns tokens, detokenised text, latency in milliseconds, vocabulary IDs "
           "and, for the attention model, the attention matrix (rows: generated words, columns: `<sos>`, "
           "source words, `<eos>`). The server also lists unknown words and warns when more than half of the "
           "input words are outside the model's vocabulary.")
    w.h1("5.7 Testing Methodology")
    w.h2("5.7.1 Model Testing")
    w.para("The models were checked after every epoch on the 1,014-sentence validation set (loss, perplexity, "
           "BLEU) and finally on the untouched 1,000-sentence test set. The same random seed (0) was used for both "
           "neural models. A `--limit-batches` option in `train.py` allows a quick smoke test of the whole "
           "training loop.")
    w.h2("5.7.2 API and Input-Validation Testing")
    w.para("Table 5.3 lists the input cases the server handles. The messages are returned by `app.py`; the project "
           "README records that the application was tested in a desktop browser and at phone width (375 px).",
           keep_next=True)
    w.table(["Test case", "Expected behaviour"],
            [["Empty text", "HTTP 400, \"Please type an English sentence.\""],
             ["Text without letters", "HTTP 400, \"Sentence has no English words to translate.\""],
             ["More than 300 characters or 60 words", "HTTP 400 with the measured length and the maximum"],
             ["Non-numeric `beam`", "HTTP 400, \"'beam' must be a whole number.\""],
             ["Beam outside 1-10", "Clamped to the range 1-10"],
             ["Body is not JSON, or `text` is not a string", "HTTP 400 with a hint about the expected format"],
             ["Body larger than 16 KB", "Rejected before parsing (HTTP 413)"],
             ["Mostly out-of-vocabulary (non-English) input", "Translation plus a warning and the unknown-word list"],
             ["Checkpoint file missing", "Model card shows the command to run (`python train.py`)"]],
            [3700, 5500], caption="Input Validation Cases", size=10)
    w.h2("5.7.3 Integration and Performance Testing")
    w.para("The browser page calls the API, which uses the same `translate()` function as the evaluation "
           "script, so a sentence typed in the demo gives the same translation as the evaluation. A "
           "warm-up pass removes start-up cost from latency measurements. On the project's GPU the attention "
           "model takes roughly 270 ms per sentence with beam 5, against about 34 ms for the no-attention "
           "baseline, because attention re-scores every source word at every step and the beam expands five "
           "hypotheses.")
    w.h1("5.8 Error Handling")
    w.bullets(["Descriptive JSON errors for all invalid input (Table 5.3).",
               "Start-up checks with a status string per model; a missing model never crashes the page.",
               "A catch-all handler that keeps HTTP error codes and logs unexpected exceptions.",
               "Graceful handling of rare words by mapping them to `<unk>` and listing them to the user."])
    w.h1("5.9 Screenshots")
    w.figure(os.path.join(REPO, "deck_work", "demo_hero.jpg"), 5.6, "Web Demo Home Page with Inference Console")
    w.figure(os.path.join(REPO, "deck_work", "demo_cards.png"), 6.0, "Side-by-Side Translations of the Three Systems")
    w.figure(os.path.join(REPO, "deck_work", "demo_align_raw.jpg"), 5.6, "Alignment View of the Attention Weights")
    w.h1("5.10 Implementation Outcome")
    w.para("All planned modules were implemented and verified: data pipeline, rule-based baseline, attention and "
           "no-attention models, training and evaluation scripts, heatmap visualisation, and the web "
           "application. Final deliverables are the three translators, the evaluation suite, the interactive demo, "
           "the demo notebook, a 26-slide deck and the viva guide.")
    w.h1("5.11 Summary")
    w.para("The implementation turned the design into a reproducible system in which every result can be regenerated "
           "from the repository with a handful of commands.")

    # ======================= CHAPTER 6 =======================
    w.chapter(6, "RESULTS AND DISCUSSION")
    w.h1("6.1 Introduction")
    w.para("This chapter evaluates the three systems on the 1,000-sentence Multi30k test 2016 Flickr set, decoded with "
           "beam width 5. Results come from `outputs/eval/metrics.json`, generated by `evaluation_report.py`. "
           "BLEU is NLTK corpus BLEU on lowercased, tokenised text.")
    w.h1("6.2 Model Performance Evaluation")
    w.h2("6.2.1 Comparative Performance Table")
    w.table(["Model", "Test BLEU", "Best val loss", "Parameters"],
            [["Rule-based dictionary", f"{R['bleu']:.2f}", "-", "5,764-word dictionary"],
             ["Seq2seq, no attention", f"{B['bleu']:.2f}", "2.579", "15.7 M"],
             ["Seq2seq + Bahdanau attention", f"{A['bleu']:.2f}", "2.208", "16.0 M"]],
            [3500, 1500, 1800, 2400], caption="Comparative Performance", align=["l", "c", "c", "c"], hl_rows=(2,))
    w.para("Attention adds **+16.1 BLEU** over the plain network for only 0.3 million extra parameters, and nearly "
           "triples the rule-based score. Both neural models beat the 22-28 BLEU target set in the proposal; the "
           "rule-based baseline falls below it, as expected of a word-by-word system. The comparison is fair: "
           "same network, data, settings and seed, with only attention removed.")
    w.h2("6.2.2 BLEU Breakdown by N-gram")
    def pr(d):
        return [f"{x:.1f}" for x in d["precisions"]]
    w.table(["Metric", "Rule-based", "No attention", "Attention"],
            [["Test BLEU", f"{R['bleu']:.2f}", f"{B['bleu']:.2f}", f"{A['bleu']:.2f}"],
             ["1-gram precision (%)", *[pr(d)[0] for d in (R, B, A)]],
             ["2-gram precision (%)", *[pr(d)[1] for d in (R, B, A)]],
             ["3-gram precision (%)", *[pr(d)[2] for d in (R, B, A)]],
             ["4-gram precision (%)", *[pr(d)[3] for d in (R, B, A)]],
             ["Brevity penalty", *[f"{d['brevity_penalty']:.3f}" for d in (R, B, A)]],
             ["Exact-match sentences (of 1,000)", *[str(d["exact_match"]) for d in (R, B, A)]],
             ["Median sentence BLEU", *[f"{d['median_sentence_bleu']:.1f}" for d in (R, B, A)]]],
            [3500, 1900, 1900, 1900], caption="BLEU Breakdown", align=["l", "c", "c", "c"])
    w.para("The 1-gram precisions are close (66-80%), so all systems pick mostly correct words. The gap grows with "
           "n: at 4-grams it is 6.8 -> 26.3 -> 43.4, which shows that attention gets word order and grammar "
           "right, not just vocabulary. The attention model reproduces the reference exactly for 176 sentences, "
           "against 100 without attention and 5 for the dictionary.")
    w.h2("6.2.3 Training Behaviour")
    w.figure(os.path.join(OUT, "bleu_curves.png"), 4.6, "Validation BLEU per Epoch: Attention versus Baseline")
    w.para("Attention is ahead at every epoch and learns faster: after epoch 1 validation BLEU is 26.2 against 13.9, "
           "and after epoch 15 it is 54.2 against 35.8. Figure 6.2 shows the loss curves. Attention reaches a best "
           "validation loss of 2.208 (perplexity about 9.1) against 2.579 (about 13.2) without it, meaning the "
           "model is uncertain between roughly 9 likely words per step instead of 13. Validation loss "
           "flattens around epoch 10; the best checkpoint is kept.", keep_next=True)
    w.figure(os.path.join(OUT, "eval", "loss_curves.png"), 6.1, "Training and Validation Loss Curves")

    w.h1("6.3 Sentence-Length Analysis: Measuring the Bottleneck")
    bl = M["by_length"]
    w.table(["Sentence length (words)", *bl["buckets"]],
            [["Sentences in test set", *[str(c) for c in bl["count"]]],
             ["Rule-based BLEU", *[f"{x:.1f}" for x in bl["rule"]]],
             ["No-attention BLEU", *[f"{x:.1f}" for x in bl["baseline"]]],
             ["Attention BLEU", *[f"{x:.1f}" for x in bl["attention"]]]],
            [2900, 1250, 1250, 1250, 1250, 1250], caption="BLEU by Source Sentence Length",
            align=["l", "c", "c", "c", "c", "c"])
    w.para("Without attention BLEU falls from 52.4 on the shortest sentences (8 words or fewer) to 21.4 on the "
           "longest (21+), a loss of 30.9 points. With attention it falls only from 58.8 to 46.3, a loss of 12.5. On "
           "sentences of 21+ words attention is more than twice as good. This is the fixed-vector bottleneck "
           "measured on real data: the decoder with attention can look back at every word, while the plain "
           "decoder must rely on one compressed vector.")

    w.h1("6.4 Error Analysis with Confusion Matrices")
    w.h2("6.4.1 Gender Agreement: un / une")
    ca = M["confusion"]
    def cm(d):
        return d["article"]
    w.table(["Reference \\ Predicted", "un", "une", "other"],
            [["un (rule-based)", *[str(v) for v in cm(ca["rule"])[0]]],
             ["une (rule-based)", *[str(v) for v in cm(ca["rule"])[1]]],
             ["un (no attention)", *[str(v) for v in cm(ca["baseline"])[0]]],
             ["une (no attention)", *[str(v) for v in cm(ca["baseline"])[1]]],
             ["un (attention)", *[str(v) for v in cm(ca["attention"])[0]]],
             ["une (attention)", *[str(v) for v in cm(ca["attention"])[1]]]],
            [3400, 1500, 1500, 1500], caption="Article Confusion Counts (n = 689)", align=["l", "c", "c", "c"])
    w.para("The rule-based system never writes \"une\" because its dictionary keeps only the most frequent French "
           "article, so all 219 feminine sentences are wrong and accuracy is 62.4%. The neural models learn gender "
           "from the whole-sentence context: 96.8% without attention and 98.0% with attention (210 of 219 \"une\" "
           "correct).", keep_next=True)
    w.figure(os.path.join(OUT, "eval", "confusion_article.png"), 6.1, "Article (un/une) Confusion Matrices")
    w.h2("6.4.2 Colour Words")
    w.para("Colour-word accuracy (n = 219 reference colours) is 96.8% for the rule-based system, 90.4% without "
           "attention and 94.5% with attention. The rule-based system always outputs the colour word, but "
           "ignores agreement (\"herbe vert\", \"clôture blanc\"). The neural models agree correctly; their "
           "errors are mainly //dropped// colours (the \"none\" column): 20 without attention and 9 with it, so "
           "attention halves the omissions.", keep_next=True)
    w.figure(os.path.join(OUT, "eval", "confusion_colour.png"), 6.1, "Colour-Word Confusion Matrices")

    w.h1("6.5 Qualitative Results")
    w.h2("6.5.1 Attention Heatmaps")
    w.para("\"A man in a red shirt is playing guitar.\" is translated as \"un homme en t-shirt rouge joue de la "
           "guitare.\" The heatmap shows the model handling the adjective-noun swap: \"t-shirt\" attends to "
           "\"shirt\" and \"rouge\" attends to \"red\", so the attention crosses the diagonal exactly where French "
           "reverses English order. Nobody told the model about alignments; it learned them from the translation "
           "loss alone. Some rows sit one word to the left of the source word they translate (for example "
           "\"un\" attends to `<sos>`): Bahdanau attention scores the source with the decoder state from //before// "
           "the current word is fed in.", keep_next=True)
    w.figure(os.path.join(OUT, "a_man_in_a_red_shirt_is_playing_guitar.png"), 4.4,
             "Attention Heatmap: \"a man in a red shirt is playing guitar.\"")
    w.figure(os.path.join(OUT, "two_young_girls_are_playing_in_the_white_snow.png"), 4.4,
             "Attention Heatmap: \"two young girls are playing in the white snow.\"")
    w.figure(os.path.join(OUT, "a_woman_is_cooking_food_in_a_small_kitchen.png"), 4.4,
             "Attention Heatmap: \"a woman is cooking food in a small kitchen.\"")
    w.h2("6.5.2 Sample Test Translations")
    w.table(["Source / Reference", "Rule-based", "No attention", "Attention"],
            [["People are fixing the roof of a house. / Des gens réparent le toit d'une maison.",
              "personnes sont répare la toit de un maison .",
              "des gens sont à l' intérieur d' une maison .",
              "des gens répare le toit d' une maison ."],
             ["A group of people standing in front of an igloo. / Un groupe de personnes debout devant un igloo.",
              "un groupe de personnes debout en devant de un igloo .",
              "un groupe de gens debout devant une banderole .",
              "un groupe de personnes debout devant un igloo ."],
             ["A man in a vest is sitting in a chair and holding magazines. / Un homme en gilet est assis dans "
              "une chaise et tient des magazines.",
              "un homme en un gilet est assis en un chaise et tenant magazines .",
              "un homme avec un gilet est assis dans une chaise et tient une chaise .",
              "un homme en gilet est assis dans une chaise et tient des magazines ."],
             ["Five people wearing winter jackets and helmets stand in the snow, with snowmobiles in the "
              "background.",
              "cinq personnes portant hiver vestes et casques debout en la neige , avec <unk> en la "
              "arrière-plan .",
              "cinq personnes portant des vestes et des vestes sont debout dans la neige , avec des vestes en "
              "arrière-plan .",
              "cinq personnes portant des vestes d' hiver et des casques sont debout dans la neige , avec des "
              "<unk> en arrière-plan ."],
             ["A Boston Terrier is running on lush green grass in front of a white fence. / Un terrier de Boston "
              "court sur l'herbe verdoyante devant une clôture blanche.",
              "un boston terrier est court sur luxuriante herbe vert en devant de un clôture blanc .",
              "un joueur de football court sur l' herbe verte devant une clôture blanche .",
              "un terrier de court court sur l' herbe verte devant une clôture blanche ."]],
            [2900, 2200, 2200, 2200], caption="Sample Test Translations", size=9, align=["l", "l", "l", "l"])
    w.para("The rule-based output keeps English order and fails gender (\"un maison\", \"un clôture blanc\") and "
           "phrases (\"est court\" for \"is running\"). The no-attention model is fluent but invents content on "
           "longer sentences (\"joueur de football\", a repeated \"vestes\"). The attention model keeps the "
           "content; its errors are rare words (\"Boston\", \"snowmobiles\" become `<unk>` or a wrong word), "
           "occasional verb agreement (\"répare\" for \"réparent\") and repeated words.")
    w.h1("6.6 Discussion of Findings")
    w.bullets(["**Attention is the largest single improvement:** +16.1 BLEU on an otherwise identical network, with a "
               "7-point to 43-point rise in 4-gram precision between the rule-based and attention systems.",
               "**It matters most on long sentences:** the BLEU lost from short to long sentences drops from 30.9 "
               "to 12.5.",
               "**It learns linguistics without labels:** the attention matrices show word reordering and "
               "gender-aware translation even though the model received no alignment labels.",
               "**Classical methods still have a role:** the rule-based system is the best of the three at always "
               "keeping a colour word (96.8%), but it fails everywhere that needs context.",
               "**Cost of attention:** inference is about eight times slower (270 ms against 34 ms) and the "
               "parameter count rises by 0.3 million."])
    w.h1("6.7 Limitations of Results")
    w.bullets(["**Unknown words:** a word-level vocabulary turns rare words into `<unk>`; subword units are the fix.",
               "**Narrow domain:** the data are short image captions, so the model fails on other kinds of text.",
               "**Metric:** BLEU is computed on lowercased text with NLTK and reads higher than sacreBLEU; no human "
               "evaluation was done, and BLEU penalises correct synonyms.",
               "**Exposure bias:** training on true previous words but decoding on own guesses can accumulate errors.",
               "**Single run:** results are for one training run with seed 0; no variance across seeds was measured."])
    w.h1("6.8 Summary")
    w.para("The attention model scores 56.76 BLEU, against 40.65 without attention and 19.17 for the rule-based "
           "system. The gains are largest on long sentences and on grammar-sensitive phenomena, and the heatmaps "
           "give direct visual evidence that the model learned meaningful word alignments.")

    # ======================= CHAPTER 7 =======================
    w.chapter(7, "CONCLUSION AND FUTURE ENHANCEMENT")
    w.h1("7.1 Introduction")
    w.para("This chapter summarises what the project achieved and how it can be extended.")
    w.h1("7.2 Conclusion")
    w.para("The project built a complete English-to-French translation system around Bahdanau attention. A "
           "Bi-LSTM encoder, additive attention and an LSTM decoder were trained on 29,000 Multi30k pairs and "
           "compared with a no-attention network and a rule-based dictionary in a controlled experiment. The "
           "attention model reached 56.76 test BLEU, 16.1 points above the same network without attention "
           "and about three times the rule-based score, with consistent gains at every sentence length, in "
           "gender agreement and in dropped colour words.")
    w.para("The attention weights were not only used but also shown: heatmaps and an interactive alignment view "
           "reveal that the model learned to reorder \"red shirt\" into \"t-shirt rouge\" with no alignment labels. "
           "A Flask web application packages the three systems, the visualisations and an inference console, "
           "and handles invalid input safely. The work shows that a small model, small data and a single laptop "
           "GPU are enough to demonstrate the central idea of modern translation systems end to end.")
    w.h1("7.3 Achievement of Objectives")
    w.table(["Objective / Proposal item", "Delivered", "Status"],
            [["Data: Multi30k EN-FR, about 29K training pairs", "29,000 / 1,014 / 1,000 pairs", "Delivered"],
             ["Tokenizer: spaCy", "Regex tokenizer that handles French elisions", "Changed"],
             ["Vocabulary: about 10K subword units", "Word level: 5,979 EN / 6,486 FR", "Changed"],
             ["Model: Bi-LSTM encoder + Bahdanau attention", "As planned; 16 M parameters", "Delivered"],
             ["Training: teacher forcing, Adam, clipping, LR schedule", "As planned, plus label smoothing", "Delivered"],
             ["Inference: beam search width 3-5", "Beam 5 with length normalisation", "Delivered"],
             ["BLEU target 22-28", "56.8 (attention) vs 40.7 (baseline)", "Exceeded"],
             ["Heatmaps: interactive notebook", "Notebook plus interactive web app", "Extended"],
             ["Evaluation: BLEU, heatmaps, manual review",
              "Plus loss curves, n-gram, length analysis and confusion matrices", "Extended"],
             ["Baselines: plain seq2seq and rule-based", "Both built and evaluated", "Delivered"],
             ["Compute: single GPU (Colab)", "Local RTX 4060 laptop GPU", "Changed"]],
            [3800, 3900, 1500], caption="Achievement of Objectives", size=10)
    w.h1("7.4 Future Enhancements")
    w.bullets(["**Subword tokenisation** (BPE or SentencePiece) to remove unknown words.",
               "**Larger and more varied data** such as WMT14 so the model leaves the image-caption domain.",
               "**Scheduled sampling** to reduce exposure bias.",
               "**Transformer comparison** to measure recurrent attention against self-attention in accuracy and speed.",
               "**Better evaluation:** report sacreBLEU and chrF next to NLTK BLEU, run multiple seeds, and add a "
               "human evaluation.",
               "**Faster inference:** batched beam search and model quantisation."])
    w.h1("7.5 Final Remarks")
    w.para("Attention changed how machines translate, and showing it working makes the idea concrete. "
           "The system built here is small, but it is complete: it learns, it translates, it measures itself "
           "honestly, and it lets anyone see where the network looks.")

    # ======================= CHAPTER 8 =======================
    w.chapter(8, "REFERENCES")
    refs = [
        "I. Sutskever, O. Vinyals, and Q. V. Le, \"Sequence to sequence learning with neural networks,\" in //Advances in "
        "Neural Information Processing Systems (NeurIPS)//, vol. 27, 2014.",
        "D. Bahdanau, K. Cho, and Y. Bengio, \"Neural machine translation by jointly learning to align and "
        "translate,\" in //Proc. International Conference on Learning Representations (ICLR)//, 2015.",
        "NLLB Team, \"Scaling neural machine translation to 200 languages,\" //Nature//, vol. 630, pp. 841-846, 2024 "
        "(preprint 2022).",
        "Bhadauria et al., \"Attention-based neural machine translation for multilingual communication,\" "
        "Springer TCCE, 2024.",
        "J. Pang et al., \"Salute the classic: Revisiting challenges of machine translation in the era of large "
        "language models,\" //Transactions of the Association for Computational Linguistics (TACL)//, 2025.",
        "A. Nourbakhsh, S. Lamsiyah, and C. Schommer, \"Attribution maps in encoder-decoder machine translation,\" "
        "in //Proc. Recent Advances in Natural Language Processing (RANLP)//, 2025.",
        "M.-T. Luong, H. Pham, and C. D. Manning, \"Effective approaches to attention-based neural machine "
        "translation,\" in //Proc. EMNLP//, 2015, pp. 1412-1421.",
        "A. Vaswani et al., \"Attention is all you need,\" in //Advances in Neural Information Processing Systems "
        "(NeurIPS)//, vol. 30, 2017.",
        "K. Cho et al., \"Learning phrase representations using RNN encoder-decoder for statistical machine "
        "translation,\" in //Proc. EMNLP//, 2014, pp. 1724-1734.",
        "S. Hochreiter and J. Schmidhuber, \"Long short-term memory,\" //Neural Computation//, vol. 9, no. 8, "
        "pp. 1735-1780, 1997.",
        "M. Schuster and K. K. Paliwal, \"Bidirectional recurrent neural networks,\" //IEEE Transactions on Signal "
        "Processing//, vol. 45, no. 11, pp. 2673-2681, 1997.",
        "P. F. Brown, S. A. Della Pietra, V. J. Della Pietra, and R. L. Mercer, \"The mathematics of statistical "
        "machine translation: Parameter estimation,\" //Computational Linguistics//, vol. 19, no. 2, pp. 263-311, 1993.",
        "D. Elliott, S. Frank, K. Sima'an, and L. Specia, \"Multi30K: Multilingual English-German image "
        "descriptions,\" in //Proc. 5th Workshop on Vision and Language//, 2016, pp. 70-74.",
        "K. Papineni, S. Roukos, T. Ward, and W.-J. Zhu, \"BLEU: a method for automatic evaluation of machine "
        "translation,\" in //Proc. ACL//, 2002, pp. 311-318.",
        "R. Sennrich, B. Haddow, and A. Birch, \"Neural machine translation of rare words with subword units,\" "
        "in //Proc. ACL//, 2016, pp. 1715-1725.",
        "D. P. Kingma and J. Ba, \"Adam: A method for stochastic optimization,\" in //Proc. ICLR//, 2015.",
        "C. Szegedy, V. Vanhoucke, S. Ioffe, J. Shlens, and Z. Wojna, \"Rethinking the Inception architecture for "
        "computer vision,\" in //Proc. IEEE CVPR//, 2016, pp. 2818-2826.",
        "A. Paszke et al., \"PyTorch: An imperative style, high-performance deep learning library,\" in //Advances in "
        "Neural Information Processing Systems (NeurIPS)//, vol. 32, 2019.",
    ]
    def key(r):
        a = r.split(",")[0].split(" and ")[0].replace(" et al.", "")
        return "NLLB" if a.startswith("NLLB") else a.split()[-1]
    from lib import add_runs
    for r in sorted(refs, key=key):
        para = w.fmt(w.p(), "j", left=LEFT + 400, first=-400, before=3, line=1.1)
        add_runs(para, r, 10.5)

    # ======================= APPENDIX A =======================
    w.chapter("APPENDIX A", "CODING")
    w.h3("A.1  model.py: Encoder, Bahdanau attention, Decoder and Seq2Seq")
    w.code(src("model.py", 1, 143), size=7.5)
    w.h3("A.2  rule_based.py: IBM Model 1 dictionary and translation rules")
    w.code(src("rule_based.py", 21, 59), size=7.5)
    w.h3("A.3  train.py: one training/validation epoch")
    w.code(src("train.py", 15, 33), size=7.5)
