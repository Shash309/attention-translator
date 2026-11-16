import copy
import json
import os
import re
import subprocess
import sys

import docx
import fitz
from lxml import etree
from docx.oxml import OxmlElement
from docx.oxml.ns import qn

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import content
from lib import FONT, LEFT, TEXT_W, Writer, add_runs, replace_in_paragraph, rewrite, set_text
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.shared import Pt, Twips

HERE = os.path.dirname(os.path.abspath(__file__))
TEMPLATE = os.path.join(HERE, "fmt.docx")
OUT_DOCX = os.path.join(HERE, "report.docx")
OUT_PDF = os.path.join(HERE, "report.pdf")

TITLE1 = "Neural Machine Translation with Attention:"
TITLE2 = "English–French Translation Using a Bi-LSTM Encoder–Decoder with Bahdanau Attention"
TITLE = TITLE1 + " " + TITLE2
MEMBERS = [("Ankam Sai Anirudh", "RA2311026010087"), ("Atharva Bhutada", "RA2311026010089"),
           ("Vansh Agrawal", "RA2311026010120"), ("Shashwat Sharma", "RA2311026010121")]
NAMES = "Ankam Sai Anirudh, Atharva Bhutada, Vansh Agrawal & Shashwat Sharma"
REGS = "RA2311026010087, RA2311026010089, RA2311026010120 & RA2311026010121"

ABSTRACT = [
    "Language remains a major barrier to access to information. Rule-based and dictionary translation systems "
    "translate word by word, cannot agree gender or reorder words reliably, and ignore the meaning of the whole "
    "sentence, while early neural encoder–decoder models compress a sentence into one fixed-size vector and lose "
    "information on long inputs.",
    "This project builds a neural machine translation (NMT) system for English to French using a bidirectional LSTM "
    "encoder, Bahdanau additive attention and an LSTM decoder, implemented from scratch in PyTorch and trained on "
    "the Multi30k corpus (29,000 training, 1,014 validation and 1,000 test sentence pairs). To isolate the "
    "contribution of attention, the same network is also trained without attention, and a rule-based baseline "
    "using an IBM Model 1 dictionary with hand-written reordering rules is built.",
    "On the 1,000-sentence test set with beam search (width 5), the attention model reaches a BLEU score of 56.76, "
    "against 40.65 for the network without attention and 19.17 for the rule-based system, an improvement of 16.1 "
    "BLEU for only 0.3 million additional parameters. Attention helps most on long sentences (46.3 versus 21.4 "
    "BLEU on sentences of 21 or more words) and on grammatical agreement (98.0% correct un/une choices against "
    "62.4% for the rule-based system).",
    "The learned attention weights are exposed as heatmaps and alignment lines, showing that the model reorders "
    "words such as “red shirt” into “t-shirt rouge” without any alignment labels. A Flask web application presents "
    "the three translators side by side with an interactive attention view, an inference console and safe "
    "handling of invalid input.",
    "The project demonstrates, with a controlled experiment on modest hardware, why attention became the "
    "foundation of modern translation systems, and identifies unknown words, domain size and inference speed as "
    "directions for future work.",
]
KEYWORDS = ("Neural Machine Translation, Attention Mechanism, Bahdanau Attention, Sequence-to-Sequence, Bi-LSTM, "
            "Encoder–Decoder, English–French, Multi30k, BLEU, Beam Search, Attention Heatmap, IBM Model 1, "
            "Explainable AI, PyTorch.")
ABBR = [("NMT", "Neural Machine Translation"), ("MT", "Machine Translation"), ("NLP", "Natural Language Processing"),
        ("RNN", "Recurrent Neural Network"), ("LSTM", "Long Short-Term Memory"),
        ("Bi-LSTM", "Bidirectional Long Short-Term Memory"), ("Seq2Seq", "Sequence-to-Sequence"),
        ("BLEU", "Bilingual Evaluation Understudy"), ("BP", "Brevity Penalty"),
        ("EM", "Expectation–Maximisation"), ("IBM-1", "IBM Model 1 (word alignment model)"),
        ("OOV", "Out of Vocabulary"), ("UNK", "Unknown token"), ("SOS / EOS", "Start / End of Sentence token"),
        ("PAD", "Padding token"), ("BPE", "Byte-Pair Encoding"), ("PPL", "Perplexity"),
        ("EN / FR", "English / French"), ("GPU", "Graphics Processing Unit"),
        ("CUDA", "Compute Unified Device Architecture"), ("API", "Application Programming Interface"),
        ("REST", "Representational State Transfer"), ("JSON", "JavaScript Object Notation"),
        ("HTTP", "Hyper Text Transfer Protocol"), ("HTML", "Hyper Text Markup Language"),
        ("UI", "User Interface"), ("SDG", "Sustainable Development Goals")]


