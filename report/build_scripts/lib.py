"""Helpers that write report content into the template docx with consistent formatting."""
import copy
import re

from docx.enum.text import WD_ALIGN_PARAGRAPH, WD_TAB_ALIGNMENT, WD_TAB_LEADER
from docx.oxml import OxmlElement
from docx.oxml.ns import qn
from docx.shared import Inches, Pt, Twips

FONT = "Times New Roman"
LEFT, RIGHT = 560, 150          # twips; makes the text block centred on the page
TEXT_W = 9930 - LEFT - RIGHT    # usable width in twips
AL = {"j": WD_ALIGN_PARAGRAPH.JUSTIFY, "l": WD_ALIGN_PARAGRAPH.LEFT, "c": WD_ALIGN_PARAGRAPH.CENTER,
      "r": WD_ALIGN_PARAGRAPH.RIGHT}
TOKEN = re.compile(r"(\*\*.+?\*\*|//.+?//|`.+?`|_\{.+?\}|\^\{.+?\})")


def set_font(run, size=None, bold=None, italic=None, mono=False):
    name = "Courier New" if mono else FONT
    run.font.name = name
    rpr = run._r.get_or_add_rPr()
    rf = rpr.find(qn("w:rFonts"))
    if rf is None:
        rf = OxmlElement("w:rFonts"); rpr.insert(0, rf)
    for a in ("w:ascii", "w:hAnsi", "w:eastAsia", "w:cs"):
        rf.set(qn(a), name)
    if size:
        run.font.size = Pt(size)
    if bold is not None:
        run.font.bold = bold
    if italic is not None:
        run.font.italic = italic


def add_runs(p, text, size=12, bold=False, italic=False, mono=False):
    for part in TOKEN.split(text):
        if not part:
            continue
        b, i, m, sub, sup = bold, italic, mono, False, False
        if part.startswith("**"):
            part, b = part[2:-2].replace("`", ""), True
        elif part.startswith("//"):
            part, i = part[2:-2], True
        elif part.startswith("`"):
            part, m = part[1:-1], True
        elif part.startswith("_{"):
            part, sub = part[2:-1], True
        elif part.startswith("^{"):
            part, sup = part[2:-1], True
        if not m:
            part = part.replace("->", "→")
        r = p.add_run(part)
        set_font(r, size - (1 if m else 0), b, i, m)
        if sub:
            r.font.subscript = True
        if sup:
            r.font.superscript = True


def shade(el_pr, fill):
    shd = OxmlElement("w:shd")
    shd.set(qn("w:val"), "clear"); shd.set(qn("w:color"), "auto"); shd.set(qn("w:fill"), fill)
    el_pr.append(shd)


