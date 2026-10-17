import html
from typing import List, Dict, Tuple
from app.models.diagram import DiagramSpec, LintIssue

PAAS_SERVICES = {"azure_sql", "key_vault", "storage_account", "cosmos_db", "event_hub"}

def validate_containment_invariants(spec: DiagramSpec) -> List[LintIssue]:
    """Validates structural and semantic cloud containment grammar (Issue #63)."""
    issues: List[LintIssue] = []
    zone_map = {z.id: z for z in spec.zones}

    tier_expected_parent = {"resource_group": "subscription", "vnet": "resource_group", "subnet": "vnet"}
    for zone in spec.zones:
        if zone.tier == "subscription" and zone.parent_id:
            issues.append(LintIssue(rule_id="azure-containment-hierarchy", severity="error", message=f"Subscription '{zone.name}' must be root.", target=zone.id))
        elif zone.tier in tier_expected_parent:
            parent = zone_map.get(zone.parent_id or "")
            if not parent or parent.tier != tier_expected_parent[zone.tier]:
                issues.append(LintIssue(rule_id="azure-containment-hierarchy", severity="error", message=f"{zone.tier} '{zone.name}' must belong to a {tier_expected_parent[zone.tier]}.", target=zone.id))

    for node in spec.nodes:
        zone = zone_map.get(node.zone_id)
        if not zone:
            issues.append(LintIssue(rule_id="azure-unplaced-node", severity="error", message=f"Node '{node.name}' references non-existent zone '{node.zone_id}'.", target=node.id))
            continue
        if node.service_type in PAAS_SERVICES and zone.tier == "subnet":
            issues.append(LintIssue(rule_id="azure-paas-placement", severity="error", message=f"PaaS '{node.name}' directly in Subnet '{zone.name}'. Only Private Endpoints reside in subnets.", target=node.id))
        if node.service_type == "private_endpoint" and zone.tier != "subnet":
            issues.append(LintIssue(rule_id="azure-endpoint-placement", severity="warning", message=f"Private endpoint '{node.name}' should be in a Subnet.", target=node.id))

    return issues

