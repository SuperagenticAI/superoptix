"""Enhanced textbox for chat input with modern UX.

Provides a proper chat-like textbox experience instead of basic terminal input.
"""

import sys
import tty
import termios
from rich.console import Console
from rich.text import Text
from rich import box


class ChatTextBox:
    """Modern chat textbox with multi-line support and visual feedback."""

    def __init__(
        self,
        console: Console,
        placeholder: str = "Type your message...",
        max_height: int = 10,
        submit_on_enter: bool = False,
        show_char_count: bool = True,
    ):
        """Initialize chat textbox.

        Args:
                console: Rich console instance
                placeholder: Placeholder text when empty
                max_height: Maximum height in lines
                submit_on_enter: If True, Enter submits (Shift+Enter for newline)
                show_char_count: Show character count
        """
        self.console = console
        self.placeholder = placeholder
        self.max_height = max_height
        self.submit_on_enter = submit_on_enter
        self.show_char_count = show_char_count
        self.buffer = []
        self.cursor_line = 0
        self.cursor_col = 0

    def _get_char(self):
        """Get a single character from stdin."""
        fd = sys.stdin.fileno()
        old_settings = termios.tcgetattr(fd)
        try:
            tty.setraw(sys.stdin.fileno())
            ch = sys.stdin.read(1)
        finally:
            termios.tcsetattr(fd, termios.TCSADRAIN, old_settings)
        return ch

    def _render_textbox(self, content_lines: list, cursor_line: int, cursor_col: int):
        """Render the textbox with current content.

        Args:
                content_lines: Lines of text
                cursor_line: Current cursor line
                cursor_col: Current cursor column
        """
        # Clear previous output
        self.console.clear()

        # Header
        header = Text()
        header.append("╭", style="bright_cyan")
        header.append("─" * 68, style="bright_cyan")
        header.append("╮", style="bright_cyan")
        self.console.print(header)

        # Title
        title_line = Text()
        title_line.append("│ ", style="bright_cyan")
        title_line.append("💬 ", style="bold cyan")
        title_line.append("Message Super CLI", style="bold white")
        title_line.append(" " * 48, style="")
        title_line.append("│", style="bright_cyan")
        self.console.print(title_line)

        # Separator
        separator = Text()
        separator.append("├", style="bright_cyan")
        separator.append("─" * 68, style="bright_cyan")
        separator.append("┤", style="bright_cyan")
        self.console.print(separator)

        # Content area
        if not content_lines or (len(content_lines) == 1 and not content_lines[0]):
            # Show placeholder
            placeholder_line = Text()
            placeholder_line.append("│ ", style="bright_cyan")
            placeholder_line.append(self.placeholder, style="dim italic")
            placeholder_line.append(" " * (66 - len(self.placeholder)), style="")
            placeholder_line.append("│", style="bright_cyan")
            self.console.print(placeholder_line)
        else:
            # Show content with cursor
            for i, line in enumerate(content_lines):
                content_line = Text()
                content_line.append("│ ", style="bright_cyan")

                if i == cursor_line:
                    # Show cursor on this line
                    before_cursor = line[:cursor_col]
                    cursor_char = line[cursor_col] if cursor_col < len(line) else " "
                    after_cursor = (
                        line[cursor_col + 1 :] if cursor_col < len(line) else ""
                    )

                    content_line.append(before_cursor, style="white")
                    content_line.append(cursor_char, style="black on white")  # Cursor
                    content_line.append(after_cursor, style="white")
                else:
                    content_line.append(line, style="white")

                # Padding
                padding = 66 - len(line)
                if i == cursor_line and cursor_col >= len(line):
                    # Cursor at end of line
                    content_line.append(" " * (cursor_col - len(line)), style="")
                    content_line.append("█", style="white")  # Block cursor
                    padding = 66 - cursor_col - 1
                content_line.append(" " * padding, style="")
                content_line.append("│", style="bright_cyan")
                self.console.print(content_line)

        # Footer with hints
        footer_sep = Text()
        footer_sep.append("├", style="bright_cyan")
        footer_sep.append("─" * 68, style="bright_cyan")
        footer_sep.append("┤", style="bright_cyan")
        self.console.print(footer_sep)

        # Hints
        hint_line = Text()
        hint_line.append("│ ", style="bright_cyan")

        if self.submit_on_enter:
            hint_line.append("Press ", style="dim")
            hint_line.append("Enter", style="cyan")
            hint_line.append(" to send • ", style="dim")
            hint_line.append("Shift+Enter", style="cyan")
            hint_line.append(" for new line", style="dim")
        else:
            hint_line.append("Press ", style="dim")
            hint_line.append("Ctrl+D", style="cyan")
            hint_line.append(" to send • ", style="dim")
            hint_line.append("Enter", style="cyan")
            hint_line.append(" for new line", style="dim")

        hint_line.append(" " * (66 - len(hint_line.plain) + 2), style="")
        hint_line.append("│", style="bright_cyan")
        self.console.print(hint_line)

        # Character count
        if self.show_char_count:
            total_chars = sum(len(line) for line in content_lines)
            count_line = Text()
            count_line.append("│ ", style="bright_cyan")
            count_text = f"{total_chars} characters"
            count_line.append(count_text, style="dim yellow")
            count_line.append(" " * (66 - len(count_text)), style="")
            count_line.append("│", style="bright_cyan")
            self.console.print(count_line)

        # Bottom border
        footer = Text()
        footer.append("╰", style="bright_cyan")
        footer.append("─" * 68, style="bright_cyan")
        footer.append("╯", style="bright_cyan")
        self.console.print(footer)

    def get_input(self) -> str:
        """Get multi-line input from user with real-time display.

        Returns:
                User's input as string
        """
        content_lines = [""]
        cursor_line = 0
        cursor_col = 0

        # Initial render
        self._render_textbox(content_lines, cursor_line, cursor_col)

        # Input loop (simplified version - real implementation would use proper terminal handling)
        # For now, fall back to basic input
        result = input("\nYour message: ")
        return result


