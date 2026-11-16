// Builds the updated NMT-with-attention deck (same visual identity as the proposal deck).
const path = require("path");
const fs = require("fs");
const pptxgen = require("pptxgenjs");
const { applyTheme } = require(process.env.PPTX_SKILL + "/scripts/apply_theme.js");

const ROOT = path.resolve(__dirname, "..");
const OUT = path.join(ROOT, process.env.DECK_NAME || "NMT_Attention_Project.pptx");

const HEX = {
  text: "1A1425", white: "FFFFFF", dark: "1F1236", lav: "EDE7F5", coral: "FF6B4A",
  deep: "2D1B4E", muted: "6E6580", line: "CFC6E6", tint: "EFEAF7", soft: "8F84AC", paleText: "B9AED0",
};
const THEME = {
  name: "NMT Attention",
  headFontFace: "Cambria",
  bodyFontFace: "Calibri",
  colors: {
    dk1: HEX.text, lt1: HEX.white, dk2: HEX.dark, lt2: HEX.lav,
    accent1: HEX.coral, accent2: HEX.deep, accent3: HEX.muted, accent4: HEX.line, accent5: HEX.tint, accent6: HEX.soft,
    hlink: HEX.coral, folHlink: HEX.soft,
  },
};

const pres = new pptxgen();
pres.layout = "LAYOUT_WIDE"; // 13.333 x 7.5
pres.title = "Neural Machine Translation with Attention";
pres.author = "Sai Anirudh, Atharva Bhutada, Vansh Agrawal, Shashwat Sharma";
pres.theme = { headFontFace: THEME.headFontFace, bodyFontFace: THEME.bodyFontFace };
const C = pres.SchemeColor;
// scheme aliases
const S = { text: C.text1, white: C.background1, dark: C.text2, lav: C.background2, coral: C.accent1,
            deep: C.accent2, muted: C.accent3, line: C.accent4, tint: C.accent5, soft: C.accent6 };

// ---- text-fit log (checked afterwards with real font metrics) ----
const fitLog = [];
let slideNo = 0;
function T(slide, text, o) {
  const opts = Object.assign({ isTextBox: true, fontFace: o.head ? "Cambria" : "Calibri", valign: "top", margin: 0 }, o);
  delete opts.head;
  slide.addText(text, opts);
  const plain = Array.isArray(text) ? text.map(r => (r.text || "") + (r.options && r.options.breakLine ? "\n" : "")).join("") : text;
  fitLog.push({ slide: slideNo, text: plain, w: opts.w, h: opts.h, size: opts.fontSize, bold: !!opts.bold,
                font: opts.fontFace, spaceAfter: opts.paraSpaceAfter || 0, bulleted: Array.isArray(text) && text.some(r => r.options && r.options.bullet) });
}

// ---- layouts ----
pres.defineSlideMaster({
  title: "DARK",
  background: { color: HEX.dark },
  objects: [
    { text: { text: "NMT WITH ATTENTION", options: { x: 0.6, y: 6.95, w: 4, h: 0.3, fontFace: "Calibri", fontSize: 10, bold: true, color: HEX.soft, charSpacing: 3, margin: 0, isTextBox: true } } },
  ],
  slideNumber: { x: 12.2, y: 6.95, w: 0.6, h: 0.3, fontFace: "Calibri", fontSize: 10, color: HEX.soft, align: "right" },
});
pres.defineSlideMaster({
  title: "LIGHT",
  background: { color: HEX.lav },
  objects: [
    { text: { text: "NMT WITH ATTENTION", options: { x: 0.6, y: 6.95, w: 4, h: 0.3, fontFace: "Calibri", fontSize: 10, bold: true, color: HEX.muted, charSpacing: 3, margin: 0, isTextBox: true } } },
    { placeholder: { options: { name: "eyebrow", type: "body", x: 0.6, y: 0.42, w: 9, h: 0.3, fontFace: "Calibri", fontSize: 12, bold: true, color: HEX.coral, charSpacing: 3, margin: 0 }, text: "" } },
    { placeholder: { options: { name: "title", type: "title", x: 0.6, y: 0.72, w: 12.1, h: 0.8, fontFace: "Cambria", fontSize: 30, bold: true, color: HEX.text, margin: 0, valign: "top" }, text: "" } },
  ],
  slideNumber: { x: 12.2, y: 6.95, w: 0.6, h: 0.3, fontFace: "Calibri", fontSize: 10, color: HEX.muted, align: "right" },
});

function light(section, eyebrow, title, notes) {
  slideNo++;
  const s = pres.addSlide({ masterName: "LIGHT", sectionTitle: section });
  s.addText(eyebrow, { placeholder: "eyebrow" });
  s.addText(title, { placeholder: "title" });
  fitLog.push({ slide: slideNo, text: title, w: 12.1, h: 0.8, size: 30, bold: true, font: "Cambria" });
  if (notes) s.addNotes(notes);
  return s;
}
function dark(section, notes) {
  slideNo++;
  const s = pres.addSlide({ masterName: "DARK", sectionTitle: section });
  if (notes) s.addNotes(notes);
  return s;
}
function card(s, x, y, w, h, fill, name) {
  s.addShape(pres.shapes.ROUNDED_RECTANGLE, { x, y, w, h, rectRadius: 0.12, fill: { color: fill || S.white }, line: { color: S.line, width: 0.75 }, objectName: name });
}
function bullets(items, size, color) {
  return items.map((t, i) => ({ text: t, options: { bullet: { indent: 16 }, breakLine: i < items.length - 1, fontSize: size, color: color || S.text } }));
}
function pill(s, x, y, w, label, fill, color) {
  s.addShape(pres.shapes.ROUNDED_RECTANGLE, { x, y, w, h: 0.34, rectRadius: 0.17, fill: { color: fill }, line: { type: "none" } });
  T(s, label, { x, y, w, h: 0.34, fontSize: 12, bold: true, color, align: "center", valign: "middle" });
}

// =========================== 1. Title ===========================
pres.addSection({ title: "Introduction" });
{
  const s = dark("Introduction", "Introduce the team and the one-line idea: an encoder-decoder network that translates English to French and shows, word by word, where it is looking. Mention this is the final project, not the proposal: everything on these slides was built and measured.");
  T(s, "PROJECT REPORT  ·  NEURAL NETWORKS & DEEP LEARNING", { x: 0.8, y: 0.8, w: 9, h: 0.35, fontSize: 13, bold: true, color: S.coral, charSpacing: 3 });
  T(s, "Bridging Languages", { x: 0.8, y: 1.45, w: 11, h: 1.0, fontSize: 54, bold: true, color: S.white, head: true });
  T(s, "Neural Machine Translation with Attention", { x: 0.8, y: 2.45, w: 11, h: 0.6, fontSize: 28, color: S.line, head: true, italic: true });
  T(s, "A Bi-LSTM encoder–decoder with Bahdanau attention that translates English → French, and shows, word by word, which English words it looked at.",
    { x: 0.8, y: 3.3, w: 7.4, h: 0.95, fontSize: 16, color: S.paleText || S.line });
  // stat chips
  const stats = [["56.8", "test BLEU"], ["+16.1", "BLEU from attention"], ["16M", "parameters"]];
  stats.forEach(([v, l], i) => {
    const x = 0.8 + i * 2.35;
    s.addShape(pres.shapes.ROUNDED_RECTANGLE, { x, y: 4.55, w: 2.15, h: 1.05, rectRadius: 0.12, fill: { color: S.deep }, line: { type: "none" } });
    T(s, v, { x: x + 0.2, y: 4.65, w: 1.8, h: 0.55, fontSize: 28, bold: true, color: S.coral, head: true });
    T(s, l, { x: x + 0.2, y: 5.2, w: 1.85, h: 0.3, fontSize: 12, color: S.line });
  });
  T(s, [
    { text: "Sai Anirudh  ·  RA2311026010087", options: { breakLine: true } },
    { text: "Atharva Bhutada  ·  RA2311026010089", options: { breakLine: true } },
    { text: "Vansh Agrawal  ·  RA2311026010120", options: { breakLine: true } },
    { text: "Shashwat Sharma  ·  RA2311026010121" },
  ], { x: 8.9, y: 4.5, w: 3.8, h: 1.3, fontSize: 13, color: S.line, paraSpaceAfter: 3 });
}

// =========================== 2. Problem ===========================
{
  const s = light("Introduction", "THE PROBLEM", "Language is still a barrier, and translation is not word-for-word",
    "Two parts. Left: why translation matters (scale of the problem). Right: why it is hard for a machine. Use the three real examples: word order flips (red shirt becomes t-shirt rouge), French nouns carry gender that adjectives and articles must match, and one English phrase can become a single French word. These are exactly the cases our rule-based baseline gets wrong.");
  const stats = [["7,100+", "living languages spoken worldwide"], ["~5.5B", "people whose first language isn't English"]];
  stats.forEach(([v, l], i) => {
    card(s, 0.6, 1.8 + i * 1.6, 4.4, 1.35, S.white);
    T(s, v, { x: 0.9, y: 1.95 + i * 1.6, w: 3.9, h: 0.65, fontSize: 36, bold: true, color: S.coral, head: true });
    T(s, l, { x: 0.9, y: 2.62 + i * 1.6, w: 3.9, h: 0.4, fontSize: 14, color: S.muted });
  });
  T(s, "Where it matters: healthcare, education, travel and emergencies, trade and diplomacy.",
    { x: 0.6, y: 5.1, w: 4.4, h: 0.8, fontSize: 14, color: S.text });
  T(s, "Why it is hard for a machine", { x: 5.6, y: 1.8, w: 7, h: 0.4, fontSize: 18, bold: true, color: S.deep, head: true });
  const ex = [
    ["Word order changes", "a red shirt", "un t-shirt rouge"],
    ["Words carry gender", "a little girl", "une petite fille"],
    ["Phrases collapse", "is running", "court"],
  ];
  ex.forEach(([h, en, fr], i) => {
    const y = 2.35 + i * 1.45;
    card(s, 5.6, y, 7.1, 1.25, S.white);
    T(s, h, { x: 5.85, y: y + 0.15, w: 3, h: 0.35, fontSize: 15, bold: true, color: S.text });
    T(s, "EN", { x: 5.85, y: y + 0.65, w: 0.4, h: 0.35, fontSize: 11, bold: true, color: S.muted });
    T(s, en, { x: 6.25, y: y + 0.6, w: 2.6, h: 0.4, fontSize: 16, color: S.text });
    T(s, "→", { x: 8.85, y: y + 0.58, w: 0.5, h: 0.4, fontSize: 18, color: S.coral, align: "center" });
    T(s, "FR", { x: 9.45, y: y + 0.65, w: 0.4, h: 0.35, fontSize: 11, bold: true, color: S.muted });
    T(s, fr, { x: 9.85, y: y + 0.6, w: 2.7, h: 0.4, fontSize: 16, bold: true, color: S.deep });
  });
}

