import html
from typing import List, Dict
from app.models.diagram import DiagramSpec, LintIssue

def validate_dataviz_invariants(spec: DiagramSpec) -> List[LintIssue]:
    """Validates honest-data rules for editorial dataviz diagrams (Issue #62)."""
    issues: List[LintIssue] = []

    if spec.diagram_type.value == "treemap":
        if not spec.dataviz_items:
            issues.append(LintIssue(rule_id="treemap-empty", severity="error", message="Treemap requires at least one data item."))
        for item in spec.dataviz_items:
            if item.value <= 0:
                issues.append(LintIssue(rule_id="honest-data-treemap-area", severity="error", message=f"Treemap area rule: '{item.label}' has non-positive value ({item.value}).", target=item.id))

    elif spec.diagram_type.value == "sankey":
        if not spec.sankey_links:
            issues.append(LintIssue(rule_id="sankey-empty", severity="error", message="Sankey diagram requires flow links."))
        inflows, outflows = {}, {}
        for link in spec.sankey_links:
            if link.value <= 0:
                issues.append(LintIssue(rule_id="honest-data-sankey-flow", severity="error", message=f"Sankey flow '{link.source}'->'{link.target}' must be positive."))
            outflows[link.source] = outflows.get(link.source, 0.0) + link.value
            inflows[link.target] = inflows.get(link.target, 0.0) + link.value

        for node in (set(inflows.keys()) | set(outflows.keys())):
            iv, ov = inflows.get(node, 0.0), outflows.get(node, 0.0)
            if iv > 0 and ov > 0 and abs(iv - ov) > 0.01 * max(iv, ov):
                issues.append(LintIssue(rule_id="honest-data-flow-conservation", severity="error", message=f"Sankey conservation violation at '{node}': inflow {iv:.1f} != outflow {ov:.1f}.", target=node))

    elif spec.diagram_type.value == "slopegraph":
        for item in spec.dataviz_items:
            if item.t1_value is None or item.t2_value is None:
                issues.append(LintIssue(rule_id="slopegraph-paired-values", severity="error", message=f"Slopegraph '{item.label}' requires paired t1_value and t2_value.", target=item.id))

    return issues

def _dv_header(w: int, h: int, cls_name: str, dtype: str) -> List[str]:
    return [
        f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {w} {h}" width="100%" height="100%" class="editorial-diagram {cls_name}" data-diagram-type="{dtype}" shape-rendering="geometricPrecision">',
        '<style>text{font-family:ui-sans-serif,system-ui,sans-serif;}.mono{font-family:ui-monospace,SFMono-Regular,Menlo,monospace;}.lbl{font-size:11px;font-weight:600;fill:#0f172a;}.val{font-size:10px;fill:#475569;}</style>'
    ]

def render_treemap_svg(spec: DiagramSpec) -> str:
    w, h, accent = spec.width, spec.height, spec.accent_color
    items = [i for i in spec.dataviz_items if i.value > 0]
    total_val = sum(i.value for i in items) or 1.0
    pad = 32.0
    elements = _dv_header(w, h, "dataviz-treemap", "treemap")
    cx, cy, cw, ch = pad, pad, w - (2 * pad), h - (2 * pad) - 24.0
    s_items = sorted(items, key=lambda x: x.value, reverse=True)

    for idx, it in enumerate(s_items):
        frac = it.value / total_val
        op = max(0.15, min(0.9, 0.2 + (0.7 * (it.value / s_items[0].value))))
        wc = cw * frac if idx < len(s_items) - 1 else cw
        elements.append(f'<rect x="{cx:.1f}" y="{cy:.1f}" width="{max(2.0, wc-2.0):.1f}" height="{ch:.1f}" fill="{accent}" fill-opacity="{op:.2f}" stroke="#ffffff" stroke-width="2" data-item-id="{it.id}" data-item-value="{it.value}" />')
        if wc > 55.0:
            elements += [
                f'<text x="{(cx+8):.1f}" y="{(cy+18):.1f}" class="lbl">{html.escape(it.label)}</text>',
                f'<text x="{(cx+8):.1f}" y="{(cy+32):.1f}" class="val mono">{it.value:.1f} ({(frac*100):.1f}%)</text>'
            ]
        cx += wc; cw -= wc

    elements += [f'<text x="{pad}" y="{h-10}" class="mono" font-size="9px" fill="#94a3b8">Honest-Data Treemap · Area encoding only · Sum: {total_val:.1f}</text>', '</svg>']
    return '\n'.join(elements)

