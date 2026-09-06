---
name: pdf
description: Read, create, or review PDF files when PDF extraction, font handling, or visual layout needs format-specific guidance.
---

# PDF

Use an available PDF library appropriate to the task: `reportlab` for generation, `pdfplumber` for extraction, or `pypdf` for structural edits. Prefer the workspace's bundled runtime and dependencies; install missing packages only when needed.

Text extraction does not establish visual fidelity. For layout changes, render affected pages and inspect the final result for clipping, overlaps, missing glyphs, and broken tables. Check document-wide pagination when the change can affect it. A text-only lookup does not require rendering every page.

With Poppler available:

```bash
pdftoppm -png "$INPUT_PDF" "$OUTPUT_PREFIX"
```

If the preferred renderer is unavailable, use another available renderer; report any unresolved visual verification limitation. Use fonts with the required character coverage, including CJK where needed, rather than restricting the document to ASCII.

Follow the current workspace's intermediate and final-output conventions. Keep citations readable and deliver the requested PDF with a usable link.
