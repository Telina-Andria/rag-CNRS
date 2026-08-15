"""
Heuristique de decoupage "heading-based" pour du texte libre (PDF/HTML) sans
rubriques explicitement balisees a l'extraction.

Deux methodes de detection de titres, essayees dans l'ordre :
1. "allcaps"     : lignes tout en MAJUSCULES (>= 3 dans le document), motif
                   frequent dans les documents avec une vraie mise en page
                   (ex: guide_candidat.json, titres du sommaire).
2. "shorttitle"  : ligne courte, sans ponctuation finale de phrase, suivie
                   d'une ligne longue (paragraphe). Motif frequent dans les
                   pages web exportees en PDF (ex: accompagnement.json,
                   avantages.json).

Si aucune des deux ne produit un decoupage de confiance suffisante, on
retombe sur un chunk par page ("page" en tant que methode).
"""

import re

DATE_RE = re.compile(r"^\d{1,2}/\d{1,2}/\d{4}\s+\d{1,2}:\d{2}$")
PAGEFRAC_RE = re.compile(r"^\d+\s*/\s*\d+$")
CTA_RE = re.compile(
    r"^(D[ée]couvrir|En savoir plus|Consulter|Voir plus|T[ée]l[ée]charger)\b",
    re.IGNORECASE,
)

MIN_AVG_BODY_LEN = 80  # en dessous, la detection "shorttitle" est jugee peu fiable


def _is_boilerplate_line(line):
    s = line.strip()
    if not s:
        return True
    if DATE_RE.match(s) or PAGEFRAC_RE.match(s):
        return True
    if s.lower().startswith("http"):
        return True
    if CTA_RE.match(s):
        return True
    return False


def clean_pages(pages):
    """pages: liste de {"page_num":.., "text":..} (une ligne de PDF par ligne
    de "text"). Retire le bruit recurrent (header/footer repete sur plus de
    la moitie des pages, dates, fractions de page, liens/CTA) et retourne une
    liste plate de (ligne, page_num)."""
    n = len(pages)
    page_lines = []
    counts = {}
    for p in pages:
        lines = [l.strip() for l in p["text"].split("\n") if l.strip()]
        page_lines.append(lines)
        for l in set(lines):
            counts[l] = counts.get(l, 0) + 1

    threshold = max(1, n // 2) if n > 1 else float("inf")
    boilerplate = {l for l, c in counts.items() if c > threshold}

    result = []
    for p, lines in zip(pages, page_lines):
        for l in lines:
            if l in boilerplate or _is_boilerplate_line(l):
                continue
            result.append((l, p["page_num"]))
    return result


def _is_allcaps_heading(line):
    s = line.strip()
    if not (3 <= len(s) <= 80):
        return False
    letters = [c for c in s if c.isalpha()]
    if len(letters) < 2:
        return False
    return all(c.isupper() for c in letters)


def _is_shorttitle_heading(line, next_line):
    s = line.strip()
    if not (3 <= len(s) <= 60):
        return False
    if s[-1] in ".,;:":
        return False
    if len(s.split()) > 8:
        return False
    if not s[0].isupper():
        return False
    if next_line is None:
        return False
    return len(next_line.strip()) >= 60


def _build_sections(lines_with_pages, flags):
    """Regroupe les lignes en sections (heading, body, page_start, page_end)
    en fusionnant les lignes-titres consecutives (titre sur plusieurs lignes
    physiques)."""
    n = len(lines_with_pages)
    sections = []
    i = 0
    current_heading = None
    current_body_lines = []
    current_pages = []

    def flush():
        if current_heading is not None or current_body_lines:
            body = "\n".join(current_body_lines).strip()
            if body:
                pages = [p for p in current_pages if p is not None]
                sections.append(
                    {
                        "heading": current_heading,
                        "body": body,
                        "page_start": min(pages) if pages else None,
                        "page_end": max(pages) if pages else None,
                    }
                )

    while i < n:
        if flags[i]:
            heading_parts = [lines_with_pages[i][0]]
            j = i + 1
            while j < n and flags[j]:
                heading_parts.append(lines_with_pages[j][0])
                j += 1
            flush()
            current_heading = " ".join(heading_parts)
            current_body_lines = []
            current_pages = []
            i = j
        else:
            line, page = lines_with_pages[i]
            current_body_lines.append(line)
            current_pages.append(page)
            i += 1
    flush()
    return sections


def _page_fallback(lines_with_pages):
    by_page = {}
    order = []
    for line, page in lines_with_pages:
        if page not in by_page:
            by_page[page] = []
            order.append(page)
        by_page[page].append(line)
    sections = []
    for page in order:
        body = "\n".join(by_page[page]).strip()
        if not body:
            continue
        sections.append(
            {
                "heading": f"Page {page}" if page is not None else None,
                "body": body,
                "page_start": page,
                "page_end": page,
            }
        )
    return sections


def heading_chunk(lines_with_pages):
    """lines_with_pages: liste de (ligne_de_texte, page_num_ou_None).
    Retourne (sections, methode) avec methode in {"allcaps", "shorttitle", "page"}."""
    n = len(lines_with_pages)
    if n == 0:
        return [], "page"

    lines = [l for l, _ in lines_with_pages]

    allcaps_flags = [_is_allcaps_heading(l) for l in lines]
    if sum(allcaps_flags) >= 3:
        return _build_sections(lines_with_pages, allcaps_flags), "allcaps"

    short_flags = [
        _is_shorttitle_heading(lines[i], lines[i + 1] if i + 1 < n else None) for i in range(n)
    ]
    sections = _build_sections(lines_with_pages, short_flags)
    if sections:
        avg_body_len = sum(len(s["body"]) for s in sections) / len(sections)
        if avg_body_len >= MIN_AVG_BODY_LEN:
            return sections, "shorttitle"

    return _page_fallback(lines_with_pages), "page"
