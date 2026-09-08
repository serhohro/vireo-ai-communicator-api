"""
Vireo Executor Agent

Specialized agent for task execution.
"""

import asyncio
import logging
from datetime import datetime
from typing import Dict, Any, Optional, List, Union

from ..agent import Agent, AgentConfig
from core.protocol import Message

logger = logging.getLogger(__name__)


class ExecutorConfig(AgentConfig):
    """Configuration for Executor agent."""
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.capabilities = ["executor", "task_execution", "workflow"]
        self.max_tasks: int = kwargs.get("max_tasks", 100)
        self.concurrent_tasks: int = kwargs.get("concurrent_tasks", 5)
        self.task_timeout: int = kwargs.get("task_timeout", 300)
        self.result_ttl: int = kwargs.get("result_ttl", 3600)  # 1 hour default
        self.enable_retry: bool = kwargs.get("enable_retry", True)
        self.max_retries: int = kwargs.get("max_retries", 3)
        self.retry_delay: int = kwargs.get("retry_delay", 5)  # seconds


class ExecutorAgent(Agent):
    """
    Executor Agent for task execution.
    
    Capabilities:
    - Task queue management
    - Concurrent execution
    - Result caching
    - Retry logic
    - Status tracking
    """
    
    def __init__(self, config: ExecutorConfig):
        super().__init__(config)
        self.executor_config = config
        
        # Task management
        self._tasks: Dict[str, Dict[str, Any]] = {}
        self._results: Dict[str, Dict[str, Any]] = {}
        self._queue: asyncio.Queue = asyncio.Queue()
        
        # Executor pool
        self._executor_semaphore = asyncio.Semaphore(config.concurrent_tasks)
        
        # Custom task handlers
        self._task_handlers: Dict[str, callable] = {}
        
        # Setup handlers
        self._setup_handlers()
        
        logger.info(f"Executor Agent initialized: {self.id}")
    
    def _setup_handlers(self) -> None:
        """Setup message handlers."""
        self.on_message("execute", self._handle_execute)
        self.on_message("status", self._handle_status)
        self.on_message("cancel", self._handle_cancel)
        self.on_message("result", self._handle_result)
    
    # ============================================================
    # Task Execution Handlers
    # ============================================================
    
    async def _handle_execute(self, message: Message) -> Optional[Message]:
        """Handle execute message."""
        task = message.payload.get("task", {})
        task_id = task.get("id", f"task_{int(datetime.now().timestamp())}_{self.id[:8]}")
        task_type = task.get("type", "unknown")
        task_data = task.get("data", {})
        
        # Check if we have a handler
        if task_type not in self._task_handlers:
            return Message(
                type="error",
                sender=self.id,
                recipient=message.sender,
                in_response_to=message.id,
                payload={
                    "error": f"Unknown task type: {task_type}",
                    "task_id": task_id,
                }
            )
        
        # Check task limit
        if len(self._tasks) >= self.executor_config.max_tasks:
            return Message(
                type="error",
                sender=self.id,
                recipient=message.sender,
                in_response_to=message.id,
                payload={
                    "error": "Task limit exceeded",
                    "task_id": task_id,
                    "max_tasks": self.executor_config.max_tasks,
                }
            )
        
        # Store task
        self._tasks[task_id] = {
            "id": task_id,
            "type": task_type,
            "data": task_data,
            "status": "queued",
            "created_at": datetime.now().isoformat(),
            "requester": message.sender,
            "message_id": message.id,
            "retries": 0,
        }
        
        # Queue task
        await self._queue.put(task_id)
        
        # Start processing if not already
        asyncio.create_task(self._process_queue())
        
        return Message(
            type="task_queued",
            sender=self.id,
            recipient=message.sender,
            in_response_to=message.id,
            payload={
                "task_id": task_id,
                "status": "queued",
                "queue_position": self._queue.qsize(),
                "timestamp": datetime.now().isoformat(),
            }
        )
    
    async def _handle_status(self, message: Message) -> Optional[Message]:
        """Handle status request."""
        task_id = message.payload.get("task_id")
        
        if task_id not in self._tasks:
            # Check if completed
            if task_id in self._results:
                return Message(
                    type="task_result",
                    sender=self.id,
                    recipient=message.sender,
                    in_response_to=message.id,
                    payload={
                        "task_id": task_id,
                        "status": "completed",
                        "result": self._results[task_id],
                        "timestamp": datetime.now().isoformat(),
                    }
                )
            else:
                return Message(
                    type="error",
                    sender=self.id,
                    recipient=message.sender,
                    in_response_to=message.id,
                    payload={
                        "error": f"Task not found: {task_id}",
                    }
                )
        
        task = self._tasks[task_id]
        return Message(
            type="task_status",
            sender=self.id,
            recipient=message.sender,
            in_response_to=message.id,
            payload={
                "task_id": task_id,
                "status": task["status"],
                "created_at": task.get("created_at"),
                "updated_at": task.get("updated_at"),
                "progress": task.get("progress", 0),
                "retries": task.get("retries", 0),
            }
        )
    
    async def _handle_cancel(self, message: Message) -> Optional[Message]:
        """Handle task cancellation."""
        task_id = message.payload.get("task_id")
        
        if task_id not in self._tasks:
            return Message(
                type="error",
                sender=self.id,
                recipient=message.sender,
                in_response_to=message.id,
                payload={
                    "error": f"Task not found: {task_id}",
                }
            )
        
        task = self._tasks[task_id]
        
        if task["status"] in ["completed", "failed", "cancelled"]:
            return Message(
                type="task_cancelled",
                sender=self.id,
                recipient=message.sender,
                in_response_to=message.id,
                payload={
                    "task_id": task_id,
                    "status": task["status"],
                    "message": "Task already in terminal state",
                }
            )
        
        task["status"] = "cancelled"
        task["updated_at"] = datetime.now().isoformat()
        
        return Message(
            type="task_cancelled",
            sender=self.id,
            recipient=message.sender,
            in_response_to=message.id,
            payload={
                "task_id": task_id,
                "status": "cancelled",
                "timestamp": datetime.now().isoformat(),
            }
        )
    
    async def _handle_result(self, message: Message) -> Optional[Message]:
        """Handle result retrieval."""
        task_id = message.payload.get("task_id")
        
        if task_id not in self._results:
            return Message(
                type="error",
                sender=self.id,
                recipient=message.sender,
                in_response_to=message.id,
                payload={
                    "error": f"Result not found for task: {task_id}",
                }
            )
        
        result = self._results[task_id]
        return Message(
            type="task_result",
            sender=self.id,
            recipient=message.sender,
            in_response_to=message.id,
            payload={
                "task_id": task_id,
                "result": result,
                "timestamp": datetime.now().isoformat(),
            }
        )
    
    # ============================================================
    # Task Processing
    # ============================================================
    
    async def _process_queue(self) -> None:
        """Process tasks from queue."""
        async with self._executor_semaphore:
            try:
                task_id = await asyncio.wait_for(
                    self._queue.get(),
                    timeout=1.0
                )
            except asyncio.TimeoutError:
                return
            
            try:
                await self._execute_task(task_id)
            except Exception as e:
                logger.error(f"Task execution error: {e}")
                self._handle_task_failure(task_id, str(e))
    
    async def _execute_task(self, task_id: str) -> None:
        """Execute a specific task."""
        if task_id not in self._tasks:
            return
        
        task = self._tasks[task_id]
        task["status"] = "running"
        task["started_at"] = datetime.now().isoformat()
        
        try:
            # Get handler
            handler = self._task_handlers.get(task["type"])
            if not handler:
                raise ValueError(f"No handler for task type: {task['type']}")
            
            # Execute with timeout
            result = await asyncio.wait_for(
                handler(task["data"]),
                timeout=self.executor_config.task_timeout
            )
            
            # Store result
            self._results[task_id] = {
                "status": "success",
                "result": result,
                "completed_at": datetime.now().isoformat(),
            }
            
            task["status"] = "completed"
            task["updated_at"] = datetime.now().isoformat()
            task["progress"] = 100
            
            # Notify requester
            await self._notify_completion(task_id)
            
        except asyncio.TimeoutError:
            self._handle_task_failure(task_id, "Task timeout")
        except Exception as e:
            self._handle_task_failure(task_id, str(e))
    
    def _handle_task_failure(self, task_id: str, error: str) -> None:
        """Handle task failure with retry logic."""
        task = self._tasks.get(task_id)
        if not task:
            return
        
        task["status"] = "failed"
        task["error"] = error
        task["updated_at"] = datetime.now().isoformat()
        
        # Store error result
        self._results[task_id] = {
            "status": "failed",
            "error": error,
            "completed_at": datetime.now().isoformat(),
        }
        
        # Retry logic
        if self.executor_config.enable_retry and task.get("retries", 0) < self.executor_config.max_retries:
            task["retries"] = task.get("retries", 0) + 1
            task["status"] = "queued"
            
            # Re-queue with delay
            asyncio.create_task(self._retry_task(task_id))
            
            logger.info(f"Task {task_id} retrying ({task['retries']}/{self.executor_config.max_retries})")
        else:
            # Notify failure
            asyncio.create_task(self._notify_completion(task_id))
    
    async def _retry_task(self, task_id: str) -> None:
        """Retry a failed task after delay."""
        await asyncio.sleep(self.executor_config.retry_delay)
        await self._queue.put(task_id)
        asyncio.create_task(self._process_queue())
    
    async def _notify_completion(self, task_id: str) -> None:
        """Notify requester of task completion."""
        task = self._tasks.get(task_id)
        if not task:
            return
        
        requester = task.get("requester")
        if not requester:
            return
        
        result = self._results.get(task_id, {})
        
        # Send notification
        await self.send_message(
            Message(
                type="task_completed",
                sender=self.id,
                recipient=requester,
                in_response_to=task.get("message_id"),
                payload={
                    "task_id": task_id,
                    "status": result.get("status", "unknown"),
                    "result": result.get("result"),
                    "error": result.get("error"),
                    "timestamp": datetime.now().isoformat(),
                }
            )
        )
    
    # ============================================================
    # Task Handler Registration
    # ============================================================
    
    def register_handler(self, task_type: str, handler: callable) -> None:
        """
        Register a task handler.
        
        Args:
            task_type: Type of task to handle
            handler: Async function that takes task data and returns result
        """
        self._task_handlers[task_type] = handler
        logger.info(f"Registered handler for task type: {task_type}")
    
    def unregister_handler(self, task_type: str) -> bool:
        """Unregister a task handler."""
        if task_type in self._task_handlers:
            del self._task_handlers[task_type]
            return True
        return False
    
    # ============================================================
    # Public Methods
    # ============================================================
    
    def get_task(self, task_id: str) -> Optional[Dict[str, Any]]:
        """Get task details."""
        return self._tasks.get(task_id)
    
    def get_result(self, task_id: str) -> Optional[Dict[str, Any]]:
        """Get task result."""
        return self._results.get(task_id)
    
    def list_tasks(self, status: Optional[str] = None) -> List[Dict[str, Any]]:
        """List tasks with optional status filter."""
        tasks = []
        for task_id, task in self._tasks.items():
            if status and task.get("status") != status:
                continue
            tasks.append({
                "id": task_id,
                "type": task.get("type"),
                "status": task.get("status"),
                "created_at": task.get("created_at"),
                "progress": task.get("progress", 0),
            })
        return tasks
    
    def cleanup_results(self) -> None:
        """Clean up old results."""
        now = datetime.now()
        to_remove = []
        
        for task_id, result in self._results.items():
            completed_at = result.get("completed_at")
            if completed_at:
                try:
                    completed = datetime.fromisoformat(completed_at)
                    if (now - completed).total_seconds() > self.executor_config.result_ttl:
                        to_remove.append(task_id)
                except:
                    pass
        
        for task_id in to_remove:
            del self._results[task_id]
        
        logger.info(f"Cleaned up {len(to_remove)} old results")