"""Enhanced thinking animations for Super CLI.

Provides Claude Code-style animations and typing effects for better UX.
"""

import time
import random
from typing import List, Optional
from rich.console import Console
from rich.live import Live
from rich.text import Text
from rich.panel import Panel
from rich.align import Align
from rich import box


class ThinkingAnimation:
    """Claude Code-style thinking animation with progressive updates."""

    # Engaging messages for different phases
    THINKING_MESSAGES = [
        "🤔 Analyzing your request",
        "🧠 Understanding what you need",
        "💭 Thinking this through",
        "🎯 Processing your command",
        "✨ Let me cook",
        "🔮 Figuring this out",
        "💡 Got an idea",
        "🌟 Making magic happen",
        "🧩 Putting pieces together",
        "🎨 Crafting the solution",
        "🔧 Assembling the parts",
        "⚡ Getting things ready",
        "🎪 Setting up the show",
        "🌈 Exploring possibilities",
        "🎵 Orchestrating the plan",
    ]

    PREPARING_MESSAGES = [
        "🔧 Preparing the command",
        "⚙️ Tuning parameters",
        "🎛️ Configuring setup",
        "📝 Writing the recipe",
        "🗺️ Charting the course",
        "🧭 Finding the path",
        "🎯 Aiming for perfection",
        "🔨 Forging the command",
        "🎬 Lights, camera",
        "🚀 Preparing for launch",
    ]

    EXECUTING_MESSAGES = [
        "⚡ Running the command",
        "🚀 Launching your request",
        "🔥 Executing with style",
        "💫 Making it happen",
        "⚙️ Gears turning",
        "🎪 Show time",
        "🧠 AI at work",
        "✨ Working the magic",
        "🎨 Creating masterpiece",
        "🔨 Building it now",
        "🎬 Action",
        "💪 Flexing AI muscles",
        "🧙 Casting the spell",
        "🎵 In the zone",
        "🌟 Shining bright",
        "⚡ Zapping into existence",
    ]

    def __init__(self, console: Console):
        """Initialize animation.

        Args:
                console: Rich console instance
        """
        self.console = console
        self._stop_animation = False
        self._current_message = ""

    def _animate_dots(self, base_message: str, duration: float = 2.0):
        """Animate thinking dots like Claude Code.

        Args:
                base_message: Base message to display
                duration: How long to animate
        """
        dots_cycle = ["   ", ".  ", ".. ", "..."]
        start_time = time.time()

        with Live(console=self.console, refresh_per_second=4) as live:
            while not self._stop_animation and (time.time() - start_time) < duration:
                for dots in dots_cycle:
                    if self._stop_animation:
                        break

                    text = Text()
                    text.append(base_message, style="dim cyan")
                    text.append(dots, style="dim cyan")

                    live.update(text)
                    time.sleep(0.15)

    def thinking(self, message: Optional[str] = None, duration: float = 1.5):
        """Show thinking animation.

        Args:
                message: Custom message or random will be chosen
                duration: How long to show animation
        """
        msg = message or random.choice(self.THINKING_MESSAGES)
        self._current_message = msg
        self._stop_animation = False
        self._animate_dots(msg, duration)

    def preparing(self, message: Optional[str] = None, duration: float = 1.0):
        """Show preparing animation.

        Args:
                message: Custom message or random will be chosen
                duration: How long to show animation
        """
        msg = message or random.choice(self.PREPARING_MESSAGES)
        self._current_message = msg
        self._stop_animation = False
        self._animate_dots(msg, duration)

    def executing(self, command: str, message: Optional[str] = None):
        """Show executing animation with command context.

        Args:
                command: Command being executed
                message: Custom message or random will be chosen
        """
        msg = message or random.choice(self.EXECUTING_MESSAGES)

        # Just show the executing message, not the technical command
        # Users don't need to see the internal commands in Super CLI
        self._current_message = msg
        self._stop_animation = False
        # Note: Don't print panel here - the animation continues in background

    def stop(self):
        """Stop the current animation."""
        self._stop_animation = True

    def multi_stage(self, stages: List[str], durations: Optional[List[float]] = None):
        """Run multi-stage animation showing progress.

        Args:
                stages: List of stage names
                durations: Duration for each stage (defaults to 1.0 each)
        """
        if durations is None:
            durations = [1.0] * len(stages)

        for i, (stage, duration) in enumerate(zip(stages, durations)):
            self.console.print(
                Text.assemble(
                    ("", ""),
                    (f"[{i + 1}/{len(stages)}] ", "dim"),
                    (stage, "cyan"),
                )
            )
            self._stop_animation = False
            self._animate_dots("  ", duration)
            self.console.print(Text.assemble(("  ✓ ", "green"), (stage, "dim green")))


