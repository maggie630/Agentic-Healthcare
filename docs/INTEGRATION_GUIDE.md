# Integration guide for the main repository

This package was authored independently because the original private repository was unavailable. No integration has been performed or verified.

1. Ask AKAASH for repository access and current `AGENTS.md` / PR conventions.
2. Get approval for `data/SCHEMA.md` before freezing fields.
3. Compare current `app/agents/*`, orchestrator registration, test fakes and dependencies with this implementation.
4. Confirm database choice, record payload shape, per-field confidence representation, MCP transport and approval identity contract.
5. Integrate only on a feature branch. Keep `main` protected and use a draft PR.
6. Have CHARAN call `save_record_draft` through the agreed MCP contract; do not give digitization direct database access.
7. Keep VARSHINI policy retrieval isolated from patient records.
8. Run the original repository test suite and this module's tests after integration.

Do not copy this package over the original repo blindly; reconcile interfaces first.
