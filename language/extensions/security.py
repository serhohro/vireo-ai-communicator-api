# ============================================================
# VIREO SECURITY EXTENSIONS
# Security, encryption, signatures
# ============================================================

SECURITY_GRAMMAR = """
// ============================================================
// SECURITY EXTENSIONS GRAMMAR
// ============================================================

security_policy: "security" block

encryption: "encrypt" "(" expression "," expression ")"

decryption: "decrypt" "(" expression "," expression ")"

signature: "sign" "(" expression "," expression ")"

verification: "verify" "(" expression "," expression "," expression ")"

did: "did:" IDENTIFIER ":" IDENTIFIER

trust: "trust" ":" expression

permission: "permission" IDENTIFIER ":" IDENTIFIER
"""


class SecurityParser:
    def __init__(self):
        self.grammar = SECURITY_GRAMMAR
    
    def parse_encryption(self, data: str, key: str) -> dict:
        return {"type": "encrypt", "data": data, "key": key}
    
    def parse_signature(self, data: str, key: str) -> dict:
        return {"type": "sign", "data": data, "key": key}


security_grammar = SECURITY_GRAMMAR