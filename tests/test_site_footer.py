from pathlib import Path
from typing import Final

INDEX_PATH: Final[Path] = Path("web/index.html")

def test_site_footer_contract() -> None:
    content = INDEX_PATH.read_text(encoding="utf-8")

    main_idx = content.find("</main>")
    footer_idx = content.find("<footer")
    assert main_idx != -1, "</main> not found"
    assert footer_idx > main_idx, "<footer> must follow </main>"

    footer_content = content[footer_idx : content.find("</footer>", footer_idx)]

    assert 'href="https://github.com/matt-FFFFFF/airchart-flash-card"' in footer_content
    assert 'target="_blank"' in footer_content
    assert 'rel="noopener noreferrer"' in footer_content
    assert "View source on GitHub" in footer_content
    assert "<svg" in footer_content
    assert 'aria-hidden="true"' in footer_content
    assert 'focusable="false"' in footer_content


def test_game_shortcuts_preserve_native_link_activation() -> None:
    script = Path("web/app.js").read_text(encoding="utf-8")

    assert "activeElement.matches('a, button, input')" in script