def render_sankey_svg(spec: DiagramSpec) -> str:
    w, h, accent = spec.width, spec.height, spec.accent_color
    pad = 40.0
    elements = _dv_header(w, h, "dataviz-sankey", "sankey")
    srcs, tgts = sorted(list({l.source for l in spec.sankey_links})), sorted(list({l.target for l in spec.sankey_links}))
    x1, x2 = pad + 40.0, w - pad - 120.0
    tot, uh = sum(l.value for l in spec.sankey_links) or 1.0, h - (2 * pad) - 40.0

    sy_map, ty_map = {}, {}
    cy = pad + 20.0
    for s in srcs:
        sv = sum(l.value for l in spec.sankey_links if l.source == s)
        hn = max(16.0, (sv / tot) * uh)
        elements += [
            f'<rect x="{x1}" y="{cy}" width="16" height="{hn}" fill="{accent}" rx="2" />',
            f'<text x="{x1-8}" y="{cy+hn/2+4}" text-anchor="end" class="lbl">{html.escape(s)}</text>',
            f'<text x="{x1-8}" y="{cy+hn/2+15}" text-anchor="end" class="val mono">{sv:.1f}</text>'
        ]
        sy_map[s] = cy; cy += hn + 14.0

    cy = pad + 20.0
    for t in tgts:
        tv = sum(l.value for l in spec.sankey_links if l.target == t)
        hn = max(16.0, (tv / tot) * uh)
        elements += [
            f'<rect x="{x2}" y="{cy}" width="16" height="{hn}" fill="{accent}" rx="2" />',
            f'<text x="{x2+24}" y="{cy+hn/2+4}" class="lbl">{html.escape(t)}</text>',
            f'<text x="{x2+24}" y="{cy+hn/2+15}" class="val mono">{tv:.1f}</text>'
        ]
        ty_map[t] = cy; cy += hn + 14.0

    s_cur, t_cur = dict(sy_map), dict(ty_map)
    for l in spec.sankey_links:
        thk = max(3.0, (l.value / tot) * uh)
        sy, ty = s_cur[l.source], t_cur[l.target]
        s_cur[l.source] += thk; t_cur[l.target] += thk
        cx1 = x1 + 16.0 + ((x2 - (x1 + 16.0)) * 0.5)
        elements.append(
            f'<path d="M {x1+16} {sy} C {cx1} {sy}, {cx1} {ty}, {x2} {ty} L {x2} {ty+thk} C {cx1} {ty+thk}, {cx1} {sy+thk}, {x1+16} {sy+thk} Z" fill="{accent}" fill-opacity="0.25" stroke="{accent}" stroke-opacity="0.4" stroke-width="0.5" data-source="{l.source}" data-target="{l.target}" data-flow="{l.value}" />'
        )

    elements += [f'<text x="{pad}" y="{h-10}" class="mono" font-size="9px" fill="#94a3b8">Sankey Flow Diagram · Flow conservation preserved · Bezier ribbons</text>', '</svg>']
    return '\n'.join(elements)

