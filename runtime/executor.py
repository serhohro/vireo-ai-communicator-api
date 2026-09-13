# ============================================================
# VIREO RUNTIME EXECUTOR
# Виконання коду та задач
# ============================================================

import asyncio
import time
import threading
from enum import Enum
from dataclasses import dataclass, field
from typing import Dict, Any, Optional, Callable, List, Union, Awaitable
from concurrent.futures import ThreadPoolExecutor, ProcessPoolExecutor
import logging

from .context import RuntimeContext, get_context
from ..core.errors import VireoRuntimeError, VireoTimeoutError

logger = logging.getLogger(__name__)


class ExecutionStatus(Enum):
    """Статус виконання."""
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    TIMEOUT = "timeout"
    CANCELLED = "cancelled"


class ExecutionMode(Enum):
    """Режим виконання."""
    SYNC = "sync"
    ASYNC = "async"
    THREAD = "thread"
    PROCESS = "process"


@dataclass
class ExecutionResult:
    """Результат виконання."""
    status: ExecutionStatus
    result: Optional[Any] = None
    error: Optional[Exception] = None
    start_time: Optional[float] = None
    end_time: Optional[float] = None
    duration: float = 0.0
    memory_used: int = 0
    cpu_used: float = 0.0
    metadata: Dict[str, Any] = field(default_factory=dict)

    @property
    def is_success(self) -> bool:
        return self.status == ExecutionStatus.COMPLETED

    @property
    def is_failure(self) -> bool:
        return self.status in (ExecutionStatus.FAILED, ExecutionStatus.TIMEOUT, ExecutionStatus.CANCELLED)

    @property
    def is_complete(self) -> bool:
        return self.status in (ExecutionStatus.COMPLETED, ExecutionStatus.FAILED, 
                              ExecutionStatus.TIMEOUT, ExecutionStatus.CANCELLED)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "status": self.status.value,
            "result": self.result,
            "error": str(self.error) if self.error else None,
            "duration": self.duration,
            "memory_used": self.memory_used,
            "cpu_used": self.cpu_used,
            "metadata": self.metadata,
        }


