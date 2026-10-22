"""La demo analiza imágenes sin exigir configuración de zonas."""

from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


def test_frontend_has_no_zone_configuration():
    html = (ROOT / "frontend/index.html").read_text(encoding="utf-8")
    script = (ROOT / "frontend/app.js").read_text(encoding="utf-8")

    for marker in ('id="zones-view"', 'id="analysis-zone"', 'id="metric-zones"',
                   'data-route="zones"', 'id="dashboard-zones"'):
        assert marker not in html
    assert "state.zones" not in script
    assert "data.append('threshold',30)" in script