// =========================== 3. Old vs neural ===========================
{
  const s = light("Introduction", "WHY NOT JUST USE WHAT WE HAVE?", "Rules break on real sentences; neural models learn from data",
    "We built both sides of this slide. The rule-based system is a dictionary learned with IBM Model 1 plus hand-written reordering rules; it scores 19.2 BLEU. The neural model learns everything end-to-end from 29,000 sentence pairs and scores 56.8. Point at the real outputs at the bottom: the rule system gets the gender of 'fille' and 'clôture' wrong and translates 'is running' literally.");
  const cols = [
    { x: 0.6, head: "RULE-BASED / DICTIONARY", score: "19.2 BLEU", fill: S.white, items: [
      "Translates word by word, not sentence meaning",
      "Hand-written rules miss real-world cases",
      "No context: can't agree gender or tense",
      "Keeps English word order unless a rule fires",
    ], mark: "✕", markColor: S.muted },
    { x: 6.85, head: "NEURAL SEQ2SEQ + ATTENTION", score: "56.8 BLEU", fill: S.deep, items: [
      "Learns meaning end-to-end from sentence pairs",
      "Encoder reads the whole sentence in context",
      "Attention re-focuses on the right words each step",
      "Learns word order and agreement by itself",
    ], mark: "✓", markColor: S.coral },
  ];
  cols.forEach(c => {
    const darkCard = c.fill === S.deep;
    s.addShape(pres.shapes.ROUNDED_RECTANGLE, { x: c.x, y: 1.8, w: 5.9, h: 3.35, rectRadius: 0.12, fill: { color: c.fill }, line: { color: S.line, width: darkCard ? 0 : 0.75 } });
    T(s, c.head, { x: c.x + 0.3, y: 2.0, w: 3.6, h: 0.35, fontSize: 13, bold: true, charSpacing: 2, color: darkCard ? S.line : S.muted });
    T(s, c.score, { x: c.x + 3.9, y: 1.98, w: 1.75, h: 0.4, fontSize: 16, bold: true, color: S.coral, align: "right" });
    c.items.forEach((it, i) => {
      T(s, c.mark, { x: c.x + 0.3, y: 2.6 + i * 0.6, w: 0.35, h: 0.4, fontSize: 16, bold: true, color: c.markColor });
      T(s, it, { x: c.x + 0.75, y: 2.6 + i * 0.6, w: 4.9, h: 0.45, fontSize: 15, color: darkCard ? S.white : S.text });
    });
  });
  card(s, 0.6, 5.35, 12.15, 1.35, S.tint);
  T(s, "Real outputs  ·  “A Boston Terrier is running on lush green grass in front of a white fence.”", { x: 0.85, y: 5.47, w: 11.6, h: 0.32, fontSize: 12, bold: true, color: S.muted });
  T(s, [
    { text: "Rule-based:  ", options: { bold: true, color: S.muted } },
    { text: "un boston terrier est court sur luxuriante herbe vert en devant de un clôture blanc", options: { color: S.text, breakLine: true } },
    { text: "Attention:     ", options: { bold: true, color: S.coral } },
    { text: "un terrier de court court sur l'herbe verte devant une clôture blanche", options: { color: S.text } },
  ], { x: 0.85, y: 5.82, w: 11.6, h: 0.8, fontSize: 14, paraSpaceAfter: 3 });
}

// =========================== 4. Literature ===========================
{
  const s = light("Introduction", "LITERATURE SURVEY", "The research this project stands on",
    "The first two rows are the foundations we implemented directly: Sutskever et al. introduced the LSTM encoder-decoder, and Bahdanau et al. introduced the additive attention our model uses. The last four are recent work from the proposal showing attention-based alignment is still relevant, and that attention maps are a reasonably faithful explanation, which justifies our heatmaps.");
  const hdr = ["Year", "Authors", "Title", "Venue", "How we use it"].map(t => ({ text: t, options: { bold: true, color: HEX.white, fill: { color: HEX.deep } } }));
  const rows = [
    ["2014", "Sutskever, Vinyals & Le", "Sequence to Sequence Learning with Neural Networks", "NeurIPS", "LSTM encoder–decoder: our backbone and baseline"],
    ["2015", "Bahdanau, Cho & Bengio", "NMT by Jointly Learning to Align and Translate", "ICLR", "The additive attention we implement"],
    ["2022", "NLLB Team (Meta AI)", "No Language Left Behind", "Nature ('24)", "Attention-based MT scales to 200+ languages"],
    ["2024", "Bhadauria et al.", "Attention-based NMT for Multilingual Communication", "Springer TCCE", "Recent applied study of attention in NMT"],
    ["2025", "Pang et al.", "Salute the Classic: MT Challenges in the LLM Era", "TACL", "Alignment is still an open NMT challenge"],
    ["2025", "Nourbakhsh, Lamsiyah & Schommer", "Attribution Maps in Encoder–Decoder MT", "RANLP", "Attention ≈ faithful attribution: basis for our heatmaps"],
  ].map((r, i) => r.map((t, j) => ({ text: t, options: { color: HEX.text, bold: j === 0, fill: { color: i < 2 ? HEX.white : HEX.tint } } })));
  s.addTable([hdr, ...rows], { x: 0.6, y: 1.8, w: 12.15, colW: [0.75, 2.6, 4.0, 1.5, 3.3], fontFace: "Calibri", fontSize: 12,
    border: { type: "solid", pt: 0.75, color: HEX.line }, rowH: 0.62, valign: "middle", margin: [0.04, 0.1, 0.04, 0.1] });
  T(s, "White rows: methods we implemented directly.  Tinted rows: recent work from our proposal.", { x: 0.6, y: 6.3, w: 12, h: 0.3, fontSize: 11, color: S.muted, italic: true });
}

// =========================== 5. Objectives ===========================
{
  const s = light("Introduction", "PROJECT OBJECTIVE", "Translate English → French, and show where the model looks",
    "These are the three objectives from the proposal. All three were delivered. Learn: the encoder-decoder trained end-to-end on Multi30k. Attend: Bahdanau attention implemented from scratch in PyTorch, not a library layer. Reveal: the alignment matrix shown as heatmaps, in a notebook and in an interactive web app.");
  const obj = [
    ["01", "Learn", "an encoder–decoder end-to-end on 29,000 real English–French sentence pairs", "Trained · 15 epochs · RTX 4060"],
    ["02", "Attend", "implement Bahdanau-style additive attention over the encoder states", "Built from scratch in PyTorch"],
    ["03", "Reveal", "expose the attention matrix as an interpretable heatmap", "Notebook + interactive web app"],
  ];
  obj.forEach(([n, h, d, done], i) => {
    const x = 0.6 + i * 4.15;
    card(s, x, 1.85, 3.85, 4.4, S.white);
    T(s, n, { x: x + 0.35, y: 2.1, w: 1.5, h: 0.6, fontSize: 30, bold: true, color: S.coral, head: true });
    T(s, h, { x: x + 0.35, y: 2.85, w: 3.2, h: 0.55, fontSize: 24, bold: true, color: S.text, head: true });
    T(s, d, { x: x + 0.35, y: 3.5, w: 3.2, h: 1.4, fontSize: 15, color: S.muted });
    pill(s, x + 0.35, 5.45, 3.15, "✓  " + done, S.tint, S.deep);
  });
}

// =========================== 6. Dataset ===========================
pres.addSection({ title: "Data" });
{
  const s = light("Data", "THE DATASET", "Multi30k: English–French image captions",
    "Multi30k comes from the WMT multimodal translation task (Elliott et al. 2016). Each Flickr image has an English caption with a professional French translation. We use the official splits: 29,000 train, 1,014 validation and 1,000 test (Test 2016 Flickr). Sentences are short scene descriptions, about 13 words. The vocabulary is built from training data only, keeping words seen at least twice.");
  const big = [["29,000", "training pairs"], ["1,014", "validation pairs"], ["1,000", "test pairs"], ["~13", "words per sentence"]];
  big.forEach(([v, l], i) => {
    const x = 0.6 + i * 3.06;
    card(s, x, 1.8, 2.85, 1.45, S.white);
    T(s, v, { x: x + 0.25, y: 1.95, w: 2.4, h: 0.7, fontSize: 36, bold: true, color: S.coral, head: true });
    T(s, l, { x: x + 0.25, y: 2.7, w: 2.4, h: 0.35, fontSize: 14, color: S.muted });
  });
  card(s, 0.6, 3.5, 6.4, 3.15, S.white);
  T(s, "Example pair (test set)", { x: 0.9, y: 3.7, w: 5.8, h: 0.35, fontSize: 15, bold: true, color: S.deep });
  T(s, [
    { text: "EN  ", options: { bold: true, color: S.muted, fontSize: 12 } },
    { text: "A group of people standing in front of an igloo.", options: { color: S.text, breakLine: true } },
    { text: "FR  ", options: { bold: true, color: S.muted, fontSize: 12 } },
    { text: "Un groupe de personnes debout devant un igloo.", options: { color: S.deep, bold: true } },
  ], { x: 0.9, y: 4.2, w: 5.8, h: 1.0, fontSize: 16, paraSpaceAfter: 6 });
  T(s, "Source: Elliott et al., 2016 (WMT Multimodal MT). Same corpus as the Kaggle mirror in our proposal; downloaded automatically by data.py.",
    { x: 0.9, y: 5.45, w: 5.8, h: 0.9, fontSize: 12, color: S.muted });
  card(s, 7.25, 3.5, 5.5, 3.15, S.deep);
  T(s, "Vocabulary (from training data)", { x: 7.55, y: 3.7, w: 5, h: 0.35, fontSize: 15, bold: true, color: S.white });
  [["5,979", "English words"], ["6,486", "French words"]].forEach(([v, l], i) => {
    T(s, v, { x: 7.55 + i * 2.5, y: 4.2, w: 2.3, h: 0.7, fontSize: 34, bold: true, color: S.coral, head: true });
    T(s, l, { x: 7.55 + i * 2.5, y: 4.9, w: 2.3, h: 0.35, fontSize: 14, color: S.line });
  });
  T(s, "Words seen fewer than 2 times become <unk>. Counts include 4 special tokens: <pad>, <sos>, <eos>, <unk>.",
    { x: 7.55, y: 5.45, w: 4.95, h: 0.9, fontSize: 13, color: S.line });
}

