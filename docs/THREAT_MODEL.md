# AgentShield Threat Model (initial)

## Assets
- Organization documents and extracted text.
- User credentials and JWT signing secret.
- Provider API keys.
- Tool permissions and approval decisions.
- Audit traces and evaluation outputs.

## Trust boundaries
- Browser to API.
- User-uploaded files to ingestion pipeline.
- Retrieved document text to model context.
- Model-generated tool proposals to server-side policy.
- Organization A data versus organization B data.

## Threats and controls
| Threat | Initial control | Residual limitation |
|---|---|---|
| Cross-tenant document access | Organization scope from authenticated user | Add PostgreSQL RLS and isolation tests |
| Prompt injection in retrieved content | Evidence is labeled untrusted; tool actions are separately gated | Prompt instructions alone are not a security boundary |
| Secret leakage | DLP redaction on ingestion and output | Pattern matching misses some secrets; expand detectors |
| Unauthorized tool invocation | Server allowlist + role policy | Demo tools do not execute side effects |
| Malicious/oversized uploads | File extension allowlist + size cap | Add malware scanning and parser sandboxing |
| Credential theft | Password hashing + JWT | Add MFA, refresh rotation, secure cookies |
| Audit tampering | Database trace records | Add append-only storage / hash chaining |
| Model/provider outage | Adapter boundary | Add retries, circuit breaker, fallback model |
| Cost abuse | Usage tracking | Add rate limits and hard quotas |

## Security assumptions
- The API server and database host are trusted.
- TLS is provided by the deployment edge.
- Operators protect environment secrets.
- Users are not authorized to test third-party systems without permission.

## Out of scope for this initial implementation
Formal certification, regulatory compliance determination, high-assurance isolation, malware analysis, and guaranteed resistance to all prompt injection or jailbreak techniques.
