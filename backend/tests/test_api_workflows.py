import pytest
import httpx
from app.main import app

@pytest.mark.asyncio
async def test_api_healthcheck():
    async with httpx.AsyncClient(transport=httpx.ASGITransport(app=app), base_url="http://test") as client:
        resp = await client.get("/health")
        assert resp.status_code == 200
        data = resp.json()
        assert data["status"] == "ok"
        assert data["service"] == "vector-console"

@pytest.mark.asyncio
async def test_compile_diagram_endpoint():
    async with httpx.AsyncClient(transport=httpx.ASGITransport(app=app), base_url="http://test") as client:
        payload = {
            "title": "API Test Diagram",
            "diagram_type": "architecture_cloud",
            "accent_color": "#0284c7"
        }
        resp = await client.post("/api/diagrams/compile", json=payload)
        assert resp.status_code == 200
        data = resp.json()
        assert "<svg" in data["svg"]
        assert "<!DOCTYPE html>" in data["html"]
        assert data["lint_report"]["is_compliant"] is True

@pytest.mark.asyncio
async def test_create_read_list_diagram_workflow(db_session):
    async with httpx.AsyncClient(transport=httpx.ASGITransport(app=app), base_url="http://test") as client:
        create_payload = {
            "title": "Integration Workflow Diagram",
            "diagram_type": "treemap",
            "accent_color": "#0284c7",
            "dataviz_items": [
                {"id": "c1", "label": "Embeddings", "value": 45.0},
                {"id": "c2", "label": "Attention", "value": 55.0}
            ]
        }
        create_resp = await client.post("/api/diagrams", json=create_payload)
        assert create_resp.status_code == 200
        created = create_resp.json()
        diag_id = created["id"]
        assert created["title"] == "Integration Workflow Diagram"
        assert "<svg" in created["svg_content"]

        # Read detail
        get_resp = await client.get(f"/api/diagrams/{diag_id}")
        assert get_resp.status_code == 200
        fetched = get_resp.json()
        assert fetched["id"] == diag_id

        # List diagrams
        list_resp = await client.get("/api/diagrams")
        assert list_resp.status_code == 200
        listing = list_resp.json()
        assert any(d["id"] == diag_id for d in listing)

        # Export SVG
        export_resp = await client.get(f"/api/diagrams/{diag_id}/export/svg")
        assert export_resp.status_code == 200
        assert "image/svg+xml" in export_resp.headers["content-type"]

@pytest.mark.asyncio
async def test_lint_svg_endpoint():
    async with httpx.AsyncClient(transport=httpx.ASGITransport(app=app), base_url="http://test") as client:
        payload = {
            "svg_content": '<svg viewBox="0 0 100 100"><rect x="0" y="0" width="50" height="50"/></svg>'
        }
        resp = await client.post("/api/lint/svg", json=payload)
        assert resp.status_code == 200
        data = resp.json()
        assert data["is_compliant"] is True
        assert data["score"] == 100.0

@pytest.mark.asyncio
async def test_run_eval_and_audit_log(db_session):
    async with httpx.AsyncClient(transport=httpx.ASGITransport(app=app), base_url="http://test") as client:
        eval_resp = await client.post("/api/eval/run")
        assert eval_resp.status_code == 200
        summary = eval_resp.json()
        assert summary["total_samples"] == 20
        assert summary["pass_rate"] >= 95.0

        # Check audit log
        audit_resp = await client.get("/api/audit")
        assert audit_resp.status_code == 200
        audits = audit_resp.json()
        assert len(audits) >= 1
        assert any(a["action"] == "RUN_EVAL" for a in audits)
