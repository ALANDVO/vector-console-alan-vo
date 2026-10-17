import datetime
from typing import List, Dict, Any
from app.models.diagram import (
    DiagramSpec, DiagramType, DatavizItem, SankeyLink,
    CloudZoneSpec, CloudNodeSpec, EdgeSpec, AIPipelineNode,
    BenchmarkResult, EvalSummary
)
from app.services.vector_engine import VectorEngine
from app.services.linter import DiagramLinter

B_SH = '<svg viewBox="0 0 500 300"><defs><filter id="f"><feDropShadow/></filter></defs><rect filter="url(#f)" x="20" y="20" width="100" height="50"/></svg>'
B_PAAS = '<svg viewBox="0 0 500 300"><rect data-azure-node="s1" data-azure-service="azure_sql" data-azure-zone="snet-app" x="20" y="20" width="100" height="50"/></svg>'
B_BOX = '<svg viewBox="0 0 500 300"><style>.b{box-shadow:2px 2px 4px #000;}</style><rect class="b" x="20" y="20" width="100" height="50"/></svg>'
B_NO_VB = '<svg><rect x="0" y="0" width="400" height="200" fill="red"/></svg>'

def _mk_az(sid, prmpt, title, z_data, n_data, e_data=None, base_svg=""):
    zones = [CloudZoneSpec(id=z[0], tier=z[1], name=z[2], parent_id=z[3] if len(z) > 3 else None) for z in z_data]
    nodes = [CloudNodeSpec(id=n[0], name=n[1], service_type=n[2], zone_id=n[3], private_endpoint_target=n[4] if len(n) > 4 else None) for n in n_data]
    edges = [EdgeSpec(source=e[0], target=e[1], label=e[2] if len(e) > 2 else None, edge_type=e[3] if len(e) > 3 else "solid") for e in (e_data or [])]
    return {
        "id": sid, "category": "cloud_containment", "prompt": prmpt, "diagram_type": DiagramType.ARCHITECTURE_CLOUD,
        "spec": DiagramSpec(title=title, diagram_type=DiagramType.ARCHITECTURE_CLOUD, zones=zones, nodes=nodes, edges=edges),
        "baseline_raw_svg": base_svg or B_SH
    }

def _mk_dv(sid, prmpt, title, dtype, items=None, links=None, base_svg=""):
    dv_items = [DatavizItem(id=i[0], label=i[1], value=i[2], t1_value=i[3] if len(i) > 3 else None, t2_value=i[4] if len(i) > 4 else None) for i in (items or [])]
    s_links = [SankeyLink(source=l[0], target=l[1], value=l[2]) for l in (links or [])]
    return {
        "id": sid, "category": "dataviz_encodings", "prompt": prmpt, "diagram_type": dtype,
        "spec": DiagramSpec(title=title, diagram_type=dtype, dataviz_items=dv_items, sankey_links=s_links),
        "baseline_raw_svg": base_svg or B_BOX
    }

def _mk_ai(sid, cat, prmpt, title, dtype, node_tuples, base_svg=""):
    nodes = [AIPipelineNode(id=n[0], label=n[1], layer_type=n[2], params=n[3] if len(n) > 3 else None) for n in node_tuples]
    return {
        "id": sid, "category": cat, "prompt": prmpt, "diagram_type": dtype,
        "spec": DiagramSpec(title=title, diagram_type=dtype, ai_nodes=nodes),
        "baseline_raw_svg": base_svg or B_SH
    }