// =========================== 7. Preprocessing ===========================
{
  const s = light("Data", "PREPROCESSING PIPELINE", "From raw text to padded batches of word IDs",
    "Walk through the five steps with the example sentence. Tokenization is a regular expression: it lowercases, splits off punctuation and keeps French elisions like j' together. Every sentence gets start and end tokens. Words become IDs using the vocabulary; rare words map to <unk>. Sentences in a batch are padded to the same length with <pad>, which is index 0 and is masked out later. Training sentences over 50 tokens are dropped.");
  const steps = [
    ["Tokenize", "lowercase, split punctuation, keep elisions", "j'aime → j' · aime"],
    ["Boundaries", "add start and end tokens", "<sos> a dog runs . <eos>"],
    ["Vocabulary", "word → ID, rare words → <unk>", "dog → 33"],
    ["Pad & batch", "equal length per batch, 128 per batch", "<pad> = 0, masked"],
    ["Filter", "drop training pairs over 50 tokens", "keeps batches efficient"],
  ];
  steps.forEach(([h, d, e], i) => {
    const x = 0.6 + i * 2.47;
    card(s, x, 2.0, 2.25, 3.6, S.white);
    s.addShape(pres.shapes.OVAL, { x: x + 0.25, y: 2.25, w: 0.6, h: 0.6, fill: { color: S.coral }, line: { type: "none" } });
    T(s, String(i + 1), { x: x + 0.25, y: 2.25, w: 0.6, h: 0.6, fontSize: 18, bold: true, color: S.white, align: "center", valign: "middle" });
    T(s, h, { x: x + 0.25, y: 3.05, w: 1.85, h: 0.4, fontSize: 17, bold: true, color: S.text, head: true });
    T(s, d, { x: x + 0.25, y: 3.5, w: 1.85, h: 0.95, fontSize: 13, color: S.muted });
    s.addShape(pres.shapes.ROUNDED_RECTANGLE, { x: x + 0.18, y: 4.65, w: 1.89, h: 0.7, rectRadius: 0.08, fill: { color: S.tint }, line: { type: "none" } });
    T(s, e, { x: x + 0.25, y: 4.68, w: 1.75, h: 0.64, fontSize: 11, color: S.deep, fontFace: "Courier New", valign: "middle" });
    if (i < steps.length - 1) T(s, "›", { x: x + 2.2, y: 3.4, w: 0.3, h: 0.5, fontSize: 24, bold: true, color: S.coral, align: "center" });
  });
  T(s, "Implemented in data.py  ·  vocabulary built from the training split only, so no test information leaks into training.",
    { x: 0.6, y: 6.0, w: 12, h: 0.35, fontSize: 12, color: S.muted, italic: true });
}

// =========================== 8. Background: encoder-decoder ===========================
pres.addSection({ title: "Model" });
{
  const s = light("Model", "BACKGROUND", "The encoder–decoder backbone, and its bottleneck",
    "A plain seq2seq model has two recurrent networks. The encoder reads the English sentence and its final state becomes a single context vector. The decoder generates French from that one vector. The bottleneck: a 3-word sentence and a 30-word sentence are squeezed into the same fixed size, so long sentences lose information. This is our no-attention baseline, and it scores 40.7 BLEU.");
  const words = ["I", "love", "Paris"];
  words.forEach((w, i) => {
    s.addShape(pres.shapes.ROUNDED_RECTANGLE, { x: 0.8, y: 2.0 + i * 0.85, w: 1.4, h: 0.6, rectRadius: 0.1, fill: { color: S.white }, line: { color: S.line, width: 0.75 } });
    T(s, w, { x: 0.8, y: 2.0 + i * 0.85, w: 1.4, h: 0.6, fontSize: 16, color: S.text, align: "center", valign: "middle" });
  });
  s.addShape(pres.shapes.ROUNDED_RECTANGLE, { x: 2.6, y: 2.0, w: 2.6, h: 2.3, rectRadius: 0.12, fill: { color: S.deep }, line: { type: "none" } });
  T(s, "ENCODER", { x: 2.6, y: 2.55, w: 2.6, h: 0.4, fontSize: 16, bold: true, color: S.white, align: "center" });
  T(s, "LSTM reads the whole sentence", { x: 2.8, y: 3.0, w: 2.2, h: 0.7, fontSize: 13, color: S.line, align: "center" });
  s.addShape(pres.shapes.OVAL, { x: 5.6, y: 2.55, w: 1.25, h: 1.25, fill: { color: S.coral }, line: { type: "none" } });
  T(s, "1 vector", { x: 5.6, y: 2.55, w: 1.25, h: 1.25, fontSize: 14, bold: true, color: S.white, align: "center", valign: "middle" });
  s.addShape(pres.shapes.ROUNDED_RECTANGLE, { x: 7.25, y: 2.0, w: 2.6, h: 2.3, rectRadius: 0.12, fill: { color: S.deep }, line: { type: "none" } });
  T(s, "DECODER", { x: 7.25, y: 2.55, w: 2.6, h: 0.4, fontSize: 16, bold: true, color: S.white, align: "center" });
  T(s, "LSTM writes French one word at a time", { x: 7.45, y: 3.0, w: 2.2, h: 0.7, fontSize: 13, color: S.line, align: "center" });
  ["J'", "aime", "Paris"].forEach((w, i) => {
    s.addShape(pres.shapes.ROUNDED_RECTANGLE, { x: 10.25, y: 2.0 + i * 0.85, w: 1.4, h: 0.6, rectRadius: 0.1, fill: { color: S.white }, line: { color: S.line, width: 0.75 } });
    T(s, w, { x: 10.25, y: 2.0 + i * 0.85, w: 1.4, h: 0.6, fontSize: 16, bold: true, color: S.deep, align: "center", valign: "middle" });
  });
  [[2.25, 2.55], [5.2, 5.6], [6.85, 7.25], [9.85, 10.25]].forEach(([a, b]) =>
    s.addShape(pres.shapes.LINE, { x: a, y: 3.17, w: b - a, h: 0, line: { color: S.soft, width: 1.5, endArrowType: "triangle" } }));
  card(s, 0.6, 4.75, 12.15, 1.75, S.white);
  T(s, "The bottleneck", { x: 0.9, y: 4.95, w: 4, h: 0.4, fontSize: 18, bold: true, color: S.coral, head: true });
  T(s, "Every source sentence (3 words or 30) is squeezed into one fixed-size vector before the decoder sees it, so long sentences lose information. This plain model is our baseline: 40.7 test BLEU.",
    { x: 0.9, y: 5.4, w: 11.5, h: 0.95, fontSize: 15, color: S.text });
}

// =========================== 9. Attention mechanism ===========================
{
  const s = light("Model", "THE FIX: BAHDANAU ATTENTION", "At every step, the decoder looks back at all English words",
    "Explain the three equations left to right. Score: a tiny feed-forward network compares the decoder's previous state with each encoder state. Softmax: scores become weights between 0 and 1 that sum to 1; padding is masked out. Context: the weighted average of the encoder states, a fresh summary for every French word. The bars on the right are real weights from our trained model when it writes 'rose': 99 percent on 'pink'. No alignment labels are used; it learns this from the translation loss alone.");
  const eq = [
    ["1  Score", "eᵢⱼ = vᵀ tanh(W·sᵢ₋₁ + U·hⱼ)", "how relevant is English word j for the next French word?"],
    ["2  Softmax", "αᵢⱼ = exp(eᵢⱼ) / Σₖ exp(eᵢₖ)", "weights in [0, 1] that sum to 1; padding masked to 0"],
    ["3  Context", "cᵢ = Σⱼ αᵢⱼ · hⱼ", "weighted mix of encoder states, recomputed every step"],
  ];
  eq.forEach(([h, f, d], i) => {
    const y = 1.8 + i * 1.5;
    card(s, 0.6, y, 6.9, 1.3, S.white);
    T(s, h, { x: 0.85, y: y + 0.15, w: 1.7, h: 0.4, fontSize: 15, bold: true, color: S.coral });
    T(s, f, { x: 2.55, y: y + 0.12, w: 4.8, h: 0.45, fontSize: 18, bold: true, color: S.deep, fontFace: "Cambria Math" });
    T(s, d, { x: 2.55, y: y + 0.65, w: 4.8, h: 0.5, fontSize: 13, color: S.muted });
  });
  T(s, "sᵢ₋₁ = previous decoder state  ·  hⱼ = encoder state of word j  ·  W, U, v learned (attention size 256)",
    { x: 0.6, y: 6.35, w: 6.9, h: 0.35, fontSize: 11, color: S.muted, italic: true });
  card(s, 7.85, 1.8, 4.9, 4.85, S.deep);
  T(s, "Real weights when writing “rose”", { x: 8.15, y: 2.0, w: 4.4, h: 0.35, fontSize: 15, bold: true, color: S.white });
  T(s, "a little girl in a pink dress …", { x: 8.15, y: 2.4, w: 4.4, h: 0.3, fontSize: 12, color: S.line, italic: true });
  const w = [["girl", 0.0], ["in", 0.0], ["a", 0.0], ["pink", 0.99], ["dress", 0.01], ["is", 0.0]];
  w.forEach(([word, v], i) => {
    const y = 2.95 + i * 0.52;
    T(s, word, { x: 8.15, y, w: 0.9, h: 0.38, fontSize: 14, color: v > 0.5 ? S.white : S.line, bold: v > 0.5, valign: "middle" });
    s.addShape(pres.shapes.RECTANGLE, { x: 9.1, y: y + 0.08, w: 2.6, h: 0.22, fill: { color: S.dark }, line: { type: "none" } });
    if (v > 0.005) s.addShape(pres.shapes.RECTANGLE, { x: 9.1, y: y + 0.08, w: Math.max(0.05, 2.6 * v), h: 0.22, fill: { color: S.coral }, line: { type: "none" } });
    T(s, Math.round(v * 100) + "%", { x: 11.8, y, w: 0.8, h: 0.38, fontSize: 13, bold: v > 0.5, color: v > 0.5 ? S.coral : S.line, valign: "middle", align: "right" });
  });
  T(s, "No alignment labels: the model learns where to look from the translation loss alone.",
    { x: 8.15, y: 6.05, w: 4.4, h: 0.5, fontSize: 12, color: S.line });
}

