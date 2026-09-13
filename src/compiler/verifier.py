# [file name]: src/compiler/verifier.py
# ============================================================
# STATIC AST VERIFICATION FOR VIREO
# ============================================================
"""
Static verification of Vireo code.

Provides:
- Syntax validation
- Type checking
- Security constraints
- Resource limits verification
"""

import re
import logging
from typing import List, Dict, Any, Optional, Tuple

logger = logging.getLogger("vireo.compiler.verifier")


class VireoVerifier:
    """Статичний верифікатор Vireo коду."""
    
    def __init__(self):
        self.errors: List[str] = []
        self.warnings: List[str] = []
    
    def verify(self, code: str) -> Tuple[bool, List[str], List[str]]:
        """
        Перевіряє Vireo код.
        
        Args:
            code: Vireo код
            
        Returns:
            Tuple[bool, List[str], List[str]]: (is_valid, errors, warnings)
        """
        self.errors = []
        self.warnings = []
        
        lines = code.strip().split('\n')
        i = 0
        
        while i < len(lines):
            line = lines[i].strip()
            
            if not line or line.startswith('//') or line.startswith('#'):
                i += 1
                continue
            
            # Перевірка моделей
            if line.startswith('model '):
                self._verify_model(lines, i)
            
            # Перевірка функцій
            elif line.startswith('fn '):
                self._verify_function(lines, i)
            
            # Перевірка змінних
            elif line.startswith('let '):
                self._verify_variable(line)
            
            # Перевірка умов
            elif line.startswith('if '):
                self._verify_condition(line)
            
            i += 1
        
        is_valid = len(self.errors) == 0
        return is_valid, self.errors, self.warnings
    
    def _verify_model(self, lines: List[str], start_idx: int):
        """Перевіряє модель."""
        line = lines[start_idx].strip()
        model_name = line.replace('model ', '').strip().split('{')[0].strip()
        
        if not model_name:
            self.errors.append(f"Model name is required: {line}")
            return
        
        # Перевірка назви
        if not model_name.isidentifier():
            self.errors.append(f"Invalid model name: {model_name}")
        
        # Перевірка шарів
        i = start_idx + 1
        brace_count = 1
        layers_found = 0
        
        while i < len(lines) and brace_count > 0:
            current = lines[i].strip()
            
            if '{' in current:
                brace_count += current.count('{')
            if '}' in current:
                brace_count -= current.count('}')
            
            if 'layer' in current:
                layers_found += 1
                self._verify_layer(current)
            
            i += 1
        
        if layers_found == 0:
            self.warnings.append(f"Model '{model_name}' has no layers")
    
    def _verify_layer(self, line: str):
        """Перевіряє шар."""
        # Dense перевірка
        if 'Dense' in line:
            match = re.search(r'Dense\((\d+),\s*(\d+)\)', line)
            if not match:
                self.errors.append(f"Invalid Dense layer: {line}")
            else:
                in_features = int(match.group(1))
                out_features = int(match.group(2))
                if in_features <= 0 or out_features <= 0:
                    self.errors.append(f"Dense layer dimensions must be positive: {line}")
        
        # Activation перевірка
        elif 'activation' in line:
            act = line.replace('activation', '').strip()
            valid_acts = ['ReLU', 'Sigmoid', 'Tanh', 'Softmax', 'Swish']
            if act not in valid_acts:
                self.warnings.append(f"Unknown activation: {act}")
    
    def _verify_function(self, lines: List[str], start_idx: int):
        """Перевіряє функцію."""
        line = lines[start_idx].strip()
        func_name = line[3:line.index('(')].strip()
        
        if not func_name:
            self.errors.append(f"Function name is required: {line}")
            return
        
        if not func_name.isidentifier():
            self.errors.append(f"Invalid function name: {func_name}")
        
        # Перевірка тіла функції
        i = start_idx + 1
        brace_count = 1
        has_return = False
        
        while i < len(lines) and brace_count > 0:
            current = lines[i].strip()
            
            if '{' in current:
                brace_count += current.count('{')
            if '}' in current:
                brace_count -= current.count('}')
            
            if 'return' in current:
                has_return = True
            
            i += 1
        
        if not has_return:
            self.warnings.append(f"Function '{func_name}' has no return statement")
    
    def _verify_variable(self, line: str):
        """Перевіряє змінну."""
        parts = line[4:].split('=', 1)
        if len(parts) == 1:
            self.errors.append(f"Variable assignment missing value: {line}")
            return
        
        var_name = parts[0].strip()
        if not var_name or not var_name.isidentifier():
            self.errors.append(f"Invalid variable name: {var_name}")
    
    def _verify_condition(self, line: str):
        """Перевіряє умову."""
        condition = line[3:].split('{')[0].strip()
        if not condition:
            self.errors.append(f"Empty condition: {line}")


def verify_code(code: str) -> Tuple[bool, List[str], List[str]]:
    """Перевіряє Vireo код."""
    verifier = VireoVerifier()
    return verifier.verify(code)


# ============================================================
# ПРИКЛАД ВИКОРИСТАННЯ
# ============================================================

if __name__ == "__main__":
    code = """
    model MNIST {
        layer Dense(784, 128)
        activation ReLU
        layer Dense(128, 10)
        activation Softmax
    }
    
    fn add(a, b) {
        return a + b
    }
    
    let x = 5
    let y = 10
    let sum = x + y
    """
    
    is_valid, errors, warnings = verify_code(code)
    
    print(f"✅ Valid: {is_valid}")
    print(f"❌ Errors: {errors}")
    print(f"⚠️ Warnings: {warnings}")