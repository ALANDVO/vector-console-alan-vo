import { useState, useEffect } from 'react';
import { DiagramSpec, DiagramType } from '../types/api';
import { api } from '../api/client';
import { SvgPreview } from './SvgPreview';

const makeSpec = (
  type: DiagramType,
  title: string,
  desc: string,
  zones: DiagramSpec['zones'] = [],
  nodes: DiagramSpec['nodes'] = [],
  edges: DiagramSpec['edges'] = [],
  dataviz: DiagramSpec['dataviz_items'] = [],
  sankey: DiagramSpec['sankey_links'] = [],
  ai: DiagramSpec['ai_nodes'] = []
): DiagramSpec => ({
  title, diagram_type: type, description: desc, accent_color: '#0284c7', width: 960, height: 560,
  zones, nodes, edges, dataviz_items: dataviz, sankey_links: sankey, ai_nodes: ai
});

const DEFAULT_SPECS: Record<DiagramType, DiagramSpec> = {
  architecture_cloud: makeSpec(
    'architecture_cloud', 'AKS Spoke with PaaS Private Endpoints',
    '4-tier Azure containment hierarchy with Private Endpoint PaaS isolation',
    [
      { id: 'sub-1', tier: 'subscription', name: 'Enterprise-Core-Sub' },
      { id: 'rg-1', tier: 'resource_group', name: 'rg-workloads-prod', parent_id: 'sub-1' },
      { id: 'vnet-1', tier: 'vnet', name: 'vnet-spoke-10.1.0.0/16', parent_id: 'rg-1' },
      { id: 'snet-app', tier: 'subnet', name: 'snet-aks-nodes', parent_id: 'vnet-1' },
      { id: 'snet-pe', tier: 'subnet', name: 'snet-private-endpoints', parent_id: 'vnet-1' }
    ],
    [
      { id: 'aks-worker', name: 'aks-agentpool-01', service_type: 'vm', zone_id: 'snet-app', ip_address: '10.1.1.4' },
      { id: 'pe-sql', name: 'pe-sql-db', service_type: 'private_endpoint', zone_id: 'snet-pe', private_endpoint_target: 'sql-db', ip_address: '10.1.2.10' },
      { id: 'sql-db', name: 'sqldb-workload-prod', service_type: 'azure_sql', zone_id: 'rg-1' }
    ],
    [
      { source: 'aks-worker', target: 'pe-sql', label: 'TDS (1433)' },
      { source: 'pe-sql', target: 'sql-db', label: 'Private Link', edge_type: 'dashed' }
    ]
  ),
  treemap: makeSpec(
    'treemap', 'Global Cloud Carbon Proportion by Provider',
    'Honest-data treemap where area strictly encodes compute share',
    [], [], [],
    [
      { id: 'c1', label: 'Hyperscaler Alpha', value: 48.5 },
      { id: 'c2', label: 'Hyperscaler Beta', value: 29.3 },
      { id: 'c3', label: 'Hyperscaler Gamma', value: 14.2 },
      { id: 'c4', label: 'Regional Edge', value: 8.0 }
    ]
  ),
  sankey: makeSpec(
    'sankey', 'Language Migration Cohorts',
    'Stage-based flow conservation solver with cubic Bezier ribbons',
    [], [], [], [],
    [
      { source: 'Python_2024', target: 'Python_2026', value: 65.0 },
      { source: 'Python_2024', target: 'Rust_2026', value: 25.0 },
      { source: 'JS_2024', target: 'TypeScript_2026', value: 70.0 },
      { source: 'JS_2024', target: 'Rust_2026', value: 15.0 }
    ]
  ),
  slopegraph: makeSpec(
    'slopegraph', 'Coding Agent Benchmark Shift (v1 vs v2)',
    'Rank change between two discrete testing periods',
    [], [], [],
    [
      { id: 'claude', label: 'Claude Code', value: 0, t1_value: 52.4, t2_value: 74.8 },
      { id: 'cursor', label: 'Cursor Agent', value: 0, t1_value: 46.1, t2_value: 69.2 },
      { id: 'copilot', label: 'GitHub Copilot', value: 0, t1_value: 38.0, t2_value: 58.5 }
    ]
  ),
  dumbbell: makeSpec(
    'dumbbell', 'Inference Latency Delta (p50 vs p99 ms)',
    'Paired categorical metrics spread',
    [], [], [],
    [
      { id: 'm1', label: 'Llama-3-8B', value: 0, t1_value: 18.2, t2_value: 41.5 },
      { id: 'm2', label: 'Mixtral-8x7B', value: 0, t1_value: 26.0, t2_value: 64.0 },
      { id: 'm3', label: 'DeepSeek-R1', value: 0, t1_value: 45.0, t2_value: 118.0 }
    ]
  ),
  ai_pipeline: makeSpec(
    'ai_pipeline', 'Transformer Multi-Head Attention Graph',
    'Detailed Q, K, V matrix projections and feed-forward layer dynamics',
    [], [], [], [], [],
    [
      { id: 'n1', label: 'Token Embeddings', layer_type: 'embedding', params: 'd=768' },
      { id: 'n2', label: 'Q, K, V Projections', layer_type: 'multihead_attention', params: '12 heads' },
      { id: 'n3', label: 'Softmax Attention', layer_type: 'multihead_attention', params: 'Scaled' },
      { id: 'n4', label: 'LayerNorm & Residual', layer_type: 'layernorm', params: 'eps=1e-5' },
      { id: 'n5', label: 'Feed-Forward SwiGLU', layer_type: 'feedforward', params: 'd_ff=3072' },
      { id: 'n6', label: 'Output Logits', layer_type: 'logit_projection', params: 'vocab=32k' }
    ]
  ),
  sbgn: makeSpec(
    'sbgn', 'MAPK Phosphorylation Pathway (SBGN PD)',
    'Systems Biology Graphical Notation process description pathway',
    [], [], [], [], [],
    [
      { id: 'kin', label: 'Kinase Alpha', layer_type: 'macromolecule', params: 'P@Y216' },
      { id: 'rxn', label: 'Phosphorylation', layer_type: 'reaction', params: 'Enzymatic' },
      { id: 'sub', label: 'Substrate-P', layer_type: 'macromolecule', params: 'P@S104' }
    ]
  )
};

