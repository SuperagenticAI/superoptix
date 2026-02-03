"""
SuperOptiX Core Tools
=====================

Essential tools for SuperOptiX agents. These are the fundamental tools
that provide basic functionality like web search, calculations, file operations, etc.
"""

import datetime
import json
import math
from pathlib import Path
from typing import List


class WebSearchTool:
    """Web search functionality for agents."""

    def __init__(self, engine: str = "duckduckgo", max_results: int = 5):
        self.engine = engine
        self.max_results = max_results

    def search(self, query: str) -> str:
        """Search the web for information."""
        try:
            # Basic implementation - integrate with actual search APIs
            results = f"🔍 Web search results for: '{query}'\n"
            results += f"Using {self.engine} search engine (max {self.max_results} results)\n\n"
            results += "[Note: Integrate with actual search API like DuckDuckGo, Serper, etc.]\n"
            results += "Sample results would appear here in production.\n"
            return results
        except Exception as e:
            return f"❌ Web search failed: {str(e)}"


class CalculatorTool:
    """Mathematical calculation tool for agents."""

    def __init__(self, precision: int = 10):
        self.precision = precision

    def calculate(self, expression: str) -> str:
        """Perform safe mathematical calculations."""
        try:
            # Safe mathematical evaluation
            import ast
            import operator as op

            # Supported operations
            operators = {
                ast.Add: op.add,
                ast.Sub: op.sub,
                ast.Mult: op.mul,
                ast.Div: op.truediv,
                ast.Pow: op.pow,
                ast.USub: op.neg,
                ast.Mod: op.mod,
            }

            # Supported functions
            functions = {
                "abs": abs,
                "round": round,
                "min": min,
                "max": max,
                "sum": sum,
                "pow": pow,
                "sqrt": math.sqrt,
                "sin": math.sin,
                "cos": math.cos,
                "tan": math.tan,
                "log": math.log,
                "exp": math.exp,
                "ceil": math.ceil,
                "floor": math.floor,
            }

            def eval_expr(expr):
                return eval_(ast.parse(expression, mode="eval").body)

            def eval_(node):
                if isinstance(node, ast.Constant):
                    return node.value
                elif isinstance(node, ast.Num):  # Legacy Python < 3.8
                    return node.n
                elif isinstance(node, ast.BinOp):
                    return operators[type(node.op)](eval_(node.left), eval_(node.right))
                elif isinstance(node, ast.UnaryOp):
                    return operators[type(node.op)](eval_(node.operand))
                elif isinstance(node, ast.Call):
                    if isinstance(node.func, ast.Name) and node.func.id in functions:
                        args = [eval_(arg) for arg in node.args]
                        return functions[node.func.id](*args)
                    else:
                        raise TypeError(f"Function '{node.func.id}' not allowed")
                elif isinstance(node, ast.Name):
                    if node.id in functions:
                        return functions[node.id]
                    else:
                        raise NameError(f"Name '{node.id}' not defined")
                else:
                    raise TypeError(f"Node type '{type(node)}' not supported")

            result = eval_expr(expression)

            # Format result with specified precision
            if isinstance(result, float):
                result = round(result, self.precision)

            return f"🧮 {expression} = {result}"

        except Exception as e:
            return f"❌ Calculation error: {str(e)}"


class FileReaderTool:
    """File reading tool with safety restrictions."""

    def __init__(
        self, allowed_extensions: List[str] = None, max_file_size_mb: int = 10
    ):
        self.allowed_extensions = allowed_extensions or [
            "txt",
            "md",
            "json",
            "yaml",
            "csv",
        ]
        self.max_file_size_bytes = max_file_size_mb * 1024 * 1024

    def read_file(self, file_path: str) -> str:
        """Read file contents safely with restrictions."""
        try:
            path = Path(file_path).resolve()

            # Security checks
            if not path.exists():
                return f"❌ File not found: {file_path}"

            if path.suffix[1:].lower() not in self.allowed_extensions:
                return f"❌ File type not allowed. Allowed: {self.allowed_extensions}"

            if path.stat().st_size > self.max_file_size_bytes:
                max_mb = self.max_file_size_bytes // (1024 * 1024)
                return f"❌ File too large (max {max_mb}MB)"

            # Read file content
            with open(path, "r", encoding="utf-8") as f:
                content = f.read()

            # Truncate if very long (for display purposes)
            max_display = 3000
            if len(content) > max_display:
                content = (
                    content[:max_display]
                    + f"\n\n... (truncated, total {len(content)} chars)"
                )

            return f"📄 File: {path.name}\n{'=' * 50}\n{content}"

        except UnicodeDecodeError:
            return "❌ Cannot read file: unsupported encoding (try UTF-8)"
        except PermissionError:
            return f"❌ Permission denied reading file: {file_path}"
        except Exception as e:
            return f"❌ File read error: {str(e)}"


