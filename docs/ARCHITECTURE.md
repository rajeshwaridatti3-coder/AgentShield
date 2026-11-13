# AgentShield Architecture

## Design principles
1. The model is not an authority: deterministic server-side code decides whether a proposed action is allowed.
2. Tenant/workspace identifiers are derived from the authenticated user, never accepted from request payloads for data access.
3. Retrieval must provide evidence; local RAG abstains when no relevant context is found.
4. Evaluations are repeatable and narrowly scoped. Passing local control checks is not a claim of universal model safety.
5. Traces store operational metadata and avoid credential fields. User-facing execution summaries do not expose private chain-of-thought.
6. Incident reconstruction is read-only and does not repeat external side effects.

## Components
- **Experience:** React 18 + TypeScript + Vite dashboard.
- **API:** FastAPI, Pydantic validation, SQLAlchemy persistence.
- **Identity:** Argon2 password hashes, JWT access tokens, member/admin roles, environment-configured bootstrap administrator.
- **Workspace isolation:** organization-scoped document, trace, approval, usage and feature-record queries; memory is user-scoped. Workspace names cannot be reused at registration, preventing silent joining.
- **Ingestion:** allowlisted TXT/MD/PDF formats, byte-size limit, PDF text extraction, DLP redaction, chunking.
- **Retrieval:** lexical score + deterministic feature-hash similarity; local baseline is reproducible but not equivalent to neural semantic embeddings.
- **Generation:** local extractive provider or optional OpenAI-compatible chat completion adapter. Evidence is framed as untrusted input.
- **Policy:** server-side allowlist, role checks, sensitive argument rejection and approval records. No arbitrary command execution.
- **Agent workflow:** bounded supervisor/research/analysis/verification/security stages. Each stage emits structured data; no hidden reasoning is returned.
- **Trust controls:** DLP, memory expiration/deletion, claim evidence candidates, synthetic red-team checks and deterministic regression suite.
- **Governance:** framework crosswalk, dependency manifest inventory/hash and evidence records. These are not certifications or live vulnerability intelligence.
- **Observability:** trace events, latency, token estimates, local usage accounting and read-only incident reconstruction.
- **Persistence:** SQLite for local development; PostgreSQL in Docker Compose. Redis is included as an optional infrastructure service but no worker queue is required by the current synchronous paths.

## RAG request flow
1. Validate bearer token and resolve user/workspace.
2. Detect and redact sensitive markers in the question.
3. Load only workspace documents.
4. Rank document chunks using lexical and feature-hash similarity.
5. Build evidence context and call selected provider.
6. Treat retrieved text as untrusted; provider is instructed to answer only from evidence.
7. Redact sensitive markers from output, record usage and trace metadata, return citations.

## Multi-agent request flow
Supervisor receives a task → research gathers workspace-scoped chunks → analysis classifies evidence sufficiency → verification reports candidate support → security stage reports DLP and scope metadata. The final response is `evidence_ready` or `abstain`. This is a deterministic orchestrated workflow, not a claim of autonomous general intelligence.

## Trust boundaries
- Browser: untrusted; all permissions are enforced server-side.
- Uploaded files: untrusted; only allowlisted formats and size-limited extraction are accepted; extracted text is redacted before storage.
- Retrieved chunks: untrusted; content must not override system policy.
- Model output: untrusted; DLP is applied before returning it.
- Tool proposals: untrusted; allowlist policy authorizes or blocks them; no arbitrary tool execution exists.
- Feature records and traces: visible only within the authenticated workspace.

## Deployment hardening checklist
Configure strong secret and CORS origins, TLS, reverse-proxy rate limits, MFA and account recovery, managed secrets, database backups/restore drills, malware scanning, parser isolation, strict retention, immutable audit export, monitoring/alert delivery, a real embedding/vector service, and independent security review before internet-facing use.
