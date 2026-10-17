# Changelog

## 1.1.0 — work-in-progress checkpoint

Partial code published for continued development. Known issues: STATUS.md.

## 1.1.0 — linter PaaS detection fix

- Fixed linter SVG PaaS-in-subnet detection: regex matched only "subnet" in zone IDs but zone IDs use "snet" abbreviation, causing zero matches.
- Extended linter to check all PAAS_SERVICES (azure_sql, key_vault, storage_account, cosmos_db, event_hub), not just azure_sql and key_vault.
- Added machine-verifiable data-azure-zone-tier attribute to rendered node elements for robust tier lookup.
- Added per-category baseline pass rate and average score to benchmark output.
- Fixed README benchmark table to reflect actual measured values (baseline 0.0%, not fabricated 20.0%).

## 1.0.0 — work-in-progress checkpoint

- Initial release of Vector Console: editorial diagram design and AI coding agent evaluation.
- Implemented deterministic editorial vector engine supporting cloud architecture containment, dataviz, and neural pipeline grammars.
- Added static linting suite enforcing honest-data rules, no-shadow styling, and machine-verifiable attributes.
- Implemented reproducible AI/ML diagram evaluation benchmark suite.
- Integrated Keycloak OIDC authentication architecture with local demo mode and opt-in multi-provider LLM adapters.
