import json
import subprocess
import sys
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


@pytest.fixture(scope="module")
def generated(tmp_path_factory: pytest.TempPathFactory) -> tuple[Path, list[CardRecord]]:
    # Given: the immutable source PDF and an empty output directory.
    output = tmp_path_factory.mktemp("generated")

    # When: the public asset generator runs through its real entry point.
    _ = subprocess.run(
        [
            sys.executable,
            "-c",
            (
                "from pathlib import Path; "
                "from legend_cards.generator import generate; "
                f"generate(Path('legend.pdf'), Path(r'{output}'))"
            ),
        ],
        check=True,
    )

    # Then: return its observable manifest for focused contract assertions.
    manifest: Manifest = json.loads((output / "cards.json").read_text(encoding="utf-8"))
    return output, manifest["cards"]


def test_manifest_has_unique_ids_and_expected_minimum(
    generated: tuple[Path, list[CardRecord]],
) -> None:
    # Given: a generated card manifest.
    _, cards = generated

    # When: card identifiers are collected.
    identifiers = [card["id"] for card in cards]

    # Then: the curated set is substantial and collision-free.
    assert len(cards) >= 25
    assert len(identifiers) == len(set(identifiers))


def test_manifest_includes_canonical_navigation_aids(
    generated: tuple[Path, list[CardRecord]],
) -> None:
    # Given: the generated legend deck.
    _, cards = generated

    # When: canonical navigation-aid identifiers are collected.
    identifiers = {card["id"] for card in cards}

    # Then: each distinct native legend symbol has an individual card.
    assert {"vor", "dme", "vor-dme", "tacan", "ndb", "other-navigational-aids"} <= identifiers


def test_navigation_definitions_expand_abbreviations(
    generated: tuple[Path, list[CardRecord]],
) -> None:
    # Given: cards for the abbreviated radio navigation aids.
    _, cards = generated
    definitions = {card["id"]: card["definition"] for card in cards}

    # When: their public definitions are inspected.
    # Then: the source legend meanings are stated rather than only repeating abbreviations.
    assert definitions["vor"] == "VOR — VHF Omnidirectional Radio Range"
    assert definitions["dme"] == "DME — Distance Measuring Equipment"
    assert definitions["vor-dme"] == "Collocated, frequency-paired VOR/DME"
    assert definitions["tacan"] == "TACAN — UHF Tactical Air Navigation Aid"
    assert definitions["ndb"] == "NDB and NDB(L) — Non-Directional Radio Beacon"


def test_point_symbols_have_white_canvas_margins(
    generated: tuple[Path, list[CardRecord]],
) -> None:
    # Given: canonical point-symbol cards that previously touched their canvas edges.
    output, cards = generated
    from PIL import Image

    identifiers = {
        "vor",
        "dme",
        "vor-dme",
        "tacan",
        "ndb",
        "other-navigational-aids",
        "visual-reference-point",
        "atz",
        "matz",
        "scheduled-danger-area",
        "hirta",
    }

    # When: every outermost pixel is inspected.
    for card in cards:
        if card["id"] not in identifiers:
            continue
        with Image.open(output / card["image"]) as image:
            borders = (
                image.crop((0, 0, image.width, 1)),
                image.crop((0, image.height - 1, image.width, image.height)),
                image.crop((0, 0, 1, image.height)),
                image.crop((image.width - 1, 0, image.width, image.height)),
            )

        # Then: the complete geometry has visible white clearance on every side.
        assert all(
            border.getextrema() == ((255, 255), (255, 255), (255, 255))
            for border in borders
        ), card["id"]


def test_glider_cards_select_exact_native_objects() -> None:
    # Given: the three glider cards that share rows with neighboring symbols.
    from legend_cards.specs import CARDS

    selected = {
        str(card.id): card.objects
        for card in CARDS
        if str(card.id)
        in {"glider-additional-winch", "glider-additional-no-cables", "hang-para-winch"}
    }

    # When: their deterministic object selectors are inspected.
    selectors = {
        identifier: (selection.drawing_indices, selection.texts)
        for identifier, selection in selected.items()
        if selection is not None
    }

    # Then: only the intended native drawings and annotation spans are selected.
    assert selectors == {
        "glider-additional-winch": ((1,), ("G/2.5",)),
        "glider-additional-no-cables": ((3,), ("G",)),
        "hang-para-winch": ((4, 5), ("/2.5",)),
    }