class SimpleChatBox:
    """Simplified chat box with better visual feedback using Rich's built-in input."""

    def __init__(
        self,
        console: Console,
        placeholder: str = "Type your message here...",
        show_hints: bool = True,
        max_display_length: int = 60,
    ):
        """Initialize simple chat box.

        Args:
                console: Rich console instance
                placeholder: Placeholder text
                show_hints: Show input hints
                max_display_length: Max length to display in box
        """
        self.console = console
        self.placeholder = placeholder
        self.show_hints = show_hints
        self.max_display_length = max_display_length

    def get_input(self) -> str:
        """Get input with enhanced visual feedback.

        Returns:
                User's input as string
        """
        from rich.prompt import Prompt

        # Create beautiful input box
        self._render_input_box()

        # Get input
        prompt_text = Text()
        prompt_text.append("│ ", style="bright_cyan")
        prompt_text.append("▶ ", style="bold yellow")

        user_input = Prompt.ask(
            prompt_text,
            console=self.console,
            default="",
        )

        # Close the box
        self._render_footer()

        return user_input

    def _render_input_box(self):
        """Render the input box header."""
        width = 70

        # Header
        header = Text()
        header.append("╭", style="bright_cyan")
        header.append("─" * width, style="bright_cyan")
        header.append("╮", style="bright_cyan")
        self.console.print(header)

        # Title
        title_line = Text()
        title_line.append("│ ", style="bright_cyan")
        title_line.append("💬 ", style="bold cyan")
        title_line.append("Your Message", style="bold white")
        padding = width - len("💬 Your Message") - 4
        title_line.append(" " * padding, style="")
        title_line.append("│", style="bright_cyan")
        self.console.print(title_line)

        # Separator
        separator = Text()
        separator.append("├", style="bright_cyan")
        separator.append("─" * width, style="bright_cyan")
        separator.append("┤", style="bright_cyan")
        self.console.print(separator)

    def _render_footer(self):
        """Render the input box footer."""
        width = 70

        # Footer with hints
        if self.show_hints:
            separator = Text()
            separator.append("├", style="bright_cyan")
            separator.append("─" * width, style="bright_cyan")
            separator.append("┤", style="bright_cyan")
            self.console.print(separator)

            # Hint line
            hint_line = Text()
            hint_line.append("│ ", style="bright_cyan")
            hint_line.append("💡 ", style="yellow")
            hint_line.append("Tip: ", style="bold cyan")
            hint_line.append("Use ", style="dim")
            hint_line.append("/help", style="cyan")
            hint_line.append(" for commands • Press ", style="dim")
            hint_line.append("Ctrl+C", style="yellow")
            hint_line.append(" to exit", style="dim")

            remaining = width - len(hint_line.plain) + 2
            hint_line.append(" " * remaining, style="")
            hint_line.append("│", style="bright_cyan")
            self.console.print(hint_line)

        # Bottom border
        footer = Text()
        footer.append("╰", style="bright_cyan")
        footer.append("─" * width, style="bright_cyan")
        footer.append("╯", style="bright_cyan")
        self.console.print(footer)


