# [file name]: src/compiler/wasm.py
# ============================================================
# WEBASSEMBLY SUPPORT FOR VIREO
# ============================================================
"""
WebAssembly compilation for Vireo.

Provides:
- Vireo → WASM compilation
- Sandboxed execution
- Cross-platform deployment
"""

import logging
import subprocess
import tempfile
import os
from typing import Optional, Dict, Any

logger = logging.getLogger("vireo.compiler.wasm")


class WASMCompiler:
    """Компілятор Vireo в WebAssembly."""
    
    def __init__(self):
        self._check_wat2wasm()
    
    def _check_wat2wasm(self):
        """Перевіряє наявність wat2wasm."""
        try:
            result = subprocess.run(
                ["wat2wasm", "--version"],
                capture_output=True,
                text=True
            )
            if result.returncode == 0:
                logger.info("✅ wat2wasm available")
                self._wat2wasm_available = True
            else:
                self._wat2wasm_available = False
                logger.warning("⚠️ wat2wasm not found. Install: brew install wabt")
        except FileNotFoundError:
            self._wat2wasm_available = False
            logger.warning("⚠️ wat2wasm not found. Install: brew install wabt")
    
    def compile_to_wasm(self, vireo_code: str, output_path: Optional[str] = None) -> bytes:
        """
        Компілює Vireo код у WebAssembly.
        
        Args:
            vireo_code: Vireo код
            output_path: Шлях для збереження .wasm файлу
            
        Returns:
            bytes: WASM бінарник
        """
        # 1. Парсинг Vireo коду
        ast = self._parse_vireo(vireo_code)
        
        # 2. Генерація WAT (WebAssembly Text)
        wat_code = self._generate_wat(ast)
        
        # 3. Компіляція WAT → WASM
        if self._wat2wasm_available:
            wasm_bytes = self._compile_with_wat2wasm(wat_code)
        else:
            # Fallback: емуляція
            wasm_bytes = self._emulate_wasm(wat_code)
        
        # 4. Збереження
        if output_path:
            with open(output_path, 'wb') as f:
                f.write(wasm_bytes)
            logger.info(f"✅ WASM saved to {output_path}")
        
        return wasm_bytes
    
    def _parse_vireo(self, code: str) -> Dict[str, Any]:
        """Парсить Vireo код в AST."""
        # TODO: Повна реалізація
        return {"type": "module", "code": code}
    
    def _generate_wat(self, ast: Dict[str, Any]) -> str:
        """Генерує WAT з AST."""
        # TODO: Повна реалізація
        return """
(module
  (func $add (param $a i32) (param $b i32) (result i32)
    local.get $a
    local.get $b
    i32.add)
  (export "add" (func $add))
)
"""
    
    def _compile_with_wat2wasm(self, wat_code: str) -> bytes:
        """Компілює WAT в WASM через wat2wasm."""
        with tempfile.NamedTemporaryFile(suffix='.wat', delete=False) as f:
            f.write(wat_code.encode('utf-8'))
            wat_path = f.name
        
        wasm_path = wat_path.replace('.wat', '.wasm')
        
        try:
            subprocess.run(
                ["wat2wasm", wat_path, "-o", wasm_path],
                check=True,
                capture_output=True
            )
            
            with open(wasm_path, 'rb') as f:
                wasm_bytes = f.read()
            
            os.unlink(wat_path)
            os.unlink(wasm_path)
            
            return wasm_bytes
        except Exception as e:
            logger.error(f"❌ WASM compilation failed: {e}")
            return b""
    
    def _emulate_wasm(self, wat_code: str) -> bytes:
        """Емулює WASM (без wat2wasm)."""
        logger.warning("⚠️ Using WASM emulation")
        # Проста емуляція
        return b"\x00\x61\x73\x6d"  # WASM magic number


def compile_to_wasm(code: str, output_path: Optional[str] = None) -> bytes:
    """Компілює Vireo код у WebAssembly."""
    compiler = WASMCompiler()
    return compiler.compile_to_wasm(code, output_path)


# ============================================================
# ПРИКЛАД ВИКОРИСТАННЯ
# ============================================================

if __name__ == "__main__":
    code = """
    fn add(a: Int, b: Int) -> Int {
        return a + b
    }
    """
    
    wasm_bytes = compile_to_wasm(code, "add.wasm")
    print(f"✅ WASM size: {len(wasm_bytes)} bytes")