class DateTimeTool:
    """Date and time utilities for agents."""

    def get_current_time(self, format_string: str = "%Y-%m-%d %H:%M:%S") -> str:
        """Get current date and time."""
        try:
            now = datetime.datetime.now()
            return f"🕐 Current time: {now.strftime(format_string)}"
        except Exception as e:
            return f"❌ Time error: {str(e)}"

    def format_date(
        self, date_string: str, input_format: str, output_format: str
    ) -> str:
        """Format date string from one format to another."""
        try:
            parsed_date = datetime.datetime.strptime(date_string, input_format)
            formatted = parsed_date.strftime(output_format)
            return f"📅 Formatted date: {formatted}"
        except Exception as e:
            return f"❌ Date formatting error: {str(e)}"


class TextAnalyzerTool:
    """Text analysis utilities for agents."""

    def analyze_text(self, text: str) -> str:
        """Analyze text for basic statistics."""
        try:
            words = text.split()
            sentences = text.split(".")
            paragraphs = text.split("\n\n")

            # Character counts
            char_count = len(text)
            char_count_no_spaces = len(text.replace(" ", ""))

            # Word analysis
            word_count = len(words)
            avg_word_length = sum(
                len(word.strip('.,!?;:"()[]{}')) for word in words
            ) / max(word_count, 1)

            # Sentence analysis
            sentence_count = len([s for s in sentences if s.strip()])
            avg_sentence_length = word_count / max(sentence_count, 1)

            analysis = f"""📊 Text Analysis Report
{"=" * 50}
Characters (total): {char_count:,}
Characters (no spaces): {char_count_no_spaces:,}
Words: {word_count:,}
Sentences: {sentence_count}
Paragraphs: {len(paragraphs)}

Averages:
- Word length: {avg_word_length:.1f} characters
- Sentence length: {avg_sentence_length:.1f} words

Readability Notes:
- Short sentences (<15 words): Good for readability
- Medium sentences (15-25 words): Moderate complexity
- Long sentences (>25 words): May reduce readability
"""
            return analysis

        except Exception as e:
            return f"❌ Text analysis error: {str(e)}"


class JSONProcessorTool:
    """JSON processing utilities for agents."""

    def parse_json(self, json_string: str) -> str:
        """Parse and validate JSON string."""
        try:
            parsed = json.loads(json_string)
            formatted = json.dumps(parsed, indent=2, ensure_ascii=False)
            return f"✅ Valid JSON:\n{formatted}"
        except json.JSONDecodeError as e:
            return f"❌ Invalid JSON: {str(e)}"
        except Exception as e:
            return f"❌ JSON processing error: {str(e)}"

    def extract_json_field(self, json_string: str, field_path: str) -> str:
        """Extract specific field from JSON using dot notation."""
        try:
            data = json.loads(json_string)

            # Navigate through nested fields using dot notation
            fields = field_path.split(".")
            current = data

            for field in fields:
                if isinstance(current, dict) and field in current:
                    current = current[field]
                else:
                    return f"❌ Field '{field_path}' not found in JSON"

            return (
                f"📄 {field_path}: {json.dumps(current, indent=2, ensure_ascii=False)}"
            )

        except json.JSONDecodeError as e:
            return f"❌ Invalid JSON: {str(e)}"
        except Exception as e:
            return f"❌ Field extraction error: {str(e)}"


