import re

PATTERNS = {
    "email": re.compile(r"\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}\b"),
    "phone": re.compile(r"(?<!\w)(?:\+?\d[\d .()-]{7,}\d)(?!\w)"),
    "api_key_like": re.compile(r"\b(?:sk-[A-Za-z0-9_-]{16,}|AKIA[A-Z0-9]{16})\b"),
    "private_key": re.compile(r"-----BEGIN (?:RSA |EC |OPENSSH )?PRIVATE KEY-----[\s\S]*?-----END (?:RSA |EC |OPENSSH )?PRIVATE KEY-----"),
}

def detect_sensitive(text: str) -> list[dict]:
    findings = []
    for kind, pattern in PATTERNS.items():
        for match in pattern.finditer(text):
            findings.append({"type": kind, "start": match.start(), "end": match.end()})
    return findings

def redact_sensitive(text: str) -> tuple[str, list[dict]]:
    findings = detect_sensitive(text)
    redacted = text
    for item in sorted(findings, key=lambda x: x["start"], reverse=True):
        redacted = redacted[:item["start"]] + f"[REDACTED:{item['type']}]" + redacted[item["end"]:]
    return redacted, findings
