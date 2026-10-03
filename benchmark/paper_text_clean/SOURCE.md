# Clean paper text: source and extraction record

## Confirmed paper identity

Before searching, the existing `examples/deseq2/DESeq.txt` identified the paper as **“Moderated estimation of fold change and dispersion for RNA-seq data with DESeq2”**, published in *Genome Biology* (2014), volume 15, article 550, DOI `10.1186/s13059-014-0550-8`.

## Selected source

- **Source type:** Publisher-hosted open-access full-text HTML, Version of Record.
- **Exact URL:** <https://link.springer.com/article/10.1186/s13059-014-0550-8>
- **Publisher article date:** 2014-12-05.
- **Retrieved:** 2026-10-03.
- **HTTP result:** Successful final `200 text/html; charset=utf-8` response after redirects.
- **Retrieval tool:** `curl 8.5.0`, HTTPS GET with redirect following (`-L`). The downloaded publisher HTML was 741,161 bytes; its SHA-256 was `f440ab5b3a9dd3e67f3b58e9ec4d8f8e80e2e2e15be6e765fabefebd179ed9df`.

The publisher page was available and supplied the article body with intact prose spacing and paragraph boundaries, so the PMC/PDF fallback routes were not used.

## Conversion and pipeline format

- **Conversion script:** `extract_publisher_html.py` (committed with this text).
- **Runtime/tool versions:** Python `3.12.3`; BeautifulSoup `4.15.0`; parser `html.parser` from Python’s standard library.
- **Input root:** Publisher article HTML element `#main-content`.
- **Output:** `paper_clean.txt`, UTF-8 plain text with blank-line-separated headings and text blocks. This matches the pipeline input contract: `run_pipeline` reads the paper via `Path.read_text(encoding="utf-8")` and passes the resulting string directly to extraction.
- **Extraction policy:** Uses the publisher’s article metadata, section headings, prose paragraphs, list items, figure-caption descriptions, display-equation text and reference-entry text. HTML whitespace is collapsed to ordinary text spacing; MathML token text is separated with spaces when flattened. No model output was used and no prose was manually edited, repaired, or matched to proposals.

## Article material represented

- The abstract, main article sections, abbreviations, acknowledgements and article information are included.
- The publisher HTML contains **9 figure captions**, all retained with figure numbers.
- The publisher HTML contains **30 display-equation blocks** and **100 MathML elements**. Equation markup is rendered as readable plain-text tokens; mathematical layout is not represented as graphical typesetting.
- The publisher article body has **no HTML table elements**. Table references in the article text remain; supplementary files (including supplementary tables) are linked but are not embedded in this plain-text extraction.
- The publisher reference section is included with **66 numbered entries**.
- Publisher navigation, recommendation widgets, author-profile controls and non-article promotional material are excluded. The linked supplementary PDF itself is not included.

## Differences from the old text

The old file `examples/deseq2/DESeq.txt` was not changed or overwritten. It is the supplied PDF-derived text: 95,675 characters and 1,919 lines, with PDF page/header artifacts and frequent fused or split words. It includes a References section numbered through 66, figure-caption text, table references, and equations split across extracted lines; it also contains publisher promotional text after the references.

The new publisher-derived text is 96,611 characters and 571 lines. It also includes the References section and all 66 reference entries and retains the 9 figure captions. Unlike the PDF text, it comes from structured publisher HTML with paragraph boundaries and MathML equation elements. It contains table references but no standalone table cells; the supplementary files are not embedded. The output excludes unrelated publisher page controls and the old text’s post-reference promotional footer. The primary intended difference is source-derived paragraph/spacing quality, not a change to any validator or saved proposal.
