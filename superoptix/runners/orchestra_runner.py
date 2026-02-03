import asyncio
import logging
import time
from collections import defaultdict
from pathlib import Path
from typing import Any, Dict, List, Set

import yaml
from rich.console import Console

from superoptix.models.base_models import (
    AgentTier,
    DependencyType,
    ExecutionStrategy,
    OrchestraFile,
    OrchestrationType,
    TierPermissionError,
    TierValidator,
)
from superoptix.runners.dspy_runner import DSPyRunner

console = Console()
logger = logging.getLogger(__name__)


class TierAwareOrchestraRunner:
    """Enhanced Orchestra Runner with tier-based access control."""

    def __init__(self, agent_tier: AgentTier = AgentTier.ORACLES):
        self.agent_tier = agent_tier
        self.console = console
        self.validation_results = None

    def validate_tier_access(self, orchestra_config: Dict[str, Any]) -> Dict[str, Any]:
        """Validate that the agent tier has access to requested orchestration features."""
        validation = TierValidator.validate_orchestration_access(
            self.agent_tier, orchestra_config
        )

        if not validation["valid"]:
            self.console.print("\n❌ [bold red]Tier Permission Error[/]")
            self.console.print(f"[yellow]Current Tier:[/] {self.agent_tier.value}")

            for error in validation["errors"]:
                self.console.print(f"[red]• {error}[/]")

            # Show available features for current tier
            features = validation["available_features"]
            self.console.print(
                f"\n[green]✅ Available Features for {self.agent_tier.value} tier:[/]"
            )
            self.console.print(
                f"[cyan]• Orchestration Types:[/] {[t.value for t in features['orchestration_types']]}"
            )
            self.console.print(
                f"[cyan]• Max Parallel Tasks:[/] {features['max_parallel_tasks']}"
            )
            self.console.print(
                f"[cyan]• Execution Strategies:[/] {features['execution_strategies']}"
            )

            if features.get("auto_scaling"):
                self.console.print("[cyan]• Auto-scaling:[/] ✅")
            if features.get("replicas"):
                self.console.print("[cyan]• Agent Replicas:[/] ✅")
            if features.get("advanced_networking"):
                self.console.print("[cyan]• Advanced Networking:[/] ✅")
            if features.get("operators"):
                self.console.print("[cyan]• Custom Operators:[/] ✅")

            # Show upgrade suggestions
            if self.agent_tier == AgentTier.ORACLES:
                self.console.print(
                    "\n[blue]💡 Upgrade to Genie tier to unlock advanced features like ReAct tools, RAG retrieval, and agent memory![/]"
                )

            raise TierPermissionError(
                "Insufficient tier permissions for requested orchestration features",
                current_tier=self.agent_tier.value,
                available_features=features,
            )

        self.validation_results = validation
        return validation

    def get_agent_tier_from_spec(self, agent_spec_path: str) -> AgentTier:
        """Extract agent tier from agent specification file."""
        try:
            if Path(agent_spec_path).exists():
                with open(agent_spec_path, "r") as f:
                    agent_spec = yaml.safe_load(f)
                    tier_str = agent_spec.get("metadata", {}).get("level", "oracles")
                    return AgentTier(tier_str)
        except Exception as e:
            logger.warning(
                f"Could not determine agent tier from {agent_spec_path}: {e}"
            )

        return AgentTier.ORACLES  # Default to oracles if unable to determine

    def detect_orchestration_mode(
        self, orchestra_config: Dict[str, Any]
    ) -> OrchestrationType:
        """Always use basic orchestration mode in current version."""
        return OrchestrationType.BASIC


class TaskExecutionResult:
    """Results from task execution."""

    def __init__(
        self,
        task_name: str,
        success: bool,
        output: Any = None,
        error: str = None,
        execution_time: float = 0,
    ):
        self.task_name = task_name
        self.success = success
        self.output = output
        self.error = error
        self.execution_time = execution_time
        self.timestamp = time.time()