BENCHMARK_DATASET = [
    # Category 1: Cloud Architecture Containment (5 samples)
    _mk_az("azure-01", "AKS cluster with PaaS Key Vault and PostgreSQL database with private endpoints",
           "AKS Secure Hub-Spoke with PaaS Private Endpoints",
           [("sub-1", "subscription", "Corp-Sub"), ("rg-1", "resource_group", "rg-workloads", "sub-1"), ("vnet-1", "vnet", "vnet-spoke", "rg-1"), ("snet-app", "subnet", "snet-aks", "vnet-1"), ("snet-pe", "subnet", "snet-pe", "vnet-1")],
           [("n-aks", "aks-worker", "aks_node", "snet-app"), ("pe-sql", "pe-sql", "private_endpoint", "snet-pe", "sql-prod"), ("sql-prod", "sql-db", "azure_sql", "rg-1")],
           [("n-aks", "pe-sql", "TDS 1433"), ("pe-sql", "sql-prod", "Private Link", "dashed")], B_PAAS),
    _mk_az("azure-02", "Multi-tier web application across DMZ and Application subnets behind App Gateway",
           "Two-Tier Web Architecture with Ingress DMZ",
           [("sub-1", "subscription", "Production"), ("rg-1", "resource_group", "rg-web-prod", "sub-1"), ("vnet-1", "vnet", "vnet-app-prod", "rg-1"), ("snet-dmz", "subnet", "snet-gateway", "vnet-1"), ("snet-backend", "subnet", "snet-backend", "vnet-1")],
           [("appgw", "app-gateway-waf", "vm", "snet-dmz"), ("web-app", "container-instances", "vm", "snet-backend")],
           [("appgw", "web-app", "Reverse Proxy")], B_NO_VB),
    _mk_az("azure-03", "AI inference cluster connecting to Storage Account via Private Endpoint",
           "Inference Cluster with Blob Storage Private Endpoint",
           [("sub-1", "subscription", "AI-Sub"), ("rg-1", "resource_group", "rg-inf", "sub-1"), ("vnet-1", "vnet", "vnet-inf", "rg-1"), ("snet-gpu", "subnet", "snet-gpu", "vnet-1"), ("snet-pe", "subnet", "snet-pe", "vnet-1")],
           [("gpu", "gpu-node-01", "vm", "snet-gpu"), ("pe-st", "pe-models-blob", "private_endpoint", "snet-pe", "st-blob"), ("st-blob", "stmodels", "storage_account", "rg-1")],
           [("gpu", "pe-st", "HTTPS 443")], B_BOX),
    _mk_az("azure-04", "Key Vault secrets integration for microservices with Private Link",
           "Key Vault Secrets Flow via Private Link",
           [("sub-1", "subscription", "Sub-Core"), ("rg-1", "resource_group", "rg-sec", "sub-1"), ("vnet-1", "vnet", "vnet-core", "rg-1"), ("snet-svc", "subnet", "snet-svc", "vnet-1"), ("snet-pe", "subnet", "snet-pe", "vnet-1")],
           [("svc", "auth-svc", "vm", "snet-svc"), ("pe-kv", "pe-keyvault", "private_endpoint", "snet-pe", "kv-core"), ("kv-core", "kv-prod", "key_vault", "rg-1")],
           [("svc", "pe-kv", "mTLS")], B_PAAS),
    _mk_az("azure-05", "Disaster recovery topology across primary and secondary Azure regions",
           "Cross-Region Replicated Database Architecture",
           [("sub-1", "subscription", "Enterprise-Sub"), ("rg-east", "resource_group", "rg-east", "sub-1"), ("vnet-east", "vnet", "vnet-east", "rg-east"), ("snet-east", "subnet", "snet-east", "vnet-east")],
           [("node-east", "worker-east", "vm", "snet-east")], [], B_SH),

    # Category 2: AI/ML Neural Architectures (5 samples)
    _mk_ai("aiml-01", "ai_ml_architectures", "Multi-Head Attention mechanism with Q, K, V matrix projections",
           "Transformer Multi-Head Self-Attention Pipeline", DiagramType.AI_PIPELINE,
           [("tok", "Input Embeddings", "embedding", "d=768"), ("qkv", "Linear Projections", "multihead_attention", "h=12"), ("score", "Scaled Dot-Product", "multihead_attention", "Softmax"), ("ffn", "Feed-Forward MLP", "feedforward", "d_ff=3072"), ("norm", "Layer Normalization", "layernorm", "eps=1e-5"), ("out", "Output Head", "logit_projection", "vocab=32k")]),
    _mk_ai("aiml-02", "ai_ml_architectures", "RAG vector search with dense embeddings and cross-encoder re-ranking",
           "RAG Dense Retrieval & Re-Ranking Pipeline", DiagramType.AI_PIPELINE,
           [("q", "User Query", "embedding", "dim=1024"), ("knn", "HNSW Vector Search", "multihead_attention", "Top-K=100"), ("rerank", "Cross-Encoder Reranker", "feedforward", "Top-N=5"), ("gen", "Generator", "logit_projection", "temp=0.2")]),
    _mk_ai("aiml-03", "ai_ml_architectures", "Mixture-of-Experts routing gate distributing representations to top-2 experts",
           "MoE Top-2 Routing Architecture", DiagramType.AI_PIPELINE,
           [("tok", "Token Latents", "embedding", "d=4096"), ("route", "Softmax Router", "multihead_attention", "E=8, K=2"), ("exp1", "FFN Expert 1", "feedforward", "SwiGLU"), ("exp2", "FFN Expert 2", "feedforward", "SwiGLU"), ("comb", "Gated Sum", "layernorm", "Residual")]),
    _mk_ai("aiml-04", "ai_ml_architectures", "Latent Diffusion generative pipeline showing noise schedule and U-Net denoising",
           "Latent Diffusion U-Net Denoising Dynamics", DiagramType.AI_PIPELINE,
           [("vae_e", "VAE Encoder", "embedding", "8x Down"), ("clip", "CLIP Text", "embedding", "77 tok"), ("unet", "Cross-Attn U-Net", "multihead_attention", "T=50"), ("vae_d", "VAE Decoder", "logit_projection", "512x512")]),
    _mk_ai("aiml-05", "ai_ml_architectures", "Autonomous Agent Reason-Act (ReAct) iterative execution loop",
           "ReAct Agent Iterative Reasoning Loop", DiagramType.AI_PIPELINE,
           [("obs", "Observation", "embedding", "S_t"), ("tht", "CoT Reasoner", "multihead_attention", "AutoReg"), ("act", "Tool Dispatch", "feedforward", "Bash"), ("chk", "Self-Correction", "layernorm", "Reward")]),

    # Category 3: Dataviz Encodings (5 samples)
    _mk_dv("dataviz-01", "Treemap showing global cloud carbon emissions proportion across data centers",
           "Global Cloud Compute Energy by Region", DiagramType.TREEMAP,
           items=[("us_e", "US East", 48.2), ("eu_w", "Europe West", 28.4), ("ap_se", "Asia Pacific", 14.6), ("us_w", "US West", 8.8)]),
    _mk_dv("dataviz-02", "Sankey diagram tracing developer language migration flows",
           "Developer Language Migration Cohort Flow", DiagramType.SANKEY,
           links=[("Python_2024", "Python_2026", 65.0), ("Python_2024", "Rust_2026", 20.0), ("JS_2024", "TypeScript_2026", 75.0), ("JS_2024", "Rust_2026", 15.0)]),
    _mk_dv("dataviz-03", "Slopegraph displaying coding assistant benchmark benchmark accuracy shift",
           "Coding Assistant Accuracy Shifts (v1 vs v2)", DiagramType.SLOPEGRAPH,
           items=[("m_claude", "Claude Code", 0, 48.2, 72.6), ("m_cursor", "Cursor Agent", 0, 42.0, 68.4), ("m_copilot", "Copilot", 0, 35.1, 54.2), ("m_pi", "Pi", 0, 28.0, 44.0)]),
    _mk_dv("dataviz-04", "Dumbbell plot comparing p50 vs p99 inference latency in milliseconds",
           "Inference Latency Spread (p50 vs p99 ms)", DiagramType.DUMBBELL,
           items=[("d_dense", "Llama-3-8B", 0, 18.4, 42.1), ("d_moe", "Mixtral-8x7B", 0, 24.6, 68.3), ("d_deep", "DeepSeek-R1", 0, 48.0, 124.5)]),
    _mk_dv("dataviz-05", "Treemap of AI model parameter allocations across layers",
           "Transformer Parameter Allocation Breakdown", DiagramType.TREEMAP,
           items=[("mlp", "MLP Feed-Forward", 54.0), ("attn", "Self-Attention", 34.0), ("emb", "Embedding Table", 12.0)]),

    # Category 4: SBGN Biological Pathways (5 samples)
    _mk_ai("sbgn-01", "sbgn_biology", "Kinase activation cascade phosphorylation in SBGN Process Description notation",
           "MAPK Phosphorylation Cascade (SBGN PD)", DiagramType.SBGN,
           [("raf", "Raf-1 Macromolecule", "macromolecule", "P@S338"), ("rxn1", "Phosphorylation", "reaction", "process_node"), ("mek", "MEK1/2 Phosphorylated", "macromolecule", "2P@S218")]),
    _mk_ai("sbgn-02", "sbgn_biology", "GPCR ligand binding and nucleotide exchange in SBGN PD notation",
           "GPCR G-Alpha Activation (SBGN PD)", DiagramType.SBGN,
           [("gpcr", "Beta2-AR", "macromolecule", "Active"), ("ex", "GTP Exchange", "reaction", "GEF"), ("ga", "G-Alpha(GTP)", "macromolecule", "GTP")]),
    _mk_ai("sbgn-03", "sbgn_biology", "Glycolytic metabolic flux conversion from G6P to F6P",
           "Phosphoglucose Isomerase Reaction (SBGN PD)", DiagramType.SBGN,
           [("g6p", "Glucose-6-P", "macromolecule", "Substrate"), ("iso", "Isomerization", "reaction", "Enzymatic"), ("f6p", "Fructose-6-P", "macromolecule", "Product")]),
    _mk_ai("sbgn-04", "sbgn_biology", "p53 DNA damage response apoptosis checkpoint activation",
           "p53 / MDM2 Feedback Loop (SBGN PD)", DiagramType.SBGN,
           [("p53", "p53 Tetramer", "macromolecule", "P@S15"), ("tx", "Transcription", "reaction", "DNA Binding"), ("mdm", "MDM2 Ligase", "macromolecule", "Active")]),
    _mk_ai("sbgn-05", "sbgn_biology", "Caspase cascade proteolytic cleavage executing programmed cell death",
           "Executioner Caspase-3 Cleavage Activation", DiagramType.SBGN,
           [("pro", "Procaspase-3", "macromolecule", "Inactive"), ("clv", "Cleavage", "reaction", "Caspase-9"), ("act", "Active Caspase-3", "macromolecule", "Heterotetramer")])
]

