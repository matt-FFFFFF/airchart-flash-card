"""Lock ``web/distractors.json`` against the published ``public/cards.json`` deck.

These contract tests guard the multiple-choice flashcard game: every generated
card must own an authored distractor pool that is large enough, duplicate-free,
free of its own answer, and backed by a real symbol image on disk.
"""

import json
from pathlib import Path
from typing import TypedDict

import pytest


class SourceBBox(TypedDict):
    page: int
    x0: float
    y0: float
    x1: float
    y1: float


class CardRecord(TypedDict):
    id: str
    definition: str
    category: str
    image: str
    source_pdf_bbox: SourceBBox


class Manifest(TypedDict):
    provenance: str
    source: str
    render_dpi: int
    cards: list[CardRecord]


MINIMUM_DISTRACTORS = 10


@pytest.fixture(scope="module")
def cards() -> list[CardRecord]:
    """Return the published card manifest records."""
    text = Path("public/cards.json").read_text(encoding="utf-8")
    manifest: Manifest = json.loads(text)
    return manifest["cards"]


@pytest.fixture(scope="module")
def distractors() -> dict[str, list[str]]:
    """Return the authored distractor pools keyed by card id."""
    text = Path("web/distractors.json").read_text(encoding="utf-8")
    pools: dict[str, list[str]] = json.loads(text)
    return pools


def test_distractor_keys_exactly_match_card_ids(
    cards: list[CardRecord],
    distractors: dict[str, list[str]],
) -> None:
    """Distractor keys mirror the manifest card ids with no gaps or extras."""
    # Given: the published card ids.
    card_ids = {card["id"] for card in cards}

    # When/Then: the distractor keys coincide exactly with the card ids.
    assert set(distractors) == card_ids


def test_each_pool_offers_at_least_ten_distractors(
    distractors: dict[str, list[str]],
) -> None:
    """Every card exposes at least ten distractor options."""
    # When: pools with fewer than the minimum number of entries are collected.
    undersized = {
        card_id: len(pool)
        for card_id, pool in distractors.items()
        if len(pool) < MINIMUM_DISTRACTORS
    }

    # Then: no pool is undersized.
    assert undersized == {}


def test_pools_have_no_normalized_duplicates(
    distractors: dict[str, list[str]],
) -> None:
    """Normalized distractors are unique and still number at least ten."""
    # When: pools whose normalized entries collide or fall short are collected.
    offenders = {
        card_id: pool
        for card_id, pool in distractors.items()
        if len({entry.strip().casefold() for entry in pool}) != len(pool)
        or len({entry.strip().casefold() for entry in pool}) < MINIMUM_DISTRACTORS
    }

    # Then: every pool is duplicate-free with a full complement of options.
    assert offenders == {}


def test_distractors_never_repeat_their_definition(
    cards: list[CardRecord],
    distractors: dict[str, list[str]],
) -> None:
    """No distractor restates its own card's definition after normalization."""
    # Given: each card's normalized correct definition.
    answers = {card["id"]: card["definition"].strip().casefold() for card in cards}

    # When: distractors matching their own answer are collected.
    leaks = {
        card_id: [entry for entry in pool if entry.strip().casefold() == answers[card_id]]
        for card_id, pool in distractors.items()
        if any(entry.strip().casefold() == answers[card_id] for entry in pool)
    }

    # Then: no pool leaks its own answer.
    assert leaks == {}


def test_every_distractor_is_a_nonempty_string(
    distractors: dict[str, list[str]],
) -> None:
    """Every distractor entry is a non-empty string after stripping whitespace."""
    # When: pools containing an empty or whitespace-only entry are collected.
    blanks = {
        card_id: pool
        for card_id, pool in distractors.items()
        if not all(entry.strip() for entry in pool)
    }

    # Then: no pool contains an empty string.
    assert blanks == {}


def test_every_card_image_exists_on_disk(
    cards: list[CardRecord],
) -> None:
    """Every manifest image path resolves to a file under public/."""
    # Given: the published images root.
    root = Path("public")

    # When: manifest images with no backing file are collected.
    missing = [card["id"] for card in cards if not (root / card["image"]).is_file()]

    # Then: every card image exists on disk.
    assert missing == []
