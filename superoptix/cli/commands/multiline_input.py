"""Multi-line input textbox for Super CLI.

Provides a proper multi-line chat experience with visual feedback.
"""

from rich.console import Console
from rich.text import Text
from rich.panel import Panel
from rich import box


class MultiLineInput:
    """Multi-line input textbox with live preview and editing."""

    def __init__(
        self,
        console: Console,
        title: str = "Your Message",
        placeholder: str = "Type your message (Ctrl+D to send, Ctrl+C to cancel)...",
        max_lines: int = 10,
        show_line_numbers: bool = False,
    ):
        """Initialize multi-line input.

        Args:
            console: Rich console instance
            title: Title for the input box
            placeholder: Placeholder text
            max_lines: Maximum number of lines
            show_line_numbers: Show line numbers
        """
        self.console = console
        self.title = title
        self.placeholder = placeholder
        self.max_lines = max_lines
        self.show_line_numbers = show_line_numbers

    def get_input(self) -> str:
        """Get multi-line input from user.

        Returns:
            User's input as string
        """
        lines = []

        # Show input panel
        self.console.print()
        panel = Panel(
            f"[dim]{self.placeholder}[/dim]\n\n"
            "[dim italic]Type your message below (press Enter for new lines)[/dim italic]\n"
            "[dim italic]When done, press Ctrl+D (or type 'END' on a new line) to send[/dim italic]",
            title=f"[bold cyan]💬 {self.title}[/bold cyan]",
            border_style="bright_cyan",
            box=box.ROUNDED,
            padding=(1, 2),
        )
        self.console.print(panel)
        self.console.print()

        # Get multi-line input
        self.console.print("[bold yellow]▼ Start typing:[/bold yellow]")
        self.console.print()

        line_num = 1
        try:
            while True:
                if self.show_line_numbers:
                    prefix = f"[dim]{line_num:2d} │[/dim] "
                    line = self.console.input(prefix)
                else:
                    line = self.console.input("[dim]│[/dim] ")

                # Check for end marker
                if line.strip().upper() == "END":
                    break

                lines.append(line)
                line_num += 1

                if len(lines) >= self.max_lines:
                    self.console.print(
                        f"\n[yellow]⚠ Maximum {self.max_lines} lines reached[/yellow]\n"
                    )
                    break

        except EOFError:
            # Ctrl+D pressed
            pass
        except KeyboardInterrupt:
            # Ctrl+C pressed
            self.console.print("\n[yellow]Input cancelled[/yellow]")
            return ""

        # Show preview of what was entered
        if lines:
            self.console.print()
            self._show_preview(lines)

        return "\n".join(lines)

    def _show_preview(self, lines: list):
        """Show preview of entered text.

        Args:
            lines: List of entered lines
        """
        content = Text()
        for i, line in enumerate(lines):
            if self.show_line_numbers:
                content.append(f"{i + 1:2d} │ ", style="dim")
            content.append(line + "\n", style="white")

        preview_panel = Panel(
            content,
            title="[bold green]✓ Message Preview[/bold green]",
            border_style="green",
            box=box.ROUNDED,
            padding=(0, 1),
        )

        self.console.print(preview_panel)