// =========================== 10. Architecture ===========================
{
  const s = light("Model", "SYSTEM ARCHITECTURE", "The full model, with real layer sizes",
    "Follow the pipeline left to right with the dimensions. Embedding: each word ID becomes a 256-number vector. Encoder: a bidirectional LSTM, 256 units each way, so every word gets a 512-dimensional state that knows both sides. The final states are projected with Linear plus tanh to start the decoder. Attention scores every encoder state at each step. The decoder LSTM cell takes the previous French word embedding plus the 512-dimensional context, 768 in total, and has 512 units. The output layer looks at hidden state, context and embedding together and produces a score for each of the 6,486 French words. About 16 million parameters; the output layer alone is 8.3 million.");
  const blocks = [
    ["Input", "English sentence", "word IDs"],
    ["Embed", "256-d vectors", "dropout 0.3"],
    ["Encode", "Bi-LSTM", "2 × 256 → hⱼ ∈ ℝ⁵¹²"],
    ["Attend", "additive, dim 256", "αᵢ over all hⱼ"],
    ["Decode", "LSTMCell", "768 → 512"],
    ["Output", "Linear 1280 → 6,486", "softmax → word"],
  ];
  blocks.forEach(([h, a, b], i) => {
    const x = 0.6 + i * 2.05, accent = i === 3;
    s.addShape(pres.shapes.ROUNDED_RECTANGLE, { x, y: 1.85, w: 1.8, h: 1.9, rectRadius: 0.12, fill: { color: accent ? S.coral : (i === 0 || i === 5 ? S.white : S.deep) }, line: { color: S.line, width: i === 0 || i === 5 ? 0.75 : 0 } });
    const onDark = !(i === 0 || i === 5);
    T(s, h, { x: x + 0.15, y: 2.0, w: 1.5, h: 0.45, fontSize: 18, bold: true, color: onDark ? S.white : S.text, head: true, align: "center" });
    T(s, a, { x: x + 0.12, y: 2.55, w: 1.56, h: 0.55, fontSize: 13, color: onDark ? S.white : S.text, align: "center" });
    T(s, b, { x: x + 0.12, y: 3.1, w: 1.56, h: 0.55, fontSize: 11, color: onDark ? S.line : S.muted, align: "center" });
    if (i < blocks.length - 1) s.addShape(pres.shapes.LINE, { x: x + 1.82, y: 2.8, w: 0.21, h: 0, line: { color: S.soft, width: 1.5, endArrowType: "triangle" } });
  });
  const parts = [
    ["Bidirectional encoder", "Reads left→right and right→left, so each word's vector knows the words on both sides. Final states → Linear + tanh → decoder's starting state."],
    ["Attention every step", "Uses the decoder's previous state to score all encoder states; U·hⱼ is computed once per sentence and reused."],
    ["Deep output layer", "Next-word scores come from [decoder state, context, word embedding] together, not the hidden state alone."],
  ];
  parts.forEach(([h, d], i) => {
    const x = 0.6 + i * 4.1;
    card(s, x, 4.1, 3.9, 2.0, S.white);
    T(s, h, { x: x + 0.25, y: 4.25, w: 3.4, h: 0.4, fontSize: 16, bold: true, color: S.deep });
    T(s, d, { x: x + 0.25, y: 4.7, w: 3.4, h: 1.3, fontSize: 13, color: S.text });
  });
  T(s, "15,965,782 parameters  ·  PyTorch  ·  model.py  ·  baseline = same network with one fixed context vector (mean of hⱼ)",
    { x: 0.6, y: 6.35, w: 12.1, h: 0.35, fontSize: 12, color: S.muted, italic: true });
}

// =========================== 10b. Architecture flowchart ===========================
{
  const s = light("Model", "ARCHITECTURE FLOWCHART", "How one French word is produced",
    "Read the flowchart in three columns. Left, the encoder runs once per sentence: the English words are embedded into 256-number vectors and read by a bidirectional LSTM, giving one 512-number state h for every English word. Middle, attention runs at every decoding step: it scores every h against the decoder's previous state, softmaxes the scores into weights, and takes the weighted sum as the context vector c. Right, the decoder takes the previous French word plus c, updates its LSTM state, and the output layer picks a word from 6,486. If the word is not <eos>, it is fed back in as the next input; if it is, the sentence is finished. Beam search keeps the 5 best partial sentences through this loop.");
  const box = (shape, x, y, w, h, fill, txt, txtColor, lineC) => {
    s.addShape(shape, { x, y, w, h, fill: { color: fill }, line: lineC ? { color: lineC, width: 1 } : { type: "none" } });
    T(s, txt, { x: x + 0.08, y, w: w - 0.16, h, fontSize: 12, color: txtColor, align: "center", valign: "middle" });
  };
  // line segment; arrow at the (x2,y2) end when arrow=true
  const seg = (x1, y1, x2, y2, arrow) => {
    const o = { x: Math.min(x1, x2), y: Math.min(y1, y2), w: Math.abs(x2 - x1), h: Math.abs(y2 - y1),
                line: { color: S.muted, width: 1.5 } };
    if (arrow) o.line[(x2 < x1 || y2 < y1) ? "beginArrowType" : "endArrowType"] = "triangle";
    s.addShape(pres.shapes.LINE, o);
  };
  const lbl = (txt, x, y, w) => T(s, txt, { x, y, w: w || 0.8, h: 0.25, fontSize: 10, italic: true, color: S.coral, bold: true });
  const P = pres.shapes;
  // column headers
  T(s, "ENCODER · once per sentence", { x: 0.6, y: 1.55, w: 3.0, h: 0.25, fontSize: 10, bold: true, color: S.muted, charSpacing: 2, align: "center" });
  T(s, "DECODER · one word per step", { x: 9.2, y: 1.55, w: 3.5, h: 0.25, fontSize: 10, bold: true, color: S.muted, charSpacing: 2, align: "center" });
  // encoder
  box(P.FLOWCHART_TERMINATOR, 0.6, 1.9, 3.0, 0.6, S.dark, "English sentence\n“a man in a red shirt”", S.white);
  box(P.FLOWCHART_PROCESS, 0.6, 2.85, 3.0, 0.6, S.deep, "Embedding  5,979 → 256", S.white);
  box(P.FLOWCHART_PROCESS, 0.6, 3.8, 3.0, 0.75, S.deep, "Bi-LSTM encoder\n→ 256  +  ← 256", S.white);
  box(P.FLOWCHART_DATA, 0.6, 4.9, 3.0, 0.65, S.white, "Encoder states h₁ … hₙ\n512 each", S.text, S.line);
  seg(2.1, 2.5, 2.1, 2.85, true); seg(2.1, 3.45, 2.1, 3.8, true); seg(2.1, 4.55, 2.1, 4.9, true);
  T(s, "Final states → Linear + tanh → s₀ (decoder start)", { x: 0.6, y: 5.75, w: 3.0, h: 0.5, fontSize: 10, italic: true, color: S.muted, align: "center" });
  // attention group
  s.addShape(P.ROUNDED_RECTANGLE, { x: 4.35, y: 1.55, w: 4.1, h: 3.6, rectRadius: 0.12, fill: { color: S.tint }, line: { color: S.coral, width: 1, dashType: "dash" } });
  T(s, "ATTENTION · every step", { x: 4.35, y: 1.65, w: 4.1, h: 0.25, fontSize: 10, bold: true, color: S.coral, charSpacing: 2, align: "center" });
  box(P.FLOWCHART_PROCESS, 4.6, 2.05, 3.6, 0.75, S.coral, "1. Score each English word\neᵢⱼ = vᵀ tanh(W sᵢ₋₁ + U hⱼ)", S.white);
  box(P.FLOWCHART_PROCESS, 4.6, 3.1, 3.6, 0.65, S.coral, "2. Softmax → weights αᵢⱼ\n(padding masked, sum = 1)", S.white);
  box(P.FLOWCHART_PROCESS, 4.6, 4.05, 3.6, 0.75, S.coral, "3. Context vector\ncᵢ = Σ αᵢⱼ hⱼ   (512)", S.white);
  seg(6.4, 2.8, 6.4, 3.1, true); seg(6.4, 3.75, 6.4, 4.05, true);
  // h -> score
  seg(3.6, 5.22, 4.1, 5.22); seg(4.1, 5.22, 4.1, 2.42); seg(4.1, 2.42, 4.6, 2.42, true); lbl("hⱼ", 3.72, 4.95, 0.4);
  // decoder
  box(P.FLOWCHART_DATA, 9.2, 1.9, 3.5, 0.6, S.white, "Previous word yᵢ₋₁\n(<sos> at the start)", S.text, S.line);
  box(P.FLOWCHART_PROCESS, 9.2, 2.85, 3.5, 0.55, S.deep, "Embedding  6,486 → 256", S.white);
  box(P.FLOWCHART_PROCESS, 9.2, 3.7, 3.5, 0.75, S.deep, "LSTMCell → new state sᵢ\n[ embedding ; cᵢ ]  768 → 512", S.white);
  box(P.FLOWCHART_PROCESS, 9.2, 4.75, 3.5, 0.6, S.deep, "Output layer 1280 → 6,486\nsoftmax → next word", S.white);
  box(P.FLOWCHART_DECISION, 9.75, 5.65, 2.4, 0.85, S.white, "word = <eos>?", S.text, S.coral);
  seg(10.95, 2.5, 10.95, 2.85, true); seg(10.95, 3.4, 10.95, 3.7, true); seg(10.95, 4.45, 10.95, 4.75, true); seg(10.95, 5.35, 10.95, 5.65, true);
  // context -> decoder
  seg(8.2, 4.42, 8.75, 4.42); seg(8.75, 4.42, 8.75, 4.2); seg(8.75, 4.2, 9.2, 4.2, true); lbl("cᵢ", 8.8, 4.25, 0.4);
  // decoder state -> score
  seg(9.2, 3.9, 8.55, 3.9); seg(8.55, 3.9, 8.55, 2.42); seg(8.55, 2.42, 8.2, 2.42, true); lbl("sᵢ₋₁", 8.6, 3.0, 0.55);
  // no -> loop back
  seg(12.15, 6.075, 12.95, 6.075); seg(12.95, 6.075, 12.95, 2.2); seg(12.95, 2.2, 12.7, 2.2, true); lbl("no: feed word back", 11.45, 6.5, 1.6);
  // yes -> output
  box(P.FLOWCHART_TERMINATOR, 4.9, 5.75, 3.0, 0.65, S.dark, "French sentence\n“un homme en t-shirt rouge”", S.white);
  seg(9.75, 6.075, 7.9, 6.075, true); lbl("yes", 8.6, 5.8, 0.5);
  T(s, "Beam search keeps the 5 best partial sentences through this loop.", { x: 4.6, y: 6.5, w: 4.4, h: 0.3, fontSize: 10, italic: true, color: S.muted, align: "center" });
}

