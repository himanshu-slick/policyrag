"""Split a policy PDF into section chunks carrying doc, section and page metadata."""
import re
from dataclasses import dataclass
from pathlib import Path

from pypdf import PdfReader

HEADING = re.compile(r"^(\d+)\.\s+(\S.*)$")
CLAUSE = re.compile(r"^\d+\.\d+\s")
MAX_CHARS = 1500


@dataclass
class Chunk:
    doc: str
    title: str
    section_no: int
    section: str
    page: int
    content: str

    @property
    def search_text(self) -> str:
        return f"{self.title}. {self.section}. {self.content}"


def _lines(path: Path):
    for page_no, page in enumerate(PdfReader(path).pages, 1):
        for line in (page.extract_text() or "").splitlines():
            if line.strip():
                yield page_no, line.strip()


def _join(lines: list[str]) -> str:
    """Re-join wrapped lines so each clause is one paragraph."""
    paras: list[str] = []
    for line in lines:
        if CLAUSE.match(line) or not paras:
            paras.append(line)
        else:
            paras[-1] += " " + line
    return "\n".join(paras)


def _split_long(text: str) -> list[str]:
    parts, current = [], ""
    for para in text.split("\n"):
        if current and len(current) + len(para) > MAX_CHARS:
            parts.append(current)
            current = ""
        current += ("\n" if current else "") + para
    return parts + [current]


def parse_pdf(path: Path) -> list[Chunk]:
    doc, title = path.stem, None
    heads: list[tuple[int, str, int, list[str]]] = []
    for page_no, line in _lines(path):
        match = HEADING.match(line)
        if title is None:
            title = line
        elif match:
            heads.append((int(match[1]), match[2], page_no, []))
        elif heads:
            heads[-1][3].append(line)
    return [
        Chunk(doc, title or doc, no, name, page, piece)
        for no, name, page, lines in heads
        for piece in _split_long(_join(lines))
    ]
