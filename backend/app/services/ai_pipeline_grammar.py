import html
from typing import List
from app.models.diagram import DiagramSpec, LintIssue

def validate_ai_pipeline_invariants(spec: DiagramSpec) -> List[LintIssue]:
    """Validates structural invariants for AI/ML neural architectures and SBGN diagrams."""
    issues: List[LintIssue] = []
    if spec.diagram_type.value == "sbgn":
        has_macro = any("macro" in (n.layer_type.lower()) or "species" in (n.layer_type.lower()) for n in spec.ai_nodes)
        has_rxn = any("reaction" in (n.layer_type.lower()) or "process" in (n.layer_type.lower()) for n in spec.ai_nodes)
        if not (has_macro and has_rxn) and spec.ai_nodes:
            issues.append(LintIssue(rule_id="sbgn-completeness", severity="warning", message="SBGN Process Description diagrams specify macromolecules and reaction nodes."))
    return issues

def render_ai_pipeline_svg(spec: DiagramSpec) -> str:
    w, h, accent = spec.width, spec.height, spec.accent_color
    pad = 40.0
    elements = [
        f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {w} {h}" width="100%" height="100%" class="editorial-diagram ai-pipeline" data-diagram-type="ai_pipeline" shape-rendering="geometricPrecision">',
        '<style>text{font-family:ui-sans-serif,system-ui,sans-serif;}.mono{font-family:ui-monospace,SFMono-Regular,Menlo,monospace;}.btitle{font-size:11px;font-weight:700;fill:#0f172a;}.bdim{font-size:9px;fill:#64748b;}</style>',
        f'<text x="{pad}" y="{pad+10}" class="mono" font-size="12px" font-weight="700" fill="#334155">TRANSFORMER MULTI-HEAD ATTENTION &amp; REASONING FLOW</text>'
    ]

    nodes = spec.ai_nodes or [
        type('Node', (), {'id': 'tok', 'label': 'Token Embeddings', 'layer_type': 'embedding', 'params': 'B × T × D'})(),
        type('Node', (), {'id': 'qkv', 'label': 'Q, K, V Projections', 'layer_type': 'multihead_attention', 'params': '3 × (B × T × D)'})(),
        type('Node', (), {'id': 'attn', 'label': 'Scaled Dot-Product', 'layer_type': 'multihead_attention', 'params': 'Softmax(QK^T / √d)'})(),
        type('Node', (), {'id': 'ffn', 'label': 'Feed-Forward SwiGLU', 'layer_type': 'feedforward', 'params': 'B × T × 4D'})(),
        type('Node', (), {'id': 'out', 'label': 'Vocabulary Logits', 'layer_type': 'logit_projection', 'params': 'B × T × V'})()
    ]

    for idx, node in enumerate(nodes):
        nx, ny = pad + ((idx % 3) * 260.0), pad + 40.0 + ((idx // 3) * 100.0)
        elements += [
            f'<rect x="{nx}" y="{ny}" width="220" height="56" rx="4" fill="#ffffff" stroke="{accent}" stroke-width="1.5" data-layer-id="{node.id}" />',
            f'<text x="{nx+12}" y="{ny+22}" class="btitle">{html.escape(node.label)}</text>',
            f'<text x="{nx+12}" y="{ny+38}" class="bdim mono">{html.escape(node.layer_type)} {html.escape(node.params or "")}</text>'
        ]

    elements += [f'<text x="{pad}" y="{h-10}" class="mono" font-size="9px" fill="#94a3b8">Neural Pipeline Vector Architecture · High precision attention flow · Clean editorial geometry</text>', '</svg>']
    return '\n'.join(elements)

def render_sbgn_svg(spec: DiagramSpec) -> str:
    w, h, accent = spec.width, spec.height, spec.accent_color
    pad = 40.0
    px, py = pad + 260, 185
    return '\n'.join([
        f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {w} {h}" width="100%" height="100%" class="editorial-diagram bio-sbgn" data-diagram-type="sbgn" shape-rendering="geometricPrecision">',
        '<style>text{font-family:ui-sans-serif,system-ui,sans-serif;}.mono{font-family:ui-monospace,SFMono-Regular,Menlo,monospace;}.mtitle{font-size:11px;font-weight:600;fill:#0f172a;}.st{font-size:8px;fill:#475569;}</style>',
        f'<text x="{pad}" y="{pad+10}" class="mono" font-size="12px" font-weight="700" fill="#334155">SBGN PROCESS DESCRIPTION (PD) · MOLECULAR REACTION PATHWAY</text>',
        f'<rect x="{pad+20}" y="120" width="130" height="48" rx="10" fill="#ffffff" stroke="{accent}" stroke-width="1.8" />',
        f'<text x="{pad+85}" y="148" text-anchor="middle" class="mtitle">Kinase_Alpha</text>',
        f'<ellipse cx="{pad+85}" cy="120" rx="16" ry="8" fill="#f8fafc" stroke="{accent}" stroke-width="1.2" />',
        f'<text x="{pad+85}" y="123" text-anchor="middle" class="st mono">P@Y216</text>',
        f'<rect x="{pad+20}" y="220" width="130" height="40" rx="6" fill="#f8fafc" stroke="#64748b" stroke-width="1.4" />',
        f'<text x="{pad+85}" y="244" text-anchor="middle" class="mtitle">ATP</text>',
        f'<rect x="{px}" y="{py}" width="24" height="24" fill="{accent}" stroke="{accent}" rx="1" />',
        f'<line x1="{pad+150}" y1="144" x2="{px}" y2="{py+12}" stroke="#334155" stroke-width="1.5" />',
        f'<line x1="{pad+150}" y1="240" x2="{px}" y2="{py+12}" stroke="#334155" stroke-width="1.5" />',
        f'<rect x="{pad+380}" y="120" width="140" height="48" rx="10" fill="#ffffff" stroke="{accent}" stroke-width="1.8" />',
        f'<text x="{pad+450}" y="148" text-anchor="middle" class="mtitle">Substrate_P</text>',
        f'<ellipse cx="{pad+450}" cy="120" rx="18" ry="8" fill="{accent}" fill-opacity="0.15" stroke="{accent}" stroke-width="1.2" />',
        f'<text x="{pad+450}" y="123" text-anchor="middle" class="st mono" fill="{accent}">P@S104</text>',
        f'<line x1="{px+24}" y1="{py+12}" x2="{pad+380}" y2="144" stroke="#334155" stroke-width="1.5" />',
        f'<polygon points="{pad+380},144 {pad+372},140 {pad+372},148" fill="#334155" />',
        f'<text x="{pad}" y="{h-10}" class="mono" font-size="9px" fill="#94a3b8">SBGN PD Pathway · Systems Biology Graphical Notation compliant · Macromolecules &amp; Process Nodes</text>',
        '</svg>'
    ])
