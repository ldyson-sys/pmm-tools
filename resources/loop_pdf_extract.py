#!/usr/bin/env python3
"""
Extract release-notes content from a Loop page PDF export.

Usage:
  python3 resources/loop_pdf_extract.py "~/Downloads/2026 M6.pdf" output/2026-06-release/

Why a PDF instead of scraping the live Loop page:
  Loop's web canvas virtualizes content (only the visible slice is in the DOM) and
  its feature headings are not semantic HTML, which makes live scraping slow, lossy,
  and unreliable for image->feature mapping. The PDF export (File > Export, or the
  browser's Print > Save as PDF) is a complete, stable snapshot: full-resolution
  images, all text in document order, and exact layout positions.

What it does:
  1. Writes the full text of every page to <out>/loop_text.txt (read this to author
     the assets: feature names, Edition, Area, What's new / Why it matters /
     How it works, and image captions).
  2. Extracts every CONTENT image to <out>/images/raw/NN.png in document order,
     skipping the repeated page-background/watermark images and tiny icons (emoji).
  3. Writes <out>/images/raw/_image_context.json mapping each NN.png to its page,
     vertical position, and the nearest text line above it (its caption/heading) so
     images are mapped to the feature they sit under, NOT by raw index.

Requires: pymupdf  (pip install pymupdf)
"""
import json, os, sys
from pathlib import Path
import fitz  # pymupdf


def main():
    if len(sys.argv) < 3:
        raise SystemExit("usage: loop_pdf_extract.py <loop.pdf> <output/YYYY-MM-release/>")
    pdf_path = Path(os.path.expanduser(sys.argv[1])).resolve()
    out = Path(sys.argv[2]).resolve()
    raw = out / "images" / "raw"
    raw.mkdir(parents=True, exist_ok=True)

    doc = fitz.open(pdf_path)

    # Identify repeated page-chrome images: same xref appearing on most pages.
    xref_pages = {}
    for pi in range(doc.page_count):
        for info in doc[pi].get_image_info(xrefs=True):
            if info.get("xref"):
                xref_pages.setdefault(info["xref"], set()).add(pi)
    chrome = {x for x, pages in xref_pages.items() if len(pages) > doc.page_count // 2}

    # Dump full text.
    parts = [f"\n===== PAGE {pi+1} =====\n" + doc[pi].get_text() for pi in range(doc.page_count)]
    (out / "loop_text.txt").write_text("".join(parts))

    # Extract content images in document order, with the nearest preceding text line.
    ctx, n = [], 0
    for pi in range(doc.page_count):
        page = doc[pi]
        lines = []
        for b in page.get_text("dict")["blocks"]:
            if b["type"] == 0:
                t = " ".join(s["text"] for l in b["lines"] for s in l["spans"]).strip()
                if t:
                    lines.append((b["bbox"][1], t))
        infos = sorted(page.get_image_info(xrefs=True), key=lambda i: i["bbox"][1])
        for info in infos:
            xref = info.get("xref")
            x0, y0, x1, y1 = info["bbox"]
            w, h = x1 - x0, y1 - y0
            if not xref or xref in chrome:
                continue
            if w < 40 or h < 40:                       # emoji / icon
                continue
            if h >= 700:                               # full-page background
                continue
            d = doc.extract_image(xref)
            n += 1
            fn = f"{n:02d}.{d['ext']}"
            (raw / fn).write_bytes(d["image"])
            preceding = ""
            for ly, lt in lines:
                if ly <= y0 + 2:
                    preceding = lt
            ctx.append({"file": fn, "page": pi + 1, "y": round(y0),
                        "native": f"{d['width']}x{d['height']}", "preceding_text": preceding[:120]})

    (raw / "_image_context.json").write_text(json.dumps(ctx, indent=2))
    print(f"Text   -> {out/'loop_text.txt'}")
    print(f"Images -> {raw}  ({n} content images)")
    print(f"Context-> {raw/'_image_context.json'}")
    print("Map each image to the feature whose section its page/preceding_text falls under — not by raw index.")


if __name__ == "__main__":
    main()
