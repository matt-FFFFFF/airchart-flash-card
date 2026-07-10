# PROJECT KNOWLEDGE BASE

**Generated:** 2026-07-10
**Commit:** 3950878
**Branch:** main

## EVERGREEN DIRECTIVE

This file is the durable source of truth for working in this repo. Keep it evergreen:
after any change that alters structure, entry points, conventions, commands, or the card
pipeline, update the relevant section in the SAME change. State only what stays true across
commits — never transient status, TODOs, or dated notes. If a fact here contradicts the code,
the code wins: fix this file. Prune anything that drifts.

## OVERVIEW

Reproducible extractor that renders curated UK CAA airchart legend symbols from `legend.pdf`
into per-symbol PNGs + a `cards.json` manifest. Pure Python 3.13, PyMuPDF (native vector
render, not raster crop) + Pillow. Package: `legend_cards`.

## STRUCTURE

```
src/legend_cards/
├── generator.py         # entry point: generate() → PNGs + cards.json + contact sheet
├── object_renderer.py   # render one card by replaying selected PDF drawings/text spans
├── card_data.py         # CARDS data: hand-tuned bbox/exclusion/object specs per symbol
├── models.py            # CardSpec/BBox/ObjectSelection + card()/object_card() builders
└── specs.py             # stable re-export shim (CARDS, CardSpec) — E501/RUF001 exempt
legend.pdf               # immutable source (1 page, 595.22×842pt, vector/text, 0 images)
public/                  # generated deliverables (cards.json, symbols/*.png, contact-sheet.png)
tests/                   # test_extract_legend.py: runs real CLI entry point end-to-end
```

## WHERE TO LOOK

| Task | Location |
|------|----------|
| Add/fix a symbol crop | `card_data.py` — add a `_card(...)` or `_object_card(...)` to `CARDS` |
| Two render paths | `generator._render`: `spec.objects` set → `render_selected`; else bbox clip + `exclusions` whiteout |
| Manifest/JSON shape | `generator._record` + `CardRecord`/`SourceBBoxRecord` TypedDicts |
| Object-replay internals | `object_renderer.py` (`_draw_path` match on draw items, `_insert_selected_text`) |
| CLI wiring | `pyproject.toml` `[project.scripts]` `extract-legend = legend_cards.generator:main` |

## CODE MAP

| Symbol | Type | Location | Role |
|--------|------|----------|------|
| `generate` | func | generator.py:133 | Orchestrator: clears symbols dir, renders all `CARDS`, writes manifest + contact sheet |
| `main` | func | generator.py:163 | Entry point → `generate(legend.pdf, public)` |
| `render_selected` | func | object_renderer.py:115 | Native replay of selected drawings/text into a clipped pixmap |
| `CardSpec` | dataclass | models.py:28 | Frozen spec: id/definition/category/bbox/exclusions/objects |
| `CARDS` | Final tuple | card_data.py:9 | The curated dataset — single source of truth for every card |

## CONVENTIONS

- **Types are strict.** basedpyright `typeCheckingMode = "all"`; ruff `select = ["ALL"]`. No
  `Any`, no `# type: ignore` without cause (`reportUnnecessaryTypeIgnoreComment = "error"`).
- **Dataclasses are `frozen=True, slots=True`.** Model data is immutable; construct via
  `card()`/`object_card()`, never mutate `CardSpec`.
- **Ignored `Callable` results are explicit** — assign to `_` (PyMuPDF/`write_text` return values),
  because `reportUnusedCallResult = "warning"`.
- **`pymupdf`/`PIL` imported inside functions** (lazy), typed via `TYPE_CHECKING` at module top.
- **Google-style docstrings**; line length 100.

## ANTI-PATTERNS (THIS PROJECT)

- Do NOT raster-crop / rasterize with external tools (`sips` etc.) — root cause of the original
  black-background/blurry/offset bug. Render natively from PDF page-space coordinates only.
- Do NOT edit `public/` by hand — it is regenerated wholesale (`generate` deletes `symbols/`).
- Do NOT hand-edit generated `cards.json`; change `card_data.py` and regenerate.
- Do NOT treat one PDF path as one symbol — legend symbols are composite drawing+text clusters;
  use `ObjectSelection(drawing_indices, texts)` via `object_card`.

## COMMANDS

```bash
make setup      # uv sync --all-groups
make test       # ruff check . && basedpyright src tests && pytest -q
make generate   # uv run extract-legend  → regenerate public/ from legend.pdf
make build      # uv build (wheel + sdist)
```

## NOTES

- Requires Python `>=3.13,<3.14`. Contact sheet needs `/System/Library/Fonts/Supplemental/Arial.ttf` (macOS-specific).
- Coordinates in `card_data.py` are native PDF points on page 0; bbox drift = wrong crop.
- Tests exercise the real CLI via `subprocess` (`filterwarnings = ["error"]`), not internal functions.
