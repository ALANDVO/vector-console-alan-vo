import json
from typing import Dict, Any, Optional
import httpx
from app.core.config import settings
from app.core.auth import redact_secrets
from app.models.diagram import AdvisoryRequest, AdvisoryResponse

class LLMClient:
    """Server-side provider-agnostic LLM adapter with bounded timeouts and credential redaction."""

    @classmethod
    async def generate_advisory(cls, request: AdvisoryRequest) -> AdvisoryResponse:
        api_key = settings.LLM_API_KEY
        provider = (request.provider or settings.LLM_PROVIDER).lower()
        model = request.model or settings.LLM_MODEL
        base_url = settings.LLM_BASE_URL

        # Grounding context from provided diagram spec or SVG
        grounding: Dict[str, Any] = {}
        if request.diagram_spec:
            grounding = {
                "diagram_type": request.diagram_spec.diagram_type.value,
                "title": request.diagram_spec.title,
                "zone_count": len(request.diagram_spec.zones),
                "node_count": len(request.diagram_spec.nodes),
                "dataviz_count": len(request.diagram_spec.dataviz_items)
            }
        elif request.raw_svg:
            grounding = {
                "input_type": "raw_svg",
                "byte_size": len(request.raw_svg.encode("utf-8"))
            }

        # Offline / deterministic fallback when key is unconfigured
        if not api_key:
            return AdvisoryResponse(
                advisory=True,
                provider=provider,
                model=model,
                content=(
                    f"[Deterministic Advisory Note - LLM_API_KEY not configured] "
                    f"To refine this {grounding.get('diagram_type', 'diagram')} design, ensure: "
                    f"1. Single-accent color palette is maintained with opacity ramps. "
                    f"2. All numeric values use monospace typography. "
                    f"3. Strict avoidance of drop-shadow filters. "
                    f"Configure LLM_API_KEY in server environment to enable live provider calls."
                ),
                grounded_evidence=grounding,
                error=None
            )

        prompt_system = (
            "You are an editorial vector diagram design advisor. "
            "You give concise, actionable critiques grounded strictly in honest-data rules, "
            "flat vector styling (no shadows, no gradients), and cloud containment invariants."
        )
        prompt_user = f"Context: {json.dumps(grounding)}\n\nQuery: {request.query}"

        try:
            async with httpx.AsyncClient(timeout=15.0) as client:
                if provider in ("openai", "openai-compatible", "ollama"):
                    headers = {
                        "Authorization": f"Bearer {api_key}",
                        "Content-Type": "application/json"
                    }
                    payload = {
                        "model": model,
                        "messages": [
                            {"role": "system", "content": prompt_system},
                            {"role": "user", "content": prompt_user}
                        ],
                        "temperature": 0.2
                    }
                    url = f"{base_url.rstrip('/')}/chat/completions"
                    resp = await client.post(url, headers=headers, json=payload)
                    resp.raise_for_status()
                    data = resp.json()
                    content = data["choices"][0]["message"]["content"]

                elif provider == "anthropic":
                    headers = {
                        "x-api-key": api_key,
                        "anthropic-version": "2023-06-01",
                        "Content-Type": "application/json"
                    }
                    payload = {
                        "model": model,
                        "max_tokens": 1024,
                        "system": prompt_system,
                        "messages": [{"role": "user", "content": prompt_user}]
                    }
                    url = f"{base_url.rstrip('/')}/v1/messages"
                    resp = await client.post(url, headers=headers, json=payload)
                    resp.raise_for_status()
                    data = resp.json()
                    content = data["content"][0]["text"]

                elif provider == "gemini":
                    url = f"{base_url.rstrip('/')}/models/{model}:generateContent?key={api_key}"
                    payload = {
                        "contents": [
                            {"role": "user", "parts": [{"text": f"{prompt_system}\n\n{prompt_user}"}]}
                        ]
                    }
                    resp = await client.post(url, json=payload)
                    resp.raise_for_status()
                    data = resp.json()
                    content = data["candidates"][0]["content"]["parts"][0]["text"]

                else:
                    return AdvisoryResponse(
                        advisory=True,
                        provider=provider,
                        model=model,
                        content="",
                        grounded_evidence=grounding,
                        error=f"Unsupported LLM provider: {provider}"
                    )

                return AdvisoryResponse(
                    advisory=True,
                    provider=provider,
                    model=model,
                    content=content,
                    grounded_evidence=grounding,
                    error=None
                )

        except Exception as e:
            # Redact secrets from error message
            safe_error = redact_secrets(str(e))
            return AdvisoryResponse(
                advisory=True,
                provider=provider,
                model=model,
                content="",
                grounded_evidence=grounding,
                error=f"LLM Provider Error: {safe_error}"
            )
