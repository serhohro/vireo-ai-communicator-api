```markdown
# 🌳 Vireo AST Specification

**Version:** 2.0.1  
**Status:** Draft  
**Last Updated:** 2026-01-15

---

## 1. Overview

The Abstract Syntax Tree (AST) represents the structure of Vireo programs in a machine-readable format.

---

## 2. AST Node Hierarchy
Program
├── ImportStmt
│ ├── name: string
│ └── alias: string (optional)
│
├── AgentDef
│ ├── name: string
│ ├── extends: string (optional)
│ ├── description: string (optional)
│ ├── capabilities: CapabilityDef[]
│ └── state: StateDef (optional)
│
├── ContractDef
│ ├── name: string
│ ├── parties: string[]
│ ├── terms: Terms
│ ├── obligations: Obligation[]
│ ├── condition: Expr (optional)
│ └── on_failure: string
│
├── ExecuteStmt
│ ├── contract_id: string
│ └── result_var: string (optional)
│
└── OutputStmt
└── value: Expr

text

---

## 3. Node Definitions

### Program

```python
@dataclass
class Program:
    imports: List[ImportStmt]
    agents: List[AgentDef]
    contracts: List[ContractDef]
    statements: List[Stmt]
ImportStmt
python
@dataclass
class ImportStmt:
    name: str
    alias: Optional[str] = None
AgentDef
python
@dataclass
class AgentDef:
    name: str
    extends: Optional[str] = None
    description: Optional[str] = None
    capabilities: List[CapabilityDef]
    state: Optional[StateDef] = None
CapabilityDef
python
@dataclass
class CapabilityDef:
    name: str
    inputs: List[ParamDef]
    output: Optional[ParamDef] = None
    action: Optional[str] = None
    cost: Optional[float] = None
    estimated_tokens: Optional[int] = None
    timeout_sec: Optional[int] = None
    requires: List[str] = field(default_factory=list)
    async_: bool = False
ParamDef
python
@dataclass
class ParamDef:
    name: str
    type: str
    default: Optional[Expr] = None
StateDef
python
@dataclass
class StateDef:
    fields: Dict[str, Expr]
ContractDef
python
@dataclass
class ContractDef:
    name: str
    parties: List[str]
    terms: Terms
    obligations: Dict[str, Obligation]
    condition: Optional[Expr] = None
    on_failure: str = "escalate"
Terms
python
@dataclass
class Terms:
    max_tokens: Optional[int] = None
    timeout_sec: Optional[int] = None
    max_cost_usd: Optional[float] = None
    max_rounds: Optional[int] = None
    deadline: Optional[str] = None
Obligation
python
@dataclass
class Obligation:
    action: str
    input: Dict[str, Expr]
    output: Optional[Dict[str, Expr]] = None
ExecuteStmt
python
@dataclass
class ExecuteStmt:
    contract_id: str
    result_var: Optional[str] = None
OutputStmt
python
@dataclass
class OutputStmt:
    value: Expr
4. Expressions
Expr Hierarchy
text
Expr
├── Literal
│   ├── StringLiteral
│   ├── NumberLiteral
│   ├── BooleanLiteral
│   └── NullLiteral
│
├── Reference
│   ├── VarRef
│   ├── FieldRef
│   └── ContractRef
│
├── Collection
│   ├── ArrayLiteral
│   └── ObjectLiteral
│
├── BinaryOp
│   ├── Add
│   ├── Sub
│   ├── Mul
│   ├── Div
│   ├── Eq
│   ├── Neq
│   ├── Lt
│   ├── Gt
│   ├── Le
│   ├── Ge
│   ├── And
│   └── Or
│
├── UnaryOp
│   ├── Neg
│   └── Not
│
├── Ternary
│   ├── condition: Expr
│   ├── true_expr: Expr
│   └── false_expr: Expr
│
└── Call
    ├── target: str
    └── args: Dict[str, Expr]
Node Definitions
python
# Literals
@dataclass
class StringLiteral:
    value: str

@dataclass
class NumberLiteral:
    value: float

@dataclass
class BooleanLiteral:
    value: bool

@dataclass
class NullLiteral:
    pass

# References
@dataclass
class VarRef:
    name: str

@dataclass
class FieldRef:
    target: Expr
    field: str

@dataclass
class ContractRef:
    contract_id: str
    field: str

# Collections
@dataclass
class ArrayLiteral:
    elements: List[Expr]

@dataclass
class ObjectLiteral:
    fields: Dict[str, Expr]

# Binary Operations
@dataclass
class BinaryOp:
    left: Expr
    right: Expr

@dataclass
class Add(BinaryOp): pass
@dataclass
class Sub(BinaryOp): pass
@dataclass
class Mul(BinaryOp): pass
@dataclass
class Div(BinaryOp): pass
@dataclass
class Eq(BinaryOp): pass
@dataclass
class Neq(BinaryOp): pass
@dataclass
class Lt(BinaryOp): pass
@dataclass
class Gt(BinaryOp): pass
@dataclass
class Le(BinaryOp): pass
@dataclass
class Ge(BinaryOp): pass
@dataclass
class And(BinaryOp): pass
@dataclass
class Or(BinaryOp): pass

# Unary Operations
@dataclass
class UnaryOp:
    operand: Expr

@dataclass
class Neg(UnaryOp): pass
@dataclass
class Not(UnaryOp): pass

# Ternary
@dataclass
class Ternary:
    condition: Expr
    true_expr: Expr
    false_expr: Expr

# Call
@dataclass
class Call:
    target: str
    args: Dict[str, Expr]
5. Type System
Types
python
from enum import Enum

class TypeKind(Enum):
    STRING = "string"
    NUMBER = "number"
    BOOLEAN = "boolean"
    JSON = "json"
    NULL = "null"
    ARRAY = "array"
    MAP = "map"
    AGENT = "agent"
    CONTRACT = "contract"
    CAPABILITY = "capability"

@dataclass
class Type:
    kind: TypeKind
    element_type: Optional['Type'] = None  # For arrays
    key_type: Optional['Type'] = None      # For maps
    value_type: Optional['Type'] = None    # For maps
Type Validation Rules
String: Any string literal

Number: Integer or float

Boolean: true or false

JSON: Valid JSON object

Array: All elements must have same type

Map: Keys must be strings

6. AST Validation
Validation Rules
python
def validate_ast(program: Program) -> bool:
    # 1. No duplicate agent names
    # 2. No duplicate contract names
    # 3. All capabilities have unique names within agent
    # 4. Contract parties must be valid agents
    # 5. Contract obligations must reference existing capabilities
    # 6. All references must resolve
    # 7. Types must match in assignments
    # 8. Contract terms must be positive
    pass
7. Serialization
JSON Serialization
json
{
  "type": "Program",
  "imports": [
    {"type": "ImportStmt", "name": "math"}
  ],
  "agents": [
    {
      "type": "AgentDef",
      "name": "analyzer",
      "capabilities": [
        {
          "type": "CapabilityDef",
          "name": "analyze",
          "inputs": [
            {"name": "image", "type": "string"}
          ],
          "output": {"name": "result", "type": "json"},
          "action": "Analyze image"
        }
      ]
    }
  ],
  "contracts": [],
  "statements": [
    {
      "type": "ExecuteStmt",
      "contract_id": "analysis_contract"
    }
  ]
}