class Executor:
    """
    Головний виконавець Vireo.
    
    Підтримує:
    - Синхронне виконання
    - Асинхронне виконання
    - Виконання в потоках
    - Виконання в процесах
    - Тайм-аути
    - Відміна завдань
    """
    
    def __init__(self, max_workers: int = 4, context: Optional[RuntimeContext] = None):
        self.max_workers = max_workers
        self.context = context or get_context()
        self._thread_pool = ThreadPoolExecutor(max_workers=max_workers)
        self._process_pool = ProcessPoolExecutor(max_workers=max_workers)
        self._tasks: Dict[str, asyncio.Task] = {}
        self._results: Dict[str, ExecutionResult] = {}
        self._lock = threading.RLock()
        self._task_counter = 0
        self._logger = logging.getLogger(f"{__name__}.Executor")
    
    def execute(
        self,
        func: Callable,
        *args,
        mode: ExecutionMode = ExecutionMode.SYNC,
        timeout: Optional[float] = None,
        **kwargs,
    ) -> ExecutionResult:
        """
        Виконання функції.
        
        Args:
            func: Функція для виконання
            *args: Аргументи функції
            mode: Режим виконання
            timeout: Тайм-аут в секундах
            **kwargs: Іменовані аргументи
            
        Returns:
            ExecutionResult: Результат виконання
        """
        if mode == ExecutionMode.SYNC:
            return self._execute_sync(func, *args, timeout=timeout, **kwargs)
        elif mode == ExecutionMode.ASYNC:
            return self._execute_async(func, *args, timeout=timeout, **kwargs)
        elif mode == ExecutionMode.THREAD:
            return self._execute_thread(func, *args, timeout=timeout, **kwargs)
        elif mode == ExecutionMode.PROCESS:
            return self._execute_process(func, *args, timeout=timeout, **kwargs)
        else:
            raise ValueError(f"Unknown execution mode: {mode}")
    
    def execute_many(
        self,
        funcs: List[Callable],
        args_list: Optional[List[tuple]] = None,
        kwargs_list: Optional[List[dict]] = None,
        mode: ExecutionMode = ExecutionMode.THREAD,
        timeout: Optional[float] = None,
    ) -> List[ExecutionResult]:
        """
        Виконання багатьох функцій.
        
        Args:
            funcs: Список функцій
            args_list: Список аргументів для кожної функції
            kwargs_list: Список іменованих аргументів
            mode: Режим виконання
            timeout: Тайм-аут
            
        Returns:
            List[ExecutionResult]: Результати виконання
        """
        results = []
        for i, func in enumerate(funcs):
            args = args_list[i] if args_list and i < len(args_list) else ()
            kwargs = kwargs_list[i] if kwargs_list and i < len(kwargs_list) else {}
            result = self.execute(func, *args, mode=mode, timeout=timeout, **kwargs)
            results.append(result)
        return results
    
    def execute_batch(
        self,
        func: Callable,
        items: List[Any],
        mode: ExecutionMode = ExecutionMode.THREAD,
        timeout: Optional[float] = None,
        **kwargs,
    ) -> List[ExecutionResult]:
        """
        Виконання функції для кожного елемента.
        
        Args:
            func: Функція
            items: Список елементів
            mode: Режим виконання
            timeout: Тайм-аут
            **kwargs: Додаткові аргументи
            
        Returns:
            List[ExecutionResult]: Результати виконання
        """
        results = []
        for item in items:
            result = self.execute(func, item, mode=mode, timeout=timeout, **kwargs)
            results.append(result)
        return results
    
    async def execute_async(
        self,
        func: Callable,
        *args,
        timeout: Optional[float] = None,
        **kwargs,
    ) -> ExecutionResult:
        """
        Асинхронне виконання функції.
        
        Args:
            func: Функція
            *args: Аргументи
            timeout: Тайм-аут
            **kwargs: Іменовані аргументи
            
        Returns:
            ExecutionResult: Результат виконання
        """
        return await asyncio.to_thread(
            self._execute_sync,
            func,
            *args,
            timeout=timeout,
            **kwargs
        )
    
    def _execute_sync(
        self,
        func: Callable,
        *args,
        timeout: Optional[float] = None,
        **kwargs,
    ) -> ExecutionResult:
        """Синхронне виконання."""
        task_id = self._generate_task_id()
        start_time = time.time()
        
        self._logger.debug(f"Executing task {task_id}: {func.__name__}")
        
        try:
            if timeout:
                result = self._execute_with_timeout(func, timeout, *args, **kwargs)
            else:
                result = func(*args, **kwargs)
            
            end_time = time.time()
            duration = end_time - start_time
            
            self._logger.debug(f"Task {task_id} completed in {duration:.3f}s")
            
            return ExecutionResult(
                status=ExecutionStatus.COMPLETED,
                result=result,
                start_time=start_time,
                end_time=end_time,
                duration=duration,
            )
        except TimeoutError as e:
            end_time = time.time()
            self._logger.warning(f"Task {task_id} timed out after {timeout}s")
            return ExecutionResult(
                status=ExecutionStatus.TIMEOUT,
                error=e,
                start_time=start_time,
                end_time=end_time,
                duration=end_time - start_time,
            )
        except Exception as e:
            end_time = time.time()
            self._logger.error(f"Task {task_id} failed: {e}")
            return ExecutionResult(
                status=ExecutionStatus.FAILED,
                error=e,
                start_time=start_time,
                end_time=end_time,
                duration=end_time - start_time,
            )
    
    def _execute_async(
        self,
        func: Callable,
        *args,
        timeout: Optional[float] = None,
        **kwargs,
    ) -> ExecutionResult:
        """Асинхронне виконання (блокуюче)."""
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        try:
            result = loop.run_until_complete(
                self.execute_async(func, *args, timeout=timeout, **kwargs)
            )
            return result
        finally:
            loop.close()
    
    def _execute_thread(
        self,
        func: Callable,
        *args,
        timeout: Optional[float] = None,
        **kwargs,
    ) -> ExecutionResult:
        """Виконання в потоці."""
        future = self._thread_pool.submit(self._execute_sync, func, *args, timeout=timeout, **kwargs)
        try:
            return future.result(timeout=timeout if timeout else None)
        except TimeoutError:
            future.cancel()
            return ExecutionResult(
                status=ExecutionStatus.TIMEOUT,
                error=TimeoutError(f"Execution timed out after {timeout}s"),
            )
    
    def _execute_process(
        self,
        func: Callable,
        *args,
        timeout: Optional[float] = None,
        **kwargs,
    ) -> ExecutionResult:
        """Виконання в процесі."""
        future = self._process_pool.submit(self._execute_sync, func, *args, timeout=timeout, **kwargs)
        try:
            return future.result(timeout=timeout if timeout else None)
        except TimeoutError:
            future.cancel()
            return ExecutionResult(
                status=ExecutionStatus.TIMEOUT,
                error=TimeoutError(f"Execution timed out after {timeout}s"),
            )
    
    def _execute_with_timeout(
        self,
        func: Callable,
        timeout: float,
        *args,
        **kwargs,
    ) -> Any:
        """Виконання з тайм-аутом."""
        import signal
        
        def timeout_handler(signum, frame):
            raise TimeoutError(f"Execution timed out after {timeout}s")
        
        # Встановлюємо тайм-аут
        old_handler = signal.signal(signal.SIGALRM, timeout_handler)
        signal.alarm(int(timeout) + 1)
        
        try:
            return func(*args, **kwargs)
        finally:
            signal.alarm(0)
            signal.signal(signal.SIGALRM, old_handler)
    
    def _generate_task_id(self) -> str:
        """Генерує ID завдання."""
        with self._lock:
            self._task_counter += 1
            return f"task-{self._task_counter:06d}"
    
    def cancel_task(self, task_id: str) -> bool:
        """Відміняє завдання."""
        with self._lock:
            if task_id in self._tasks:
                task = self._tasks[task_id]
                if not task.done():
                    task.cancel()
                    return True
        return False
    
    def get_task_status(self, task_id: str) -> Optional[ExecutionStatus]:
        """Отримує статус завдання."""
        with self._lock:
            if task_id in self._results:
                return self._results[task_id].status
            if task_id in self._tasks:
                return ExecutionStatus.RUNNING
        return None
    
    def get_stats(self) -> Dict[str, Any]:
        """Отримує статистику."""
        with self._lock:
            return {
                "total_tasks": self._task_counter,
                "pending": sum(1 for r in self._results.values() if r.status == ExecutionStatus.PENDING),
                "running": len(self._tasks),
                "completed": sum(1 for r in self._results.values() if r.status == ExecutionStatus.COMPLETED),
                "failed": sum(1 for r in self._results.values() if r.status == ExecutionStatus.FAILED),
                "timeout": sum(1 for r in self._results.values() if r.status == ExecutionStatus.TIMEOUT),
                "cancelled": sum(1 for r in self._results.values() if r.status == ExecutionStatus.CANCELLED),
                "max_workers": self.max_workers,
            }
    
    def shutdown(self, wait: bool = True) -> None:
        """Завершує роботу виконавця."""
        self._thread_pool.shutdown(wait=wait)
        self._process_pool.shutdown(wait=wait)
    
    def __enter__(self):
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        self.shutdown()


# ============================================================
# ЗРУЧНІ ФУНКЦІЇ
# ============================================================

_default_executor: Optional[Executor] = None


def get_executor() -> Executor:
    """Отримує глобальний виконавець."""
    global _default_executor
    if _default_executor is None:
        _default_executor = Executor()
    return _default_executor


def set_executor(executor: Executor) -> None:
    """Встановлює глобальний виконавець."""
    global _default_executor
    _default_executor = executor


def execute(
    func: Callable,
    *args,
    mode: ExecutionMode = ExecutionMode.SYNC,
    timeout: Optional[float] = None,
    **kwargs,
) -> ExecutionResult:
    """Зручна функція для виконання."""
    return get_executor().execute(func, *args, mode=mode, timeout=timeout, **kwargs)


async def execute_async(
    func: Callable,
    *args,
    timeout: Optional[float] = None,
    **kwargs,
) -> ExecutionResult:
    """Зручна функція для асинхронного виконання."""
    return await get_executor().execute_async(func, *args, timeout=timeout, **kwargs)