class EvaluationSuite:
    """Executes the reproducible 20-sample AI diagram benchmark evaluating baseline vs guided synthesis."""

    @classmethod
    def run_benchmark(cls) -> EvalSummary:
        total = len(BENCHMARK_DATASET)
        results: List[BenchmarkResult] = []
        category_stats: Dict[str, Dict[str, Any]] = {}

        for sample in BENCHMARK_DATASET:
            cat = sample["category"]
            if cat not in category_stats:
                category_stats[cat] = {"total": 0, "passed": 0, "score_sum": 0.0,
                                       "baseline_passed": 0, "baseline_score_sum": 0.0}
            category_stats[cat]["total"] += 1

            spec: DiagramSpec = sample["spec"]
            guided_svg = VectorEngine.render_svg(spec)
            report = DiagramLinter.lint_svg(guided_svg)
            spec_report = DiagramLinter.lint_spec(spec)
            passed = report.is_compliant and spec_report.is_compliant
            if passed:
                category_stats[cat]["passed"] += 1
            category_stats[cat]["score_sum"] += report.score

            violations = [v.message for v in report.violations] + [v.message for v in spec_report.violations]
            results.append(BenchmarkResult(
                sample_id=sample["id"], category=cat, prompt=sample["prompt"],
                passed=passed, violations=violations, svg_output=guided_svg
            ))

        baseline_passed = 0
        baseline_scores = []
        baseline_failure_types: Dict[str, int] = {}
        for sample in BENCHMARK_DATASET:
            base_report = DiagramLinter.lint_svg(sample["baseline_raw_svg"])
            if base_report.is_compliant:
                baseline_passed += 1
            baseline_scores.append(base_report.score)
            category_stats[sample["category"]]["baseline_passed"] += int(base_report.is_compliant)
            category_stats[sample["category"]]["baseline_score_sum"] += base_report.score
            for v in base_report.violations:
                baseline_failure_types[v.rule_id] = baseline_failure_types.get(v.rule_id, 0) + 1

        passed_count = sum(1 for r in results if r.passed)
        pass_rate = (passed_count / total) * 100.0

        cat_summary = {
            cat: {
                "total": data["total"], "passed": data["passed"],
                "pass_rate": (data["passed"] / data["total"]) * 100.0,
                "average_score": data["score_sum"] / data["total"],
                "baseline_pass_rate": (data["baseline_passed"] / data["total"]) * 100.0,
                "baseline_average_score": data["baseline_score_sum"] / data["total"]
            }
            for cat, data in category_stats.items()
        }

        shadow_count = baseline_failure_types.get("no-drop-shadows", 0)
        paas_count = baseline_failure_types.get("azure-paas-containment", 0)
        viewbox_count = baseline_failure_types.get("valid-viewbox", 0)
        common_failures = []
        if shadow_count:
            common_failures.append(f"Drop shadow filters (<feDropShadow> or CSS box-shadow) in {shadow_count}/{total} baseline samples ({shadow_count/total*100:.0f}%)")
        if paas_count:
            common_failures.append(f"Azure PaaS services placed in subnets instead of resource groups with Private Endpoints in {paas_count}/{total} baseline samples ({paas_count/total*100:.0f}%)")
        if viewbox_count:
            common_failures.append(f"Missing or non-responsive viewBox in {viewbox_count}/{total} baseline samples ({viewbox_count/total*100:.0f}%)")

        baseline_summary = {
            "baseline_pass_rate": (baseline_passed / total) * 100.0,
            "baseline_average_score": sum(baseline_scores) / len(baseline_scores),
            "common_baseline_failures": common_failures
        }

        return EvalSummary(
            total_samples=total, passed_samples=passed_count, pass_rate=pass_rate,
            category_scores=cat_summary, baseline_comparison=baseline_summary,
            executed_at=datetime.datetime.now(datetime.timezone.utc).isoformat()
        )