// =========================== 11. Training ===========================
pres.addSection({ title: "Training" });
{
  const s = light("Training", "TRAINING", "How the model learns",
    "Left: the training settings, each with a one-line reason. Teacher forcing means the decoder sees the correct previous French word during training; the trade-off is exposure bias at test time. Gradient clipping prevents exploding gradients in the LSTM. Label smoothing stops over-confidence. Right: validation BLEU after every epoch for both models, from our training logs. Attention is ahead at every epoch and finishes about 18 points higher. Both trained with identical settings, so the gap is due to attention.");
  const rows = [
    ["Loss", "Cross-entropy per word, padding ignored"],
    ["Label smoothing", "0.1, avoids over-confidence"],
    ["Optimizer", "Adam, learning rate 1e-3"],
    ["Gradient clipping", "norm 1.0, prevents exploding gradients"],
    ["Teacher forcing", "1.0, feed the true previous word"],
    ["Batch / epochs", "128 / 15, keep best validation loss"],
    ["Hardware", "NVIDIA RTX 4060 laptop GPU"],
  ].map(([k, v], i) => [
    { text: k, options: { bold: true, color: HEX.deep, fill: { color: i % 2 ? HEX.tint : HEX.white } } },
    { text: v, options: { color: HEX.text, fill: { color: i % 2 ? HEX.tint : HEX.white } } },
  ]);
  s.addTable(rows, { x: 0.6, y: 1.85, w: 5.6, colW: [1.9, 3.7], fontFace: "Calibri", fontSize: 13, rowH: 0.58,
    border: { type: "solid", pt: 0.75, color: HEX.line }, valign: "middle", margin: [0.04, 0.12, 0.04, 0.12] });
  const ep = Array.from({ length: 15 }, (_, i) => String(i + 1));
  s.addChart(pres.charts.LINE, [
    { name: "With attention", labels: ep, values: [26.17, 38.25, 43.91, 46.46, 48.24, 49.82, 50.33, 51.33, 52.30, 53.39, 53.58, 53.29, 53.86, 53.74, 54.16] },
    { name: "No attention", labels: ep, values: [13.89, 22.26, 26.06, 28.52, 30.25, 31.55, 32.33, 32.63, 33.91, 34.61, 34.65, 35.06, 35.39, 36.09, 35.81] },
  ], {
    x: 6.6, y: 1.75, w: 6.15, h: 4.6,
    chartColors: [HEX.coral, HEX.soft], lineSize: 2.5, lineDataSymbol: "circle", lineDataSymbolSize: 5,
    showTitle: true, title: "Validation BLEU per epoch", titleFontFace: "+mn-lt", titleFontSize: 14, titleColor: HEX.text,
    showLegend: true, legendPos: "b", legendFontFace: "+mn-lt", legendFontSize: 12, legendColor: HEX.text,
    catAxisTitle: "epoch", showCatAxisTitle: true, catAxisTitleFontSize: 11, catAxisTitleColor: HEX.muted,
    catAxisLabelColor: HEX.muted, valAxisLabelColor: HEX.muted, catAxisLabelFontFace: "+mn-lt", valAxisLabelFontFace: "+mn-lt",
    catAxisLabelFontSize: 11, valAxisLabelFontSize: 11, valAxisMinVal: 0, valAxisMaxVal: 60, valAxisMajorUnit: 10,
    valGridLine: { color: HEX.line, size: 0.5 }, catGridLine: { style: "none" },
    plotArea: { fill: { color: HEX.white } },
  });
  T(s, "Teacher forcing speeds up training; the trade-off is exposure bias at test time.", { x: 0.6, y: 6.05, w: 5.6, h: 0.5, fontSize: 12, color: S.muted, italic: true });
}

// =========================== 12. Inference ===========================
{
  const s = light("Training", "INFERENCE", "Beam search: keep the 5 best sentences, not just the best word",
    "At test time there is no teacher. Greedy decoding picks the single most likely word at every step and can get stuck with an early mistake. Beam search keeps the 5 best partial translations, expands each one, and keeps the best 5 again, until they end with <eos> or reach 60 words. Because every extra word adds a negative log-probability, plain scores prefer short sentences, so we divide by length to the power 0.7. The web demo lets you change the beam width.");
  const cols = [
    { h: "Greedy (beam = 1)", fill: S.white, items: ["Pick the single most likely word each step", "Fast, but one early mistake is permanent", "Can miss a better sentence overall"] },
    { h: "Beam search (beam = 5)", fill: S.deep, items: ["Keep the 5 best partial sentences each step", "Expand each, keep the top 5 again", "Stop at <eos> or 60 words, pick the best"] },
  ];
  cols.forEach((c, i) => {
    const x = 0.6 + i * 4.2, d = c.fill === S.deep;
    s.addShape(pres.shapes.ROUNDED_RECTANGLE, { x, y: 1.85, w: 3.95, h: 3.0, rectRadius: 0.12, fill: { color: c.fill }, line: { color: S.line, width: d ? 0 : 0.75 } });
    T(s, c.h, { x: x + 0.3, y: 2.05, w: 3.4, h: 0.45, fontSize: 18, bold: true, color: d ? S.coral : S.text, head: true });
    T(s, bullets(c.items, 14, d ? S.white : S.text), { x: x + 0.3, y: 2.65, w: 3.4, h: 2.0, paraSpaceAfter: 8 });
  });
  card(s, 9.0, 1.85, 3.75, 3.0, S.white);
  T(s, "Length normalization", { x: 9.3, y: 2.05, w: 3.2, h: 0.45, fontSize: 18, bold: true, color: S.text, head: true });
  T(s, "score = log P(y) / |y|⁰·⁷", { x: 9.3, y: 2.65, w: 3.2, h: 0.5, fontSize: 18, bold: true, color: S.deep, fontFace: "Cambria Math" });
  T(s, "Each extra word lowers the total log-probability, so without this the search prefers sentences that are too short.",
    { x: 9.3, y: 3.3, w: 3.2, h: 1.4, fontSize: 13, color: S.muted });
  card(s, 0.6, 5.15, 12.15, 1.45, S.tint);
  T(s, "Example: beam search in action", { x: 0.9, y: 5.3, w: 6, h: 0.35, fontSize: 13, bold: true, color: S.muted });
  T(s, [
    { text: "two dogs are playing with a red ball in the snow.  →  ", options: { color: S.text } },
    { text: "deux chiens jouent avec une balle rouge dans la neige.", options: { color: S.deep, bold: true } },
  ], { x: 0.9, y: 5.75, w: 11.6, h: 0.6, fontSize: 16 });
}

// =========================== 13. Results ===========================
pres.addSection({ title: "Results" });
{
  const s = light("Results", "QUANTITATIVE RESULTS", "Attention adds +16.1 BLEU for only 0.3M extra parameters",
    "Test BLEU on 1,000 held-out sentences with beam size 5. Rule-based 19.2, plain seq2seq 40.7, with attention 56.8. Validation perplexity drops from 13.2 to 9.1. The comparison is controlled: same network, data, settings and seed; only attention is removed. Be upfront about the caveat: BLEU here is computed on lowercased, tokenized text with NLTK, which reads higher than the detokenized sacreBLEU used in papers, and Multi30k is an easy dataset. The relative gains are the real result.");
  s.addChart(pres.charts.BAR, [{ name: "Test BLEU", labels: ["Rule-based dictionary", "Seq2seq, no attention", "Seq2seq + attention"], values: [19.17, 40.65, 56.76] }], {
    x: 0.6, y: 1.75, w: 7.2, h: 4.9, barDir: "col", barGapWidthPct: 60,
    chartColors: [HEX.soft, HEX.deep, HEX.coral], varyColors: true,
    showValue: true, dataLabelPosition: "outEnd", dataLabelFontSize: 16, dataLabelFontBold: true, dataLabelColor: HEX.text, dataLabelFontFace: "+mn-lt",
    showTitle: true, title: "Test BLEU (Multi30k Test 2016, beam 5)", titleFontFace: "+mn-lt", titleFontSize: 14, titleColor: HEX.text,
    showLegend: false, catAxisLabelColor: HEX.text, valAxisLabelColor: HEX.muted, catAxisLabelFontFace: "+mn-lt", valAxisLabelFontFace: "+mn-lt",
    catAxisLabelFontSize: 12, valAxisLabelFontSize: 11, valAxisMinVal: 0, valAxisMaxVal: 70, valAxisMajorUnit: 10,
    valGridLine: { color: HEX.line, size: 0.5 }, catGridLine: { style: "none" }, plotArea: { fill: { color: HEX.white } },
  });
  const st = [["+16.1", "BLEU from adding attention"], ["13.2 → 9.1", "validation perplexity"], ["~3×", "the rule-based score"]];
  st.forEach(([v, l], i) => {
    card(s, 8.2, 1.8 + i * 1.3, 4.55, 1.12, i === 0 ? S.deep : S.white);
    T(s, v, { x: 8.45, y: 1.88 + i * 1.3, w: 4.1, h: 0.55, fontSize: 28, bold: true, color: S.coral, head: true });
    T(s, l, { x: 8.45, y: 2.45 + i * 1.3, w: 4.1, h: 0.35, fontSize: 13, color: i === 0 ? S.line : S.muted });
  });
  T(s, "Fair test: same network, data, settings and seed; only attention removed (15.7M vs 16.0M parameters). BLEU here is NLTK on lowercased tokens, which reads higher than sacreBLEU; the relative gains are the real result.",
    { x: 8.2, y: 5.75, w: 4.55, h: 1.0, fontSize: 11, color: S.muted, italic: true });
}