class InlineTextBox:
    """Inline textbox that expands as user types (best UX for most cases)."""

    def __init__(
        self,
        console: Console,
        placeholder: str = "Type your message...",
        show_char_count: bool = True,
        emoji_support: bool = True,
    ):
        """Initialize inline textbox.

        Args:
            console: Rich console instance
            placeholder: Placeholder text
            show_char_count: Show character count
            emoji_support: Show emoji hint
        """
        self.console = console
        self.placeholder = placeholder
        self.show_char_count = show_char_count
        self.emoji_support = emoji_support

    def get_input(self) -> str:
        """Get input with inline textbox.

        Returns:
            User's input
        """
        from rich.prompt import Prompt

        # Beautiful textbox header
        width = 72

        # Top border
        top = Text()
        top.append("╭", style="bright_cyan")
        top.append("─" * width, style="bright_cyan")
        top.append("╮", style="bright_cyan")
        self.console.print(top)

        # Title
        title_line = Text()
        title_line.append("│ ", style="bright_cyan")
        title_line.append("💬 ", style="bold cyan")
        title_line.append("Your Message to Super CLI", style="bold white")
        title_line.append(" " * (width - 30), style="")
        title_line.append("│", style="bright_cyan")
        self.console.print(title_line)

        # Separator
        sep = Text()
        sep.append("├", style="bright_cyan")
        sep.append("─" * width, style="bright_cyan")
        sep.append("┤", style="bright_cyan")
        self.console.print(sep)

        # Input line with gradient SuperOptiX prompt
        prompt_prefix = Text()
        prompt_prefix.append("│ ", style="bright_cyan")
        prompt_prefix.append("Super", style="bold bright_magenta")
        prompt_prefix.append("Opti", style="bold bright_cyan")
        prompt_prefix.append("X", style="bold bright_yellow")
        prompt_prefix.append(" › ", style="dim")

        user_input = Prompt.ask(prompt_prefix, console=self.console, default="")

        # Show character count if enabled
        if self.show_char_count and user_input:
            count_line = Text()
            count_line.append("│ ", style="bright_cyan")
            count_text = f"✓ {len(user_input)} characters"
            count_line.append(count_text, style="dim green")
            count_line.append(" " * (width - len(count_text) - 4), style="")
            count_line.append("│", style="bright_cyan")
            self.console.print(count_line)

        # Hint separator
        hint_sep = Text()
        hint_sep.append("├", style="bright_cyan")
        hint_sep.append("─" * width, style="bright_cyan")
        hint_sep.append("┤", style="bright_cyan")
        self.console.print(hint_sep)

        # Hints
        hint = Text()
        hint.append("│ ", style="bright_cyan")
        hint.append("💡 ", style="yellow")
        hint.append("Tip: ", style="bold cyan")
        hint.append("Use ", style="dim")
        hint.append("/help", style="cyan")
        hint.append(" for commands • ", style="dim")
        hint.append("/exit", style="cyan")
        hint.append(" to quit", style="dim")

        if self.emoji_support:
            hint.append(" • ", style="dim")
            hint.append("Emojis work! 🚀", style="dim")

        remaining = width - len(hint.plain) + 2
        hint.append(" " * remaining, style="")
        hint.append("│", style="bright_cyan")
        self.console.print(hint)

        # Bottom border
        bottom = Text()
        bottom.append("╰", style="bright_cyan")
        bottom.append("─" * width, style="bright_cyan")
        bottom.append("╯", style="bright_cyan")
        self.console.print(bottom)

        return user_input


class CompactChatInput:
    """Most compact chat input - perfect for quick interactions."""

    def __init__(self, console: Console):
        """Initialize compact chat input.

        Args:
            console: Rich console instance
        """
        self.console = console

    def get_input(self) -> str:
        """Get input with compact design.

        Returns:
            User's input
        """
        from rich.prompt import Prompt

        # Single-line compact box
        self.console.print()

        # Top with updated title
        self.console.print(
            Text(
                "┌─ 💬 Your Message to Super CLI ───────────────────────┐",
                style="bright_cyan",
            )
        )

        # Input with gradient SuperOptiX prompt
        prompt = Text()
        prompt.append("│ ", style="bright_cyan")
        prompt.append("Super", style="bold bright_magenta")
        prompt.append("Opti", style="bold bright_cyan")
        prompt.append("X", style="bold bright_yellow")
        prompt.append(" › ", style="dim")

        user_input = Prompt.ask(prompt, console=self.console)

        # Bottom
        self.console.print(
            Text(
                "└──────────────────────────────────────────────────────┘",
                style="bright_cyan",
            )
        )

        # Inline hint
        self.console.print(
            Text.assemble(
                ("  💡 ", "yellow"),
                ("Tip: ", "cyan"),
                ("Type ", "dim"),
                ("/help", "cyan"),
                (" for commands or ", "dim"),
                ("/exit", "cyan"),
                (" to quit", "dim"),
            )
        )

        return user_input
