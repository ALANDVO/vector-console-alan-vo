import pytest
from app.models.diagram import DiagramSpec, DiagramType, DatavizItem, SankeyLink
from app.services.vector_engine import VectorEngine

def test_vector_engine_renders_cloud_architecture():
    spec = DiagramSpec(
        title="Production Cloud Architecture",
        diagram_type=DiagramType.ARCHITECTURE_CLOUD,
        accent_color="#0284c7"
    )
    svg, html_doc = VectorEngine.compile(spec)
    assert "<svg" in svg
    assert 'class="editorial-diagram cloud-containment"' in svg
    assert "viewBox=" in svg
    assert "<feDropShadow" not in svg
    assert "box-shadow" not in svg
    assert "<!DOCTYPE html>" in html_doc
    assert "Production Cloud Architecture" in html_doc

def test_vector_engine_renders_treemap():
    spec = DiagramSpec(
        title="Compute Allocation Treemap",
        diagram_type=DiagramType.TREEMAP,
        dataviz_items=[
            DatavizItem(id="item1", label="Inference", value=65.0),
            DatavizItem(id="item2", label="Training", value=35.0)
        ]
    )
    svg, _ = VectorEngine.compile(spec)
    assert 'class="editorial-diagram dataviz-treemap"' in svg
    assert 'data-item-id="item1"' in svg
    assert 'data-item-value="65.0"' in svg

def test_vector_engine_renders_sankey():
    spec = DiagramSpec(
        title="Language Migration Flow",
        diagram_type=DiagramType.SANKEY,
        sankey_links=[
            SankeyLink(source="Python", target="Rust", value=40.0)
        ]
    )
    svg, _ = VectorEngine.compile(spec)
    assert 'class="editorial-diagram dataviz-sankey"' in svg
    assert 'data-source="Python"' in svg
    assert 'data-target="Rust"' in svg

def test_vector_engine_renders_slopegraph_and_dumbbell():
    spec = DiagramSpec(
        title="Benchmark Delta",
        diagram_type=DiagramType.SLOPEGRAPH,
        dataviz_items=[
            DatavizItem(id="m1", label="Model A", value=0, t1_value=50.0, t2_value=85.0)
        ]
    )
    svg_slope, _ = VectorEngine.compile(spec)
    assert 'class="editorial-diagram dataviz-slopegraph"' in svg_slope

    spec.diagram_type = DiagramType.DUMBBELL
    svg_dumb, _ = VectorEngine.compile(spec)
    assert 'class="editorial-diagram dataviz-dumbbell"' in svg_dumb
