import pytest
from app.models.diagram import DiagramSpec, DiagramType, CloudZoneSpec, CloudNodeSpec, EdgeSpec
from app.services.containment_grammar import validate_containment_invariants, render_cloud_containment_svg

def test_valid_cloud_containment_hierarchy():
    spec = DiagramSpec(
        title="Valid 4-Tier Topology",
        diagram_type=DiagramType.ARCHITECTURE_CLOUD,
        zones=[
            CloudZoneSpec(id="sub-1", tier="subscription", name="Sub-Prod"),
            CloudZoneSpec(id="rg-1", tier="resource_group", name="rg-core", parent_id="sub-1"),
            CloudZoneSpec(id="vnet-1", tier="vnet", name="vnet-east", parent_id="rg-1"),
            CloudZoneSpec(id="snet-1", tier="subnet", name="snet-app", parent_id="vnet-1")
        ],
        nodes=[
            CloudNodeSpec(id="vm-1", name="worker-01", service_type="vm", zone_id="snet-1")
        ]
    )
    issues = validate_containment_invariants(spec)
    assert len(issues) == 0

    svg = render_cloud_containment_svg(spec)
    assert 'data-azure-tier="subscription"' in svg
    assert 'data-azure-tier="resource_group"' in svg
    assert 'data-azure-tier="vnet"' in svg
    assert 'data-azure-tier="subnet"' in svg
    assert 'data-azure-node="vm-1"' in svg

def test_invalid_paas_placement_rejected():
    # Azure SQL placed directly in subnet without private endpoint
    spec = DiagramSpec(
        title="Invalid PaaS Topology",
        diagram_type=DiagramType.ARCHITECTURE_CLOUD,
        zones=[
            CloudZoneSpec(id="sub-1", tier="subscription", name="Sub-Prod"),
            CloudZoneSpec(id="rg-1", tier="resource_group", name="rg-core", parent_id="sub-1"),
            CloudZoneSpec(id="vnet-1", tier="vnet", name="vnet-east", parent_id="rg-1"),
            CloudZoneSpec(id="snet-1", tier="subnet", name="snet-data", parent_id="vnet-1")
        ],
        nodes=[
            CloudNodeSpec(id="sql-1", name="prod-db", service_type="azure_sql", zone_id="snet-1")
        ]
    )
    issues = validate_containment_invariants(spec)
    assert any(i.rule_id == "azure-paas-placement" and i.severity == "error" for i in issues)

def test_valid_private_endpoint_placement_accepted():
    spec = DiagramSpec(
        title="Compliant PaaS with Private Endpoint",
        diagram_type=DiagramType.ARCHITECTURE_CLOUD,
        zones=[
            CloudZoneSpec(id="sub-1", tier="subscription", name="Sub-Prod"),
            CloudZoneSpec(id="rg-1", tier="resource_group", name="rg-core", parent_id="sub-1"),
            CloudZoneSpec(id="vnet-1", tier="vnet", name="vnet-east", parent_id="rg-1"),
            CloudZoneSpec(id="snet-pe", tier="subnet", name="snet-endpoints", parent_id="vnet-1")
        ],
        nodes=[
            CloudNodeSpec(id="pe-sql", name="pe-db", service_type="private_endpoint", zone_id="snet-pe", private_endpoint_target="sql-db"),
            CloudNodeSpec(id="sql-db", name="prod-db", service_type="azure_sql", zone_id="rg-1")
        ]
    )
    issues = validate_containment_invariants(spec)
    assert len(issues) == 0
