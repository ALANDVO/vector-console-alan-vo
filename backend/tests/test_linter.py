import pytest
from app.services.linter import DiagramLinter

def test_linter_detects_fedropshadow_filters():
    svg_with_shadow = (
        '<svg viewBox="0 0 500 300">'
        '<defs><filter id="f"><feDropShadow dx="2" dy="2"/></filter></defs>'
        '<rect filter="url(#f)" x="10" y="10" width="100" height="50"/>'
        '</svg>'
    )
    report = DiagramLinter.lint_svg(svg_with_shadow)
    assert not report.is_compliant
    assert any(v.rule_id == "no-drop-shadows" for v in report.violations)

def test_linter_detects_css_box_shadow():
    svg_with_box_shadow = (
        '<svg viewBox="0 0 500 300">'
        '<style>rect { box-shadow: 2px 2px 4px rgba(0,0,0,0.5); }</style>'
        '<rect x="10" y="10" width="100" height="50"/>'
        '</svg>'
    )
    report = DiagramLinter.lint_svg(svg_with_box_shadow)
    assert not report.is_compliant
    assert any(v.rule_id == "no-drop-shadows" for v in report.violations)

def test_linter_checks_viewbox():
    svg_missing_viewbox = '<svg width="500" height="300"><rect x="0" y="0" width="50" height="50"/></svg>'
    report = DiagramLinter.lint_svg(svg_missing_viewbox)
    assert any(v.rule_id == "valid-viewbox" for v in report.violations)

def test_linter_clean_editorial_svg_passes():
    clean_svg = (
        '<svg viewBox="0 0 800 600" class="editorial-diagram">'
        '<style>.mono { font-family: ui-monospace; }</style>'
        '<rect x="20" y="20" width="200" height="100" fill="#f8fafc" stroke="#0284c7" stroke-width="1.5"/>'
        '<text x="30" y="50" class="mono">Cluster Latency 12.4ms</text>'
        '</svg>'
    )
    report = DiagramLinter.lint_svg(clean_svg)
    assert report.is_compliant
    assert report.score == 100.0
