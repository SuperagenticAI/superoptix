import re
import shutil
import sys
from pathlib import Path


def extract_main_package_dependencies():
    """Extract dependencies from the main SuperOptiX package."""
    # Get the root directory of the SuperOptiX package
    package_root = Path(__file__).parent.parent.parent.parent

    # Read dependencies from pyproject.toml
    pyproject_toml_path = package_root / "pyproject.toml"

    dependencies = []
    extras_require = {}

    if pyproject_toml_path.exists():
        with open(pyproject_toml_path, "r") as f:
            content = f.read()

        # Extract dependencies from pyproject.toml
        deps_match = re.search(r"dependencies\s*=\s*\[(.*?)\]", content, re.DOTALL)
        if deps_match:
            deps_str = deps_match.group(1)
            dependencies = re.findall(r'"([^"]+)"', deps_str)

        # Extract optional dependencies
        optional_deps_match = re.search(
            r"\[project\.optional-dependencies\](.*?)(?=\[|$)", content, re.DOTALL
        )
        if optional_deps_match:
            optional_deps_str = optional_deps_match.group(1)
            # Extract dev dependencies
            dev_match = re.search(r"dev\s*=\s*\[(.*?)\]", optional_deps_str, re.DOTALL)
            if dev_match:
                dev_deps_str = dev_match.group(1)
                dev_deps = re.findall(r'"([^"]+)"', dev_deps_str)
                extras_require["dev"] = dev_deps

    return dependencies, extras_require


def create_project_files(base_dir: Path, system_name: str):
    """Create all project files."""
    # Create all necessary project files (uv-compatible)
    create_pyproject_toml(base_dir, system_name)
    create_readme(base_dir, system_name)
    create_precommit_config(base_dir)


def create_env_file(base_dir: Path):
    """Create .env file with default configurations."""
    env_content = """# Cloud Provider API Keys
OPENAI_API_KEY=your_openai_key
ANTHROPIC_API_KEY=your_anthropic_key

# Local Provider Settings
OLLAMA_API_BASE=http://localhost:11434
MLX_API_BASE=http://localhost:8000
LMSTUDIO_API_BASE=http://localhost:1234
"""
    env_file = base_dir / ".env"
    env_file.write_text(env_content)


def create_project_structure(system_name: str):
    """Create the initial project structure."""
    root_dir = Path.cwd()
    base_dir = root_dir / system_name
    module_dir = base_dir / f"{system_name}"

    # Create base directories
    base_dir.mkdir(parents=True, exist_ok=True)
    module_dir.mkdir(parents=True, exist_ok=True)

    # Create .super file
    soda_file = base_dir / ".super"
    soda_file.write_text(f"project: {system_name}\nversion: 0.1.0\n")

    # Create empty agents directory instead of copying playbooks
    agents_dest = module_dir / "agents"
    agents_dest.mkdir(exist_ok=True)
    (agents_dest / "__init__.py").touch()

    # Create .env file
    create_env_file(base_dir)

    # Create .gitignore
    gitignore_content = """# Environment variables
.env

# Python
__pycache__/
*.py[cod]
*$py.class
.Python
build/
develop-eggs/
dist/
eggs/
.eggs/
*.egg-info/

# Virtual Environment
.venv/
venv/
ENV/

# IDE
.vscode/
.idea/
"""
    (base_dir / ".gitignore").write_text(gitignore_content)

    # Create core directories
    core_dirs = [
        "teams",
        "servers",
        "knowledge",
        "memory",
        "tools",
        "guardrails",
        "protocols",
        "evals",
        "optimizers",
    ]

    for dir in core_dirs:
        dir_path = module_dir / dir
        dir_path.mkdir(parents=True, exist_ok=True)
        (dir_path / "__init__.py").touch()

    # Create tests directory
    tests_dir = base_dir / "tests"
    tests_dir.mkdir(exist_ok=True)

    # Create all project files
    create_project_files(base_dir, system_name)
    create_test_files(tests_dir, system_name)

    # Return created paths for reference
    return base_dir, module_dir


def copy_templates(base_dir: Path):
    """Copy templates from DSL templates directory."""
    # Get the package root directory
    package_root = Path(__file__).parent.parent.parent
    template_source = package_root / "dsl" / "templates"
    template_dest = base_dir / "templates"

    if not template_source.exists():
        raise FileNotFoundError(f"Template directory not found at {template_source}")

    # Create templates directory
    template_dest.mkdir(exist_ok=True)

    # Copy all template files
    for template_file in template_source.glob("*.yaml"):
        shutil.copy2(template_file, template_dest / template_file.name)


def create_pyproject_toml(base_dir: Path, agent_name: str):
    # Extract dependencies from main package
    dependencies, extras_require = extract_main_package_dependencies()

    # Format dependencies for pyproject.toml
    deps_str = ",\n    ".join(f'"{dep}"' for dep in dependencies)

    # Format optional dependencies
    optional_deps_str = ""
    if extras_require:
        optional_items = []
        for key, deps in extras_require.items():
            deps_formatted = ",\n    ".join(f'"{dep}"' for dep in deps)
            optional_items.append(f"{key} = [\n    {deps_formatted}\n]")
        optional_deps_str = "\n".join(optional_items)

    content = f'''[build-system]
requires = ["hatchling"]
build-backend = "hatchling.build"

[project]
name = "{agent_name}"
version = "0.1.0"
description = "An autonomous agent system powered by SuperOptiX"
authors = [
    {{name = "Your Name", email = "your.email@example.com"}},
]
readme = "README.md"
license = {{text = "MIT"}}
requires-python = ">=3.11"
dependencies = [
    {deps_str}
]

[project.optional-dependencies]
{optional_deps_str}

[project.urls]
Homepage = "https://github.com/yourusername/{agent_name}"
Repository = "https://github.com/yourusername/{agent_name}.git"
"Bug Tracker" = "https://github.com/yourusername/{agent_name}/issues"

[project.scripts]
{agent_name} = "{agent_name}.cli.main:main"

[tool.hatch.build.targets.wheel]
packages = ["{agent_name}"]

[tool.hatch.build.targets.wheel.sources]
"{agent_name}" = "{agent_name}"

[tool.black]
line-length = 88
target-version = ["py311"]

[tool.isort]
profile = "black"
multi_line_output = 3

[tool.ruff]
line-length = 88
target-version = "py311"
'''
    (base_dir / "pyproject.toml").write_text(content)


