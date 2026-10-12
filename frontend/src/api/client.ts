import {
  DiagramSpec,
  DiagramResponse,
  DiagramListSummary,
  LintReport,
  EvalSummary,
  AdvisoryResponse,
  AuditItem,
  AuthUser
} from '../types/api';

const API_BASE = '';

class ApiClient {
  private csrfToken: string = '';

  setCsrfToken(token: string) {
    this.csrfToken = token;
  }

  private async request<T>(path: string, options: RequestInit = {}): Promise<T> {
    const headers = new Headers(options.headers || {});
    if (!headers.has('Content-Type') && !(options.body instanceof FormData)) {
      headers.set('Content-Type', 'application/json');
    }
    if (this.csrfToken && ['POST', 'PUT', 'DELETE', 'PATCH'].includes(options.method || 'GET')) {
      headers.set('X-CSRF-Token', this.csrfToken);
    }

    const response = await fetch(`${API_BASE}${path}`, {
      ...options,
      headers
    });

    if (!response.ok) {
      let errorMsg = `HTTP Error ${response.status}`;
      try {
        const errorJson = await response.json();
        errorMsg = errorJson.detail || errorMsg;
      } catch {
        // Fallback to status text
      }
      throw new Error(errorMsg);
    }

    return response.json();
  }

  // Auth
  async getCurrentUser(): Promise<AuthUser> {
    return this.request<AuthUser>('/api/auth/me');
  }

  async switchDemoRole(role: string): Promise<{ success: boolean; role: string }> {
    return this.request<{ success: boolean; role: string }>('/api/auth/demo-switch', {
      method: 'POST',
      body: JSON.stringify({ role })
    });
  }

  async logout(): Promise<{ success: boolean }> {
    return this.request<{ success: boolean }>('/api/auth/logout', { method: 'POST' });
  }

  // Diagrams
  async compileDiagram(spec: DiagramSpec): Promise<{ svg: string; html: string; lint_report: LintReport }> {
    return this.request('/api/diagrams/compile', {
      method: 'POST',
      body: JSON.stringify(spec)
    });
  }

  async listDiagrams(diagramType?: string, search?: string): Promise<DiagramListSummary[]> {
    const params = new URLSearchParams();
    if (diagramType) params.append('diagram_type', diagramType);
    if (search) params.append('search', search);
    return this.request<DiagramListSummary[]>(`/api/diagrams?${params.toString()}`);
  }

  async getDiagram(id: string): Promise<DiagramResponse> {
    return this.request<DiagramResponse>(`/api/diagrams/${id}`);
  }

  async createDiagram(spec: DiagramSpec): Promise<DiagramResponse> {
    return this.request<DiagramResponse>('/api/diagrams', {
      method: 'POST',
      body: JSON.stringify(spec)
    });
  }

  async updateDiagram(id: string, spec: DiagramSpec): Promise<DiagramResponse> {
    return this.request<DiagramResponse>(`/api/diagrams/${id}`, {
      method: 'PUT',
      body: JSON.stringify(spec)
    });
  }

  async deleteDiagram(id: string): Promise<{ success: boolean }> {
    return this.request<{ success: boolean }>(`/api/diagrams/${id}`, {
      method: 'DELETE'
    });
  }

  // Linting
  async lintSvg(svgContent: string): Promise<LintReport> {
    return this.request<LintReport>('/api/lint/svg', {
      method: 'POST',
      body: JSON.stringify({ svg_content: svgContent })
    });
  }

  async lintSpec(spec: DiagramSpec): Promise<LintReport> {
    return this.request<LintReport>('/api/lint/spec', {
      method: 'POST',
      body: JSON.stringify(spec)
    });
  }

  // Evaluation Benchmark
  async runBenchmark(): Promise<EvalSummary> {
    return this.request<EvalSummary>('/api/eval/run', {
      method: 'POST'
    });
  }

  async getLatestBenchmark(): Promise<EvalSummary> {
    return this.request<EvalSummary>('/api/eval/latest');
  }

  // Audit Logs
  async listAuditLogs(action?: string): Promise<AuditItem[]> {
    const params = new URLSearchParams();
    if (action) params.append('action', action);
    return this.request<AuditItem[]>(`/api/audit?${params.toString()}`);
  }

  // LLM Advisory
  async getAdvisory(query: string, spec?: DiagramSpec, rawSvg?: string): Promise<AdvisoryResponse> {
    return this.request<AdvisoryResponse>('/api/llm/advisory', {
      method: 'POST',
      body: JSON.stringify({ query, diagram_spec: spec, raw_svg: rawSvg })
    });
  }
}

export const api = new ApiClient();