class DependencyResolver:
    """Resolves task dependencies and determines execution order."""

    def __init__(self, tasks: List):
        self.tasks = {task.name: task for task in tasks}
        self.completed_tasks: Set[str] = set()
        self.failed_tasks: Set[str] = set()

    def get_ready_tasks(self) -> List[str]:
        """Get tasks that are ready to execute (all dependencies met)."""
        ready_tasks = []

        for task_name, task in self.tasks.items():
            if task_name in self.completed_tasks or task_name in self.failed_tasks:
                continue

            # Check if all dependencies are satisfied
            dependencies_met = True
            for dep in task.dependencies:
                if dep.dependency_type in [
                    DependencyType.REQUIRES_OUTPUT,
                    DependencyType.REQUIRES_COMPLETION,
                ]:
                    if dep.task_name not in self.completed_tasks:
                        dependencies_met = False
                        break
                elif dep.dependency_type == DependencyType.BLOCKS:
                    if dep.task_name in self.completed_tasks:
                        dependencies_met = False
                        break

            if dependencies_met:
                ready_tasks.append(task_name)

        return ready_tasks

    def mark_completed(self, task_name: str):
        """Mark a task as completed."""
        self.completed_tasks.add(task_name)

    def mark_failed(self, task_name: str):
        """Mark a task as failed."""
        self.failed_tasks.add(task_name)

    def has_pending_tasks(self) -> bool:
        """Check if there are tasks still pending execution."""
        total_tasks = len(self.tasks)
        processed_tasks = len(self.completed_tasks) + len(self.failed_tasks)
        return processed_tasks < total_tasks


class TaskScheduler:
    """Handles task scheduling based on dependencies and execution strategy."""

    def __init__(
        self, tasks: List[Dict[str, Any]], execution_strategy: ExecutionStrategy
    ):
        self.tasks = {task["name"]: task for task in tasks}
        self.execution_strategy = execution_strategy
        self.dependency_graph = self._build_dependency_graph()
        self.completed_tasks = set()
        self.running_tasks = set()
        self.failed_tasks = set()

    def _build_dependency_graph(self) -> Dict[str, Set[str]]:
        """Build a dependency graph from task definitions."""
        graph = defaultdict(set)

        for task_name, task in self.tasks.items():
            dependencies = task.get("dependencies", [])
            for dep in dependencies:
                if isinstance(dep, dict):
                    dep_name = dep.get("task_name") or dep.get("task")
                else:
                    dep_name = dep

                if dep_name and dep_name in self.tasks:
                    graph[task_name].add(dep_name)

        return graph

    def get_ready_tasks(self, max_parallel: int = None) -> List[str]:
        """Get tasks that are ready to execute based on dependencies."""
        ready_tasks = []

        for task_name, _task in self.tasks.items():
            if (
                task_name not in self.completed_tasks
                and task_name not in self.running_tasks
                and task_name not in self.failed_tasks
            ):
                # Check if all dependencies are completed
                dependencies = self.dependency_graph.get(task_name, set())
                if dependencies.issubset(self.completed_tasks):
                    ready_tasks.append(task_name)

        # Sort by priority
        def get_priority_value(task_name):
            priority = self.tasks[task_name].get("priority", "medium")
            priority_map = {"critical": 4, "high": 3, "medium": 2, "low": 1}
            return priority_map.get(priority, 2)

        ready_tasks.sort(key=get_priority_value, reverse=True)

        if max_parallel:
            ready_tasks = ready_tasks[: max_parallel - len(self.running_tasks)]

        return ready_tasks

    def mark_task_completed(self, task_name: str):
        """Mark a task as completed."""
        self.running_tasks.discard(task_name)
        self.completed_tasks.add(task_name)

    def mark_task_failed(self, task_name: str):
        """Mark a task as failed."""
        self.running_tasks.discard(task_name)
        self.failed_tasks.add(task_name)

    def mark_task_running(self, task_name: str):
        """Mark a task as currently running."""
        self.running_tasks.add(task_name)


