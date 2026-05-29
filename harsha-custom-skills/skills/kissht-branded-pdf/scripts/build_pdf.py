#!/usr/bin/env python3
"""
Build a Kissht house-style PDF from a Markdown file.

Pipeline: Markdown -> pandoc (custom LaTeX template + Lua filter) -> xelatex -> PDF.

Usage:
  python3 build_pdf.py INPUT.md OUTPUT.pdf \
      --title "LAP Credit Policy" \
      --subtitle "How the automated decision engine works" \
      --tagline "BRE v0.2.200 - Live from 29 May 2026 - Plain-English explainer" \
      --footer "Source: Finbox BRE export LAP_BRE_POLICY v0.2.200" \
      --brand 1F4E79

Authoring conventions in the Markdown (see references/authoring.md):
  - `#` is reserved for nothing; use `##` for sections, `###` for sub-sections.
  - Callout boxes via fenced divs:
        ::: summary
        One-line takeaway.
        :::
        ::: note title="The exception"
        ...
        :::
        ::: warn title="1 - Watch this"
        ...
        :::
  - Tables get a shaded brand header automatically.
  - Use the rupee sign directly (Rs / the unicode glyph); it is rendered via a fallback font.

Dependencies: pandoc + a TeX install providing xelatex (texlive-xetex), the
Lato font (or pass --mainfont), and DejaVu Sans for the rupee glyph.
"""
import argparse
import os
import re
import shutil
import subprocess
import sys
import tempfile

HERE = os.path.dirname(os.path.abspath(__file__))
ASSETS = os.path.normpath(os.path.join(HERE, "..", "assets"))
TEMPLATE = os.path.join(ASSETS, "kissht.latex")
FILTER = os.path.join(ASSETS, "callouts.lua")

# Symbols xelatex's default math/mono fonts can't render -> safe ASCII.
REPLACE = {"≥": ">=", "≤": "<=", "≠": "!=", "→": "->",
           "⇒": "=>", "‘": "'", "’": "'", "“": '"', "”": '"'}
# Emoji / pictographs that break xelatex -> drop.
EMOJI = re.compile("[\U0001F000-\U0001FAFF☀-➿️⬀-⯿]")


def preflight():
    missing = [t for t in ("pandoc", "xelatex") if shutil.which(t) is None]
    if missing:
        sys.exit("ERROR: missing required tool(s): " + ", ".join(missing) +
                 "\nInstall pandoc and a TeX distribution with xelatex (e.g. texlive-xetex).")


def clean(md_text):
    for k, v in REPLACE.items():
        md_text = md_text.replace(k, v)
    return EMOJI.sub("", md_text)


def tex_escape(s):
    """Escape LaTeX specials in metadata values (title/subtitle/tagline/footer),
    which pandoc passes through to the template verbatim (NOT auto-escaped)."""
    s = clean(s)
    s = s.replace("\\", r"\textbackslash{}")
    for ch in "&%$#_{}":
        s = s.replace(ch, "\\" + ch)
    s = s.replace("~", r"\textasciitilde{}").replace("^", r"\textasciicircum{}")
    return s


def main():
    ap = argparse.ArgumentParser(description="Build a Kissht house-style PDF from Markdown.")
    ap.add_argument("input")
    ap.add_argument("output")
    ap.add_argument("--title", default="")
    ap.add_argument("--subtitle", default="")
    ap.add_argument("--tagline", default="")
    ap.add_argument("--footer", default="")
    ap.add_argument("--brand", default="1F4E79", help="brand colour as a 6-digit hex, no '#'")
    ap.add_argument("--mainfont", default="Lato")
    ap.add_argument("--margin", default="1.9cm")
    args = ap.parse_args()

    preflight()
    if not os.path.isfile(args.input):
        sys.exit(f"ERROR: input not found: {args.input}")

    with open(args.input, encoding="utf-8") as fh:
        body = clean(fh.read())

    with tempfile.NamedTemporaryFile("w", suffix=".md", delete=False, encoding="utf-8") as tmp:
        tmp.write(body)
        tmp_md = tmp.name

    cmd = [
        "pandoc", tmp_md, "-o", args.output,
        "--template", TEMPLATE, "--lua-filter", FILTER,
        "--pdf-engine", "xelatex", "--from", "markdown",
        "-V", f"brandcolor={args.brand}", "-V", f"mainfont={args.mainfont}",
        "-V", f"margin={args.margin}",
    ]
    for var, val in (("title", args.title), ("subtitle", args.subtitle),
                     ("tagline", args.tagline), ("footer", args.footer)):
        if val:
            cmd += ["-V", f"{var}={tex_escape(val)}"]

    try:
        subprocess.run(cmd, check=True)
    except subprocess.CalledProcessError as exc:
        sys.exit(f"ERROR: pandoc/xelatex failed (exit {exc.returncode}). "
                 "Run with the same args to see the LaTeX log.")
    finally:
        os.unlink(tmp_md)

    print(f"OK -> {args.output}")


if __name__ == "__main__":
    main()