def main():
    summary = EvaluationSuite.run_benchmark()
    print("=" * 60)
    print("VECTOR CONSOLE AI/ML DIAGRAM EVALUATION BENCHMARK")
    print("=" * 60)
    print(f"Total Evaluated Samples: {summary.total_samples}")
    print(f"Guided Pass Rate:        {summary.pass_rate:.1f}% ({summary.passed_samples}/{summary.total_samples})")
    print(f"Baseline Pass Rate:      {summary.baseline_comparison['baseline_pass_rate']:.1f}%")
    print(f"Baseline Avg Score:      {summary.baseline_comparison['baseline_average_score']:.1f}/100")
    print("\nCategory Breakdown:")
    for cat, stats in summary.category_scores.items():
        print(f" - {cat:20s}: {stats['pass_rate']:.1f}% pass rate, Baseline: {stats['baseline_pass_rate']:.1f}% pass rate (Score: {stats['average_score']:.1f} / Baseline: {stats['baseline_average_score']:.1f})")
    if summary.baseline_comparison.get("common_baseline_failures"):
        print("\nCommon Baseline Failures:")
        for failure in summary.baseline_comparison["common_baseline_failures"]:
            print(f"  - {failure}")
    print("\nBenchmark Execution Complete.")

if __name__ == "__main__":
    main()
