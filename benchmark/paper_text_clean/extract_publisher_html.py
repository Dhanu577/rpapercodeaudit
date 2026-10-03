from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path
from typing import Iterable

from bs4 import BeautifulSoup, NavigableString, Tag


INCLUDED_SECTIONS = {
    "Abs1-section",
    "Sec1-section",
    "Sec2-section",
    "Sec17-section",
    "Sec18-section",
    "Sec33-section",
    "abbreviations-section",
    "Bib1-section",
    "Ack1-section",
    "additional-information-section",
    "Sec34-section",
}


def collapse_whitespace(text: str) -> str:
    return re.sub(r"\s+", " ", text.replace("\xa0", " ")).strip()


def text_from_node(node: Tag) -> str:
    """Flatten visible source text, using MathML token boundaries for readable math."""
    clone = BeautifulSoup(str(node), "html.parser")
    root = clone.find()
    if root is None:
        return ""
    for unwanted in root.find_all(["script", "style", "noscript"]):
        unwanted.decompose()
    for math in root.find_all("math"):
        math_text = collapse_whitespace(math.get_text(" ", strip=True))
        math.replace_with(f" {math_text} ")
    pieces: list[str] = []
    for item in root.descendants:
        if isinstance(item, NavigableString):
            parent = item.parent
            if parent and parent.name not in {"script", "style", "noscript"}:
                pieces.append(str(item))
    return collapse_whitespace("".join(pieces))


def figure_number(description: Tag) -> str:
    match = re.search(r"figure-(\d+)-desc", description.get("id", ""))
    if match:
        return match.group(1)
    figure = description.find_parent("figure")
    describedby = (figure.get("aria-describedby", "") if figure else "")
    match = re.search(r"figure-(\d+)-desc", describedby)
    if match:
        return match.group(1)
    return ""


def is_inside(node: Tag, class_name: str) -> bool:
    return node.find_parent(class_=lambda value: value and class_name in (value if isinstance(value, list) else str(value).split())) is not None


def section_blocks(section: Tag) -> Iterable[str]:
    content = section.select_one(":scope > .c-article-section__content")
    if content is None:
        content = section.select_one(".c-article-section__content")
    if content is None:
        return

    section_id = section.get("id", "")
    if section_id == "Bib1-section":
        bibliography = content.select("li.c-article-references__item")
        for number, item in enumerate(bibliography, 1):
            reference = item.select_one(".c-article-references__text")
            if reference:
                text = text_from_node(reference)
                if text:
                    yield f"{number}. {text}"
        return

    for node in content.find_all(True):
        classes = node.get("class", [])
        class_set = set(classes if isinstance(classes, list) else str(classes).split())
        if is_inside(node, "c-article-equation"):
            continue
        if is_inside(node, "c-article-section__figure-description"):
            continue
        if node.name in {"script", "style", "noscript"}:
            continue

        if "c-article-equation" in class_set:
            text = text_from_node(node)
            if text:
                yield text
            continue

        if "c-article-section__figure-description" in class_set:
            text = text_from_node(node)
            number = figure_number(node)
            if text:
                yield f"Figure {number}. {text}" if number else text
            continue

        if node.name in {"h3", "h4", "h5"}:
            text = text_from_node(node)
            if text:
                yield text
        elif node.name == "p":
            if node.find_parent("li"):
                continue
            text = text_from_node(node)
            if text:
                yield text
        elif node.name == "li":
            if node.find_parent("li"):
                continue
            text = text_from_node(node)
            if text:
                yield f"• {text}"


def extract(html_path: Path) -> tuple[str, dict[str, object]]:
    soup = BeautifulSoup(html_path.read_bytes(), "html.parser")
    root = soup.find(id="main-content")
    if root is None:
        raise ValueError("Publisher HTML does not contain the expected #main-content article root")

    def meta(name: str) -> list[str]:
        return [x.get("content", "") for x in soup.find_all("meta", attrs={"name": name}) if x.get("content")]

    title_tag = root.find("h1")
    title = text_from_node(title_tag) if title_tag else (meta("citation_title") or [""])[0]
    journal = (meta("citation_journal_title") or [""])[0]
    volume = (meta("citation_volume") or [""])[0]
    article_number = (meta("citation_firstpage") or [""])[0]
    doi = (meta("citation_doi") or [""])[0]
    authors = meta("citation_author")
    publication_date = (meta("citation_online_date") or meta("citation_publication_date") or [""])[0]
    publication_year = publication_date[:4] if publication_date else ""

    blocks = [title]
    publication_line = ", ".join(x for x in [journal, f"Volume {volume}, article {article_number} ({publication_year})" if volume and article_number else ""] if x)
    if publication_line:
        blocks.append(publication_line)
    if publication_date:
        blocks.append(f"Published: {publication_date}")
    if doi:
        blocks.append(f"DOI: {doi}")
    if authors:
        blocks.append("Authors: " + "; ".join(authors))

    selected = [
        section for section in root.select(".c-article-section")
        if section.get("id") in INCLUDED_SECTIONS
    ]
    section_count = 0
    reference_count = 0
    for section in selected:
        title_node = section.select_one(":scope > .c-article-section__title")
        section_title = text_from_node(title_node) if title_node else ""
        if section_title:
            blocks.append(section_title)
            section_count += 1
        section_id = section.get("id", "")
        section_content = section.select_one(":scope > .c-article-section__content")
        if section_id == "Bib1-section" and section_content:
            reference_count = len(section_content.select("li.c-article-references__item"))
        blocks.extend(section_blocks(section))

    output = "\n\n".join(collapse_whitespace(x) for x in blocks if collapse_whitespace(x)) + "\n"
    counts = {
        "section_headings": section_count,
        "figures_in_source_article_root": len(root.find_all("figure")),
        "figure_captions_extracted": len(root.select(".c-article-section__figure-description")),
        "display_equations_in_source_article_root": len(root.select(".c-article-equation")),
        "mathml_elements_in_source_article_root": len(root.find_all("math")),
        "html_tables_in_source_article_root": len(root.find_all("table")),
        "references_extracted": reference_count,
        "clean_text_characters": len(output),
        "clean_text_lines": len(output.splitlines()),
        "title": title,
        "journal": journal,
        "doi": doi,
        "publication_metadata": meta("citation_publication_date"),
        "author_metadata": authors,
    }
    return output, counts


def main() -> None:
    parser = argparse.ArgumentParser(description="Convert publisher-hosted DESeq2 paper HTML to plain text.")
    parser.add_argument("html", type=Path, help="Downloaded publisher article HTML")
    parser.add_argument("output", type=Path, help="Destination plain-text path")
    args = parser.parse_args()
    text, counts = extract(args.html)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(text, encoding="utf-8", newline="\n")
    print("\n".join(f"{key}: {value}" for key, value in counts.items()))


if __name__ == "__main__":
    main()