def roman(n):
    vals = [(10, "x"), (9, "ix"), (5, "v"), (4, "iv"), (1, "i")]
    out = ""
    for v, s in vals:
        while n >= v:
            out += s; n -= v
    return out


def drop_scans(P):
    """Remove the full-page signed scans on the declaration and bonafide pages (keep logos)."""
    for idx, rid in ((34, "rId10"), (60, "rId12")):
        for dr in P[idx]._p.iter(qn("w:drawing")):
            blip = dr.find(".//" + qn("a:blip"))
            if blip is not None and blip.get(qn("r:embed")) == rid:
                run = dr.getparent()
                while run.tag != qn("w:r"):
                    run = run.getparent()
                run.getparent().remove(run)
                break


def edit_front(d, P):
    # cover
    set_text(P[1], TITLE1)
    set_text(P[2], TITLE2)
    set_text(P[8], f"{MEMBERS[0][0]} [{MEMBERS[0][1]}]")
    set_text(P[9], f"{MEMBERS[1][0]} [{MEMBERS[1][1]}]")
    prev = P[9]._p
    for name, reg in MEMBERS[2:]:
        el = copy.deepcopy(P[9]._p)
        prev.addnext(el)
        prev = el
        # set text of the copied element
        t = el.findall(".//" + qn("w:t"))
        t[0].text = f"{name} [{reg}]"
        for x in t[1:]:
            x.text = ""
    set_text(P[4], "21CSC406J - NEURAL NETWORKS AND DEEP LEARNING")
    set_text(P[14], "Dr. C. Sherin Shibi")
    set_text(P[32], "NOVEMBER 2026")
    # declaration
    set_text(P[43], "Ankam Sai Anirudh, Atharva Bhutada,\nVansh Agrawal, Shashwat Sharma", keep=5)
    set_text(P[45], "RA2311026010087, RA2311026010089,\nRA2311026010120, RA2311026010121", keep=3)
    last = copy.deepcopy(P[45].runs[-1]._r)
    for t in last.findall(qn("w:t")):
        t.text = ""
    P[47]._p.append(last)
    from docx.text.run import Run
    Run(last, P[47]).text = TITLE1 + "\n" + "English–French Translation Using a Bi-LSTM Encoder–Decoder\nwith Bahdanau Attention"
    # bonafide
    rewrite(P[69], [
        ("Certified that 21CSC406J - NEURAL NETWORKS AND DEEP LEARNING project report titled “", False), (TITLE, True),
        ("” is the Bonafide work of “", False),
        (", ".join(f"{n} [{r}]" for n, r in MEMBERS), True),
        ("” who carried out the project work under my supervision. Certified further, that to the best of my "
         "knowledge the work reported herein does not form any other project report or dissertation on the basis "
         "of which a degree or award was conferred on an earlier occasion on this or any other candidate.", False)])
    cell = d.tables[1].rows[0].cells[0]
    cps = cell.paragraphs
    set_text(cps[1], "DR. C. SHERIN SHIBI")
    for r in cps[1].runs:
        r.font.size = Pt(10.5)
    set_text(cps[2], "ASSISTANT PROFESSOR")
    cps[3]._p.getparent().remove(cps[3]._p)
    # declaration layout: names column, title textbox, tighter spacing, signature names
    for i in (41, 43, 45, 47):
        pf = P[i].paragraph_format
        pf.left_indent, pf.first_line_indent = Twips(3300), Twips(-3300)
        for tb in P[i]._p.findall(".//" + qn("w:tabs")):
            tb.getparent().remove(tb)
        pf.tab_stops.add_tab_stop(Twips(2900))
        pf.tab_stops.add_tab_stop(Twips(3300))
    for i in (34, 35, 36):
        pf = P[i].paragraph_format
        pf.left_indent, pf.right_indent, pf.first_line_indent = Twips(0), Twips(0), Twips(0)
        pf.alignment = WD_ALIGN_PARAGRAPH.CENTER
        pf.space_before = Pt(2)
    P[34].paragraph_format.space_before = Pt(0)
    P[36].paragraph_format.space_after = Pt(10)
    for i in (38, 49, 51, 59):
        P[i].paragraph_format.left_indent = Twips(0)
        P[i].paragraph_format.right_indent = Twips(0)
        P[i].paragraph_format.alignment = WD_ALIGN_PARAGRAPH.JUSTIFY
    P[39].paragraph_format.left_indent = Twips(0)
    P[39].alignment = WD_ALIGN_PARAGRAPH.CENTER
    P[39].paragraph_format.space_before = Pt(6)
    for r in P[46]._p.findall(qn("w:r")):
        if b"drawing" in etree.tostring(r):
            P[46]._p.remove(r)
    for row in d.tables[0].rows:
        for cell in row.cells:
            for p in cell.paragraphs:
                if "Vansh Agrawal" in p.text:
                    set_text(p, "Ankam Sai Anirudh          Atharva Bhutada          Vansh Agrawal          "
                                "Shashwat Sharma")
                    p.alignment = WD_ALIGN_PARAGRAPH.CENTER
                    for r in p.runs:
                        r.font.size = Pt(8.5)
    tp = d.tables[0]._tbl.tblPr.find(qn("w:tblpPr"))
    if tp is not None:
        d.tables[0]._tbl.tblPr.remove(tp)
    for i in (41, 43, 45, 47, 49, 51):
        P[i].paragraph_format.space_before = Pt(9)
    jc = OxmlElement("w:jc"); jc.set(qn("w:val"), "center")
    d.tables[0]._tbl.tblPr.append(jc)
    P[57].paragraph_format.space_after = Pt(10)
    P[59].paragraph_format.space_before = Pt(10)
    P[63].paragraph_format.page_break_before = True
    P[85].paragraph_format.page_break_before = True
    P[107].paragraph_format.page_break_before = True
    for i in (53, 54, 55, 56, 57):
        P[i].paragraph_format.space_before = Pt(3)
    for i in (37, 40, 42, 44, 48, 50, 52, 58, 60, 61, 62, 66, 67, 70, 71, 72, 73, 120, 121, 122, 123, 124, 125, 126, 127, 128):
        el = P[i]._p
        if el.getparent() is not None:
            el.getparent().remove(el)
    # acknowledgements
    set_text(P[101], "Our inexpressible respect and thanks to our guide, Dr. C. Sherin Shibi, Assistant Professor, "
                     "Department of Computational Intelligence, SRM Institute of Science and Technology, for "
                     "providing us with an opportunity to pursue our project under her mentorship. She provided us "
                     "with the freedom and support to explore the research topics of our interest. Her passion for "
                     "solving problems and making a difference in the world has always been inspiring. ")
    for i in (99, 100):  # faculty-advisor paragraph (advisor differs per student) and its spacer
        P[i]._p.getparent().remove(P[i]._p)
    set_text(P[106], NAMES)
    P[106].alignment = WD_ALIGN_PARAGRAPH.RIGHT
    # abstract
    for k, txt in zip((109, 111, 113, 115, 117), ABSTRACT):
        set_text(P[k], txt)
    rewrite(P[119], [("Keywords: ", True), (KEYWORDS, False)])


