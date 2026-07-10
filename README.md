# Airchart Legend Flashcards

Learn the UK CAA VFR chart legend (ICAO 1:500 000) as a flashcard game — see the
symbol, name what it means. It runs entirely in your browser and is published to
GitHub Pages.

**▶ Play it: https://matt-ffffff.github.io/airchart-flash-card/**

The symbol images and their definitions are generated straight from the official
`legend.pdf` by a small Python pipeline; the game is a static site layered on top.

---

## Playing the game

- **On load** the deck is shuffled and the first symbol is shown.
- **Multiple choice** — pick the correct definition from four options. Your score
  (`correct / answered`) is tracked, and a final score is shown at the end of the deck.
- **Answer only** — study mode: press **Reveal** to see the definition. No score is kept.
- **Reset** re-shuffles the deck and starts over. Switching mode also reshuffles and
  clears the score.
- **Keyboard:** `1`–`4` pick an option, `Space` / `Enter` reveals / advances.

No accounts, no tracking, nothing saved between visits.

---

## Project layout

```
legend.pdf                     # immutable source: the official CAA legend
src/legend_cards/              # Python extractor (PyMuPDF + Pillow)
public/                        # GENERATED assets — do not edit by hand
├── cards.json                 #   the deck: id, definition, category, image
├── symbols/*.png              #   one rendered symbol per card
└── contact-sheet.png
web/                           # AUTHORED flashcard app (this is the game)
├── index.html · styles.css · app.js
└── distractors.json           #   curated wrong answers for multiple-choice
scripts/build-site.sh          # assembles public/ + web/ into _site/ for deploy
.github/workflows/pages.yml    # deploys _site/ to GitHub Pages on push to main
tests/                         # pytest suites (asset pipeline + game data)
```

> `public/` is regenerated wholesale and is byte-locked by a test, so authored web
> files live in `web/` and are combined with `public/` only at build/deploy time.

---

## Running it locally

Requires Python `>=3.13,<3.14` and [`uv`](https://docs.astral.sh/uv/).

```bash
make setup      # install dependencies (uv sync)
make preview    # assemble the site into _site/ and serve at http://localhost:8000
make test       # ruff + basedpyright + pytest
```

Regenerate the card assets from the PDF (rarely needed):

```bash
make generate   # re-render public/ from legend.pdf
```

### Editing the game

- **UI / logic:** `web/index.html`, `web/styles.css`, `web/app.js`
- **Wrong-answer options:** `web/distractors.json` (≥10 plausible distractors per card;
  the multiple-choice mode picks 3 at random). It is locked by
  `tests/test_flashcard_data.py`, so keep it in sync with `public/cards.json`.

---

## Deployment

Every push to `main` triggers the **Deploy to GitHub Pages** Action, which runs
`scripts/build-site.sh` and publishes the assembled `_site/`.

**One-time setup:** in the repository's **Settings → Pages**, set **Source** to
**"GitHub Actions"**. After that, deployment is automatic.

---

## Credits

Symbols derived from the **Civil Aviation Authority, Aeronautical Chart ICAO
1:500 000 legend (2006)**. This project is for training/revision purposes and is not
an official navigation source — always use current, authoritative charts for flight.

---

## License

This project's source code is licensed under the **Mozilla Public License 2.0** — see
[`LICENSE`](LICENSE). The bundled `legend.pdf` and symbols derived from it remain
© Civil Aviation Authority; the MPL 2.0 grant covers this project's own code, not that
source material.