def render_slopegraph_svg(spec: DiagramSpec) -> str:
    w, h, accent = spec.width, spec.height, spec.accent_color
    pad, x1, x2 = 40.0, 180.0, w - 180.0
    elements = _dv_header(w, h, "dataviz-slopegraph", "slopegraph") + [
        f'<text x="{x1}" y="{pad+12}" text-anchor="middle" class="mono" font-weight="700">PERIOD 1 (T1)</text>',
        f'<text x="{x2}" y="{pad+12}" text-anchor="middle" class="mono" font-weight="700">PERIOD 2 (T2)</text>',
        f'<line x1="{x1}" y1="{pad+24}" x2="{x1}" y2="{h-pad-20}" stroke="#e2e8f0" stroke-width="1" />',
        f'<line x1="{x2}" y1="{pad+24}" x2="{x2}" y2="{h-pad-20}" stroke="#e2e8f0" stroke-width="1" />'
    ]

    vals = [v for it in spec.dataviz_items if it.t1_value is not None and it.t2_value is not None for v in (it.t1_value, it.t2_value)]
    min_v, max_v = (min(vals), max(vals)) if vals else (0.0, 100.0)
    span, ph = (max_v - min_v) or 1.0, h - (2 * pad) - 60.0

    for it in spec.dataviz_items:
        if it.t1_value is None or it.t2_value is None: continue
        y1 = (pad + 40.0) + ((1.0 - ((it.t1_value - min_v) / span)) * ph)
        y2 = (pad + 40.0) + ((1.0 - ((it.t2_value - min_v) / span)) * ph)
        delta = it.t2_value - it.t1_value
        col = accent if abs(delta) > 5.0 else "#64748b"
        elements += [
            f'<line x1="{x1}" y1="{y1}" x2="{x2}" y2="{y2}" stroke="{col}" stroke-width="1.8" data-item="{it.id}" />',
            f'<circle cx="{x1}" cy="{y1}" r="3.5" fill="{col}" /><circle cx="{x2}" cy="{y2}" r="3.5" fill="{col}" />',
            f'<text x="{x1-10}" y="{y1+4}" text-anchor="end" class="lbl">{html.escape(it.label)} <tspan class="mono" font-weight="700">{it.t1_value:.1f}</tspan></text>',
            f'<text x="{x2+10}" y="{y2+4}" class="lbl"><tspan class="mono" font-weight="700">{it.t2_value:.1f}</tspan> {html.escape(it.label)} <tspan class="mono" fill="{col}">({delta:+.1f})</tspan></text>'
        ]

    elements += [f'<text x="{pad}" y="{h-10}" class="mono" font-size="9px" fill="#94a3b8">Slopegraph · Two-moment rank comparison · Monospace delta</text>', '</svg>']
    return '\n'.join(elements)

def render_dumbbell_svg(spec: DiagramSpec) -> str:
    w, h, accent = spec.width, spec.height, spec.accent_color
    pad = 40.0
    elements = _dv_header(w, h, "dataviz-dumbbell", "dumbbell")
    items = [i for i in spec.dataviz_items if i.t1_value is not None and i.t2_value is not None]
    vals = [v for it in items for v in (it.t1_value, it.t2_value)]
    min_v, max_v = (min(vals), max(vals)) if vals else (0.0, 100.0)
    span = (max_v - min_v) or 1.0
    xs, xe = pad + 120.0, w - pad - 60.0
    xw = xe - xs
    sy = max(32.0, (h - (2 * pad) - 40.0) / max(1, len(items)))

    for idx, it in enumerate(items):
        cy = pad + 30.0 + (idx * sy)
        cx1 = xs + (((it.t1_value - min_v) / span) * xw)
        cx2 = xs + (((it.t2_value - min_v) / span) * xw)
        elements += [
            f'<text x="{xs-12}" y="{cy+4}" text-anchor="end" class="lbl">{html.escape(it.label)}</text>',
            f'<line x1="{xs}" y1="{cy}" x2="{xe}" y2="{cy}" stroke="#f1f5f9" stroke-width="1" />',
            f'<line x1="{cx1}" y1="{cy}" x2="{cx2}" y2="{cy}" stroke="{accent}" stroke-width="2.5" />',
            f'<circle cx="{cx1}" cy="{cy}" r="4.5" fill="#64748b" /><circle cx="{cx2}" cy="{cy}" r="4.5" fill="{accent}" />',
            f'<text x="{cx2+10}" y="{cy+4}" class="mono" font-size="10px" fill="{accent}">{it.t2_value - it.t1_value:+.1f}</text>'
        ]

    elements += [f'<text x="{pad}" y="{h-10}" class="mono" font-size="9px" fill="#94a3b8">Dumbbell Delta Plot · Paired comparison per category · Gray (Baseline) vs Accent</text>', '</svg>']
    return '\n'.join(elements)