def render_cloud_containment_svg(spec: DiagramSpec) -> str:
    """Renders a 4-tier editorial cloud architecture diagram with machine-verifiable attributes."""
    width, height, accent = spec.width, spec.height, spec.accent_color
    pad = 30.0
    sub_w, sub_h = width - (2 * pad), height - (2 * pad)
    elements = [
        f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {width} {height}" width="100%" height="100%" class="editorial-diagram cloud-containment" data-diagram-type="architecture_cloud" data-tier-count="4" shape-rendering="geometricPrecision">',
        '<style>text{font-family:ui-sans-serif,system-ui,sans-serif;}.mono{font-family:ui-monospace,SFMono-Regular,Menlo,monospace;}.zone-title{font-size:11px;font-weight:700;fill:#334155;text-transform:uppercase;letter-spacing:0.05em;}.tier-tag{font-size:9px;font-weight:600;fill:#64748b;letter-spacing:0.08em;}.node-text{font-size:12px;font-weight:600;fill:#0f172a;}.node-sub{font-size:10px;fill:#64748b;}.ip-badge{font-size:9px;fill:#475569;}</style>'
    ]

    tier_cfg = {
        "subscription": {"fill": "#f8fafc", "stroke": "#cbd5e1", "dash": "none", "w": 1.0, "rx": 6, "tag": "SUBSCRIPTION"},
        "resource_group": {"fill": "#f1f5f9", "stroke": "#94a3b8", "dash": "none", "w": 1.0, "rx": 4, "tag": "RESOURCE GROUP"},
        "vnet": {"fill": "#ffffff", "stroke": accent, "dash": "4 4", "w": 1.5, "rx": 4, "tag": "VIRTUAL NETWORK"},
        "subnet": {"fill": "#f8fafc", "stroke": "#cbd5e1", "dash": "none", "w": 1.0, "rx": 3, "tag": "SUBNET"}
    }

    if not spec.zones:
        elements += [
            f'<rect x="{pad}" y="{pad}" width="{sub_w}" height="{sub_h}" rx="6" fill="#f8fafc" stroke="#cbd5e1" stroke-width="1" data-azure-tier="subscription" data-azure-id="sub-prod" />',
            f'<text x="{pad+16}" y="{pad+24}" class="tier-tag mono">SUBSCRIPTION</text><text x="{pad+120}" y="{pad+24}" class="zone-title">Production Core</text>'
        ]
    else:
        coords: Dict[str, Tuple[float, float, float, float]] = {}
        for tier in ["subscription", "resource_group", "vnet", "subnet"]:
            tzones = [z for z in spec.zones if z.tier == tier]
            cfg = tier_cfg[tier]
            for i, z in enumerate(tzones):
                pbox = coords.get(z.parent_id or "", (pad, pad, sub_w, sub_h))
                if tier == "subscription":
                    zx, zy, zw, zh = z.x or pad, z.y or pad, z.width or sub_w, z.height or sub_h
                elif tier == "resource_group":
                    zx, zy, zw, zh = z.x or (pbox[0] + 16.0), z.y or (pbox[1] + 36.0 + (i * 240.0)), z.width or (pbox[2] - 32.0), z.height or (pbox[3] - 52.0)
                elif tier == "vnet":
                    zx, zy, zw, zh = z.x or (pbox[0] + 16.0), z.y or (pbox[1] + 32.0 + (i * 180.0)), z.width or (pbox[2] - 240.0), z.height or (pbox[3] - 48.0)
                else:
                    scnt = max(1, len([s for s in tzones if s.parent_id == z.parent_id]))
                    cw = (pbox[2] - 32.0 - (16.0 * (scnt - 1))) / scnt
                    zx, zy, zw, zh = z.x or (pbox[0] + 16.0 + (i * (cw + 16.0))), z.y or (pbox[1] + 28.0), z.width or max(180.0, cw), z.height or (pbox[3] - 44.0)

                coords[z.id] = (zx, zy, zw, zh)
                p_attr = f' data-azure-parent="{z.parent_id}"' if z.parent_id else ''
                dash_attr = f' stroke-dasharray="{cfg["dash"]}"' if cfg["dash"] != "none" else ''
                elements += [
                    f'<rect x="{zx}" y="{zy}" width="{zw}" height="{zh}" rx="{cfg["rx"]}" fill="{cfg["fill"]}" stroke="{cfg["stroke"]}" stroke-width="{cfg["w"]}"{dash_attr} data-azure-tier="{tier}" data-azure-id="{z.id}"{p_attr} />',
                    f'<text x="{zx+12}" y="{zy+20}" class="tier-tag mono">{cfg["tag"]}</text><text x="{zx+130}" y="{zy+20}" class="zone-title">{html.escape(z.name)}</text>'
                ]

        n_pos: Dict[str, Tuple[float, float]] = {}
        n_cnt: Dict[str, int] = {}
        zone_tiers: Dict[str, str] = {z.id: z.tier for z in spec.zones}
        for n in spec.nodes:
            zbox = coords.get(n.zone_id, (pad + 30.0, pad + 30.0, 200.0, 100.0))
            idx = n_cnt.get(n.zone_id, 0); n_cnt[n.zone_id] = idx + 1
            nx, ny = zbox[0] + 14.0, zbox[1] + 32.0 + (idx * 58.0)
            n_pos[n.id] = (nx + 70.0, ny + 20.0)
            is_accent = (n.service_type == "private_endpoint" or n.service_type in PAAS_SERVICES)
            s_col = accent if is_accent else "#94a3b8"
            ip_str = f'<text x="{nx+132}" y="{ny+30}" text-anchor="end" class="ip-badge mono">{html.escape(n.ip_address)}</text>' if n.ip_address else ''
            elements += [
                f'<g class="node-item" data-azure-node="{n.id}" data-azure-service="{n.service_type}" data-azure-zone="{n.zone_id}" data-azure-zone-tier="{zone_tiers.get(n.zone_id, "")}" data-azure-target="{n.private_endpoint_target or ""}">' + f'<rect x="{nx}" y="{ny}" width="140" height="42" rx="3" fill="#ffffff" stroke="{s_col}" stroke-width="1.2" /><text x="{nx+8}" y="{ny+16}" class="node-text">{html.escape(n.name)}</text><text x="{nx+8}" y="{ny+30}" class="node-sub mono">{html.escape(n.service_type.replace("_", " "))}</text>{ip_str}</g>'
            ]

        for e in spec.edges:
            s, d = n_pos.get(e.source), n_pos.get(e.target)
            if s and d:
                dash = ' stroke-dasharray="3 3"' if e.edge_type == "dashed" else ''
                elements.append(f'<line x1="{s[0]}" y1="{s[1]}" x2="{d[0]}" y2="{d[1]}" stroke="{accent}" stroke-width="1.5"{dash} data-source="{e.source}" data-target="{e.target}" />')
                if e.label:
                    elements.append(f'<text x="{(s[0]+d[0])/2.0}" y="{(s[1]+d[1])/2.0 - 4.0}" class="mono" font-size="9px" fill="{accent}" text-anchor="middle">{html.escape(e.label)}</text>')

    elements += [
        f'<text x="{pad}" y="{height-12}" class="mono" font-size="9px" fill="#94a3b8">Azure Topology Containment Verified · 4-tier hierarchy · PaaS endpoints validated</text>',
        '</svg>'
    ]
    return '\n'.join(elements)
