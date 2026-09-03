# ============================================================
# VIREO COMPILER OPTIMIZER
# ============================================================
"""
LLVM-based optimizer for Vireo code.

Provides:
- AST optimization passes
- Constant folding
- Dead code elimination
- Loop unrolling
- Inlining
- LLVM IR optimization
"""

import logging
from typing import List, Dict, Any, Optional
from dataclasses import dataclass, field

logger = logging.getLogger(__name__)


@dataclass
class OptimizationPass:
    """An optimization pass."""
    name: str
    description: str
    enabled: bool = True


class Optimizer:
    """
    LLVM-based optimizer for Vireo code.
    
    Features:
    - Multiple optimization passes
    - Constant propagation
    - Dead code elimination
    - Loop optimization
    - Function inlining
    """
    
    def __init__(self, optimization_level: int = 2):
        """
        Initialize optimizer.
        
        Args:
            optimization_level: 0 (none) to 3 (aggressive)
        """
        self.optimization_level = optimization_level
        self.passes: List[OptimizationPass] = []
        self._register_default_passes()
    
    def _register_default_passes(self):
        """Register default optimization passes."""
        passes = [
            ("constant_folding", "Fold constant expressions"),
            ("dead_code_elimination", "Remove unreachable code"),
            ("loop_unrolling", "Unroll small loops"),
            ("function_inlining", "Inline small functions"),
            ("common_subexpression_elimination", "Eliminate common subexpressions"),
            ("strength_reduction", "Replace expensive operations"),
            ("copy_propagation", "Propagate copies"),
            ("algebraic_identity", "Simplify algebraic expressions"),
        ]
        
        for name, desc in passes:
            self.passes.append(OptimizationPass(name, desc))
    
    def optimize(self, ast: Dict[str, Any]) -> Dict[str, Any]:
        """
        Optimize an AST.
        
        Args:
            ast: Abstract Syntax Tree
            
        Returns:
            Optimized AST
        """
        if self.optimization_level == 0:
            return ast
        
        # Apply passes
        optimized = ast
        
        # 1. Constant folding
        if self.optimization_level >= 1:
            optimized = self._fold_constants(optimized)
        
        # 2. Dead code elimination
        if self.optimization_level >= 1:
            optimized = self._eliminate_dead_code(optimized)
        
        # 3. Loop unrolling
        if self.optimization_level >= 2:
            optimized = self._unroll_loops(optimized)
        
        # 4. Function inlining
        if self.optimization_level >= 2:
            optimized = self._inline_functions(optimized)
        
        # 5. Common subexpression elimination
        if self.optimization_level >= 3:
            optimized = self._eliminate_common_subexpressions(optimized)
        
        return optimized
    
    def _fold_constants(self, node: Dict[str, Any]) -> Dict[str, Any]:
        """Fold constant expressions."""
        # Simple constant folding implementation
        if node.get("type") == "binary_op":
            left = node.get("left")
            right = node.get("right")
            
            if left and right:
                # Check if both sides are constants
                if left.get("type") == "number" and right.get("type") == "number":
                    op = node.get("op")
                    left_val = left.get("value", 0)
                    right_val = right.get("value", 0)
                    
                    if op == "+":
                        node["value"] = left_val + right_val
                        node["type"] = "number"
                        node.pop("left", None)
                        node.pop("right", None)
                        node.pop("op", None)
                    elif op == "-":
                        node["value"] = left_val - right_val
                        node["type"] = "number"
                        node.pop("left", None)
                        node.pop("right", None)
                        node.pop("op", None)
                    elif op == "*":
                        node["value"] = left_val * right_val
                        node["type"] = "number"
                        node.pop("left", None)
                        node.pop("right", None)
                        node.pop("op", None)
                    elif op == "/":
                        if right_val != 0:
                            node["value"] = left_val / right_val
                            node["type"] = "number"
                            node.pop("left", None)
                            node.pop("right", None)
                            node.pop("op", None)
        
        # Recurse into children
        for key, value in node.items():
            if isinstance(value, dict):
                node[key] = self._fold_constants(value)
            elif isinstance(value, list):
                node[key] = [self._fold_constants(item) if isinstance(item, dict) else item for item in value]
        
        return node
    
    def _eliminate_dead_code(self, node: Dict[str, Any]) -> Dict[str, Any]:
        """Eliminate dead code."""
        # Simple dead code elimination
        if node.get("type") == "block":
            statements = node.get("statements", [])
            # Remove statements after return
            for i, stmt in enumerate(statements):
                if stmt.get("type") == "return":
                    node["statements"] = statements[:i + 1]
                    break
        
        # Recurse into children
        for key, value in node.items():
            if isinstance(value, dict):
                node[key] = self._eliminate_dead_code(value)
            elif isinstance(value, list):
                node[key] = [self._eliminate_dead_code(item) if isinstance(item, dict) else item for item in value]
        
        return node
    
    def _unroll_loops(self, node: Dict[str, Any]) -> Dict[str, Any]:
        """Unroll small loops."""
        # Simple loop unrolling for small loops
        if node.get("type") == "for_loop":
            iterations = node.get("iterations", 0)
            body = node.get("body", {})
            
            # Unroll if iterations <= 4
            if iterations <= 4 and iterations > 0:
                # TODO: Implement full unrolling
                pass
        
        # Recurse into children
        for key, value in node.items():
            if isinstance(value, dict):
                node[key] = self._unroll_loops(value)
            elif isinstance(value, list):
                node[key] = [self._unroll_loops(item) if isinstance(item, dict) else item for item in value]
        
        return node
    
    def _inline_functions(self, node: Dict[str, Any]) -> Dict[str, Any]:
        """Inline small functions."""
        # Simple function inlining
        if node.get("type") == "function_call":
            function_name = node.get("name")
            # TODO: Look up function definition and inline if small
        
        # Recurse into children
        for key, value in node.items():
            if isinstance(value, dict):
                node[key] = self._inline_functions(value)
            elif isinstance(value, list):
                node[key] = [self._inline_functions(item) if isinstance(item, dict) else item for item in value]
        
        return node
    
    def _eliminate_common_subexpressions(self, node: Dict[str, Any]) -> Dict[str, Any]:
        """Eliminate common subexpressions."""
        # Simple CSE - track seen expressions
        seen = {}
        
        def process(n):
            if isinstance(n, dict):
                if n.get("type") == "binary_op":
                    # Create key from operation and operands
                    key = f"{n.get('op')}:{str(n.get('left'))}:{str(n.get('right'))}"
                    if key in seen:
                        # Replace with reference to previous result
                        return {"type": "reference", "name": seen[key]}
                    else:
                        seen[key] = f"__cse_{len(seen)}"
                
                # Process children
                for k, v in n.items():
                    if isinstance(v, dict):
                        n[k] = process(v)
                    elif isinstance(v, list):
                        n[k] = [process(item) if isinstance(item, dict) else item for item in v]
            return n
        
        return process(node)
    
    def optimize_llvm_ir(self, ir: str) -> str:
        """
        Optimize LLVM IR.
        
        Args:
            ir: LLVM IR string
            
        Returns:
            Optimized LLVM IR
        """
        try:
            import llvmlite.binding as llvm
            
            # Initialize LLVM
            llvm.initialize()
            llvm.initialize_native_target()
            llvm.initialize_native_asmprinter()
            
            # Parse IR
            module = llvm.parse_assembly(ir)
            module.verify()
            
            # Create pass manager
            pm = llvm.create_module_pass_manager()
            pm.add_analysis_passes()
            
            # Add optimization passes based on level
            if self.optimization_level >= 1:
                pm.add_instruction_combining_pass()
                pm.add_reassociation_pass()
            
            if self.optimization_level >= 2:
                pm.add_gvn_pass()
                pm.add_early_cse_pass()
            
            if self.optimization_level >= 3:
                pm.add_dead_store_elimination_pass()
                pm.add_licm_pass()
            
            # Run passes
            pm.run(module)
            
            # Return optimized IR
            return str(module)
            
        except ImportError:
            logger.warning("llvmlite not available, skipping LLVM optimization")
            return ir
        except Exception as e:
            logger.error(f"LLVM optimization error: {e}")
            return ir
    
    def get_pass_info(self) -> List[Dict[str, Any]]:
        """Get information about optimization passes."""
        return [
            {
                "name": p.name,
                "description": p.description,
                "enabled": p.enabled
            }
            for p in self.passes
            if p.enabled
        ]
    
    def get_stats(self) -> Dict[str, Any]:
        """Get optimizer statistics."""
        return {
            "optimization_level": self.optimization_level,
            "passes_count": len(self.passes),
            "enabled_passes": len([p for p in self.passes if p.enabled])
        }


# ============================================================
# OPTIMIZATION FUNCTIONS
# ============================================================

def create_optimizer(level: int = 2) -> Optimizer:
    """Create an optimizer with the specified level."""
    return Optimizer(optimization_level=level)


def optimize_code(code: str, level: int = 2) -> str:
    """
    Optimize Vireo code.
    
    Args:
        code: Vireo code
        level: Optimization level (0-3)
    
    Returns:
        Optimized code
    """
    # Parse code to AST
    # This is a placeholder - actual implementation would parse and optimize
    return code


def optimize_llvm(ir: str, level: int = 2) -> str:
    """
    Optimize LLVM IR.
    
    Args:
        ir: LLVM IR
        level: Optimization level (0-3)
    
    Returns:
        Optimized LLVM IR
    """
    optimizer = create_optimizer(level)
    return optimizer.optimize_llvm_ir(ir)


# ============================================================
# SINGLETON
# ============================================================

_default_optimizer: Optional[Optimizer] = None


def get_optimizer(level: int = 2) -> Optimizer:
    """Get the global optimizer instance."""
    global _default_optimizer
    if _default_optimizer is None:
        _default_optimizer = create_optimizer(level)
    return _default_optimizer