def test_aerodrome_cards_select_complete_native_drawings() -> None:
    # Given: aerodrome symbols whose neighboring leader lines overlap their rows.
    from legend_cards.specs import CARDS

    selected = {
        str(card.id): card.objects.drawing_indices
        for card in CARDS
        if card.objects is not None
        and str(card.id)
        in {
            "aerodrome-government-civil",
            "aerodrome-government",
            "aerodrome-disused",
        }
    }

    # When: the source drawing selections are inspected.
    # Then: every complete symbol path is rendered without its leader line.
    assert selected == {
        "aerodrome-government-civil": (154, 155, 156),
        "aerodrome-government": (159, 160),
        "aerodrome-disused": (157, 158),
    }


def test_boundary_cards_select_complete_native_drawings() -> None:
    # Given: compound boundaries that touch neighboring labels in the source legend.
    from legend_cards.specs import CARDS

    identifiers = {"atz", "matz"}
    selected = {
        str(card.id): card.objects.drawing_indices
        for card in CARDS
        if card.objects is not None and str(card.id) in identifiers
    }

    # When: their native object selections are inspected.
    # Then: each complete boundary is replayed independently of nearby text.
    assert selected == {
        "atz": (147, 148),
        "matz": tuple(range(192, 207)),
    }


def test_beacon_cards_include_annotation_and_morse(
    generated: tuple[Path, list[CardRecord]],
) -> None:
    # Given: both operational aerodrome light beacon cards.
    output, cards = generated
    from PIL import Image

    beacons = [card for card in cards if card["id"].startswith("aerodrome-light-beacon")]

    # When: their generated image geometry is inspected.
    widths: list[int] = []
    for card in beacons:
        with Image.open(output / card["image"]) as image:
            widths.append(image.width)

    # Then: each crop spans the star, text, and Morse annotation—not only the star.
    assert len(beacons) == 2
    assert min(widths) >= 250


def test_beacon_definitions_name_flashing_colours(
    generated: tuple[Path, list[CardRecord]],
) -> None:
    # Given: the two aerodrome light beacon cards.
    _, cards = generated

    # When: their definitions are selected.
    definitions = {
        card["definition"] for card in cards if card["id"].startswith("aerodrome-light-beacon")
    }

    # Then: operational flashing colours replace print-production colour names.
    assert definitions == {
        "Aerodrome light beacon — flashing green",
        "Aerodrome light beacon — flashing red",
    }


def test_visual_reference_point_uses_generic_native_marker(
    generated: tuple[Path, list[CardRecord]],
) -> None:
    # Given: the visual reference point card.
    _, cards = generated
    card = next(card for card in cards if card["id"] == "visual-reference-point")

    # When: its source rectangle is inspected.
    clip = card["source_pdf_bbox"]

    # Then: it tightly encloses the generic circled-cross marker, not SANDBACH.
    assert clip == {"page": 0, "x0": 480.75, "y0": 224.35, "x1": 488.95, "y1": 232.6}


def test_contact_sheet_renders_unicode_labels(
    generated: tuple[Path, list[CardRecord]],
) -> None:
    # Given: the Unicode-capable font used by the generated contact sheet.
    _, _ = generated
    from PIL import ImageFont

    from legend_cards.generator import CONTACT_FONT_PATH

    # When: its em-dash glyph is rendered.
    font = ImageFont.truetype(CONTACT_FONT_PATH, 20)

    # Then: the font provides a real nonempty em-dash glyph.
    assert font.getmask("—").getbbox() is not None