// =========================== Evaluation metrics (from evaluation_report.py) ===========================
const M = JSON.parse(fs.readFileSync(path.join(ROOT, "outputs", "eval", "metrics.json"), "utf8"));
const chartBase = () => ({
  catAxisLabelColor: HEX.muted, valAxisLabelColor: HEX.muted, catAxisLabelFontFace: "+mn-lt", valAxisLabelFontFace: "+mn-lt",
  catAxisLabelFontSize: 11, valAxisLabelFontSize: 11, titleFontFace: "+mn-lt", titleFontSize: 14, titleColor: HEX.text, showTitle: true,
  legendFontFace: "+mn-lt", legendFontSize: 12, legendColor: HEX.text, legendPos: "b",
  valGridLine: { color: HEX.line, size: 0.5 }, catGridLine: { style: "none" }, plotArea: { fill: { color: HEX.white } },
});
const r1 = x => Math.round(x * 10) / 10;

// ---- Loss curves ----
{
  const s = light("Results", "EVALUATION · LOSS", "Loss curves: attention learns faster and generalizes better",
    "Cross-entropy loss per epoch from our training logs. Solid lines are validation loss, dashed are training. The attention model's validation loss ends at 2.21 versus 2.58 without attention, which is perplexity 9.1 versus 13.2: at each word the attention model is effectively choosing between about 9 candidates instead of 13. Validation loss flattens after about epoch 10 while training loss keeps falling, which is the start of overfitting; we keep the epoch with the best validation loss.");
  const a = M.curves.attention, b = M.curves.baseline, ep = a.epoch.map(String);
  s.addChart(pres.charts.LINE, [
    { name: "Attention · train", labels: ep, values: a.train_loss },
    { name: "Attention · val", labels: ep, values: a.val_loss },
    { name: "No attention · train", labels: ep, values: b.train_loss },
    { name: "No attention · val", labels: ep, values: b.val_loss },
  ], Object.assign(chartBase(), {
    x: 0.6, y: 1.75, w: 8.0, h: 4.95, title: "Cross-entropy loss per epoch",
    chartColors: [HEX.coral, HEX.coral, HEX.deep, HEX.deep], lineSize: 2.25, lineDataSymbol: "circle", lineDataSymbolSize: 4,
    lineDash: ["dash", "solid", "dash", "solid"], showLegend: true,
    valAxisMinVal: 1.5, valAxisMaxVal: 4.5, valAxisMajorUnit: 0.5, showCatAxisTitle: true, catAxisTitle: "epoch",
    catAxisTitleFontSize: 11, catAxisTitleColor: HEX.muted,
  }));
  const st = [
    [`${a.val_loss[a.val_loss.length - 1].toFixed(2)} vs ${Math.min(...b.val_loss).toFixed(2)}`, "best validation loss (attention vs no attention)"],
    ["9.1 vs 13.2", "validation perplexity: ~9 likely words per step instead of ~13"],
    ["~epoch 10", "validation loss flattens; we keep the best epoch"],
  ];
  st.forEach(([v, l], i) => {
    card(s, 8.95, 1.8 + i * 1.65, 3.8, 1.45, i === 0 ? S.deep : S.white);
    T(s, v, { x: 9.2, y: 1.92 + i * 1.65, w: 3.35, h: 0.55, fontSize: 24, bold: true, color: S.coral, head: true });
    T(s, l, { x: 9.2, y: 2.5 + i * 1.65, w: 3.35, h: 0.65, fontSize: 13, color: i === 0 ? S.line : S.muted });
  });
}

// ---- BLEU breakdown ----
{
  const s = light("Results", "EVALUATION · BLEU BREAKDOWN", "Attention wins most on longer word sequences",
    "BLEU is built from four precisions: the share of predicted 1-, 2-, 3- and 4-word sequences that also appear in the human translation, times a brevity penalty for outputs that are too short. Single words are similar across systems, 66 to 80 percent, because even a dictionary gets most words right. The gap grows with phrase length: for 4-word phrases the rule-based system gets 7 percent, no attention 26, attention 43. That means attention gets word order and grammar right, not just vocabulary. The table adds exact matches: 176 of 1,000 test sentences are identical to the human translation with attention, versus 100 and 5.");
  const order = [["rule", "Rule-based"], ["baseline", "No attention"], ["attention", "With attention"]];
  s.addChart(pres.charts.BAR, order.map(([k, n]) => ({ name: n, labels: ["1-gram", "2-gram", "3-gram", "4-gram"], values: M[k].precisions.map(r1) })),
    Object.assign(chartBase(), {
      x: 0.6, y: 1.75, w: 7.4, h: 4.95, barDir: "col", barGrouping: "clustered", barGapWidthPct: 70,
      title: "n-gram precision on the test set (%)", chartColors: [HEX.soft, HEX.deep, HEX.coral], showLegend: true,
      showValue: true, dataLabelPosition: "outEnd", dataLabelFontSize: 10, dataLabelColor: HEX.text, dataLabelFontFace: "+mn-lt",
      valAxisMinVal: 0, valAxisMaxVal: 100, valAxisMajorUnit: 20,
    }));
  const hdr = ["", "Rule", "No attn", "Attn"].map((t, j) => ({ text: t, options: { bold: true, color: HEX.white, fill: { color: j === 3 ? HEX.coral : HEX.deep }, align: j ? "center" : "left" } }));
  const row = (label, f) => [{ text: label, options: { bold: true, color: HEX.deep } }, ...order.map(([k], j) => ({ text: f(k), options: { color: HEX.text, bold: j === 2, align: "center" } }))];
  s.addTable([hdr,
    row("Corpus BLEU", k => r1(M[k].bleu).toFixed(1)),
    row("Brevity penalty", k => M[k].brevity_penalty.toFixed(3)),
    row("Exact matches / 1,000", k => String(M[k].exact_match)),
    row("Median sentence BLEU", k => r1(M[k].median_sentence_bleu).toFixed(1)),
  ], { x: 8.3, y: 1.85, w: 4.45, colW: [1.9, 0.85, 0.85, 0.85], fontFace: "Calibri", fontSize: 13, rowH: 0.5,
       border: { type: "solid", pt: 0.75, color: HEX.line }, fill: { color: HEX.white }, valign: "middle", margin: [0.03, 0.08, 0.03, 0.08] });
  card(s, 8.3, 4.65, 4.45, 2.0, S.white);
  T(s, "How to read it", { x: 8.55, y: 4.8, w: 4, h: 0.35, fontSize: 15, bold: true, color: S.deep });
  T(s, "Similar 1-gram scores mean all systems pick mostly the right words. The 4-gram gap (7 → 26 → 43) shows attention gets the order and grammar right.",
    { x: 8.55, y: 5.18, w: 4, h: 1.35, fontSize: 13, color: S.text });
}

// ---- BLEU by sentence length ----
{
  const s = light("Results", "EVALUATION · SENTENCE LENGTH", "The bottleneck, measured on long sentences",
    "This chart proves the bottleneck from slide 8 with data. We split the 1,000 test sentences by English length and computed BLEU for each group. On short sentences, up to 8 words, the two neural models are close: 59 versus 52. As sentences get longer, the no-attention model collapses to 21 BLEU on sentences of 21 words or more, because the whole sentence must fit in one vector. The attention model only drops to 46, because it can look back at every word. The rule-based system is flat and low at every length.");
  const L = M.by_length;
  const labels = L.buckets.map((b, i) => `${b} words (n=${L.count[i]})`);
  s.addChart(pres.charts.LINE, [
    { name: "With attention", labels, values: L.attention.map(r1) },
    { name: "No attention", labels, values: L.baseline.map(r1) },
    { name: "Rule-based", labels, values: L.rule.map(r1) },
  ], Object.assign(chartBase(), {
    x: 0.6, y: 1.75, w: 8.0, h: 4.95, title: "Test BLEU by English sentence length",
    chartColors: [HEX.coral, HEX.deep, HEX.soft], lineSize: 3, lineDataSymbol: "circle", lineDataSymbolSize: 7, showLegend: true,
    showValue: true, dataLabelPosition: "t", dataLabelFontSize: 10, dataLabelColor: HEX.text, dataLabelFontFace: "+mn-lt",
    valAxisMinVal: 0, valAxisMaxVal: 70, valAxisMajorUnit: 10, catAxisLabelFontSize: 10,
  }));
  const drop = (k) => r1(L[k][0] - L[k][L[k].length - 1]);
  const st = [
    [`−${drop("baseline")}`, "BLEU lost by the no-attention model from the shortest to the longest sentences"],
    [`−${drop("attention")}`, "BLEU lost with attention: it can look back at every word"],
    [`${r1(L.attention[4])} vs ${r1(L.baseline[4])}`, "on sentences of 21+ words, more than double"],
  ];
  st.forEach(([v, l], i) => {
    card(s, 8.95, 1.8 + i * 1.65, 3.8, 1.45, i === 2 ? S.deep : S.white);
    T(s, v, { x: 9.2, y: 1.92 + i * 1.65, w: 3.35, h: 0.55, fontSize: 26, bold: true, color: S.coral, head: true });
    T(s, l, { x: 9.2, y: 2.5 + i * 1.65, w: 3.35, h: 0.65, fontSize: 13, color: i === 2 ? S.line : S.muted });
  });
}