class TypeWriter:
    """Typing animation for text output like Claude Code."""

    def __init__(self, console: Console, speed: str = "fast"):
        """Initialize typewriter.

        Args:
                console: Rich console instance
                speed: Typing speed - "slow", "medium", "fast", "instant"
        """
        self.console = console

        # Speed settings (seconds per character)
        speeds = {"slow": 0.05, "medium": 0.03, "fast": 0.01, "instant": 0.001}
        self.delay = speeds.get(speed, 0.01)

    def type_text(self, text: str, style: str = ""):
        """Type out text with animation.

        Args:
                text: Text to type
                style: Rich style to apply
        """
        for char in text:
            self.console.print(char, end="", style=style)
            time.sleep(self.delay)
        self.console.print()  # New line at end

    def type_panel(self, content: str, title: str = "", border_style: str = "cyan"):
        """Type out panel content.

        Args:
                content: Panel content
                title: Panel title
                border_style: Border color
        """
        # Create panel but type the content
        self.console.print()

        # Type title if provided
        if title:
            self.console.print(
                Text(f"╭─ {title} ", style=f"bold {border_style}"), end=""
            )
            self.console.print(Text("─" * (60 - len(title)), style=border_style))
        else:
            self.console.print(Text("╭" + "─" * 60 + "╮", style=border_style))

        # Type content line by line
        for line in content.split("\n"):
            self.console.print(Text("│ ", style=border_style), end="")
            for char in line:
                self.console.print(char, end="")
                time.sleep(self.delay)
            self.console.print(Text(" " * (58 - len(line)) + "│", style=border_style))

        self.console.print(Text("╰" + "─" * 60 + "╯", style=border_style))
        self.console.print()


class ProgressiveStatus:
    """Progressive status updates like Claude Code showing what's happening."""

    def __init__(self, console: Console):
        """Initialize progressive status.

        Args:
                console: Rich console instance
        """
        self.console = console
        self.steps: List[tuple] = []
        self.current_step = 0

    def add_step(self, name: str, description: str = ""):
        """Add a step to track.

        Args:
                name: Step name
                description: Step description
        """
        self.steps.append((name, description, "pending"))

    def start_step(self, index: int):
        """Start a step.

        Args:
                index: Step index
        """
        if index < len(self.steps):
            name, desc, _ = self.steps[index]
            self.steps[index] = (name, desc, "running")
            self.current_step = index
            self._render()

    def complete_step(self, index: int):
        """Complete a step.

        Args:
                index: Step index
        """
        if index < len(self.steps):
            name, desc, _ = self.steps[index]
            self.steps[index] = (name, desc, "complete")
            self._render()

    def _render(self):
        """Render current status."""
        self.console.print()

        for i, (name, desc, status) in enumerate(self.steps):
            if status == "complete":
                icon = "✓"
                style = "green"
            elif status == "running":
                icon = "▶"
                style = "cyan"
            else:
                icon = "○"
                style = "dim"

            text = Text()
            text.append(f"  {icon} ", style=style)
            text.append(name, style=style if status == "running" else "dim")

            if desc and status == "running":
                text.append(f" - {desc}", style="dim")

            self.console.print(text)

        self.console.print()


def create_chat_box(console: Console, title: str = "Message Super CLI") -> tuple:
    """Create beautiful chatbox UI.

    Args:
            console: Rich console instance
            title: Chatbox title

    Returns:
            Tuple of (header_text, footer_text, prompt_text)
    """
    width = 70

    # Header
    header = Text()
    header.append("╭", style="bright_cyan")
    header.append("─" * width, style="bright_cyan")
    header.append("╮", style="bright_cyan")

    # Title line
    title_line = Text()
    title_line.append("│ ", style="bright_cyan")
    title_line.append("💬 ", style="bold cyan")
    title_line.append(title, style="bold white")
    padding = width - len(title) - 4
    title_line.append(" " * padding, style="")
    title_line.append("│", style="bright_cyan")

    # Separator
    separator = Text()
    separator.append("├", style="bright_cyan")
    separator.append("─" * width, style="bright_cyan")
    separator.append("┤", style="bright_cyan")

    # Prompt
    prompt = Text()
    prompt.append("│ ", style="bright_cyan")
    prompt.append("Super", style="bold bright_magenta")
    prompt.append("Opti", style="bold bright_cyan")
    prompt.append("X", style="bold bright_yellow")
    prompt.append(" › ", style="dim")

    # Footer
    footer = Text()
    footer.append("╰", style="bright_cyan")
    footer.append("─" * width, style="bright_cyan")
    footer.append("╯", style="bright_cyan")

    return header, title_line, separator, prompt, footer


def show_thinking_panel(console: Console, message: str, emoji: str = "🤔"):
    """Show thinking panel with animation.

    Args:
            console: Rich console instance
            message: Message to display
            emoji: Emoji to use
    """
    panel = Panel(
        Align.center(
            Text.assemble(
                (emoji + " ", "yellow"),
                (message, "cyan"),
            )
        ),
        border_style="dim cyan",
        box=box.ROUNDED,
        padding=(0, 2),
    )
    console.print(panel)
