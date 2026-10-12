import pytest
from app.models.diagram import DiagramSpec, DiagramType, DatavizItem, SankeyLink
from app.services.dataviz_grammar import validate_dataviz_invariants

def test_treemap_rejects_non_positive_values():
    spec = DiagramSpec(
        title="Invalid Treemap",
        diagram_type=DiagramType.TREEMAP,
        dataviz_items=[
            DatavizItem(id="item1", label="Valid Item", value=50.0),
            DatavizItem(id="item2", label="Zero Item", value=0.0)
        ]
    )
    issues = validate_dataviz_invariants(spec)
    assert any(i.rule_id == "honest-data-treemap-area" for i in issues)

def test_sankey_flow_conservation_detection():
    # Intermediate node B receives 100 but only sends 40
    spec = DiagramSpec(
        title="Leaking Sankey Flow",
        diagram_type=DiagramType.SANKEY,
        sankey_links=[
            SankeyLink(source="A", target="B", value=100.0),
            SankeyLink(source="B", target="C", value=40.0)
        ]
    )
    issues = validate_dataviz_invariants(spec)
    assert any(i.rule_id == "honest-data-flow-conservation" for i in issues)

def test_sankey_balanced_flow_passes():
    spec = DiagramSpec(
        title="Conserved Sankey Flow",
        diagram_type=DiagramType.SANKEY,
        sankey_links=[
            SankeyLink(source="SourceA", target="Stage2", value=60.0),
            SankeyLink(source="SourceB", target="Stage2", value=40.0),
            SankeyLink(source="Stage2", target="DestFinal", value=100.0)
        ]
    )
    issues = validate_dataviz_invariants(spec)
    assert len(issues) == 0
