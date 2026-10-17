# Product development plan

Each round completes one feature or repair. Future items are planned, not implemented claims.

## Current round

linter-paas-detection-fix

## Roadmap

### editorial-vector-engine — Editorial Vector Engine and Cloud Containment Grammar

Status: done

Acceptance:
- Compiles self-contained editorial SVG diagrams with zero drop shadows, single-accent ink ramps, and monospace numbers
- Enforces 4-tier cloud containment hierarchy (Subscription, Resource Group, VNet, Subnet) with PaaS private endpoint validation
- Deterministic offline core passes 100% of unit and integration test suites without external network calls

Implementation: `backend/app/services/vector_engine.py`, `backend/app/services/containment_grammar.py`, `backend/app/api/diagrams.py`

Tests: `backend/tests/test_vector_engine.py`, `backend/tests/test_containment_grammar.py`

### dataviz-and-ai-grammars — Honest Dataviz and AI Pipeline Vector Grammars

Status: done

Acceptance:
- Computes Treemap proportions, Sankey flow conservation, and Slopegraph rank transitions
- Renders Transformer neural attention flows and SBGN process description pathways in editorial SVG

Implementation: `backend/app/services/dataviz_grammar.py`, `backend/app/services/ai_pipeline_grammar.py`

Tests: `backend/tests/test_dataviz_grammar.py`, `backend/tests/test_vector_engine.py`

### linter-and-eval-benchmark — Diagram Static Analysis Linter and Agent Evaluation Benchmark

Status: done

Acceptance:
- Lints arbitrary SVG and JSON specs against editorial design rules and containment invariants
- Executes 20-sample reproducible AI/ML diagram evaluation benchmark measuring syntax, containment, and editorial rule compliance

Implementation: `backend/app/services/linter.py`, `backend/app/services/eval_suite.py`, `backend/app/api/lint.py`, `backend/app/api/eval.py`

Tests: `backend/tests/test_linter.py`, `backend/tests/test_eval_suite.py`

### linter-paas-detection-fix — Fix PaaS-in-Subnet SVG Linter Detection and Per-Category Baseline Metrics

Status: done

Acceptance:
- Linter SVG PaaS-in-subnet detection covers all PAAS_SERVICES (azure_sql, key_vault, storage_account, cosmos_db, event_hub)
- Linter detects PaaS-in-subnet via data-azure-zone-tier attribute or data-azure-zone containing snet/subnet
- Rendered SVG includes machine-verifiable data-azure-zone-tier attribute on node elements
- Benchmark computes per-category baseline pass rate and average score
- README benchmark table reflects actual measured values

Implementation: `backend/app/services/linter.py`, `backend/app/services/containment_grammar.py`, `backend/app/services/eval_suite.py`

Tests: `backend/tests/test_linter.py`, `backend/tests/test_containment_grammar.py`, `backend/tests/test_eval_suite.py`

### oidc-auth-and-multi-provider-llm — Enterprise OIDC Authentication and Multi-Provider Advisory LLM

Status: planned

Acceptance:
- Enforces OIDC authorization-code Keycloak login with PKCE, state/nonce, role-based access control, and demo mode
- Connects advisory LLM explanations to OpenAI, Anthropic, Gemini, and Olla with bounded timeouts and error redaction