class EnhancedOrchestraRunner:
    """Enhanced Orchestra Runner with support for multiple execution strategies."""

    def __init__(
        self,
        orchestra_file: str,
        workspace_path: str = None,
        agent_tier: AgentTier = None,
    ):
        self.orchestra_file = orchestra_file
        self.workspace_path = workspace_path
        self.console = console
        self.results = {}
        self.execution_stats = {
            "start_time": None,
            "end_time": None,
            "total_tasks": 0,
            "completed_tasks": 0,
            "failed_tasks": 0,
            "execution_times": {},
        }

        # Determine agent tier
        if agent_tier:
            self.agent_tier = agent_tier
        else:
            # Try to determine from orchestra file or agents
            self.agent_tier = self._determine_agent_tier()

        # Initialize tier-aware runner
        self.tier_runner = TierAwareOrchestraRunner(self.agent_tier)

        # Initialize workspace directory creation
        self._initialized_workspaces = set()

    def _determine_agent_tier(self) -> AgentTier:
        """Determine agent tier from orchestra configuration or agents."""
        try:
            # Load orchestra to check for tier hints
            with open(self.orchestra_file, "r") as f:
                orchestra_data = yaml.safe_load(f)

            # Check if tier is specified in orchestra
            required_tier = orchestra_data.get("orchestra", {}).get("required_tier")
            if required_tier:
                return AgentTier(required_tier)

            # Check agents for tier information
            agents = orchestra_data.get("agents", [])
            if agents:
                # For now, assume first agent's tier
                # In a real implementation, this would check the actual agent spec files
                pass

        except Exception as e:
            logger.warning(f"Could not determine agent tier: {e}")

        return AgentTier.ORACLES  # Default to oracles

    async def run_orchestra(self, input_data: str, **kwargs) -> Dict[str, Any]:
        """Run the orchestra with tier validation."""
        self.execution_stats["start_time"] = time.time()

        try:
            # Load and validate orchestra configuration
            orchestra = self._load_orchestra()
            orchestra_config = self._extract_config_for_validation(orchestra)

            # Ensure workspace directory exists
            workspace_config = getattr(orchestra.orchestra, "workspace", None)
            if workspace_config:
                workspace_path = self._ensure_workspace_directory(
                    workspace_config.__dict__
                    if hasattr(workspace_config, "__dict__")
                    else workspace_config
                )
                if workspace_path:
                    self.console.print(f"[cyan]📂 Using workspace:[/] {workspace_path}")

            # Validate tier access
            self.console.print(
                f"[blue]🔐 Validating tier access for {self.agent_tier.value} tier...[/]"
            )
            self.tier_runner.validate_tier_access(orchestra_config)
            self.console.print("[green]✅ Tier validation passed![/]")

            # Always use basic orchestration mode
            orchestration_mode = OrchestrationType.BASIC
            self.console.print(
                f"[blue]🎼 Using {orchestration_mode.value} orchestration mode[/]"
            )

            # Only use the basic runner
            return await self._run_basic_style(orchestra, input_data, **kwargs)

        except TierPermissionError as e:
            self.console.print(
                "\n[red]❌ Orchestra execution blocked due to tier restrictions[/]"
            )
            return {
                "success": False,
                "error": str(e),
                "current_tier": e.current_tier,
                "available_features": e.available_features,
            }
        except Exception as e:
            self.console.print(f"[red]❌ Orchestra execution failed: {str(e)}[/]")
            return {"success": False, "error": str(e)}
        finally:
            self.execution_stats["end_time"] = time.time()

    def _extract_config_for_validation(
        self, orchestra: OrchestraFile
    ) -> Dict[str, Any]:
        """Extract configuration for tier validation."""
        config = {
            "execution": {
                "max_parallel_tasks": orchestra.orchestra.execution.max_parallel_tasks,
                "strategy": orchestra.orchestra.execution.strategy.value,
            },
            "orchestration_type": orchestra.orchestra.orchestration_type.value,
        }

        # Add any advanced features that might be present
        if hasattr(orchestra.orchestra, "replicas"):
            config["replicas"] = orchestra.orchestra.replicas

        return config

    async def _run_basic_style(
        self, orchestra: OrchestraFile, input_data: str, **kwargs
    ) -> Dict[str, Any]:
        """Run orchestra using basic (CrewAI-style) orchestration."""
        self.console.print(
            f"[green]🚀 Running Basic Orchestra: {orchestra.orchestra.name}[/]"
        )

        execution_strategy = orchestra.orchestra.execution.strategy
        _ = min(
            orchestra.orchestra.execution.max_parallel_tasks,
            self.tier_runner.validation_results["available_features"][
                "max_parallel_tasks"
            ],
        )  # noqa: F841

        if execution_strategy == ExecutionStrategy.SEQUENTIAL:
            return await self._execute_sequential(orchestra.tasks, input_data)
        else:
            # For current version, only sequential is supported
            self.console.print(
                "[yellow]⚠️ Only sequential execution is supported in current version[/]"
            )
            return await self._execute_sequential(orchestra.tasks, input_data)

    async def _run_kubernetes_style(
        self, orchestra: OrchestraFile, input_data: str, **kwargs
    ) -> Dict[str, Any]:
        """Run orchestra using Kubernetes-style orchestration."""
        self.console.print(
            f"[green]🚀 Running Kubernetes-Style Orchestra: {orchestra.orchestra.name}[/]"
        )
        self.console.print(
            f"[blue]⚡ Advanced features enabled for {self.agent_tier.value} tier[/]"
        )

        # For now, this falls back to enhanced basic orchestration
        # In a full implementation, this would handle AgentPods, Deployments, etc.
        return await self._run_basic_style(orchestra, input_data, **kwargs)

    def _load_orchestra(self) -> OrchestraFile:
        """Load orchestra configuration from file."""
        with open(self.orchestra_file, "r") as f:
            data = yaml.safe_load(f)
            return OrchestraFile(**data)

    async def _execute_sequential(
        self, tasks: List[Any], input_data: str
    ) -> Dict[str, Any]:
        """Execute tasks sequentially."""
        self.console.print(
            f"[yellow]📋 Executing {len(tasks)} tasks sequentially...[/]"
        )

        results = {}
        current_input = input_data

        for i, task in enumerate(tasks, 1):
            self.console.print(f"\n[blue]🔄 Task {i}/{len(tasks)}: {task.name}[/]")

            try:
                start_time = time.time()
                result = await self._execute_task(task, current_input)
                execution_time = time.time() - start_time

                results[task.name] = TaskExecutionResult(
                    task_name=task.name,
                    success=True,
                    output=result,
                    execution_time=execution_time,
                )

                # Pass output to next task as input
                current_input = result
                self.execution_stats["completed_tasks"] += 1

                self.console.print(
                    f"[green]✅ Task {task.name} completed in {execution_time:.2f}s[/]"
                )

            except Exception as e:
                self.execution_stats["failed_tasks"] += 1
                results[task.name] = TaskExecutionResult(
                    task_name=task.name, success=False, error=str(e)
                )
                self.console.print(f"[red]❌ Task {task.name} failed: {str(e)}[/]")
                break

        return self._format_results(results)

    async def _execute_parallel(
        self, tasks: List[Any], input_data: str, max_parallel: int
    ) -> Dict[str, Any]:
        """Execute tasks in parallel."""
        self.console.print(
            f"[yellow]🚀 Executing {len(tasks)} tasks in parallel (max: {max_parallel})...[/]"
        )

        semaphore = asyncio.Semaphore(max_parallel)

        async def execute_with_semaphore(task):
            async with semaphore:
                try:
                    start_time = time.time()
                    result = await self._execute_task(task, input_data)
                    execution_time = time.time() - start_time

                    self.execution_stats["completed_tasks"] += 1
                    self.console.print(
                        f"[green]✅ Task {task.name} completed in {execution_time:.2f}s[/]"
                    )

                    return TaskExecutionResult(
                        task_name=task.name,
                        success=True,
                        output=result,
                        execution_time=execution_time,
                    )
                except Exception as e:
                    self.execution_stats["failed_tasks"] += 1
                    self.console.print(f"[red]❌ Task {task.name} failed: {str(e)}[/]")

                    return TaskExecutionResult(
                        task_name=task.name, success=False, error=str(e)
                    )

        # Execute all tasks in parallel
        task_coroutines = [execute_with_semaphore(task) for task in tasks]
        task_results = await asyncio.gather(*task_coroutines, return_exceptions=True)

        # Process results
        results = {}
        for result in task_results:
            if isinstance(result, TaskExecutionResult):
                results[result.task_name] = result
            elif isinstance(result, Exception):
                self.console.print(f"[red]❌ Unexpected error: {str(result)}[/]")

        return self._format_results(results)

    async def _execute_mixed(
        self, orchestra: OrchestraFile, input_data: str, max_parallel: int
    ) -> Dict[str, Any]:
        """Execute tasks using mixed strategy with task groups and dependencies."""
        self.console.print(
            "[yellow]🎯 Executing mixed strategy with dependencies...[/]"
        )

        # Convert tasks to dict format for scheduler
        task_dicts = []
        for task in orchestra.tasks:
            task_dict = {
                "name": task.name,
                "agent": task.agent,
                "description": task.description,
                "priority": task.priority.value
                if hasattr(task.priority, "value")
                else task.priority,
                "dependencies": [],
            }

            # Convert dependencies
            for dep in task.dependencies:
                if hasattr(dep, "task_name"):
                    task_dict["dependencies"].append(
                        {"task": dep.task_name, "type": dep.dependency_type.value}
                    )

            task_dicts.append(task_dict)

        scheduler = TaskScheduler(task_dicts, ExecutionStrategy.MIXED)
        results = {}

        # Execute tasks based on dependency resolution
        while len(results) < len(task_dicts):
            ready_tasks = scheduler.get_ready_tasks(max_parallel)

            if not ready_tasks:
                # Check if we're deadlocked
                remaining_tasks = (
                    set(scheduler.tasks.keys())
                    - scheduler.completed_tasks
                    - scheduler.failed_tasks
                )
                if remaining_tasks:
                    self.console.print(
                        f"[red]❌ Deadlock detected. Remaining tasks: {remaining_tasks}[/]"
                    )
                    break
                else:
                    break

            # Execute ready tasks in parallel
            self.console.print(
                f"[blue]🔄 Executing {len(ready_tasks)} ready tasks: {ready_tasks}[/]"
            )

            # Mark tasks as running
            for task_name in ready_tasks:
                scheduler.mark_task_running(task_name)

            # Execute tasks
            task_coroutines = []
            for task_name in ready_tasks:
                task_obj = next(t for t in orchestra.tasks if t.name == task_name)
                task_coroutines.append(
                    self._execute_task_with_result(task_obj, input_data, scheduler)
                )

            batch_results = await asyncio.gather(
                *task_coroutines, return_exceptions=True
            )

            # Process batch results
            for i, result in enumerate(batch_results):
                task_name = ready_tasks[i]
                if isinstance(result, TaskExecutionResult):
                    results[task_name] = result
                    if result.success:
                        scheduler.mark_task_completed(task_name)
                    else:
                        scheduler.mark_task_failed(task_name)
                else:
                    # Handle exception
                    scheduler.mark_task_failed(task_name)
                    results[task_name] = TaskExecutionResult(
                        task_name=task_name, success=False, error=str(result)
                    )

        return self._format_results(results)

    async def _execute_task_with_result(
        self, task: Any, input_data: str, scheduler: TaskScheduler
    ) -> TaskExecutionResult:
        """Execute a single task and return TaskExecutionResult."""
        try:
            start_time = time.time()
            result = await self._execute_task(task, input_data)
            execution_time = time.time() - start_time

            self.execution_stats["completed_tasks"] += 1
            self.console.print(
                f"[green]✅ Task {task.name} completed in {execution_time:.2f}s[/]"
            )

            return TaskExecutionResult(
                task_name=task.name,
                success=True,
                output=result,
                execution_time=execution_time,
            )
        except Exception as e:
            self.execution_stats["failed_tasks"] += 1
            self.console.print(f"[red]❌ Task {task.name} failed: {str(e)}[/]")

            return TaskExecutionResult(task_name=task.name, success=False, error=str(e))

    async def _execute_task(self, task: Any, input_data: str) -> Any:
        """Execute a single task using DSPy runner."""
        # Find project root from orchestra file path
        project_root = None
        project_name = None

        try:
            # Extract project root and name from the orchestra file path
            # The orchestra file is typically at: {project_root}/{project_name}/orchestras/{orchestra_name}.yaml
            orchestra_path = Path(self.orchestra_file).resolve()
            if orchestra_path.exists():
                # Go up three levels: orchestras/{file} -> orchestras -> {project_name} -> {project_root}
                potential_project_root = orchestra_path.parent.parent.parent
                potential_project_name = orchestra_path.parent.parent.name

                # Verify this is actually the project root by checking for .super file
                if (potential_project_root / ".super").exists():
                    project_root = potential_project_root
                    project_name = potential_project_name
        except Exception:
            pass

        # Create DSPy runner for the task
        runner = DSPyRunner(
            agent_name=task.agent, project_name=project_name, project_root=project_root
        )

        # Execute the task
        result = await runner.run(input_data)

        # Write task output to workspace if workspace is configured
        await self._write_task_output_to_workspace(task, result)

        return result

    def _format_results(
        self, results: Dict[str, TaskExecutionResult]
    ) -> Dict[str, Any]:
        """Format execution results."""
        total_time = (
            self.execution_stats["end_time"] - self.execution_stats["start_time"]
            if self.execution_stats["end_time"]
            else 0
        )

        return {
            "success": self.execution_stats["failed_tasks"] == 0,
            "total_execution_time": total_time,
            "stats": self.execution_stats,
            "task_results": {
                name: {
                    "success": result.success,
                    "output": result.output,
                    "error": result.error,
                    "execution_time": result.execution_time,
                }
                for name, result in results.items()
            },
            "tier_info": {
                "agent_tier": self.agent_tier.value,
                "available_features": self.tier_runner.validation_results[
                    "available_features"
                ]
                if self.tier_runner.validation_results
                else None,
            },
        }

    def _ensure_workspace_directory(
        self, workspace_config: Dict[str, Any] = None
    ) -> str:
        """Ensure workspace directory exists and return its path."""
        workspace_path = None

        # Check if workspace path was provided in constructor
        if self.workspace_path:
            workspace_path = self.workspace_path
        # Check if workspace is configured in orchestra file
        elif workspace_config:
            workspace_path = workspace_config.get("path")

        if workspace_path:
            # Convert relative paths to absolute paths
            if not Path(workspace_path).is_absolute():
                # Find project root by looking for .super file
                project_root = None
                try:
                    # Start from orchestra file directory and search upward
                    search_path = Path(self.orchestra_file).parent
                    for _ in range(5):  # Search up to 5 levels up
                        if (search_path / ".super").exists():
                            project_root = search_path
                            break
                        parent = search_path.parent
                        if parent == search_path:  # Reached filesystem root
                            break
                        search_path = parent

                    if not project_root:
                        # Fall back to current working directory
                        project_root = Path.cwd()

                except Exception:
                    project_root = Path.cwd()

                # Resolve relative to project root
                workspace_path = str(project_root / workspace_path)

            # Create directory if it doesn't exist
            workspace_dir = Path(workspace_path).resolve()
            if str(workspace_dir) not in self._initialized_workspaces:
                try:
                    workspace_dir.mkdir(parents=True, exist_ok=True)
                    self.console.print(
                        f"[green]📁 Created workspace directory:[/] {workspace_dir}"
                    )
                    self._initialized_workspaces.add(str(workspace_dir))
                except Exception as e:
                    self.console.print(
                        f"[yellow]⚠️ Warning: Could not create workspace directory {workspace_dir}: {e}[/]"
                    )

            return str(workspace_dir)

        return None

    async def _write_task_output_to_workspace(self, task: Any, result: Any) -> None:
        """Write task output to the workspace directory."""
        try:
            # Load orchestra to get workspace configuration
            orchestra = self._load_orchestra()
            workspace_config = getattr(orchestra.orchestra, "workspace", None)

            if not workspace_config:
                return  # No workspace configured

            # Get workspace path
            workspace_path = self._ensure_workspace_directory(
                workspace_config.__dict__
                if hasattr(workspace_config, "__dict__")
                else workspace_config
            )

            if not workspace_path:
                return  # Could not create/access workspace

            workspace_dir = Path(workspace_path)

            # Create task-specific output files
            task_name = getattr(task, "name", "unknown_task")
            task_agent = getattr(task, "agent", "unknown_agent")

            # Write main result as JSON
            import json
            from datetime import datetime

            result_file = workspace_dir / f"{task_name}_result.json"

            # Prepare result data for JSON serialization
            result_data = {
                "task_name": task_name,
                "agent": task_agent,
                "timestamp": datetime.now().isoformat(),
                "result": self._sanitize_for_json(result),
            }

            with open(result_file, "w", encoding="utf-8") as f:
                json.dump(result_data, f, indent=2, ensure_ascii=False)

            self.console.print(f"[cyan]📝 Wrote task output to:[/] {result_file}")

            # If result contains specific output fields, write them as separate files
            if isinstance(result, dict):
                # Look for common output field names
                output_fields = [
                    "implementation",
                    "code",
                    "test_plan",
                    "analysis",
                    "response",
                    "output",
                    "content",
                    "solution",
                ]

                for field in output_fields:
                    if field in result and isinstance(result[field], str):
                        # Write field content to a text file
                        field_file = workspace_dir / f"{task_name}_{field}.txt"
                        with open(field_file, "w", encoding="utf-8") as f:
                            f.write(result[field])
                        self.console.print(
                            f"[cyan]📝 Wrote {field} to:[/] {field_file}"
                        )

        except Exception as e:
            self.console.print(
                f"[yellow]⚠️ Warning: Could not write task output to workspace: {e}[/]"
            )

    def _sanitize_for_json(self, obj):
        """Sanitize object for JSON serialization."""
        if isinstance(obj, dict):
            return {k: self._sanitize_for_json(v) for k, v in obj.items()}
        elif isinstance(obj, list):
            return [self._sanitize_for_json(item) for item in obj]
        elif isinstance(obj, (str, int, float, bool, type(None))):
            return obj
        else:
            # Convert non-serializable objects to string
            return str(obj)


# Backward compatibility alias
OrchestraRunner = EnhancedOrchestraRunner
