import re
import xml.etree.ElementTree as ET
from typing import List, Dict, Any, Optional
from app.models.diagram import DiagramSpec, LintIssue, LintReport
from app.services.containment_grammar import validate_containment_invariants, PAAS_SERVICES
from app.services.dataviz_grammar import validate_dataviz_invariants
from app.services.ai_pipeline_grammar import validate_ai_pipeline_invariants

NEUTRAL_COLORS = {
    "#ffffff", "#000000", "#f8fafc", "#f1f5f9", "#e2e8f0", "#cbd5e1",
    "#94a3b8", "#64748b", "#475569", "#334155", "#1e293b", "#0f172a",
    "white", "black", "none", "transparent"
}

class DiagramLinter:
    """Static analysis linter enforcing editorial design, honest data, and containment rules."""

    @classmethod
    def lint_svg(cls, svg_str: str) -> LintReport:
        issues: List[LintIssue] = []

        # 1. Rule: No drop shadows (strictly no <filter>, <feDropShadow>, box-shadow, filter: drop-shadow)
        if re.search(r'<(?:feDropShadow|feGaussianBlur|feOffset)', svg_str, re.IGNORECASE):
            issues.append(LintIssue(
                rule_id="no-drop-shadows",
                severity="error",
                message="Editorial rule violation: drop shadow SVG filter detected (<feDropShadow>/<feGaussianBlur>). Editorial diagrams must use flat, crisp vector edges."
            ))

        if re.search(r'(?:box-shadow|drop-shadow\s*\()', svg_str, re.IGNORECASE):
            issues.append(LintIssue(
                rule_id="no-drop-shadows",
                severity="error",
                message="Editorial rule violation: CSS drop-shadow or box-shadow detected. Shadows are prohibited."
            ))

        # 2. Rule: Valid viewBox
        vb_match = re.search(r'viewBox=["\']([^"\']+)["\']', svg_str)
        if not vb_match:
            issues.append(LintIssue(
                rule_id="valid-viewbox",
                severity="error",
                message="SVG must declare an explicit, responsive viewBox attribute."
            ))
        else:
            vb_parts = vb_match.group(1).strip().split()
            if len(vb_parts) != 4 or float(vb_parts[2]) <= 0 or float(vb_parts[3]) <= 0:
                issues.append(LintIssue(
                    rule_id="valid-viewbox",
                    severity="error",
                    message="viewBox must have 4 numerical coordinates with positive width and height."
                ))

        # 3. Rule: Single accent color
        # Extract all hex colors
        hex_colors = set(re.findall(r'#[0-9a-fA-F]{3,8}', svg_str))
        chromatic_colors = {c.lower() for c in hex_colors if c.lower() not in NEUTRAL_COLORS}
        if len(chromatic_colors) > 2: # Allow primary accent + secondary tint
            issues.append(LintIssue(
                rule_id="single-accent-palette",
                severity="warning",
                message=f"Editorial palette rule: at most 1 primary accent is allowed. Detected {len(chromatic_colors)} chromatic colors ({', '.join(sorted(chromatic_colors))}). Use ink-opacity ramps instead of multi-color stops."
            ))

        # 4. Rule: Monospace numbers
        # If numbers appear in <text> elements without class="mono" or monospace font-family
        text_nodes = re.findall(r'<text([^>]*)>([^<]+)</text>', svg_str)
        for attrs, text_content in text_nodes:
            # Check if text contains numerical digits
            if re.search(r'\b\d+(?:\.\d+)?%?\b', text_content):
                has_mono = ("mono" in attrs.lower() or "monospace" in attrs.lower() or "SFMono" in attrs)
                if not has_mono and len(text_content.strip()) > 0:
                    issues.append(LintIssue(
                        rule_id="monospace-numbers",
                        severity="warning",
                        message=f"Monospace rule: number '{text_content.strip()}' should be rendered with a monospace font family or .mono class."
                    ))
                    break # Report once per document

        # 5. Rule: Check PaaS in Subnet via data attributes
        services_pattern = '|'.join(sorted(PAAS_SERVICES))
        if re.search(rf'data-azure-service="({services_pattern})"', svg_str):
            # Match PaaS nodes in subnet zones via either machine-verifiable
            # data-azure-zone-tier="subnet" (engine output) or data-azure-zone
            # containing "snet"/"subnet" (raw or agent SVG).
            paas_subnet_matches = re.findall(
                rf'data-azure-node="([^"]+)"[^>]*data-azure-service="({services_pattern})"[^>]*data-(?:azure-zone-tier="subnet"|azure-zone="([^"]*(?:snet|subnet)[^"]*)")',
                svg_str
            )
            for node_id, service, zone in paas_subnet_matches:
                zone_str = zone if zone else "(tier=subnet)"
                issues.append(LintIssue(
                    rule_id="azure-paas-containment",
                    severity="error",
                    message=f"Azure PaaS rule: '{node_id}' ({service}) is mapped into subnet zone '{zone_str}'. PaaS services belong to Resource Groups; only Private Endpoints reside in subnets.",
                    target=node_id
                ))

        # Compute compliance score
        error_count = sum(1 for i in issues if i.severity == "error")
        warning_count = sum(1 for i in issues if i.severity == "warning")
        deduction = (error_count * 25.0) + (warning_count * 10.0)
        score = max(0.0, 100.0 - deduction)
        is_compliant = (error_count == 0)

        stats = {
            "error_count": error_count,
            "warning_count": warning_count,
            "chromatic_color_count": len(chromatic_colors),
            "svg_length_bytes": len(svg_str.encode("utf-8"))
        }

        summary = (
            f"Diagram passes all editorial checks (Score: {score:.1f}/100)"
            if is_compliant else
            f"Found {error_count} errors and {warning_count} warnings (Score: {score:.1f}/100)"
        )

        return LintReport(
            is_compliant=is_compliant,
            score=score,
            violations=issues,
            editorial_stats=stats,
            summary=summary
        )

    @classmethod
    def lint_spec(cls, spec: DiagramSpec) -> LintReport:
        issues: List[LintIssue] = []

        # Check diagram invariants
        issues.extend(validate_containment_invariants(spec))
        issues.extend(validate_dataviz_invariants(spec))
        issues.extend(validate_ai_pipeline_invariants(spec))

        error_count = sum(1 for i in issues if i.severity == "error")
        warning_count = sum(1 for i in issues if i.severity == "warning")
        score = max(0.0, 100.0 - ((error_count * 25.0) + (warning_count * 10.0)))

        return LintReport(
            is_compliant=(error_count == 0),
            score=score,
            violations=issues,
            editorial_stats={
                "error_count": error_count,
                "warning_count": warning_count,
                "zones": len(spec.zones),
                "nodes": len(spec.nodes),
                "dataviz_items": len(spec.dataviz_items)
            },
            summary="Spec is valid" if error_count == 0 else f"{error_count} spec errors detected"
        )
