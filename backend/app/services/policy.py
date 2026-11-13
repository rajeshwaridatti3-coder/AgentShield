from dataclasses import dataclass

@dataclass
class PolicyDecision:
    allowed: bool
    requires_approval: bool
    reason: str

# Explicit allowlist: no arbitrary shell, Python, filesystem or network tools.
TOOL_POLICIES = {
    "search_documents": {"roles": {"member", "admin"}, "approval": False},
    "export_report": {"roles": {"admin"}, "approval": True},
    "delete_document": {"roles": set(), "approval": True},
}

def evaluate_tool(user, tool_name: str, arguments: dict) -> PolicyDecision:
    policy = TOOL_POLICIES.get(tool_name)
    if not policy:
        return PolicyDecision(False, False, "Tool is not registered")
    if user.role not in policy["roles"]:
        return PolicyDecision(False, False, "User role is not authorized for this tool")
    if any(k.lower() in {"password", "secret", "api_key", "token"} for k in arguments):
        return PolicyDecision(False, False, "Sensitive arguments are not accepted")
    return PolicyDecision(True, policy["approval"], "Authorized by server-side policy")
