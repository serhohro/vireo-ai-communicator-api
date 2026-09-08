# ============================================================
# VIREO LLVM BACKEND
# LLVM IR генерація та JIT компіляція
# ============================================================

import ctypes
from dataclasses import dataclass, field
from typing import Dict, Any, Optional, List, Tuple, Union
import subprocess
import tempfile
import os
import logging

from ..context import RuntimeContext, get_context

logger = logging.getLogger(__name__)

try:
    import llvmlite.ir as ir
    import llvmlite.binding as llvm
    from llvmlite import ir as llvm_ir
    LLVM_AVAILABLE = True
except ImportError:
    LLVM_AVAILABLE = False
    logger.warning("llvmlite not installed. JIT features disabled.")


@dataclass
class LLVMConfig:
    """Конфігурація LLVM."""
    optimization_level: int = 2
    target_machine: Optional[str] = None
    enable_jit: bool = True
    enable_opt_passes: bool = True
    enable_debug: bool = False
    triple: str = "x86_64-pc-linux-gnu"
    cpu: str = "native"
    features: List[str] = field(default_factory=list)


class LLVMBackend:
    """
    LLVM Backend для Vireo.
    
    Генерує LLVM IR та компілює в машинний код.
    """
    
    def __init__(self, config: Optional[LLVMConfig] = None):
        self.config = config or LLVMConfig()
        self._module: Optional['ir.Module'] = None
        self._builder: Optional['ir.IRBuilder'] = None
        self._context = get_context()
        
        if LLVM_AVAILABLE:
            self._init_llvm()
        else:
            self._available = False
            logger.warning("LLVM backend not available")
    
    def _init_llvm(self):
        """Ініціалізація LLVM."""
        if not LLVM_AVAILABLE:
            return
        
        llvm.initialize()
        llvm.initialize_native_target()
        llvm.initialize_native_asmprinter()
        
        self._module = ir.Module(name="vireo_module")
        self._builder = ir.IRBuilder()
        
        # Налаштовуємо ціль
        if self.config.triple:
            self._module.triple = self.config.triple
        
        if self.config.target_machine:
            target = llvm.Target.from_default_triple()
            tm = target.create_target_machine(
                cpu=self.config.cpu,
                features=self.config.features,
                opt_level=self.config.optimization_level
            )
            self._module.data_layout = tm.target_data
        
        self._available = True
        logger.info("LLVM backend initialized")
    
    def create_module(self, name: str = "vireo_module") -> 'ir.Module':
        """Створює LLVM модуль."""
        if not self._available:
            raise RuntimeError("LLVM not available")
        
        module = ir.Module(name=name)
        module.triple = self.config.triple
        return module
    
    def compile_function(
        self,
        func_name: str,
        args: List[Tuple[str, 'ir.Type']],
        return_type: 'ir.Type',
        body: List[str],
    ) -> bytes:
        """
        Компілює функцію в машинний код.
        
        Args:
            func_name: Ім'я функції
            args: Аргументи (ім'я, тип)
            return_type: Тип повернення
            body: Тіло функції (LLVM IR рядки)
            
        Returns:
            bytes: Машинний код
        """
        if not self._available:
            raise RuntimeError("LLVM not available")
        
        module = self.create_module(f"vireo_{func_name}")
        
        # Створюємо функцію
        func_type = ir.FunctionType(return_type, [t for _, t in args])
        func = ir.Function(module, func_type, name=func_name)
        
        # Додаємо аргументи
        for (arg_name, _), arg in zip(args, func.args):
            arg.name = arg_name
        
        # Будуємо тіло
        builder = ir.IRBuilder()
        builder.position_at_end(ir.Block(func, "entry"))
        
        for line in body:
            # Парсимо та додаємо інструкції
            # (спрощена реалізація)
            pass
        
        # Повертаємо результат
        builder.ret(builder.add(func.args[0], func.args[1]))
        
        # Компілюємо
        return self.compile_module(module)
    
    def compile_module(self, module: 'ir.Module') -> bytes:
        """
        Компілює LLVM модуль в машинний код.
        
        Args:
            module: LLVM модуль
            
        Returns:
            bytes: Машинний код
        """
        if not self._available:
            raise RuntimeError("LLVM not available")
        
        # Оптимізація
        ir_str = str(module)
        if self.config.enable_opt_passes:
            ir_str = self.optimize_ir(ir_str)
        
        # Компіляція
        target = llvm.Target.from_default_triple()
        tm = target.create_target_machine(
            cpu=self.config.cpu,
            features=self.config.features,
            opt_level=self.config.optimization_level
        )
        
        # Парсинг та компіляція
        llvm_module = llvm.parse_assembly(ir_str)
        llvm_module.verify()
        
        # Оптимізація модуля
        pm = llvm.create_module_pass_manager()
        pm.add_constant_merge_pass()
        if self.config.optimization_level >= 1:
            pm.add_licm_pass()
        if self.config.optimization_level >= 2:
            pm.add_gvn_pass()
        pm.run(llvm_module)
        
        # Машинний код
        return tm.emit_object(llvm_module)
    
    def optimize_ir(self, ir_str: str) -> str:
        """Оптимізує LLVM IR."""
        if not self._available:
            return ir_str
        
        try:
            # Парсимо в модуль
            module = llvm.parse_assembly(ir_str)
            
            # Оптимізація
            pm = llvm.create_module_pass_manager()
            pm.add_constant_merge_pass()
            pm.add_licm_pass()
            pm.add_gvn_pass()
            pm.run(module)
            
            return str(module)
        except Exception as e:
            logger.error(f"Optimization failed: {e}")
            return ir_str
    
    def execute_native(self, code: bytes, func_name: str, *args) -> Any:
        """
        Виконує скомпільований код.
        
        Args:
            code: Машинний код
            func_name: Ім'я функції
            *args: Аргументи
            
        Returns:
            Any: Результат виконання
        """
        # Записуємо в тимчасовий файл
        with tempfile.NamedTemporaryFile(suffix='.o', delete=False) as f:
            f.write(code)
            obj_path = f.name
        
        try:
            # Компілюємо в shared library
            so_path = obj_path.replace('.o', '.so')
            cmd = [
                'gcc', '-shared', '-o', so_path, obj_path,
                '-fPIC', '-O2'
            ]
            subprocess.run(cmd, check=True, capture_output=True)
            
            # Завантажуємо
            lib = ctypes.CDLL(so_path)
            func = getattr(lib, func_name)
            
            # Викликаємо
            return func(*args)
        finally:
            # Чистимо
            for path in [obj_path, so_path]:
                if os.path.exists(path):
                    os.unlink(path)
    
    def is_available(self) -> bool:
        """Перевіряє доступність LLVM."""
        return self._available


def compile_to_llvm(ast, backend: Optional[LLVMBackend] = None) -> str:
    """
    Компілює AST в LLVM IR.
    
    Args:
        ast: AST
        backend: LLVM Backend
        
    Returns:
        str: LLVM IR
    """
    if backend is None:
        backend = LLVMBackend()
    
    # Спрощена реалізація
    module = backend.create_module("vireo_compiled")
    
    # Додаємо main функцію
    i32 = ir.IntType(32)
    func_type = ir.FunctionType(i32, [])
    func = ir.Function(module, func_type, name="main")
    block = ir.Block(func, "entry")
    builder = ir.IRBuilder()
    builder.position_at_end(block)
    builder.ret(ir.Constant(i32, 0))
    
    return str(module)


def compile_to_native(ast, backend: Optional[LLVMBackend] = None) -> bytes:
    """Компілює AST в машинний код."""
    if backend is None:
        backend = LLVMBackend()
    
    ir_str = compile_to_llvm(ast, backend)
    return backend.compile_module(ir_str)


def optimize_ir(ir_str: str, backend: Optional[LLVMBackend] = None) -> str:
    """Оптимізує LLVM IR."""
    if backend is None:
        backend = LLVMBackend()
    return backend.optimize_ir(ir_str)