// ---- Confusion matrix: article gender ----
{
  const s = light("Results", "EVALUATION · CONFUSION MATRIX", "Grammatical gender: the dictionary never writes “une”",
    "Translation has no class labels, so we built confusion matrices for two word choices that matter in French. This one is grammatical gender: for the 689 test sentences whose human translation starts with un or une, we compare the article each system wrote. Rows are the correct article, columns the predicted one. The rule-based dictionary maps 'a' to 'un' and never writes 'une', so all 219 feminine sentences are wrong, 203 of them as 'un': 62 percent accuracy overall. Both neural models learned gender from context: 97 percent without attention and 98 percent with attention.");
  const W = 12.15, H = W * 578 / 1700;
  s.addImage({ path: path.join(ROOT, "outputs", "eval", "confusion_article.png"), x: 0.6, y: 1.7, w: W, h: H,
    altText: "Article gender confusion matrices: rule-based 62%, no attention 97%, with attention 98% correct" });
  const C3 = M.confusion;
  const st = [
    [`${Math.round(C3.rule.article_acc * 100)}%`, "Rule-based: never writes “une”; all 219 feminine sentences wrong", S.white],
    [`${Math.round(C3.baseline.article_acc * 100)}%`, "No attention: gender learned from the whole-sentence context", S.white],
    [`${Math.round(C3.attention.article_acc * 100)}%`, `With attention: ${C3.attention.article[1][1]} of 219 “une” correct`, S.deep],
  ];
  st.forEach(([v, l, f], i) => {
    const x = 0.6 + i * 4.1;
    card(s, x, 5.95, 3.9, 0.85, f);
    T(s, v, { x: x + 0.2, y: 6.02, w: 0.95, h: 0.7, fontSize: 24, bold: true, color: S.coral, head: true, valign: "middle" });
    T(s, l, { x: x + 1.15, y: 6.02, w: 2.6, h: 0.7, fontSize: 11, color: f === S.deep ? S.line : S.text, valign: "middle" });
  });
}

// ---- Confusion matrix: colour words ----
{
  const s = light("Results", "EVALUATION · CONFUSION MATRIX", "Colour words: neural errors are dropped colours",
    "Second confusion matrix: the 219 test sentences whose reference has exactly one colour. Rows are the correct colour, columns the colour the system wrote, and 'none' means the colour was left out. Off-diagonal mix-ups between colours are almost zero for every system. The neural models' errors are almost all in the 'none' column: the colour was dropped. No attention drops 20, attention 9. The rule-based system scores highest here, 97 percent, because a dictionary always translates a colour word, but this check ignores gender agreement: it writes 'herbe vert' where French needs 'herbe verte'.");
  const W = 12.15, H = W * 714 / 2210;
  s.addImage({ path: path.join(ROOT, "outputs", "eval", "confusion_colour.png"), x: 0.6, y: 1.65, w: W, h: H,
    altText: "Colour-word confusion matrices for rule-based, no attention and attention models" });
  const C3 = M.confusion;
  const st = [
    [`${Math.round(C3.rule.colour_acc * 100)}%`, "Rule-based: always outputs the colour, but ignores agreement (“herbe vert”)"],
    [`${Math.round(C3.baseline.colour_acc * 100)}%`, "No attention: errors are dropped colours (“none” column)"],
    [`${Math.round(C3.attention.colour_acc * 100)}%`, "With attention: half the dropped colours, and agreement is correct"],
  ];
  st.forEach(([v, l], i) => {
    const x = 0.6 + i * 4.1;
    card(s, x, 5.85, 3.9, 0.95, i === 2 ? S.deep : S.white);
    T(s, v, { x: x + 0.2, y: 5.95, w: 0.95, h: 0.75, fontSize: 24, bold: true, color: S.coral, head: true, valign: "middle" });
    T(s, l, { x: x + 1.15, y: 5.95, w: 2.6, h: 0.75, fontSize: 11, color: i === 2 ? S.line : S.text, valign: "middle" });
  });
}

// =========================== 14. Heatmap ===========================
{
  const s = light("Results", "QUALITATIVE RESULTS", "The heatmap shows the model learned to reorder words",
    "This is a real heatmap from our trained model. Rows are the French words it generated, columns the English words, and darker means more attention. Most of it follows the diagonal, but look at 't-shirt rouge': 't-shirt' looks at 'shirt' and 'rouge' looks at 'red', crossing the diagonal because French puts the colour after the noun. Nobody gave it that rule. Some rows sit one word early, for example 'un' on <sos>, because Bahdanau attention uses the decoder state from before the current word.");
  const H = 4.95, W = H * 1080 / 825;
  s.addImage({ path: path.join(ROOT, "outputs", "a_man_in_a_red_shirt_is_playing_guitar.png"), x: 0.6, y: 1.7, w: W, h: H,
    altText: "Attention heatmap for 'a man in a red shirt is playing guitar' translated to 'un homme en t-shirt rouge joue de la guitare'" });
  const x0 = 0.6 + W + 0.4, w0 = 12.75 - x0;
  card(s, x0, 1.8, w0, 1.5, S.deep);
  T(s, "INPUT", { x: x0 + 0.25, y: 1.92, w: 2, h: 0.3, fontSize: 11, bold: true, color: S.line, charSpacing: 2 });
  T(s, "A man in a red shirt is playing guitar.", { x: x0 + 0.25, y: 2.2, w: w0 - 0.5, h: 0.35, fontSize: 14, color: S.white });
  T(s, "OUTPUT", { x: x0 + 0.25, y: 2.6, w: 2, h: 0.3, fontSize: 11, bold: true, color: S.line, charSpacing: 2 });
  T(s, "Un homme en t-shirt rouge joue de la guitare.", { x: x0 + 0.25, y: 2.88, w: w0 - 0.5, h: 0.35, fontSize: 14, bold: true, color: S.coral });
  const pts = [
    ["Word order flips", "“red shirt” → “t-shirt rouge”: the attention crosses the diagonal."],
    ["Learned, not coded", "No grammar rules or alignment labels were given."],
    ["One-word shift", "Some rows sit one word early (“un” → <sos>): Bahdanau uses the previous decoder state."],
  ];
  pts.forEach(([h, d], i) => {
    const y = 3.55 + i * 1.05;
    T(s, h, { x: x0, y, w: w0, h: 0.35, fontSize: 15, bold: true, color: S.deep });
    T(s, d, { x: x0, y: y + 0.35, w: w0, h: 0.62, fontSize: 13, color: S.text });
  });
}

// =========================== 15. Side by side ===========================
{
  const s = light("Results", "SIDE BY SIDE", "Same sentence, three systems",
    "Real outputs from all three systems. In the first sentence both neural models are correct, and the attention map shows the two colour swaps: robe rose with 99 percent of attention on pink, and herbe verte. The rule-based system gets gender wrong three times and translates 'is running' literally. In the longer second sentence, the no-attention model invents 'joueur de football', a football player, while the attention model keeps 'terrier'. Its remaining errors are a repeated word and a rare word it can't translate.");
  const rows = [
    ["A little girl in a pink dress is running on the green grass.",
      "un petite fille en un robe rose est court sur la herbe vert", "une petite fille en robe rose court sur l'herbe verte", "une petite fille en robe rose court sur l'herbe verte"],
    ["A Boston Terrier is running on lush green grass in front of a white fence.",
      "un boston terrier est court sur luxuriante herbe vert en devant de un clôture blanc", "un joueur de football court sur l'herbe verte devant une clôture blanche", "un terrier de court court sur l'herbe verte devant une clôture blanche"],
  ];
  const hdr = [["English", HEX.deep], ["Rule-based", HEX.soft], ["No attention", HEX.deep], ["With attention", HEX.coral]].map(([t, c]) => ({ text: t, options: { bold: true, color: HEX.white, fill: { color: c } } }));
  const body = rows.map(r => r.map((t, j) => ({ text: t, options: { color: j === 3 ? HEX.deep : HEX.text, bold: j === 3, fill: { color: j === 0 ? HEX.tint : HEX.white } } })));
  s.addTable([hdr, ...body], { x: 0.6, y: 1.8, w: 12.15, colW: [3.0, 3.05, 3.05, 3.05], fontFace: "Calibri", fontSize: 13,
    border: { type: "solid", pt: 0.75, color: HEX.line }, rowH: [0.45, 1.2, 1.45], valign: "middle", margin: [0.06, 0.12, 0.06, 0.12] });
  const notes = [
    ["Rule-based", "gender wrong (un fille, herbe vert, clôture blanc); “is running” → “est court”"],
    ["No attention", "fluent, but invents content on the longer sentence (“joueur de football”)"],
    ["With attention", "keeps the content; errors are a rare word (Boston) and a repeated word"],
  ];
  notes.forEach(([h, d], i) => {
    const x = 0.6 + i * 4.1;
    card(s, x, 5.3, 3.9, 1.35, S.white);
    T(s, h, { x: x + 0.25, y: 5.42, w: 3.4, h: 0.35, fontSize: 14, bold: true, color: i === 2 ? S.coral : S.deep });
    T(s, d, { x: x + 0.25, y: 5.78, w: 3.4, h: 0.8, fontSize: 12, color: S.text });
  });
}

