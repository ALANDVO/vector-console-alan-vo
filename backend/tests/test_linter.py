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
def test_linter_detects_paas_in_subnet_via_zone_id():
    """PaaS services placed in a subnet zone (snet abbreviation) must be flagged."""
    svg_with_paas = (
        '<svg viewBox="0 0 500 300">'
        '<rect data-azure-node="sql-1" data-azure-service="azure_sql" data-azure-zone="snet-app" x="20" y="20" width="100" height="50"/>'
        '<rect data-azure-node="st-1" data-azure-service="storage_account" data-azure-zone="snet-data" x="20" y="80" width="100" height="50"/>'
        '</svg>'
    )
    report = DiagramLinter.lint_svg(svg_with_paas)
    assert not report.is_compliant
    paas_violations = [v for v in report.violations if v.rule_id == "azure-paas-containment"]
    assert len(paas_violations) == 2


def test_linter_detects_all_paas_services_in_subnet():
    """All 5 PaaS services must be flagged when placed in subnet zones."""
    paas_services = ["azure_sql", "key_vault", "storage_account", "cosmos_db", "event_hub"]
    svg_parts = ['<svg viewBox="0 0 500 500">']
    for i, svc in enumerate(paas_services):
        y = 20 + i * 60
        svg_parts.append(
            f'<rect data-azure-node="{svc}-1" data-azure-service="{svc}" '
            f'data-azure-zone="snet-{svc}" x="20" y="{y}" width="100" height="50"/>'
        )
    svg_parts.append('</svg>')
    svg_with_all_paas = ''.join(svg_parts)

    report = DiagramLinter.lint_svg(svg_with_all_paas)
    assert not report.is_compliant
    paas_violations = [v for v in report.violations if v.rule_id == "azure-paas-containment"]
    assert len(paas_violations) == 5
    detected_services = {v.target.split('-')[0] for v in paas_violations}
    assert detected_services == set(paas_services)
def test_linter_detects_paas_in_subnet_via_zone_tier():
    """PaaS services in zones marked with data-azure-zone-tier=subnet must be flagged."""
    svg_with_paas = (
        '<svg viewBox="0 0 500 300">'
        '<rect data-azure-node="kv-1" data-azure-service="key_vault" data-azure-zone="kv-zone" data-azure-zone-tier="subnet" x="20" y="20" width="100" height="50"/>'
        '</svg>'
    )
    report = DiagramLinter.lint_svg(svg_with_paas)
    assert not report.is_compliant
    assert any(v.rule_id == "azure-paas-containment" for v in report.violations)

def test_linter_passes_paas_in_resource_group():
    """PaaS services correctly placed in a resource group zone must pass."""
    svg_clean = (
        '<svg viewBox="0 0 500 300">'
        '<rect data-azure-node="sql-1" data-azure-service="azure_sql" data-azure-zone="rg-core" data-azure-zone-tier="resource_group" x="20" y="20" width="100" height="50"/>'
        '</svg>'
    )
    report = DiagramLinter.lint_svg(svg_clean)
    assert report.is_compliant
    assert not any(v.rule_id == "azure-paas-containment" for v in report.violations)

