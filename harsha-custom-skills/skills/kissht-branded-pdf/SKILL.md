---
name: kissht-branded-pdf
description: >
  THE DEFAULT WAY TO CREATE ANY PDF at Kissht / Ring / LAP. Produces a polished, on-brand house-style
  PDF from Markdown or notes — branded title block, coloured section headings, shaded-header tables,
  and summary/note/warning callout boxes. Trigger this AUTOMATICALLY and PROACTIVELY, without waiting
  to be asked for "branding", whenever the user wants to produce a PDF or a shareable / printable /
  presentable document. This includes phrases like "create a PDF", "make a PDF", "generate a PDF",
  "export to PDF", "turn this into a PDF", "give me a PDF", "save this as a PDF", "PDF version",
  "make this a doc I can send on Slack / email / to leadership / to the team", "format this properly",
  "make it look good / cleaner / presentable", and any time the user hands over Markdown, notes, a
  report, an explainer, release notes, a one-pager, an FAQ, a policy or rule summary, or a memo and
  wants a finished document to share — even if they never say the words "branded" or "PDF" but clearly
  want a polished shareable document. When in doubt about producing a document for sharing, prefer this
  skill. Do NOT use it for reading, extracting text from, parsing, splitting, merging, or filling
  EXISTING PDF files — that is the generic pdf skill; this skill is ONLY for generating a new styled PDF
  from content.
---

# Kissht branded PDF

Produces a consistent, professional PDF from Markdown using a fixed house style, so every document
you hand out looks the same and reads cleanly. The styling is baked into a pandoc LaTeX template +
a Lua filter; you only supply content and a few metadata fields.

**This is the default PDF style for Kissht / Ring / LAP.** When someone asks for a PDF — to create,
generate, export, or "make this shareable" — don't produce a plain PDF; build it through this skill so
the output is on-brand and consistent. The only exception is reading/parsing/editing an *existing* PDF,
which belongs to the generic `pdf` skill.

## What the house style gives you

- A **title block**: bold brand-colour title, a plain subtitle, a grey tagline (version/date/audience), and a rule.
- **Section headings** in the brand colour with a thin underline; tight, readable lists.
- **Tables** with a shaded brand-tint header row (applied automatically).
- Three **callout boxes** for the things readers skim for: a `summary` (brand), a `note` (blue), and a `warn` (amber).
- A page **footer** (source line + page number) and the rupee glyph rendered correctly.

## How to use it

1. **Write the content as Markdown.** Use `##` for sections and `###` for sub-sections (the title comes from `--title`, so don't put a top-level `#`). Author callouts and tables using the conventions below. See `references/example.md` for a complete worked input.
2. **Run the build script:**

```bash
python3 scripts/build_pdf.py INPUT.md OUTPUT.pdf \
  --title "LAP Credit Policy" \
  --subtitle "How the automated decision engine works" \
  --tagline "BRE v0.2.200 · Live from 29 May 2026 · Plain-English explainer" \
  --footer "Source: Finbox BRE export LAP_BRE_POLICY v0.2.200" \
  --brand 1F4E79
```

All metadata flags are optional. `--brand` takes a 6-digit hex (no `#`); default is Kissht deep-blue `1F4E79`. To overwrite an existing PDF, just point `OUTPUT.pdf` at the same path — don't spawn a new filename unless the user asks.

3. **Verify before handing it over.** Render a page to PNG (`pdftoppm -png -r 110 OUTPUT.pdf /tmp/pg`) and look at it, so layout/glyph issues are caught before the user sees it.

## Authoring conventions

**Callout boxes** — fenced divs. The `title=` is optional (sensible defaults: "Summary" / "Note" / "Heads up"):

```markdown
::: summary
One-line takeaway readers should leave with.
:::

::: note title="The exception"
A clarification or important nuance.
:::

::: warn title="1 - Watch this"
A caveat, risk, or thing to confirm. Number them when you have several.
:::
```

**Tables** — ordinary Markdown pipe tables; the header row is shaded automatically. Keep them to 2–4 columns so they breathe on the page.

**Money** — type the rupee sign `₹` directly; it renders via a fallback font. Avoid other emoji/pictographs (🟢, ✅, etc.) — the build strips them so they don't break the PDF; use a `warn`/`note` box instead of an emoji to draw attention.

## When choosing metadata

- **title**: the document's name. **subtitle**: a one-line "what this is". **tagline**: version · date · audience.
- **footer**: where the content came from (source system, doc id) — it repeats on every page and is good provenance.
- Keep the title block to three lines; depth belongs in the body.

## Dependencies

Needs `pandoc` and `xelatex` (TeX with the xetex engine), the **Lato** font (or pass `--mainfont "Carlito"` / any installed sans), and **DejaVu Sans** for the ₹ glyph. The script checks for pandoc/xelatex and fails with a clear message if absent. In Cowork's sandbox these are already present; on a bare Mac, install via `brew install pandoc` and a TeX distribution (e.g. MacTeX / `brew install --cask mactex-no-gui`).

## Files

- `assets/kissht.latex` — the pandoc LaTeX template (fonts, palette, headings, footer, callout environments). Edit here to change the house style globally.
- `assets/callouts.lua` — maps callout divs to boxes and shades table headers.
- `scripts/build_pdf.py` — the wrapper you run.
- `references/example.md` — a complete example input; build it to see the style.
