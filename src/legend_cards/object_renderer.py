"""Render cards from selected native PDF drawing and text objects."""

from __future__ import annotations

import json
from typing import TYPE_CHECKING, Literal, TypedDict

if TYPE_CHECKING:
    from pathlib import Path

    import pymupdf

    from legend_cards.models import CardSpec

type DrawItem = (
    tuple[Literal["l"], pymupdf.Point, pymupdf.Point]
    | tuple[Literal["re"], pymupdf.Rect, int]
    | tuple[Literal["qu"], pymupdf.Quad]
    | tuple[Literal["c"], pymupdf.Point, pymupdf.Point, pymupdf.Point, pymupdf.Point]
)


class DrawingPath(TypedDict):
    """PyMuPDF drawing fields consumed by native object replay."""

    items: list[DrawItem]
    fill: tuple[float, ...] | None
    color: tuple[float, ...] | None
    dashes: str
    even_odd: bool
    closePath: bool | None
    lineJoin: int | None
    lineCap: tuple[int, ...] | None
    width: float | None
    stroke_opacity: float | None
    fill_opacity: float | None


class _TextSpan(TypedDict):
    text: str
    bbox: tuple[float, float, float, float]
    origin: tuple[float, float]
    font: str
    size: float
    color: int


class _TextLine(TypedDict):
    spans: list[_TextSpan]


class _TextBlock(TypedDict, total=False):
    lines: list[_TextLine]


class _TextPage(TypedDict):
    blocks: list[_TextBlock]


def _draw_path(shape: pymupdf.Shape, drawing: DrawingPath) -> None:
    for item in drawing["items"]:
        match item:
            case ("l", start, end):
                _ = shape.draw_line(start, end)
            case ("re", rect, _):
                _ = shape.draw_rect(rect)
            case ("qu", quad):
                _ = shape.draw_quad(quad)
            case ("c", start, control_1, control_2, end):
                _ = shape.draw_bezier(start, control_1, control_2, end)
    shape.finish(
        fill=drawing["fill"],
        color=drawing["color"],
        dashes=drawing["dashes"],
        even_odd=drawing["even_odd"],
        closePath=drawing["closePath"] or False,
        lineJoin=drawing["lineJoin"] or 0,
        lineCap=max(drawing["lineCap"] or (0,)),
        width=drawing["width"] or 1,
        stroke_opacity=drawing["stroke_opacity"] or 1,
        fill_opacity=drawing["fill_opacity"] or 1,
    )


def _insert_selected_text(source: pymupdf.Page, target: pymupdf.Page, spec: CardSpec) -> None:
    import pymupdf

    selection = spec.objects
    if selection is None:
        return
    text_page: _TextPage = json.loads(json.dumps(source.get_text("dict")))
    for block in text_page["blocks"]:
        for line in block.get("lines", ()):
            for span in line["spans"]:
                selected = span["text"] in selection.texts
                x0, y0, x1, y1 = span["bbox"]
                inside_clip = (
                    x0 < spec.bbox.x1
                    and x1 > spec.bbox.x0
                    and y0 < spec.bbox.y1
                    and y1 > spec.bbox.y0
                )
                if not selected or not inside_clip:
                    continue
                _ = target.insert_text(
                    span["origin"],
                    span["text"],
                    fontsize=span["size"],
                    fontname="hebo",
                    color=pymupdf.sRGB_to_pdf(span["color"]),
                    overlay=True,
                )


def render_selected(page: pymupdf.Page, spec: CardSpec, path: Path, dpi: int) -> None:
    """Render only the exact source objects selected by a card specification."""
    import pymupdf

    selection = spec.objects
    if selection is None:
        return
    output = pymupdf.open()
    target = output.new_page(width=page.rect.width, height=page.rect.height)
    shape = target.new_shape()
    drawings: list[DrawingPath] = json.loads(
        json.dumps(page.get_drawings(), default=tuple)
    )
    for index in selection.drawing_indices:
        _draw_path(shape, drawings[index])
    shape.commit()
    _insert_selected_text(page, target, spec)
    clip = pymupdf.Rect(spec.bbox.x0, spec.bbox.y0, spec.bbox.x1, spec.bbox.y1)
    pixmap = target.get_pixmap(dpi=dpi, colorspace=pymupdf.csRGB, alpha=False, clip=clip)
    pixmap.set_dpi(dpi, dpi)
    pixmap.save(path)
    output.close()