// =========================== 16. Web demo ===========================
pres.addSection({ title: "Demo" });
{
  const s = light("Demo", "LIVE DEMO", "An interactive web app that shows the model's internals",
    "The demo is a Flask server that loads all three models once, plus a single-page frontend. Type an English sentence or pick an example. You get the three translations side by side, the alignment view where line thickness is attention, a heatmap tab, and an under-the-hood console that prints the tokens, their vocabulary IDs, the real tensor shapes, a per-step trace of which English word each French word focused on, and the latency of each model. It also handles bad input: empty text, overly long text, and non-English text. Run it with python app.py.");
  const H = 4.75, W = H * 800 / 609;
  s.addImage({ path: path.join(__dirname, "demo_hero.jpg"), x: 0.6, y: 1.75, w: W, h: H, altText: "Screenshot of the web demo with the under-the-hood inference trace" });
  const x0 = 0.6 + W + 0.4, w0 = 12.75 - x0;
  const feats = [
    ["Three translations side by side", "attention, no attention, and rule-based, with test BLEU"],
    ["Alignment & heatmap views", "line thickness = attention weight; hover a French word"],
    ["Under-the-hood console", "tokens → IDs → tensor shapes → per-step attention → latency"],
    ["Safe with bad input", "empty, too long or non-English text gets a clear message"],
  ];
  feats.forEach(([h, d], i) => {
    const y = 1.8 + i * 1.05;
    s.addShape(pres.shapes.OVAL, { x: x0, y: y + 0.05, w: 0.42, h: 0.42, fill: { color: S.coral }, line: { type: "none" } });
    T(s, String(i + 1), { x: x0, y: y + 0.05, w: 0.42, h: 0.42, fontSize: 13, bold: true, color: S.white, align: "center", valign: "middle" });
    T(s, h, { x: x0 + 0.6, y, w: w0 - 0.6, h: 0.35, fontSize: 15, bold: true, color: S.text });
    T(s, d, { x: x0 + 0.6, y: y + 0.37, w: w0 - 0.6, h: 0.6, fontSize: 12, color: S.muted });
  });
  s.addShape(pres.shapes.ROUNDED_RECTANGLE, { x: x0, y: 6.05, w: w0, h: 0.5, rectRadius: 0.08, fill: { color: S.deep }, line: { type: "none" } });
  T(s, "python app.py  →  http://127.0.0.1:5000", { x: x0 + 0.2, y: 6.05, w: w0 - 0.4, h: 0.5, fontSize: 13, color: S.white, fontFace: "Courier New", valign: "middle" });
}

// =========================== 17. Alignment view ===========================
{
  const s = light("Demo", "ALIGNMENT VIEW", "Crossing lines show where French reverses English word order",
    "This is the alignment view from the demo for the sentence about the girl in the pink dress. English is on top, French below, and line thickness is the attention weight. The two crossings are the adjective-noun swaps: pink dress becomes robe rose, and green grass becomes herbe verte. The console trace below gives the same information as numbers.");
  const W = 12.15, H = W * 190 / 740;
  s.addImage({ path: path.join(__dirname, "demo_align.png"), x: 0.6, y: 1.8, w: W, h: H, altText: "Alignment view: lines from English words to French words, crossing at pink dress / robe rose and green grass / herbe verte" });
  const tr = [["robe", "dress", 76], ["rose", "pink", 99], ["herbe", "grass", 93], ["verte", "green", 86]];
  tr.forEach(([fr, en, p], i) => {
    const x = 0.6 + i * 3.1;
    card(s, x, 5.2, 2.85, 1.4, S.white);
    T(s, [{ text: fr, options: { bold: true, color: S.deep } }, { text: "  ←  ", options: { color: S.muted } }, { text: en, options: { color: S.text } }],
      { x: x + 0.25, y: 5.35, w: 2.4, h: 0.45, fontSize: 18 });
    T(s, p + "% attention", { x: x + 0.25, y: 5.88, w: 2.4, h: 0.45, fontSize: 18, bold: true, color: S.coral, head: true });
  });
}

// =========================== 18. Proposal vs delivered ===========================
pres.addSection({ title: "Wrap-up" });
{
  const s = light("Wrap-up", "PROPOSAL VS DELIVERED", "What we planned, and what we built",
    "Be transparent about what changed from the proposal. We used a regular-expression tokenizer instead of spaCy, a word-level vocabulary instead of subwords, and a local GPU instead of Colab. Everything else was delivered, and we added a no-attention baseline, a rule-based baseline and an interactive web app. The BLEU target was exceeded, with the metric caveat from the results slide.");
  const rows = [
    ["Data", "Multi30k EN–FR, ~29K train pairs", "Multi30k EN–FR: 29,000 / 1,014 / 1,000", "Delivered"],
    ["Tokenizer", "spaCy tokenizers", "Regex tokenizer (handles French elisions)", "Changed"],
    ["Vocabulary", "~10K subword units", "Word-level: 5,979 EN / 6,486 FR", "Changed"],
    ["Model", "Bi-LSTM encoder + Bahdanau attention", "As planned; 16M parameters", "Delivered"],
    ["Training", "Teacher forcing, Adam, clipping, LR schedule", "As planned, plus label smoothing", "Delivered"],
    ["Inference", "Beam search, width 3–5", "Beam 5 with length normalization", "Delivered"],
    ["BLEU target", "22–28 on Multi30k test", "56.8 (attention) vs 40.7 (baseline)", "Exceeded"],
    ["Heatmaps", "Interactive heatmap notebook", "Notebook + interactive web app", "Extended"],
    ["Evaluation", "BLEU + heatmaps + manual review", "+ loss curves, n-gram, length, confusion matrices", "Extended"],
    ["Baselines", "Plain seq2seq + rule-based contrast", "Both built and evaluated", "Delivered"],
    ["Compute", "Single GPU (Colab)", "Local RTX 4060 laptop GPU", "Changed"],
  ];
  const tag = { Delivered: HEX.deep, Changed: HEX.soft, Exceeded: HEX.coral, Extended: HEX.coral };
  const hdr = ["", "Proposal", "Delivered", "Status"].map(t => ({ text: t, options: { bold: true, color: HEX.white, fill: { color: HEX.deep } } }));
  const body = rows.map((r, i) => r.map((t, j) => ({ text: t, options: {
    bold: j === 0 || j === 3, color: j === 3 ? tag[t] : HEX.text, fill: { color: i % 2 ? HEX.tint : HEX.white } } })));
  s.addTable([hdr, ...body], { x: 0.6, y: 1.75, w: 12.15, colW: [1.7, 4.2, 4.6, 1.65], fontFace: "Calibri", fontSize: 13,
    border: { type: "solid", pt: 0.75, color: HEX.line }, rowH: 0.4, valign: "middle", margin: [0.03, 0.12, 0.03, 0.12] });
}

// =========================== 19. Limitations ===========================
{
  const s = light("Wrap-up", "LIMITATIONS & FUTURE WORK", "What it can't do yet, and how we would fix it",
    "Four honest limitations, each paired with a concrete fix. Rare words become <unk>, which subword tokenization would solve. The model only knows image-caption language. Teacher forcing causes exposure bias, which scheduled sampling addresses. Attention is slower, about 270 milliseconds versus 34 in the demo, because it rescores every English word at every French step, and RNNs can't be parallelised the way Transformers can. Next steps: compare against a Transformer, train on a larger dataset, and report sacreBLEU and chrF alongside our BLEU.");
  const items = [
    ["Unknown words", "Rare words become <unk> (“snowmobiles”, “Boston”).", "Subword tokenization (BPE / SentencePiece)"],
    ["Narrow domain", "Only knows short image captions.", "Train on larger, varied data (e.g. WMT14)"],
    ["Exposure bias", "Trained on true words, tested on its own guesses.", "Scheduled sampling"],
    ["Speed", "~270 ms vs 34 ms without attention; RNNs run step by step.", "Transformer comparison"],
  ];
  items.forEach(([h, d, f], i) => {
    const x = 0.6 + (i % 2) * 6.15, y = 1.8 + Math.floor(i / 2) * 2.1;
    card(s, x, y, 5.95, 1.9, S.white);
    T(s, h, { x: x + 0.3, y: y + 0.18, w: 5.3, h: 0.4, fontSize: 17, bold: true, color: S.text, head: true });
    T(s, d, { x: x + 0.3, y: y + 0.62, w: 5.3, h: 0.55, fontSize: 14, color: S.muted });
    T(s, [{ text: "Fix  ", options: { bold: true, color: S.coral } }, { text: f, options: { color: S.deep, bold: true } }],
      { x: x + 0.3, y: y + 1.3, w: 5.3, h: 0.4, fontSize: 14 });
  });
  T(s, "Also: report sacreBLEU and chrF alongside our BLEU, and run a human evaluation.", { x: 0.6, y: 6.1, w: 12, h: 0.4, fontSize: 13, color: S.muted, italic: true });
}

// =========================== 20. Takeaways ===========================
{
  const s = dark("Wrap-up", "Close with the three takeaways, then open for questions. The headline number to remember: attention takes BLEU from 40.7 to 56.8 on the same network.");
  T(s, "KEY TAKEAWAYS", { x: 0.8, y: 0.8, w: 6, h: 0.35, fontSize: 13, bold: true, color: S.coral, charSpacing: 3 });
  T(s, "A small model that makes a big idea visible", { x: 0.8, y: 1.3, w: 11.5, h: 0.8, fontSize: 36, bold: true, color: S.white, head: true });
  const tk = [
    ["1", "Seq2seq learns translation end-to-end", "No grammar rules: one network maps English to French and beats the rule-based system 3×."],
    ["2", "Attention removes the bottleneck", "+16.1 BLEU on the same network, and the weights show what the model is looking at."],
    ["3", "Small data, one GPU, real insight", "29,000 pairs and a laptop GPU were enough to show the mechanism end-to-end."],
  ];
  tk.forEach(([n, h, d], i) => {
    const x = 0.8 + i * 4.0;
    s.addShape(pres.shapes.ROUNDED_RECTANGLE, { x, y: 2.55, w: 3.7, h: 2.85, rectRadius: 0.12, fill: { color: S.deep }, line: { type: "none" } });
    T(s, n, { x: x + 0.3, y: 2.75, w: 1, h: 0.6, fontSize: 30, bold: true, color: S.coral, head: true });
    T(s, h, { x: x + 0.3, y: 3.4, w: 3.1, h: 0.8, fontSize: 17, bold: true, color: S.white });
    T(s, d, { x: x + 0.3, y: 4.25, w: 3.1, h: 1.05, fontSize: 13, color: S.line });
  });
  T(s, "Thank you, questions welcome.", { x: 0.8, y: 5.85, w: 7, h: 0.5, fontSize: 22, color: S.white, head: true, italic: true });
  T(s, "github.com/Shash309/attention-translator", { x: 7.5, y: 5.92, w: 5.25, h: 0.4, fontSize: 14, color: S.line, align: "right" });
}

(async () => {
  await pres.writeFile({ fileName: OUT });
  await applyTheme(OUT, THEME);
  fs.writeFileSync(path.join(__dirname, "fitlog.json"), JSON.stringify(fitLog));
  console.log("wrote", OUT, "slides:", slideNo);
})();
