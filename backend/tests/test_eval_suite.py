import pytest
from app.services.eval_suite import EvaluationSuite, BENCHMARK_DATASET

def test_evaluation_benchmark_dataset_size():
    assert len(BENCHMARK_DATASET) == 20
    categories = {s["category"] for s in BENCHMARK_DATASET}
    assert categories == {"cloud_containment", "ai_ml_architectures", "dataviz_encodings", "sbgn_biology"}

def test_run_benchmark_metrics():
    summary = EvaluationSuite.run_benchmark()
    assert summary.total_samples == 20
    assert summary.pass_rate >= 95.0
    assert summary.baseline_comparison["baseline_pass_rate"] < summary.pass_rate
    for cat in ["cloud_containment", "ai_ml_architectures", "dataviz_encodings", "sbgn_biology"]:
        assert cat in summary.category_scores
        assert summary.category_scores[cat]["total"] == 5
        assert "baseline_pass_rate" in summary.category_scores[cat]
        assert "baseline_average_score" in summary.category_scores[cat]
        assert summary.category_scores[cat]["baseline_pass_rate"] < summary.category_scores[cat]["pass_rate"]
