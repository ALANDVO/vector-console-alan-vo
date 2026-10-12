import re
import html
from typing import Dict, Any, Tuple
from app.models.diagram import DiagramSpec, DiagramType
from app.services.containment_grammar import render_cloud_containment_svg, validate_containment_invariants
from app.services.dataviz_grammar import (
    render_treemap_svg, render_sankey_svg, render_slopegraph_svg, render_dumbbell_svg,
    validate_dataviz_invariants
)
from app.services.ai_pipeline_grammar import (
    render_ai_pipeline_svg, render_sbgn_svg,
    validate_ai_pipeline_invariants
)

class VectorEngine:
    """Core deterministic vector graphics synthesis engine adhering to editorial diagram design rules."""

    @staticmethod
    def render_svg(spec: DiagramSpec) -> str:
        dtype = spec.diagram_type
        if dtype == DiagramType.ARCHITECTURE_CLOUD:
            svg = render_cloud_containment_svg(spec)
        elif dtype == DiagramType.TREEMAP:
            svg = render_treemap_svg(spec)
        elif dtype == DiagramType.SANKEY:
            svg = render_sankey_svg(spec)
        elif dtype == DiagramType.SLOPEGRAPH:
            svg = render_slopegraph_svg(spec)
        elif dtype == DiagramType.DUMBBELL:
            svg = render_dumbbell_svg(spec)
        elif dtype == DiagramType.SBGN:
            svg = render_sbgn_svg(spec)
        elif dtype == DiagramType.AI_PIPELINE:
            svg = render_ai_pipeline_svg(spec)
        else:
            svg = render_cloud_containment_svg(spec)

        return svg

    @staticmethod
    def render_html_document(spec: DiagramSpec, svg_content: str) -> str:
        """Wraps SVG in a self-contained, responsive editorial HTML document without external CDNs."""
        escaped_title = html.escape(spec.title)
        escaped_desc = html.escape(spec.description or "")
        return f"""<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>{escaped_title} | Vector Console Editorial Diagram</title>
  <style>
    :root {{
      --bg: #ffffff;
      --fg: #0f172a;
      --muted: #64748b;
      --border: #e2e8f0;
      --accent: {spec.accent_color};
    }}
    * {{ box-sizing: border-box; margin: 0; padding: 0; }}
    body {{
      font-family: ui-sans-serif, system-ui, -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif;
      background: var(--bg);
      color: var(--fg);
      padding: 2.5rem 1.5rem;
      display: flex;
      flex-direction: column;
      align-items: center;
      min-height: 100vh;
    }}
    .diagram-card {{
      max-width: 1024px;
      width: 100%;
      border: 1px solid var(--border);
      border-radius: 8px;
      padding: 1.5rem;
      background: #ffffff;
    }}
    .diagram-header {{
      margin-bottom: 1.25rem;
      border-bottom: 1px solid var(--border);
      padding-bottom: 0.75rem;
    }}
    .diagram-header h1 {{
      font-size: 1.25rem;
      font-weight: 700;
      letter-spacing: -0.01em;
      margin-bottom: 0.25rem;
    }}
    .diagram-header p {{
      font-size: 0.875rem;
      color: var(--muted);
    }}
    .svg-container {{
      width: 100%;
      overflow: hidden;
      display: flex;
      justify-content: center;
    }}
    .diagram-footer {{
      margin-top: 1rem;
      padding-top: 0.75rem;
      border-top: 1px solid var(--border);
      font-family: ui-monospace, SFMono-Regular, Menlo, monospace;
      font-size: 0.75rem;
      color: var(--muted);
      display: flex;
      justify-content: space-between;
    }}
  </style>
</head>
<body>
  <div class="diagram-card">
    <div class="diagram-header">
      <h1>{escaped_title}</h1>
      <p>{escaped_desc}</p>
    </div>
    <div class="svg-container">
      {svg_content}
    </div>
    <div class="diagram-footer">
      <span>Vector Console Editorial Engine</span>
      <span>Type: {spec.diagram_type.value} · Accent: {spec.accent_color}</span>
    </div>
  </div>
</body>
</html>
"""

    @classmethod
    def compile(cls, spec: DiagramSpec) -> Tuple[str, str]:
        svg = cls.render_svg(spec)
        html_doc = cls.render_html_document(spec, svg)
        return svg, html_doc
