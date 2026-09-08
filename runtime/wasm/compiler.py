# ============================================================
# VIREO WASM COMPILER
# Компіляція в WebAssembly
# ============================================================

from dataclasses import dataclass, field
from typing import Dict, Any, Optional, List
import logging

logger = logging.getLogger(__name__)

try:
    import wasmtime
    WASMTIME_AVAILABLE = True
except ImportError:
    WASMTIME_AVAILABLE = False
    logger.warning("wasmtime not installed. WASM features disabled.")


@dataclass
class WASMConfig:
    """Конфігурація WASM."""
    optimize: bool = True
    debug: bool = False
    target: str = "wasm32-unknown-unknown"
    features: List[str] = field(default_factory=list)
    memory_pages: int = 1
    max_memory_pages: int = 100


class WASMCompiler:
    """
    Компілятор Vireo в WASM.
    
    Перетворює AST в WebAssembly модуль.
    """
    
    def __init__(self, config: Optional[WASMConfig] = None):
        self.config = config or WASMConfig()
        self._available = WASMTIME_AVAILABLE
    
    def compile(self, ast) -> bytes:
        """
        Компілює AST в WASM.
        
        Args:
            ast: AST
            
        Returns:
            bytes: WASM модуль
        """
        if not self._available:
            raise RuntimeError("WASM not available")
        
        # Спрощена реалізація
        wasm_code = self._generate_wasm(ast)
        return self._compile_wasm(wasm_code)
    
    def _generate_wasm(self, ast) -> str:
        """Генерує WASM текстовий формат."""
        lines = [
            "(module",
            '  (import "env" "print" (func $print (param i32)))',
            "  (memory $mem 1)",
            "  (export "memory" (memory $mem))",
        ]
        
        # Генеруємо код
        lines.extend(self._generate_code(ast))
        
        lines.append(")")
        return "\n".join(lines)
    
    def _generate_code(self, ast) -> List[str]:
        """Генерує код з AST."""
        lines = []
        
        # Спрощена реалізація
        lines.extend([
            '  (func $main (export "main")',
            '    (i32.const 42)',
            '    (call $print)',
            '  )',
        ])
        
        return lines
    
    def _compile_wasm(self, wasm_text: str) -> bytes:
        """Компілює WASM текст у байти."""
        if not WASMTIME_AVAILABLE:
            return b""
        
        try:
            # Використовуємо wasmtime для компіляції
            engine = wasmtime.Engine()
            module = wasmtime.Module(engine, wasm_text)
            return module.serialize()
        except Exception as e:
            logger.error(f"WASM compilation failed: {e}")
            return b""
    
    def is_available(self) -> bool:
        """Перевіряє доступність WASM."""
        return self._available


def compile_to_wasm(ast) -> bytes:
    """Зручна функція для компіляції в WASM."""
    compiler = WASMCompiler()
    return compiler.compile(ast)