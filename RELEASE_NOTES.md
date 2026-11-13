# AgentShield 1.0.0 — release contents

This release integrates the dashboard and backend modules listed in `docs/FEATURES.md`.

- Added persisted feature records and platform dashboard endpoints.
- Added structured multi-stage agent workflow and claim evidence candidate endpoint.
- Added interactive DLP scan, memory governance, governance register, local supply-chain inventory, regression evaluation and read-only incident reconstruction.
- Reworked the synthetic red-team suite so each reported pass corresponds to a deterministic local control check; persisted run history is available.
- Added Argon2 password hashing, configurable bootstrap admin, workspace-name uniqueness on registration, production secret guard and configurable CORS origins.
- Redacts sensitive markers from chat questions before retrieval/provider submission and from generated answers before returning them.
- Added implementation map and updated architecture and run instructions.

Verification in the build environment: Python compilation succeeded and 7 backend service tests passed. The frontend dependency installation did not complete in this environment, so a Vite production build was not verified here. Install frontend dependencies on the target laptop and run `npm run build` as part of local verification.
