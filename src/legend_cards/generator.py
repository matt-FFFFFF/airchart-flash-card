"""Render curated CAA legend symbols and publish their manifest."""

from __future__ import annotations

import json
import shutil
import textwrap
from dataclasses import dataclass
from pathlib import Path
from typing import TYPE_CHECKING, Final, TypedDict

from legend_cards.object_renderer import render_selected
from legend_cards.specs import CARDS, CardSpec

if TYPE_CHECKING:
    import pymupdf

DPI: Final = 600
CONTACT_WIDTH: Final = 1800
CELL_WIDTH: Final = 600
CELL_HEIGHT: Final = 270
CONTACT_FONT_PATH: Final = Path("/System/Library/Fonts/Supplemental/Arial.ttf")


class SourceBBoxRecord(TypedDict):
    """Serialized native PDF rectangle."""

    page: int
    x0: float
    y0: float
    x1: float
    y1: float


class CardRecord(TypedDict):
    """Public JSON card shape."""

    id: str
    definition: str
    category: str
    image: str
    source_pdf_bbox: SourceBBoxRecord


@dataclass(frozen=True, slots=True)
class RenderedCard:
    """A rendered symbol paired with its source specification."""

    spec: CardSpec
    path: Path


def _record(spec: CardSpec) -> CardRecord:
    return {
        "id": spec.id,
        "definition": spec.definition,
        "category": spec.category,
        "image": f"symbols/{spec.id}.png",
        "source_pdf_bbox": {
            "page": 0,
            "x0": spec.bbox.x0,
            "y0": spec.bbox.y0,
            "x1": spec.bbox.x1,
            "y1": spec.bbox.y1,
        },
    }


def _render(page: pymupdf.Page, spec: CardSpec, path: Path) -> RenderedCard:
    import pymupdf
    from PIL import Image, ImageDraw

    if spec.objects is not None:
        render_selected(page, spec, path, DPI)
        return RenderedCard(spec, path)
    clip = pymupdf.Rect(spec.bbox.x0, spec.bbox.y0, spec.bbox.x1, spec.bbox.y1)
    pixmap = page.get_pixmap(dpi=DPI, colorspace=pymupdf.csRGB, alpha=False, clip=clip)
    pixmap.set_dpi(DPI, DPI)
    pixmap.save(path)
    if spec.exclusions:
        scale = DPI / 72
        with Image.open(path) as source:
            image = source.copy()
        draw = ImageDraw.Draw(image)
        for exclusion in spec.exclusions:
            draw.rectangle(
                (
                    round((exclusion.x0 - spec.bbox.x0) * scale),
                    round((exclusion.y0 - spec.bbox.y0) * scale),
                    round((exclusion.x1 - spec.bbox.x0) * scale),
                    round((exclusion.y1 - spec.bbox.y0) * scale),
                ),
                fill="white",
            )
        image.save(path, dpi=(DPI, DPI))
    return RenderedCard(spec, path)


def _contact_sheet(cards: tuple[RenderedCard, ...], path: Path) -> None:
    from PIL import Image, ImageDraw, ImageFont

    rows = (len(cards) + 2) // 3
    sheet = Image.new("RGB", (CONTACT_WIDTH, rows * CELL_HEIGHT), "white")
    draw = ImageDraw.Draw(sheet)
    font = ImageFont.truetype(CONTACT_FONT_PATH, 20)
    label_font = ImageFont.truetype(CONTACT_FONT_PATH, 16)
    for index, card in enumerate(cards):
        column, row = index % 3, index // 3
        origin_x, origin_y = column * CELL_WIDTH, row * CELL_HEIGHT
        with Image.open(card.path) as source:
            symbol = source.copy()
        symbol.thumbnail((CELL_WIDTH - 40, 170), Image.Resampling.LANCZOS)
        symbol_x = origin_x + (CELL_WIDTH - symbol.width) // 2
        sheet.paste(symbol, (symbol_x, origin_y + 10))
        label = "\n".join(textwrap.wrap(card.spec.definition, width=48))
        draw.multiline_text(
            (origin_x + 16, origin_y + 184), label, fill="black", font=font, spacing=2
        )
        draw.text(
            (origin_x + 16, origin_y + 236),
            f"{card.spec.id} | {card.spec.category}",
            fill="#555555",
            font=label_font,
        )
        draw.rectangle(
            (origin_x, origin_y, origin_x + CELL_WIDTH - 1, origin_y + CELL_HEIGHT - 1),
            outline="#cccccc",
            width=2,
        )
    sheet.save(path, dpi=(150, 150))


def generate(pdf_path: Path, output_dir: Path) -> None:
    """Render all curated native PDF clips and their public metadata."""
    import pymupdf

    symbols_dir = output_dir / "symbols"
    if symbols_dir.exists():
        shutil.rmtree(symbols_dir)
    symbols_dir.mkdir(parents=True, exist_ok=True)
    with pymupdf.open(pdf_path) as document:
        page = document[0]
        rendered = tuple(_render(page, spec, symbols_dir / f"{spec.id}.png") for spec in CARDS)
    records = [_record(card.spec) for card in rendered]
    _ = (output_dir / "cards.json").write_text(
        json.dumps(
            {
                "provenance": (
                    "Civil Aviation Authority, Aeronautical Chart ICAO 1:500 000 legend, 2006"
                ),
                "source": pdf_path.name,
                "render_dpi": DPI,
                "cards": records,
            },
            indent=2,
        )
        + "\n",
        encoding="utf-8",
    )
    _contact_sheet(rendered, output_dir / "contact-sheet.png")


def main() -> None:
    """Generate the repository's public assets from legend.pdf."""
    generate(Path("legend.pdf"), Path("public"))