def create_readme(base_dir: Path, agent_name: str):
    content = f"""# {agent_name.title()} Agent System

An autonomous agent system for {agent_name.lower()} tasks.

## Installation

```bash
# Using uv (recommended)
uv sync
uv run python -m {agent_name.lower()}

# Or using pip
pip install -e .
```

## Project Structure

```
{agent_name.lower()}/
├── {agent_name.lower()}/
│   ├── agents/
│   │   └── playbook/     # Agent playbooks directory
│   ├── teams/
│   ├── servers/
│   ├── knowledge/
│   ├── memory/
│   ├── tools/
│   └── guardrails/
    ├── protocols/
│   ├── evals/
│   └── optimizers/
├── .env                # Environment variables
├── .gitignore          # Git ignore file
├── .pre-commit-config.yaml  # Pre-commit hooks configuration
├── pyproject.toml      # Project metadata and dependencies (uv-compatible)
├── README.md           # Project documentation
    ├── .super                # SuperOptiX project metadata
├── tests/
│   ├── conftest.py
│   └── test_agents.py
└── ...
```

## Running Tests

```bash
pytest tests/
```

## License

MIT
"""
    (base_dir / "README.md").write_text(content)


def create_precommit_config(base_dir: Path):
    content = """repos:
-   repo: https://github.com/pre-commit/pre-commit-hooks
    rev: v4.4.0
    hooks:
    -   id: trailing-whitespace
    -   id: end-of-file-fixer
    -   id: check-yaml
    -   id: check-added-large-files

-   repo: https://github.com/psf/black
    rev: 23.3.0
    hooks:
    -   id: black

-   repo: https://github.com/pycqa/isort
    rev: 5.12.0
    hooks:
    -   id: isort
        args: ["--profile", "black"]

-   repo: https://github.com/pycqa/flake8
    rev: 6.1.0
    hooks:
    -   id: flake8
"""
    (base_dir / ".pre-commit-config.yaml").write_text(content)


def create_test_files(tests_dir: Path, agent_name: str):
    """Create initial test files."""
    # Create __init__.py for tests
    (tests_dir / "__init__.py").touch()

    # Create conftest.py
    conftest_content = """import pytest

@pytest.fixture
def test_config():
    return {
        "name": "test_agent",
        "version": "0.1.0"
    }
"""
    (tests_dir / "conftest.py").write_text(conftest_content)

    # Create test_agents.py
    test_agents_content = f'''import pytest
from {agent_name}.agents import Agent

def test_agent_creation(test_config):
    """Test basic agent creation."""
    agent = Agent(test_config)
    assert agent.name == "test_agent"
    assert agent.version == "0.1.0"
'''
    (tests_dir / "test_agents.py").write_text(test_agents_content)


def init_project(args):
    """Initialize a new project with the given agent system."""
    try:
        system_name = args.name.lower()
        if not system_name:
            print("Please specify an agent system name")
            sys.exit(1)

        base_dir, module_dir = create_project_structure(system_name)

        # Create project files
        create_project_files(base_dir, system_name)
        create_test_files(base_dir / "tests", system_name)

        # Import Rich for colorful output
        from rich.console import Console
        from rich.panel import Panel

        console = Console()

        # Success celebration
        console.print("\n" + "=" * 80)
        console.print(
            Panel(
                f"🎉 [bold bright_green]SUCCESS![/] Your full-blown shippable Agentic System '[bold bright_cyan]{system_name}[/]' is ready!\n\n"
                f"🚀 [bold]You now own a complete agentic AI system in '[bold bright_cyan]{system_name}[/]'.[/]\n\nStart making it production-ready by evaluating, optimizing, and orchestrating with advanced agent engineering.",
                style="bright_green",
                border_style="bright_green",
            )
        )

        # Essential next steps
        next_steps = f"""🚀 [bold bright_cyan]GETTING STARTED[/]

[yellow]1. Move to your new project root and confirm setup:[/]
   [cyan]cd {system_name}[/]
   [dim]# You should see a .super file here – always run super commands from this directory[/]

[yellow]2. Pull your first agent:[/]
   [cyan]super agent pull developer[/]  [dim]# swap 'developer' for any agent name[/]

[yellow]3. Explore the marketplace:[/]
   [cyan]super market[/]

[yellow]4. Need the full guide?[/]
   [cyan]super docs[/]"""

        console.print(
            Panel(
                next_steps,
                title="🎯 Your Journey Starts Here",
                border_style="bright_cyan",
                padding=(1, 2),
            )
        )

        # Final message
        console.print("=" * 80)
        console.print(
            "🎯 [bold bright_green]Welcome to your Agentic System![/] Ready to build intelligent agents? 🚀"
        )
        console.print(f"📍 [bold]Next steps:[/] [cyan]cd {system_name}[/]")
        console.print("=" * 80 + "\n")

    except Exception as e:
        from rich.console import Console

        console = Console()
        console.print(f"\n[bold red]❌ Error initializing project:[/] {str(e)}")
        sys.exit(1)
