export type DiagramType =
  | 'architecture_cloud'
  | 'ai_pipeline'
  | 'treemap'
  | 'sankey'
  | 'slopegraph'
  | 'dumbbell'
  | 'sbgn';

export interface CloudZoneSpec {
  id: string;
  tier: string;
  name: string;
  parent_id?: string;
  x?: number;
  y?: number;
  width?: number;
  height?: number;
}

export interface CloudNodeSpec {
  id: string;
  name: string;
  service_type: string;
  zone_id: string;
  private_endpoint_target?: string;
  ip_address?: string;
}

export interface DatavizItem {
  id: string;
  label: string;
  value: number;
  group?: string;
  t1_value?: number;
  t2_value?: number;
}

export interface SankeyLink {
  source: string;
  target: string;
  value: number;
}

export interface AIPipelineNode {
  id: string;
  label: string;
  layer_type: string;
  params?: string;
}

export interface EdgeSpec {
  source: string;
  target: string;
  label?: string;
  edge_type?: string;
}

export interface DiagramSpec {
  title: string;
  diagram_type: DiagramType;
  description?: string;
  accent_color: string;
  width: number;
  height: number;
  zones: CloudZoneSpec[];
  nodes: CloudNodeSpec[];
  edges: EdgeSpec[];
  dataviz_items: DatavizItem[];
  sankey_links: SankeyLink[];
  ai_nodes: AIPipelineNode[];
  metadata?: Record<string, unknown>;
}

export interface DiagramResponse {
  id: string;
  title: string;
  diagram_type: DiagramType;
  spec: DiagramSpec;
  svg_content: string;
  html_content: string;
  created_at: string;
  updated_at: string;
  created_by: string;
}

export interface DiagramListSummary {
  id: string;
  title: string;
  diagram_type: DiagramType;
  created_at: string;
  created_by: string;
}

export interface LintIssue {
  rule_id: string;
  severity: 'error' | 'warning' | 'info';
  message: string;
  target?: string;
}

export interface LintReport {
  is_compliant: boolean;
  score: number;
  violations: LintIssue[];
  editorial_stats: Record<string, unknown>;
  summary: string;
}

export interface BenchmarkResult {
  sample_id: string;
  category: string;
  prompt: string;
  passed: boolean;
  violations: string[];
  svg_output?: string;
}

export interface CategoryScore {
  total: number;
  passed: number;
  pass_rate: number;
  average_score: number;
}

export interface EvalSummary {
  total_samples: number;
  passed_samples: number;
  pass_rate: number;
  category_scores: Record<string, CategoryScore>;
  baseline_comparison: {
    baseline_pass_rate: number;
    baseline_average_score: number;
    common_baseline_failures: string[];
  };
  executed_at: string;
}

export interface AdvisoryResponse {
  advisory: boolean;
  provider: string;
  model: string;
  content: string;
  grounded_evidence: Record<string, unknown>;
  error?: string;
}

export interface AuditItem {
  id: string;
  timestamp: string;
  actor: string;
  action: string;
  resource_type: string;
  resource_id: string;
  details: Record<string, unknown>;
}

export interface AuthUser {
  sub: string;
  email: string;
  name: string;
  role: 'viewer' | 'analyst' | 'admin';
  csrf_token: string;
  is_demo: boolean;
}