def locate(pdf_path, body_toc, lof, lot):
    """Find page numbers from the rendered PDF. Returns dict of results."""
    doc = fitz.open(pdf_path)
    texts = [re.sub(r"\s+", " ", pg.get_text()) for pg in doc]
    pdf_lines = [pg.get_text().strip().split("\n") for pg in doc]
    firsts = [re.sub(r"\s+", " ", pg.get_text().strip().split("\n")[0]).strip() if pg.get_text().strip() else ""
              for pg in doc]
    res = {"front": {}, "toc": {}, "lof": {}, "lot": {}}
    for title in ("ABSTRACT", "TABLE OF CONTENTS", "LIST OF FIGURES", "LIST OF TABLES", "ABBREVIATIONS"):
        for i, f in enumerate(firsts):
            if i > 3 and title in [l.strip() for l in pdf_lines[i][:4]]:
                res["front"][title] = roman(i + 1)
                break
    p1 = None
    for i, t in enumerate(texts):
        if "CHAPTER 1 INTRODUCTION" in t and i > 5:
            p1 = i
    # pick the first occurrence after abbreviations page
    abbr_i = next((i for i, f in enumerate(firsts) if f == "ABBREVIATIONS"), 0)
    for i, t in enumerate(texts):
        if i > abbr_i and "CHAPTER 1 INTRODUCTION" in t:
            p1 = i
            break
    res["p1"] = p1
    res["total"] = len(doc)
    cur = p1
    for entry in body_toc:
        key = re.sub(r"\s+", " ", entry[3].replace("->", "→"))
        for i in range(cur, len(texts)):
            if key in texts[i]:
                cur = i
                res["toc"][entry[3]] = str(i - p1 + 1)
                break
    cur = p1
    for kind, lst, pref in (("lof", lof, "Fig. "), ("lot", lot, "Table ")):
        cur = p1
        for n, title in lst:
            key = f"{pref}{n} {title}"
            for i in range(cur, len(texts)):
                if key in texts[i]:
                    cur = i
                    res[kind][n] = str(i - p1 + 1)
                    break
    return res