class EnhancedChatInput:
    """Enhanced chat input with typing indicator and better UX."""

    def __init__(self, console: Console):
        """Initialize enhanced chat input.

        Args:
                console: Rich console instance
        """
        self.console = console

    def get_input(self) -> str:
        """Get input with enhanced UX including typing feedback.

        Returns:
                User's input string
        """
        from rich.prompt import Prompt
        from rich.panel import Panel

        # Create input panel
        self.console.print()
        self.console.print()

        # Input panel with beautiful styling
        input_panel = Panel(
            "",
            title="[bold cyan]💬 Your Message[/bold cyan]",
            title_align="left",
            border_style="bright_cyan",
            box=box.ROUNDED,
            padding=(0, 1),
        )

        self.console.print(input_panel)

        # Move cursor up to type inside the panel
        # For simplicity, use prompt below the box
        prompt_text = Text()
        prompt_text.append("▶ ", style="bold yellow")
        prompt_text.append("Type here: ", style="dim")

        user_input = Prompt.ask(
            prompt_text,
            console=self.console,
        )

        return user_input


def create_modern_input_box(console: Console) -> tuple:
    """Create a modern input box with all components.

    Args:
            console: Rich console instance

    Returns:
            Tuple of rendering components
    """
    width = 70

    # Top border with gradient
    top = Text()
    top.append("╭", style="bright_cyan")
    top.append("─" * width, style="bright_cyan")
    top.append("╮", style="bright_cyan")

    # Title bar
    title = Text()
    title.append("│ ", style="bright_cyan")
    title.append("💬 ", style="bold cyan")
    title.append("Message Super CLI", style="bold white")
    title.append(" " * (width - 22), style="")
    title.append("│", style="bright_cyan")

    # Separator
    sep = Text()
    sep.append("├", style="bright_cyan")
    sep.append("─" * width, style="bright_cyan")
    sep.append("┤", style="bright_cyan")

    # Prompt prefix
    prompt = Text()
    prompt.append("│ ", style="bright_cyan")
    prompt.append("▶ ", style="bold yellow")

    # Hint separator
    hint_sep = Text()
    hint_sep.append("├", style="bright_cyan")
    hint_sep.append("─" * width, style="bright_cyan")
    hint_sep.append("┤", style="bright_cyan")

    # Hint text
    hint = Text()
    hint.append("│ ", style="bright_cyan")
    hint.append("💡 ", style="yellow")
    hint.append("Press ", style="dim")
    hint.append("Enter", style="cyan")
    hint.append(" to send • ", style="dim")
    hint.append("Ctrl+C", style="yellow")
    hint.append(" to exit • ", style="dim")
    hint.append("/help", style="cyan")
    hint.append(" for commands", style="dim")
    remaining = width - len(hint.plain) + 2
    hint.append(" " * remaining, style="")
    hint.append("│", style="bright_cyan")

    # Bottom border
    bottom = Text()
    bottom.append("╰", style="bright_cyan")
    bottom.append("─" * width, style="bright_cyan")
    bottom.append("╯", style="bright_cyan")

    return top, title, sep, prompt, hint_sep, hint, bottom