class Writer:
    def __init__(self, doc, anchor=None, chap="0"):
        self.doc, self.anchor, self.chap = doc, anchor, chap
        self.toc, self.lof, self.lot = [], [], []
        self.nfig = self.ntab = 0

    # ---- placement -------------------------------------------------------
    def _place(self, el):
        if self.anchor is not None:
            self.anchor.addprevious(el)
        return el

    def p(self):
        para = self.doc.add_paragraph()
        self._place(para._p)
        return para

    def fmt(self, para, align="j", left=LEFT, right=RIGHT, first=0, before=6, after=0, line=1.5,
            keep_next=False, pbb=False, keep_lines=False):
        pf = para.paragraph_format
        para.alignment = AL[align]
        pf.left_indent, pf.right_indent = Twips(left), Twips(right)
        pf.first_line_indent = Twips(first) if first else None
        pf.space_before, pf.space_after = Pt(before), Pt(after)
        pf.line_spacing = line
        pf.keep_with_next = keep_next
        pf.keep_together = keep_lines
        pf.page_break_before = pbb
        return para

    # ---- text ------------------------------------------------------------
    def para(self, text, align="j", size=12, bold=False, italic=False, before=6, after=0, left=LEFT, first=0,
             keep_next=False, line=1.5):
        para = self.fmt(self.p(), align, left=left, first=first, before=before, after=after,
                        keep_next=keep_next, line=line)
        add_runs(para, text, size, bold, italic)
        return para

    def chapter(self, num, title):
        self.chap = str(num); self.nfig = self.ntab = 0
        a = self.fmt(self.p(), "c", before=0, after=0, pbb=True, line=1.5, keep_next=True)
        add_runs(a, f"CHAPTER {num}" if str(num).isdigit() else str(num), 18, True)
        b = self.fmt(self.p(), "c", before=0, after=12, line=1.5, keep_next=True)
        add_runs(b, title, 18, True)
        if str(num).isdigit():
            self.toc.append((0, str(num), title, f"CHAPTER {num}"))
        else:
            self.toc.append((0, "", f"{num}: {title}", str(num)))

    def h1(self, text, pbb=False):
        para = self.fmt(self.p(), "l", before=14, after=4, keep_next=True, pbb=pbb)
        add_runs(para, text, 14, True)
        self.toc.append((1, text.split(" ", 1)[0], text.split(" ", 1)[1], text))

    def h2(self, text):
        para = self.fmt(self.p(), "l", before=10, after=2, keep_next=True)
        add_runs(para, text, 12, True)
        self.toc.append((2, text.split(" ", 1)[0], text.split(" ", 1)[1], text))

    def h3(self, text):  # unnumbered run-in label, not in TOC
        para = self.fmt(self.p(), "l", before=8, after=0, keep_next=True)
        add_runs(para, text, 12, True)

    def bullets(self, items, mark="•", size=12, left=LEFT + 300, hang=280, before=2):
        for k, it in enumerate(items, 1):
            m = mark if mark != "1" else f"{k}."
            para = self.fmt(self.p(), "j", left=left + hang, first=-hang, before=before, line=1.35)
            para.paragraph_format.tab_stops.add_tab_stop(Twips(left + hang))
            add_runs(para, f"{m}\t{it}", size)

    def numbered(self, items, **kw):
        self.bullets(items, mark="1", **kw)

    def eq(self, text, num=None):
        para = self.fmt(self.p(), "c", before=6, after=6, line=1.3, keep_lines=True)
        add_runs(para, text, 12, italic=True)
        if num:
            add_runs(para, f"        ({num})", 12)

    def code(self, text, size=8.5):
        lines = text.rstrip("\n").split("\n")
        for k, ln in enumerate(lines):
            para = self.fmt(self.p(), "l", left=LEFT + 150, right=RIGHT, before=0, after=0, line=1.0,
                            keep_lines=True, keep_next=(k < len(lines) - 1 and k < 3))
            ppr = para._p.get_or_add_pPr()
            shade(ppr, "F4F4F4")
            r = para.add_run(ln if ln else " ")
            set_font(r, size, mono=True)
        self.fmt(self.p(), "l", before=0, after=0, line=0.6)

    def pagebreak(self):
        para = self.p()
        para.add_run().add_break(__import__("docx").enum.text.WD_BREAK.PAGE)

    # ---- tables / figures -------------------------------------------------
    def caption(self, kind, title, above):
        if kind == "Table":
            self.ntab += 1; n = f"{self.chap}.{self.ntab}"; label = f"Table {n}"
            self.lot.append((n, title))
        else:
            self.nfig += 1; n = f"{self.chap}.{self.nfig}"; label = f"Fig. {n}"
            self.lof.append((n, title))
        para = self.fmt(self.p(), "c", before=8 if above else 4, after=4 if above else 8, line=1.2,
                        keep_next=above)
        add_runs(para, f"{label} {title}", 11.5, bold=above)
        return label

    def table(self, header, rows, widths, caption=None, size=10.5, align=None, bold_first_col=False,
              hl_rows=()):
        if caption:
            self.caption("Table", caption, above=True)
        t = self.doc.add_table(rows=1 + len(rows), cols=len(header))
        self._place(t._tbl)
        t.alignment = 1
        t.autofit = False
        tblPr = t._tbl.tblPr
        borders = OxmlElement("w:tblBorders")
        for edge in ("top", "left", "bottom", "right", "insideH", "insideV"):
            e = OxmlElement(f"w:{edge}")
            e.set(qn("w:val"), "single"); e.set(qn("w:sz"), "4"); e.set(qn("w:space"), "0")
            e.set(qn("w:color"), "444444")
            borders.append(e)
        tblPr.append(borders)
        lay = OxmlElement("w:tblLayout"); lay.set(qn("w:type"), "fixed"); tblPr.append(lay)
        tw = sum(widths)
        scale = min(1.0, TEXT_W / tw) if tw > TEXT_W else 1.0
        widths = [int(w * scale) for w in widths]
        for ri, row in enumerate([header] + rows):
            tr = t.rows[ri]
            trPr = tr._tr.get_or_add_trPr()
            cs = OxmlElement("w:cantSplit"); trPr.append(cs)
            if ri == 0:
                th = OxmlElement("w:tblHeader"); trPr.append(th)
            for ci, val in enumerate(row):
                cell = tr.cells[ci]
                cell.width = Twips(widths[ci])
                tcPr = cell._tc.get_or_add_tcPr()
                mar = OxmlElement("w:tcMar")
                for side in ("top", "bottom"):
                    m = OxmlElement(f"w:{side}"); m.set(qn("w:w"), "40"); m.set(qn("w:type"), "dxa"); mar.append(m)
                for side in ("left", "right"):
                    m = OxmlElement(f"w:{side}"); m.set(qn("w:w"), "80"); m.set(qn("w:type"), "dxa"); mar.append(m)
                tcPr.append(mar)
                if ri == 0:
                    shade(tcPr, "D9D9D9")
                elif (ri - 1) in hl_rows:
                    shade(tcPr, "E8F1FB")
                para = cell.paragraphs[0]
                a = (align[ci] if align else "l") if ri else "c"
                self.fmt(para, a, left=0, right=0, before=1, after=1, line=1.1,
                         keep_next=(len(rows) <= 12 and ri < len(rows)))
                add_runs(para, str(val), size, bold=(ri == 0 or (bold_first_col and ci == 0) or (ri - 1) in hl_rows))
        self.fmt(self.p(), "l", before=0, after=0, line=0.8)
        return t

    def figure(self, path, width_in, caption):
        para = self.fmt(self.p(), "c", left=0, right=0, before=6, after=0, line=1.0, keep_next=True)
        para.add_run().add_picture(path, width=Inches(width_in))
        self.caption("Fig", caption, above=False)

    # ---- generated lists ---------------------------------------------------
    def dotted(self, label, text, page, indent=0, bold=False, size=11.5, num_w=0):
        para = self.fmt(self.p(), "l", left=LEFT + indent + num_w, right=RIGHT, first=-num_w, before=2, after=0,
                        line=1.15)
        ts = para.paragraph_format.tab_stops
        if num_w:
            ts.add_tab_stop(Twips(LEFT + indent + num_w))
        ts.add_tab_stop(Twips(LEFT + TEXT_W), WD_TAB_ALIGNMENT.RIGHT, WD_TAB_LEADER.DOTS)
        add_runs(para, f"{label}\t{text}\t{page}" if num_w else f"{text}\t{page}", size, bold)
        return para

    def title(self, text, pbb=True):
        para = self.fmt(self.p(), "c", before=0, after=14, pbb=pbb, line=1.2)
        add_runs(para, text, 16, True)


