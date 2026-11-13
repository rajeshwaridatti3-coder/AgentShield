# Architecture Decision Records

## ADR-001: FastAPI for the API
**Decision:** Use FastAPI and Pydantic.  
**Reason:** Strong Python ecosystem for AI orchestration, typed request contracts and generated API docs.

## ADR-002: PostgreSQL as deployment database; SQLite for local quick start
**Decision:** Support both through SQLAlchemy.  
**Reason:** Easy local onboarding with a path to a robust relational database.

## ADR-003: Server-side policy enforcement
**Decision:** Tool proposals are checked by deterministic server policy before any execution.  
**Reason:** LLM output is untrusted and cannot grant itself permissions.

## ADR-004: Local deterministic mode by default
**Decision:** The app runs without external AI credentials.  
**Reason:** Reproducible development, safer onboarding and easy reviewer demonstration. Real provider mode is opt-in.

## ADR-005: Evidence-grounded generation
**Decision:** Context is retrieved from organization-scoped documents and citations are returned.  
**Reason:** Answers should be inspectable and unsupported questions should abstain.
