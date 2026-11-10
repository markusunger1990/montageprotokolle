#!/usr/bin/env python3
"""Füllt montage/vorlage.pdf aus einer JSON-Datei.
Aufruf: python3 fill.py daten/<datei>.json  -> protokolle/<datei>.pdf
JSON-Felder (alle optional): projektname, auftragsnummer, kunde, montagedatum,
montageort, monteure, montagebeginn, montageende, arbeiten, hinweise,
funktionspruefung (true/false), abnahme_name, abnahme_datum, abnahme_bemerkungen,
unterschrift_name, unterschrift_funktion, unterschrift_datum
"""
import json, sys, io, os
from pypdf import PdfReader, PdfWriter
from reportlab.pdfgen import canvas
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont

BASE = os.path.dirname(os.path.abspath(__file__))
pdfmetrics.registerFont(TTFont("DV", "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"))
pdfmetrics.registerFont(TTFont("DVB", "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"))
W, H = 595.28, 841.89
F = "DV"

def y(top):  # pdfplumber-top -> reportlab-y
    return H - top

# Einzeilige Felder: (x, Linie_top, max_x)
SINGLE = {
    "projektname": (197, 186, 543), "auftragsnummer": (197, 202, 543),
    "kunde": (197, 218, 543), "montagedatum": (197, 234, 543),
    "montageort": (197, 249, 543), "monteure": (197, 265, 543),
    "montagebeginn": (197, 330, 300), "montageende": (378, 330, 543),
    "abnahme_name": (226, 569, 375), "abnahme_datum": (226, 585, 375),
    "unterschrift_name": (197, 681, 543), "unterschrift_funktion": (197, 696, 543),
    "unterschrift_datum": (197, 726, 543),
}
# Mehrzeilige Felder: Titel, Baselines (top), x/Breite der ersten Zeile, x/Breite Folgezeilen
MULTI = {
    "arbeiten": ("Beschreibung der ausgeführten Arbeiten", [374, 388, 402], (57, 484), (57, 484)),
    "hinweise": ("Hinweise / Auffälligkeiten", [471, 485, 499], (57, 484), (57, 484)),
    "abnahme_bemerkungen": ("Bemerkungen zur Abnahme", [597, 612, 626, 640], (226, 315), (57, 484)),
}

def wrap(txt, size, first_w, rest_w):
    out = []
    for para in txt.split("\n"):
        words, cur = para.split(), ""
        if not words: out.append(""); continue
        for wd in words:
            w_av = first_w if not out else rest_w
            t = (cur + " " + wd).strip()
            if pdfmetrics.stringWidth(t, F, size) <= w_av: cur = t
            else:
                out.append(cur); cur = wd
        out.append(cur)
    return out

def fit_single(c, text, x, top, xmax):
    size = 10
    while size > 6 and c.stringWidth(text, F, size) > xmax - x - 2:
        size -= 0.5
    c.setFont(F, size); c.drawString(x, y(top) + 2.5, text)

def main(path):
    d = json.load(open(path, encoding="utf-8"))
    buf = io.BytesIO(); c = canvas.Canvas(buf, pagesize=(W, H))
    c.setFillColorRGB(0.05, 0.15, 0.45)
    for k, (x, top, xmax) in SINGLE.items():
        if d.get(k): fit_single(c, str(d[k]), x, top, xmax)
    fp = d.get("funktionspruefung")
    if fp is not None:
        c.setFont("DVB", 10)
        c.drawCentredString(219.1 if fp else 267.5, y(551.2) + 1.5, "X")
    overflow = []
    for k, (title, bases, (x1, w1), (x2, w2)) in MULTI.items():
        txt = (d.get(k) or "").strip()
        if not txt: continue
        size = 9
        lines = wrap(txt, size, w1, w2)
        if len(lines) > len(bases):
            lines_full = wrap(txt, 10, 480, 480)
            overflow.append((title, lines_full))
            lines = wrap(txt, size, w1, w2)[:len(bases) - 1] + ["→ Fortsetzung siehe Anlage (Seite 2)"]
        c.setFont(F, size)
        for i, ln in enumerate(lines):
            c.drawString(x1 if i == 0 else x2, y(bases[i]) + 0.5, ln)
    c.showPage()
    if overflow:  # Anlage-Seite
        c.setFillColorRGB(0, 0, 0); c.setFont("DVB", 16); c.drawString(57, H - 80, "Montageprotokoll – Anlage")
        c.setFont(F, 9); c.drawString(57, H - 96, f"{d.get('projektname','')}  ·  Auftrag {d.get('auftragsnummer','')}  ·  {d.get('montagedatum','')}")
        cy = H - 130
        for title, lines in overflow:
            c.setFont("DVB", 11); c.drawString(57, cy, title + ":"); cy -= 16
            c.setFont(F, 10)
            for ln in lines:
                if cy < 60:
                    c.showPage(); cy = H - 60; c.setFont(F, 10)
                c.drawString(57, cy, ln); cy -= 13
            cy -= 12
        c.showPage()
    c.save(); buf.seek(0)
    ov = PdfReader(buf); tpl = PdfReader(os.path.join(BASE, "vorlage.pdf"))
    w = PdfWriter(); page = tpl.pages[0]; page.merge_page(ov.pages[0]); w.add_page(page)
    for p in ov.pages[1:]: w.add_page(p)
    out = os.path.join(BASE, "protokolle", os.path.splitext(os.path.basename(path))[0] + ".pdf")
    w.write(open(out, "wb")); print(out)

if __name__ == "__main__":
    main(sys.argv[1])