export const DiagramEditor: React.FC = () => {
  const [selectedType, setSelectedType] = useState<DiagramType>('architecture_cloud');
  const [spec, setSpec] = useState<DiagramSpec>(DEFAULT_SPECS.architecture_cloud);
  const [svgContent, setSvgContent] = useState<string>('');
  const [htmlContent, setHtmlContent] = useState<string>('');
  const [isCompiling, setIsCompiling] = useState<boolean>(false);
  const [savedDiagrams, setSavedDiagrams] = useState<Array<{ id: string; title: string; diagram_type: string }>>([]);
  const [saveStatus, setSaveStatus] = useState<string>('');
  const [errorMsg, setErrorMsg] = useState<string>('');

  const compileCurrentSpec = async (targetSpec: DiagramSpec) => {
    try {
      setIsCompiling(true);
      setErrorMsg('');
      const result = await api.compileDiagram(targetSpec);
      setSvgContent(result.svg);
      setHtmlContent(result.html);
    } catch (err: unknown) {
      setErrorMsg(err instanceof Error ? err.message : 'Compile failed');
    } finally {
      setIsCompiling(false);
    }
  };

  const loadSavedList = async () => {
    try {
      setSavedDiagrams(await api.listDiagrams());
    } catch {
      // Ignored
    }
  };

  useEffect(() => {
    compileCurrentSpec(spec);
    loadSavedList();
  }, []);

  const handleTypeChange = (type: DiagramType) => {
    setSelectedType(type);
    const newSpec = DEFAULT_SPECS[type];
    setSpec(newSpec);
    compileCurrentSpec(newSpec);
  };

  const handleTitleChange = (newTitle: string) => {
    const updated = { ...spec, title: newTitle };
    setSpec(updated);
    compileCurrentSpec(updated);
  };

  const handleAccentChange = (accent: string) => {
    const updated = { ...spec, accent_color: accent };
    setSpec(updated);
    compileCurrentSpec(updated);
  };

  const handleSaveDiagram = async () => {
    try {
      setSaveStatus('Saving...');
      const saved = await api.createDiagram(spec);
      setSaveStatus(`Saved #${saved.id.slice(0, 8)}`);
      loadSavedList();
      setTimeout(() => setSaveStatus(''), 4000);
    } catch (err: unknown) {
      setSaveStatus(`Error: ${err instanceof Error ? err.message : 'Save failed'}`);
    }
  };

  const handleLoadDiagram = async (id: string) => {
    if (!id) return;
    try {
      const diag = await api.getDiagram(id);
      setSpec(diag.spec);
      setSelectedType(diag.spec.diagram_type);
      setSvgContent(diag.svg_content);
      setHtmlContent(diag.html_content);
      setSaveStatus(`Loaded ${diag.title}`);
    } catch (err: unknown) {
      setErrorMsg(err instanceof Error ? err.message : 'Load failed');
    }
  };

  return (
    <div>
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '1.25rem' }}>
        <div>
          <h2 style={{ fontSize: '1.35rem', fontWeight: 800 }}>Diagram Design & Vector Studio</h2>
          <p style={{ fontSize: '0.875rem', color: 'var(--text-muted)' }}>
            Editorial synthesis for Cloud Containment, Dataviz proportions, Neural Architectures & SBGN
          </p>
        </div>

        <div style={{ display: 'flex', alignItems: 'center', gap: '0.75rem' }}>
          {savedDiagrams.length > 0 && (
            <select
              className="form-select"
              style={{ width: '220px', fontSize: '0.8rem' }}
              onChange={(e) => handleLoadDiagram(e.target.value)}
              defaultValue=""
            >
              <option value="" disabled>Load Saved Diagram...</option>
              {savedDiagrams.map((d) => (
                <option key={d.id} value={d.id}>{d.title} ({d.diagram_type})</option>
              ))}
            </select>
          )}

          <button className="btn btn-primary" onClick={handleSaveDiagram} disabled={isCompiling}>
            {isCompiling ? 'Compiling...' : 'Save Diagram'}
          </button>
          {saveStatus && <span className="mono" style={{ fontSize: '0.75rem', color: 'var(--accent)' }}>{saveStatus}</span>}
        </div>
      </div>

      {errorMsg && (
        <div style={{ background: 'var(--error-tint)', color: 'var(--error)', padding: '0.75rem', borderRadius: '4px', marginBottom: '1rem', border: '1px solid var(--error)' }}>
          {errorMsg}
        </div>
      )}

      <div className="grid-2">
        <div className="card">
          <h3 className="card-title">Specification Parameters</h3>
          <p className="card-desc">Select grammar type and configure editorial aesthetics</p>

          <div className="form-group">
            <label className="form-label">Diagram Type Grammar</label>
            <select
              className="form-select"
              value={selectedType}
              onChange={(e) => handleTypeChange(e.target.value as DiagramType)}
            >
              <option value="architecture_cloud">Cloud Containment (4-tier Azure Hierarchy)</option>
              <option value="treemap">Treemap (Squarified Area Proportion)</option>
              <option value="sankey">Sankey (Flow Conservation Ribbons)</option>
              <option value="slopegraph">Slopegraph (Rank Change Over Time)</option>
              <option value="dumbbell">Dumbbell Plot (Category Delta Metrics)</option>
              <option value="ai_pipeline">AI / Neural Architecture Pipeline</option>
              <option value="sbgn">SBGN Process Description Pathway</option>
            </select>
          </div>

          <div className="form-group">
            <label className="form-label">Diagram Title</label>
            <input
              type="text"
              className="form-input"
              value={spec.title}
              onChange={(e) => handleTitleChange(e.target.value)}
            />
          </div>

          <div className="grid-2" style={{ marginBottom: '1rem' }}>
            <div>
              <label className="form-label">Single Accent Palette</label>
              <select
                className="form-select"
                value={spec.accent_color}
                onChange={(e) => handleAccentChange(e.target.value)}
              >
                <option value="#0284c7">Cyan Ink (#0284c7)</option>
                <option value="#2563eb">Cobalt Ink (#2563eb)</option>
                <option value="#059669">Emerald Ink (#059669)</option>
                <option value="#d97706">Amber Ink (#d97706)</option>
                <option value="#7c3aed">Violet Ink (#7c3aed)</option>
              </select>
            </div>

            <div>
              <label className="form-label">Dimensions (W × H)</label>
              <div style={{ display: 'flex', gap: '0.5rem' }}>
                <input
                  type="number"
                  className="form-input mono"
                  value={spec.width}
                  readOnly
                  style={{ width: '50%' }}
                />
                <input
                  type="number"
                  className="form-input mono"
                  value={spec.height}
                  readOnly
                  style={{ width: '50%' }}
                />
              </div>
            </div>
          </div>

          <div style={{ marginTop: '1.25rem', borderTop: '1px solid var(--border-color)', paddingTop: '1rem' }}>
            <h4 style={{ fontSize: '0.85rem', fontWeight: 700, marginBottom: '0.5rem' }}>Active Grammar Structure</h4>
            {selectedType === 'architecture_cloud' && (
              <div style={{ fontSize: '0.75rem', color: 'var(--text-muted)' }}>
                <p>• Zones: <strong>{spec.zones.length}</strong> (Subscription, RG, VNet, Subnet)</p>
                <p>• Nodes: <strong>{spec.nodes.length}</strong> (AKS node, Private Endpoints, PaaS)</p>
                <p>• PaaS Rule: Validated (No direct PaaS placement in Subnets)</p>
              </div>
            )}
            {(selectedType === 'treemap' || selectedType === 'slopegraph' || selectedType === 'dumbbell') && (
              <div style={{ fontSize: '0.75rem', color: 'var(--text-muted)' }}>
                <p>• Dataviz Items: <strong>{spec.dataviz_items.length}</strong></p>
                <p>• Proportions: Strictly area encoded; no drop shadows</p>
              </div>
            )}
            {selectedType === 'sankey' && (
              <div style={{ fontSize: '0.75rem', color: 'var(--text-muted)' }}>
                <p>• Flow Links: <strong>{spec.sankey_links.length}</strong></p>
                <p>• Invariant: Intermediate node flow conservation checked</p>
              </div>
            )}
            {(selectedType === 'ai_pipeline' || selectedType === 'sbgn') && (
              <div style={{ fontSize: '0.75rem', color: 'var(--text-muted)' }}>
                <p>• Functional Units: <strong>{spec.ai_nodes.length}</strong></p>
                <p>• High-precision vector coordinates without raster filters</p>
              </div>
            )}
          </div>
        </div>

        <div>
          <SvgPreview
            svgContent={svgContent}
            title={spec.title}
            htmlContent={htmlContent}
          />
        </div>
      </div>
    </div>
  );
};
