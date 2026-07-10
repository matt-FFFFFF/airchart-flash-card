"""Typed card specification model and constructor."""

from dataclasses import dataclass
from typing import NewType

CardId = NewType("CardId", str)


@dataclass(frozen=True, slots=True)
class BBox:
    """Native PDF page-space rectangle in points."""

    x0: float
    y0: float
    x1: float
    y1: float


@dataclass(frozen=True, slots=True)
class ObjectSelection:
    """Exact source-page drawings and text spans used to render one card."""

    drawing_indices: tuple[int, ...]
    texts: tuple[str, ...]


@dataclass(frozen=True, slots=True)
class CardSpec:
    """Curated mapping from one legend definition to its canonical symbol."""

    id: CardId
    definition: str
    category: str
    bbox: BBox
    exclusions: tuple[BBox, ...] = ()
    objects: ObjectSelection | None = None


def card(
    identifier: str,
    definition: str,
    category: str,
    bbox: tuple[float, float, float, float],
    exclusions: tuple[tuple[float, float, float, float], ...] = (),
) -> CardSpec:
    """Construct a typed card specification from compact coordinate tuples."""
    return CardSpec(
        CardId(identifier),
        definition,
        category,
        BBox(*bbox),
        tuple(BBox(*exclusion) for exclusion in exclusions),
    )


def object_card(
    identifier: str,
    definition: str,
    category: str,
    bbox: tuple[float, float, float, float],
    objects: ObjectSelection,
) -> CardSpec:
    """Construct a card rendered from selected source objects."""
    return CardSpec(CardId(identifier), definition, category, BBox(*bbox), objects=objects)