def test_manifest_bboxes_are_valid_native_page_clips(
    generated: tuple[Path, list[CardRecord]],
) -> None:
    # Given: the source PDF's native page rectangle.
    _, cards = generated

    # When: every curated source rectangle is checked.
    clips = [card["source_pdf_bbox"] for card in cards]

    # Then: every tight clip lies on the sole, unrotated native page.
    assert all(clip["page"] == 0 for clip in clips)
    assert all(0 <= clip["x0"] < clip["x1"] <= 595.22 for clip in clips)
    assert all(0 <= clip["y0"] < clip["y1"] <= 842 for clip in clips)


def test_single_unlighted_obstacle_excludes_cable_symbol(
    generated: tuple[Path, list[CardRecord]],
) -> None:
    # Given: the curated single unlighted obstacle card.
    _, cards = generated
    card = next(card for card in cards if card["id"] == "obstacle-single-unlighted")

    # When: its native crop is inspected.
    clip = card["source_pdf_bbox"]

    # Then: it contains the annotation and triangular obstacle, ending before the cable drawing.
    assert clip == {"page": 0, "x0": 221.5, "y0": 518.5, "x1": 244.5, "y1": 535.5}
    from PIL import Image

    output, _ = generated
    with Image.open(output / card["image"]) as image:
        lower_right = image.crop((110, 92, image.width, image.height))
        assert lower_right.getbbox() is not None
        assert lower_right.getextrema() == ((255, 255), (255, 255), (255, 255))


def test_manifest_and_images_are_consistent(
    generated: tuple[Path, list[CardRecord]],
) -> None:
    # Given: a completed generation run.
    output, cards = generated

    # When: manifest paths and generated symbol files are compared.
    manifest_paths = {card["image"] for card in cards}
    image_paths = {f"symbols/{path.name}" for path in (output / "symbols").glob("*.png")}

    # Then: each card has exactly one image and no unreferenced image exists.
    assert manifest_paths == image_paths
    assert (output / "contact-sheet.png").is_file()


def test_public_assets_match_fresh_generation(
    generated: tuple[Path, list[CardRecord]],
) -> None:
    # Given: checked-in public assets and a fresh deterministic generation.
    output, _ = generated
    public = Path("public")
    expected = {
        path.relative_to(output): path.read_bytes()
        for path in output.rglob("*")
        if path.is_file()
    }
    actual = {
        path.relative_to(public): path.read_bytes()
        for path in public.rglob("*")
        if path.is_file()
    }

    # When: their complete file sets and bytes are compared.
    # Then: source specifications and published assets cannot silently drift apart.
    assert actual == expected


def test_generation_removes_stale_symbol_images(tmp_path: Path) -> None:
    # Given: an output directory containing an unmanifested malformed image.
    symbols = tmp_path / "symbols"
    symbols.mkdir()
    stale = symbols / "malformed-stale.png"
    _ = stale.write_bytes(b"stale")

    # When: the real generator publishes a fresh deck.
    _ = subprocess.run(
        [
            sys.executable,
            "-c",
            (
                "from pathlib import Path; "
                "from legend_cards.generator import generate; "
                f"generate(Path('legend.pdf'), Path(r'{tmp_path}'))"
            ),
        ],
        check=True,
    )

    # Then: stale symbol assets are removed before rendering.
    assert not stale.exists()


def test_symbol_images_are_opaque_rgb_white_backed_and_nonblank(
    generated: tuple[Path, list[CardRecord]],
) -> None:
    # Given: directly rendered card images.
    from PIL import Image, ImageChops

    output, cards = generated

    # When: their pixel contracts are inspected.
    with Image.open(output / cards[0]["image"]) as first:
        expected_dpi = first.info["dpi"]
    images = [Image.open(output / card["image"]) for card in cards]

    # Then: every crop is opaque RGB at 600 DPI, white-backed, and nonblank.
    try:
        assert expected_dpi == pytest.approx((600, 600), abs=0.1)
        assert all(image.mode == "RGB" for image in images)
        assert all((255, 255, 255) in image.get_flattened_data() for image in images)
        assert all(
            ImageChops.difference(image, Image.new("RGB", image.size, "white")).getbbox()
            for image in images
        )
    finally:
        for image in images:
            image.close()
