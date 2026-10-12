from enum import Enum
from typing import List, Dict, Any, Optional
from pydantic import BaseModel, Field

class DiagramType(str, Enum):
    ARCHITECTURE_CLOUD = "architecture_cloud"
    AI_PIPELINE = "ai_pipeline"
    TREEMAP = "treemap"
    SANKEY = "sankey"
    SLOPEGRAPH = "slopegraph"
    DUMBBELL = "dumbbell"
    SBGN = "sbgn"

class CloudZoneSpec(BaseModel):
    id: str
    tier: str # subscription, resource_group, vnet, subnet
    name: str
    parent_id: Optional[str] = None
    x: Optional[float] = None
    y: Optional[float] = None
    width: Optional[float] = None
    height: Optional[float] = None

class CloudNodeSpec(BaseModel):
    id: str
    name: str
    service_type: str # vm, aks_node, private_endpoint, azure_sql, key_vault, storage_account
    zone_id: str
    private_endpoint_target: Optional[str] = None
    ip_address: Optional[str] = None

class DatavizItem(BaseModel):
    id: str
    label: str
    value: float
    group: Optional[str] = None
    t1_value: Optional[float] = None
    t2_value: Optional[float] = None

class SankeyLink(BaseModel):
    source: str
    target: str
    value: float

class AIPipelineNode(BaseModel):
    id: str
    label: str
    layer_type: str # embedding, multihead_attention, feedforward, layernorm, logit_projection
    params: Optional[str] = None

class EdgeSpec(BaseModel):
    source: str
    target: str
    label: Optional[str] = None
    edge_type: Optional[str] = "solid"

class DiagramSpec(BaseModel):
    title: str = Field(..., min_length=1, max_length=120)
    diagram_type: DiagramType
    description: Optional[str] = ""
    accent_color: str = Field(default="#0284c7") # Clean editorial cyan/blue
    width: int = Field(default=960, ge=400, le=2400)
    height: int = Field(default=600, ge=300, le=2400)
    zones: List[CloudZoneSpec] = Field(default_factory=list)
    nodes: List[CloudNodeSpec] = Field(default_factory=list)
    edges: List[EdgeSpec] = Field(default_factory=list)
    dataviz_items: List[DatavizItem] = Field(default_factory=list)
    sankey_links: List[SankeyLink] = Field(default_factory=list)
    ai_nodes: List[AIPipelineNode] = Field(default_factory=list)
    metadata: Dict[str, Any] = Field(default_factory=dict)

class DiagramResponse(BaseModel):
    id: str
    title: str
    diagram_type: DiagramType
    spec: DiagramSpec
    svg_content: str
    html_content: str
    created_at: str
    updated_at: str
    created_by: str

class DiagramListSummary(BaseModel):
    id: str
    title: str
    diagram_type: DiagramType
    created_at: str
    created_by: str

class LintIssue(BaseModel):
    rule_id: str
    severity: str # error, warning, info
    message: str
    target: Optional[str] = None

class LintReport(BaseModel):
    is_compliant: bool
    score: float # 0.0 - 100.0
    violations: List[LintIssue]
    editorial_stats: Dict[str, Any]
    summary: str

class BenchmarkResult(BaseModel):
    sample_id: str
    category: str
    prompt: str
    passed: bool
    violations: List[str]
    svg_output: Optional[str] = None

class EvalSummary(BaseModel):
    total_samples: int
    passed_samples: int
    pass_rate: float
    category_scores: Dict[str, Dict[str, Any]]
    baseline_comparison: Dict[str, Any]
    executed_at: str

class AdvisoryRequest(BaseModel):
    diagram_spec: Optional[DiagramSpec] = None
    raw_svg: Optional[str] = None
    query: str
    provider: Optional[str] = None
    model: Optional[str] = None

class AdvisoryResponse(BaseModel):
    advisory: bool = True
    provider: str
    model: str
    content: str
    grounded_evidence: Dict[str, Any]
    error: Optional[str] = None
