# AgentShield feature implementation map

| Feature | Backend implementation | Dashboard | Persistence / evidence |
|---|---|---|---|
| Authentication / roles | `api/auth.py`, `core/security.py` | Login / registration | `users` |
| Secure document RAG | `api/documents.py`, `api/chat.py`, `services/retrieval.py`, `services/llm.py` | Documents, RAG Assistant | `documents`, `usage`, `traces` |
| Policy firewall / approvals | `services/policy.py`, `api/tools.py` | Policy & Approvals | `approvals`, `traces` |
| DLP | `services/dlp.py`, `api/platform.py` | DLP Scanner | `feature_records`, `traces` |
| Memory governance | `api/memory.py` | Memory Governance | `memories` |
| Multi-agent orchestration | `api/platform.py` (`/agents/run`) | Agent Workflow | `feature_records`, `traces` |
| Claim verification | `api/platform.py` (`/claims/verify`) | Claim Verification | `feature_records` |
| Red-team checks | `services/evaluation.py`, `api/redteam.py` | Red Team Lab | `feature_records`, `traces` |
| Regression evaluation | `api/platform.py` (`/evaluations/run`) | Evaluation Lab | `feature_records` |
| Governance crosswalk | `api/platform.py` (`/governance`) | Governance Center | feature evidence register |
| Supply-chain inventory | `api/platform.py` (`/supply-chain/scan`) | Supply Chain | `feature_records` |
| Incident reconstruction | `api/platform.py` (`/incidents/replay`) | Incident Replay | `feature_records` |
| Observability | `api/observability.py`, `services/tracing.py` | Observability | `traces`, `usage` |

All platform records are scoped by the authenticated user's workspace. Memory records are additionally scoped by user ID. The application deliberately exposes structured execution summaries rather than private chain-of-thought. Tool proposals are not executed as arbitrary external actions.
