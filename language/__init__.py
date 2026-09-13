# ============================================================
# VIREO LANGUAGE MODULE
# Vireo Language v3.0.0
# ============================================================
#
# Core components:
#   - Lexer: Tokenization
#   - Parser: Vireo → AST (Lark-based)
#   - AST: Abstract Syntax Tree
#   - Semantic: Semantic analysis
#   - Compiler: AST → Python/WASM/LLVM
#   - Grammar: Lark EBNF grammar
#
# Usage:
#   from language import parse, tokenize, compile_to_python
#   from language import NodeType, AST, ASTNode
#   from language.extensions import MLParser, TensorParser
#
# ============================================================

__version__ = "3.0.0"
__author__ = "Serhii (serhohro)"
__license__ = "Apache 2.0"

# ============================================================
# CORE МОДУЛІ
# ============================================================

from .lexer import (
    Lexer,
    Token,
    TokenType,
    tokenize,
)

from .parser import (
    Parser,
    parse,
)

from .ast import (
    AST,
    ASTNode,
    NodeType,
)

from .grammar_core import (
    grammar,
    LarkParser,
)

from .semantic import (
    SemanticAnalyzer,
    Symbol,
    SymbolKind,
    Scope,
    analyze,
)

from .compiler import (
    Compiler,
    compile_to_python,
    compile_to_wasm,
    compile_to_llvm,
    compile_to_bytecode,
)

# ============================================================
# ДОДАТКОВІ МОДУЛІ
# ============================================================

try:
    from .optimizer import (
        Optimizer,
        optimize,
    )
except ImportError:
    pass

try:
    from .codegen import (
        CodeGenerator,
        generate_code,
    )
except ImportError:
    pass

try:
    from .validator import (
        Validator,
        validate,
    )
except ImportError:
    pass

# ============================================================
# РОЗШИРЕННЯ (Extensions)
# ============================================================

from .extensions import (
    MLParser,
    ml_grammar,
    TensorParser,
    tensor_grammar,
    VisionParser,
    vision_grammar,
    NLPParser,
    nlp_grammar,
    ProtocolParser,
    protocol_grammar,
    SecurityParser,
    security_grammar,
)

# ============================================================
# СТАНДАРТНА БІБЛІОТЕКА
# ============================================================

from .stdlib import (
    math,
    tensor,
    agent,
    contract,
    crypto,
    network,
    io,
    protocol,
    neural,
    security,
)

# ============================================================
# ЕКСПОРТИ
# ============================================================

__all__ = [
    "__version__",
    "__author__",
    "__license__",
    "Lexer",
    "Token",
    "TokenType",
    "tokenize",
    "Parser",
    "parse",
    "AST",
    "ASTNode",
    "NodeType",
    "grammar",
    "LarkParser",
    "SemanticAnalyzer",
    "Symbol",
    "SymbolKind",
    "Scope",
    "analyze",
    "Compiler",
    "compile_to_python",
    "compile_to_wasm",
    "compile_to_llvm",
    "compile_to_bytecode",
    "Optimizer",
    "optimize",
    "CodeGenerator",
    "generate_code",
    "Validator",
    "validate",
    "MLParser",
    "ml_grammar",
    "TensorParser",
    "tensor_grammar",
    "VisionParser",
    "vision_grammar",
    "NLPParser",
    "nlp_grammar",
    "ProtocolParser",
    "protocol_grammar",
    "SecurityParser",
    "security_grammar",
    "math",
    "tensor",
    "agent",
    "contract",
    "crypto",
    "network",
    "io",
    "protocol",
    "neural",
    "security",
]

# ============================================================
# ЗРУЧНІ ФУНКЦІЇ
# ============================================================

def compile_source(source: str, target: str = "python") -> str:
    """Компілює Vireo код у цільову мову."""
    from .parser import parse
    from .semantic import analyze
    from .compiler import Compiler
    
    ast = parse(source)
    analyzer = SemanticAnalyzer()
    analyzer.analyze(ast)
    compiler = Compiler()
    
    if target == "python":
        return compile_to_python(ast)
    elif target == "wasm":
        return compile_to_wasm(ast)
    elif target == "llvm":
        return compile_to_llvm(ast)
    elif target == "bytecode":
        return compile_to_bytecode(ast)
    else:
        raise ValueError(f"Unknown target: {target}")

def get_version() -> str:
    return __version__

def get_info() -> dict:
    return {
        "name": "Vireo",
        "version": __version__,
        "author": __author__,
        "license": __license__,
        "description": "The World's First AI-to-AI Communication Language",
        "features": [
            "AI-to-AI communication",
            "Protocol state machine",
            "Cryptographic security",
            "ML/Neural network support",
            "Multi-agent orchestration",
            "Smart contracts",
            "Tensor operations"
        ],
        "extensions": [
            "ML (machine learning)",
            "Tensor operations",
            "Vision (computer vision)",
            "NLP (natural language processing)",
            "Protocol",
            "Security"
        ],
        "stdlib": [
            "math", "tensor", "agent", "contract", "crypto",
            "network", "io", "protocol", "neural", "security"
        ]
    }

def _check_imports():
    import importlib
    imports = ["lexer", "parser", "ast", "grammar_core", "semantic", "compiler", "extensions", "stdlib"]
    missing = []
    for module in imports:
        try:
            importlib.import_module(f"language.{module}")
        except ImportError:
            missing.append(module)
    if missing:
        print(f"⚠️ Missing modules: {', '.join(missing)}")
        return False
    return True

_check_imports()

if __name__ == "__main__":
    print(f"Vireo Language v{__version__}")
    print(f"Author: {__author__}")
    print(f"License: {__license__}")
    print()
    print("Available modules:")
    for module in __all__:
        if not module.startswith("_"):
            print(f"  - {module}")
    print()
    print("Usage:")
    print("  from language import parse, compile_to_python")
    print("  from language.extensions import MLParser")
    print("  from language.stdlib import math, tensor")