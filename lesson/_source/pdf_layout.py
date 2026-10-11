"""Shared Vietnamese PDF layout helpers for topic-first study guides."""

from __future__ import annotations

import html
import re
from pathlib import Path

from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER, TA_LEFT
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle
from reportlab.lib.units import mm
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.platypus import (
    HRFlowable,
    KeepTogether,
    PageBreak,
    Paragraph,
    Preformatted,
    SimpleDocTemplate,
    Spacer,
    Table,
    TableStyle,
)


ROOT = Path(__file__).resolve().parents[2]
SOURCE = ROOT / "lesson" / "_source"
OUTPUT = ROOT / "lesson"
FONT_DIR = Path(r"C:\Windows\Fonts")
pdfmetrics.registerFont(TTFont("Arial", str(FONT_DIR / "arial.ttf")))
pdfmetrics.registerFont(TTFont("Arial-Bold", str(FONT_DIR / "arialbd.ttf")))
pdfmetrics.registerFont(TTFont("Consolas", str(FONT_DIR / "consola.ttf")))
pdfmetrics.registerFontFamily("Arial", normal="Arial", bold="Arial-Bold")

INK = colors.HexColor("#17324D")
BLUE = colors.HexColor("#1769A5")
LIGHT = colors.HexColor("#EAF2F8")
GRAY = colors.HexColor("#526374")

STYLES = {
    "cover": ParagraphStyle("Cover", fontName="Arial-Bold", fontSize=27, leading=35, textColor=INK, spaceAfter=20),
    "subcover": ParagraphStyle("SubCover", fontName="Arial", fontSize=12, leading=19, textColor=GRAY),
    "h2": ParagraphStyle("H2", fontName="Arial-Bold", fontSize=15, leading=21, textColor=INK, spaceBefore=18, spaceAfter=8, keepWithNext=True),
    "h3": ParagraphStyle("H3", fontName="Arial-Bold", fontSize=11.5, leading=16, textColor=BLUE, spaceBefore=12, spaceAfter=5, keepWithNext=True),
    "body": ParagraphStyle("Body", fontName="Arial", fontSize=10.1, leading=15.6, textColor=INK, spaceAfter=8),
    "bullet": ParagraphStyle("Bullet", fontName="Arial", fontSize=9.8, leading=15, leftIndent=15, firstLineIndent=-10, textColor=INK, spaceAfter=4),
    "table": ParagraphStyle("Table", fontName="Arial", fontSize=8.3, leading=11.3, textColor=INK),
    "code": ParagraphStyle("Code", fontName="Consolas", fontSize=7.1, leading=10, textColor=INK, leftIndent=8, rightIndent=5, spaceAfter=7),
    "small": ParagraphStyle("Small", fontName="Arial", fontSize=8.7, leading=12.4, textColor=GRAY, spaceAfter=5),
}


def safe(value: str) -> str:
    value = value.replace("\u2011", "-").replace("\u2013", "-").replace("\u2014", "-")
    value = html.escape(value)
    value = re.sub(
        r"\[([^\]]+)\]\((https?://[^)]+)\)",
        lambda match: f'<link href="{match.group(2)}" color="#11618E">{match.group(1)}</link>',
        value,
    )
    value = re.sub(r"`([^`]+)`", r'<font color="#11618E"><b>\1</b></font>', value)
    value = re.sub(r"\*\*([^*]+)\*\*", r"<b>\1</b>", value)
    return value


def code_block(lines: list[str]) -> list:
    # Keep long commands legible and within the page frame.
    wrapped = []
    for line in lines:
        while len(line) > 94:
            wrapped.append(line[:94])
            line = "    " + line[94:]
        wrapped.append(line)
    blocks = []
    for start in range(0, len(wrapped), 48):
        chunk = wrapped[start:start + 48]
        blocks.append(Table([[Preformatted("\n".join(chunk) or " ", STYLES["code"])]], colWidths=[168 * mm], style=TableStyle([
            ("BACKGROUND", (0, 0), (-1, -1), LIGHT),
            ("BOX", (0, 0), (-1, -1), .3, colors.HexColor("#C9DCEB")),
            ("LEFTPADDING", (0, 0), (-1, -1), 3 * mm),
            ("RIGHTPADDING", (0, 0), (-1, -1), 2 * mm),
            ("TOPPADDING", (0, 0), (-1, -1), 2 * mm),
            ("BOTTOMPADDING", (0, 0), (-1, -1), 2 * mm),
        ])))
    return blocks


def parse_markdown(content: str) -> list:
    story = []
    lines = content.splitlines()
    i = 0
    paragraph = []

    def flush():
        if paragraph:
            story.append(Paragraph(safe(" ".join(paragraph)), STYLES["body"]))
            paragraph.clear()

    while i < len(lines):
        line = lines[i]
        stripped = line.strip()
        if not stripped:
            flush()
            i += 1
            continue
        if stripped.startswith("```"):
            flush()
            i += 1
            block = []
            while i < len(lines) and not lines[i].strip().startswith("```"):
                block.append(lines[i])
                i += 1
            story.extend(code_block(block))
            i += 1
            continue
        if stripped.startswith("| ") and i + 1 < len(lines) and re.match(r"^\|[- :|]+\|$", lines[i + 1].strip()):
            flush()
            rows = []
            while i < len(lines) and lines[i].strip().startswith("|"):
                if not re.match(r"^\|[- :|]+\|$", lines[i].strip()):
                    cells = [Paragraph(safe(c.strip()), STYLES["table"]) for c in lines[i].strip().strip("|").split("|")]
                    rows.append(cells)
                i += 1
            if rows:
                width = 168 * mm / max(len(row) for row in rows)
                table = Table(rows, colWidths=[width] * len(rows), repeatRows=1, hAlign="LEFT")
                table.setStyle(TableStyle([
                    ("BACKGROUND", (0, 0), (-1, 0), LIGHT),
                    ("GRID", (0, 0), (-1, -1), .3, colors.HexColor("#C9DCEB")),
                    ("VALIGN", (0, 0), (-1, -1), "TOP"),
                    ("LEFTPADDING", (0, 0), (-1, -1), 5),
                    ("RIGHTPADDING", (0, 0), (-1, -1), 5),
                    ("TOPPADDING", (0, 0), (-1, -1), 5),
                    ("BOTTOMPADDING", (0, 0), (-1, -1), 5),
                ]))
                story.append(table)
                story.append(Spacer(1, 7))
            continue
        if stripped.startswith("# "):
            flush()
            i += 1
            continue
        if stripped.startswith("## "):
            flush()
            story.append(Paragraph(safe(stripped[3:]), STYLES["h2"]))
        elif stripped.startswith("### "):
            flush()
            story.append(Paragraph(safe(stripped[4:]), STYLES["h3"]))
        elif re.match(r"^(?:[-*] |\d+\. )", stripped):
            flush()
            item = re.sub(r"^(?:[-*] |\d+\. )", "", stripped)
            story.append(Paragraph("• " + safe(item), STYLES["bullet"]))
        else:
            paragraph.append(stripped)
        i += 1
    flush()
    return story