class CodeFormatterTool:
    """Code formatting utilities for agents."""

    def format_code(self, code: str, language: str = "python") -> str:
        """Format code with basic syntax highlighting and structure."""
        try:
            lines = code.split("\n")
            formatted_lines = []
            indent_level = 0

            for line in lines:
                stripped = line.strip()
                if not stripped:
                    formatted_lines.append("")
                    continue

                # Adjust indentation for Python-like languages
                if language.lower() in ["python", "py"]:
                    if stripped.endswith(":"):
                        formatted_lines.append("    " * indent_level + stripped)
                        indent_level += 1
                    elif stripped.startswith(("return", "break", "continue", "pass")):
                        formatted_lines.append("    " * indent_level + stripped)
                    elif stripped.startswith(("else:", "elif", "except:", "finally:")):
                        indent_level = max(0, indent_level - 1)
                        formatted_lines.append("    " * indent_level + stripped)
                        indent_level += 1
                    else:
                        formatted_lines.append("    " * indent_level + stripped)
                else:
                    formatted_lines.append(stripped)

            formatted_code = "\n".join(formatted_lines)

            return f"""💻 Formatted {language.upper()} Code:
{"=" * 50}
```{language}
{formatted_code}
```
"""
        except Exception as e:
            return f"❌ Code formatting error: {str(e)}"


class DataProcessorTool:
    """Data processing utilities for agents."""

    def process_csv_data(self, csv_data: str, operation: str = "analyze") -> str:
        """Process CSV data with various operations."""
        try:
            lines = csv_data.strip().split("\n")
            if len(lines) < 2:
                return "❌ CSV data must have at least a header and one data row"

            headers = [h.strip() for h in lines[0].split(",")]
            rows = []

            for line in lines[1:]:
                row = [cell.strip() for cell in line.split(",")]
                if len(row) == len(headers):
                    rows.append(row)

            if operation == "analyze":
                return f"""📊 CSV Data Analysis:
{"=" * 50}
Columns: {len(headers)}
Rows: {len(rows)}
Headers: {", ".join(headers)}

Sample data (first 3 rows):
{self._format_table(headers, rows[:3])}
"""
            elif operation == "summary":
                numeric_cols = []
                for i, header in enumerate(headers):
                    try:
                        values = [
                            float(row[i])
                            for row in rows
                            if row[i].replace(".", "").replace("-", "").isdigit()
                        ]
                        if values:
                            numeric_cols.append((header, values))
                    except:
                        continue

                summary = "📈 Numeric Column Summary:\n"
                for col_name, values in numeric_cols:
                    avg = sum(values) / len(values)
                    minimum = min(values)
                    maximum = max(values)
                    summary += f"\n{col_name}:\n"
                    summary += f"  Average: {avg:.2f}\n"
                    summary += f"  Min: {minimum}\n"
                    summary += f"  Max: {maximum}\n"

                return (
                    summary if numeric_cols else "No numeric columns found for summary"
                )

            return "❌ Unsupported operation. Use 'analyze' or 'summary'"

        except Exception as e:
            return f"❌ Data processing error: {str(e)}"

    def _format_table(self, headers: List[str], rows: List[List[str]]) -> str:
        """Format data as a simple table."""
        if not rows:
            return "No data rows"

        # Calculate column widths
        col_widths = [len(h) for h in headers]
        for row in rows:
            for i, cell in enumerate(row):
                if i < len(col_widths):
                    col_widths[i] = max(col_widths[i], len(str(cell)))

        # Format table
        separator = "+" + "+".join(["-" * (w + 2) for w in col_widths]) + "+"
        header_row = (
            "|"
            + "|".join([f" {h:<{col_widths[i]}} " for i, h in enumerate(headers)])
            + "|"
        )

        table = separator + "\n" + header_row + "\n" + separator + "\n"

        for row in rows:
            row_str = (
                "|"
                + "|".join(
                    [
                        f" {str(row[i]):<{col_widths[i]}} "
                        if i < len(row)
                        else f" {'':>{col_widths[i]}} "
                        for i in range(len(headers))
                    ]
                )
                + "|"
            )
            table += row_str + "\n"

        table += separator
        return table


# Export all core tools
__all__ = [
    "WebSearchTool",
    "CalculatorTool",
    "FileReaderTool",
    "DateTimeTool",
    "TextAnalyzerTool",
    "JSONProcessorTool",
    "CodeFormatterTool",
    "DataProcessorTool",
]
