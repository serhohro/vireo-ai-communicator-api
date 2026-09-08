# ============================================================
# VIREO PROTOCOL EXTENSIONS
# Protocol state machine and messaging
# ============================================================

PROTOCOL_GRAMMAR = """
// ============================================================
// PROTOCOL EXTENSIONS GRAMMAR
// ============================================================

protocol_def: "protocol" IDENTIFIER block

protocol_state: "state" IDENTIFIER block

protocol_transition: "transition" IDENTIFIER "->" IDENTIFIER ["when" expression]

protocol_message: "message" IDENTIFIER "(" [message_fields] ")"

message_fields: field ["," field]*
field: IDENTIFIER ":" type

protocol_handler: "on" IDENTIFIER block
"""


class ProtocolParser:
    def __init__(self):
        self.grammar = PROTOCOL_GRAMMAR
    
    def parse_protocol(self, name: str, states: list, transitions: list) -> dict:
        return {"name": name, "states": states, "transitions": transitions}
    
    def parse_message(self, name: str, fields: list) -> dict:
        return {"name": name, "fields": fields}


protocol_grammar = PROTOCOL_GRAMMAR