def export_pdf(docx_path, pdf_path):
    ps = (f"$w = New-Object -ComObject Word.Application; $w.Visible=$false; "
          f"$d=$w.Documents.Open('{docx_path}',$false,$true); $d.ExportAsFixedFormat('{pdf_path}',17); "
          f"$d.Close($false); $w.Quit()")
    subprocess.run(["powershell", "-NoProfile", "-Command", ps], check=True)


def build(pages=None):
    d = docx.Document(TEMPLATE)
    P = list(d.paragraphs)
    body = d.element.body
    el346, el1375 = P[346]._p, P[1375]._p
    el129 = P[129]._p
    sect3 = copy.deepcopy(el1375.find(qn("w:pPr")).find(qn("w:sectPr")))

    edit_front(d, P)
    drop_scans(P)

    # wipe old chapters + appendices
    children = list(body)
    i346 = children.index(el346)
    for el in children[i346 + 1:]:
        body.remove(el)
    body.append(sect3)
    # wipe old TOC / lists / abbreviations
    children = list(body)
    a, b = children.index(el129), children.index(el346)
    for el in children[a:b]:
        body.remove(el)

    # body chapters
    w = Writer(d)
    content.write_body(w)
    pages = pages or {"front": {}, "toc": {}, "lof": {}, "lot": {}}

    # front lists, written before the front-matter section break
    f = Writer(d, anchor=el346)
    f.title("TABLE OF CONTENTS")
    rows = [(-1, "No.", "Title", "Page")]
    for t_ in ("ABSTRACT", "TABLE OF CONTENTS", "LIST OF FIGURES", "LIST OF TABLES", "ABBREVIATIONS"):
        rows.append((0, "", t_, pages["front"].get(t_, "x")))
    for lvl, label, title, key in w.toc:
        rows.append((lvl, label, title.upper() if (lvl == 0 and label) else title, pages["toc"].get(key, "x")))
    f.index_table(rows)
    f.title("LIST OF FIGURES")
    f.index_table([(-1, "Fig. No.", "Title", "Page")] +
                  [(1, n, t_, pages["lof"].get(n, "x")) for n, t_ in w.lof])
    f.title("LIST OF TABLES")
    f.index_table([(-1, "Table No.", "Title", "Page")] +
                  [(1, n, t_, pages["lot"].get(n, "x")) for n, t_ in w.lot])
    f.title("ABBREVIATIONS")
    for a_, b_ in ABBR:
        para = f.fmt(f.p(), "l", left=900, first=0, before=2, line=1.15)
        para.paragraph_format.tab_stops.add_tab_stop(Twips(2700))
        add_runs(para, f"{a_}\t{b_}", 11.5)
    d.core_properties.title = TITLE
    d.core_properties.author = NAMES
    d.save(OUT_DOCX)
    return w


if __name__ == "__main__":
    w = build()
    export_pdf(OUT_DOCX, OUT_PDF)
    for rnd in range(2):
        pages = locate(OUT_PDF, w.toc, w.lof, w.lot)
        w = build(pages)
        export_pdf(OUT_DOCX, OUT_PDF)
    pages2 = locate(OUT_PDF, w.toc, w.lof, w.lot)
    ok = pages2 == pages
    print("p1", pages2["p1"], "total", pages2["total"], "stable", ok)
    missing = [e[3] for e in w.toc if e[3] not in pages2["toc"]]
    print("missing toc:", missing[:10], "lof", len(pages2["lof"]), "/", len(w.lof), "lot", len(pages2["lot"]), "/",
          len(w.lot))
    json.dump(pages2, open(os.path.join(HERE, "pages.json"), "w"), indent=1)