# ---- template editing helpers ------------------------------------------------
def replace_in_paragraph(p, old, new):
    runs = p.runs
    full = "".join(r.text for r in runs)
    if old not in full:
        return False
    pos = full.index(old)
    acc = 0
    first = True
    for r in runs:
        s, e = acc, acc + len(r.text)
        acc = e
        if e <= pos or s >= pos + len(old):
            continue
        a, b = max(pos, s) - s, min(pos + len(old), e) - s
        r.text = r.text[:a] + (new if first else "") + r.text[b:]
        first = False
    return True


def set_text(p, text, keep=0):
    """Set the paragraph's text in its first run (after `keep` runs), blank the rest."""
    runs = p.runs
    runs[keep].text = text
    for r in runs[keep + 1:]:
        r.text = ""


def rewrite(p, segments):
    """Replace runs with segments [(text, bold)], cloning the first run's formatting."""
    base = copy.deepcopy(p.runs[0]._r)
    for r in list(p.runs):
        r._r.getparent().remove(r._r)
    for text, bold in segments:
        r = copy.deepcopy(base)
        for t in r.findall(qn("w:t")):
            r.remove(t)
        for tag in ("w:lastRenderedPageBreak",):
            for x in r.findall(qn(tag)):
                r.remove(x)
        rpr = r.find(qn("w:rPr"))
        if rpr is not None:
            for tag in ("w:b", "w:bCs"):
                for x in rpr.findall(qn(tag)):
                    rpr.remove(x)
            if bold:
                rpr.append(OxmlElement("w:b"))
        t = OxmlElement("w:t"); t.text = text; t.set("{http://www.w3.org/XML/1998/namespace}space", "preserve")
        r.append(t)
        p._p.append(r)
