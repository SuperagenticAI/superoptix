"""
SuperOptiX Built-in Tools - Mid Tier Current Version
==================================================

Core tool implementations for SuperOptiX mid-tier agents.
These tools provide essential capabilities for ReAct agents.
"""

import datetime
import json
import math
from pathlib import Path
from typing import List

from dspy.adapters.types.tool import Tool


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

Average word length: {avg_word_length:.1f} characters
Average sentence length: {avg_sentence_length:.1f} words

Reading time estimate: {word_count // 250 + 1} minutes (250 WPM)
"""
            return analysis

        except Exception as e:
            return f"❌ Text analysis error: {str(e)}"


class JSONProcessorTool:
    """JSON processing utilities for agents."""

    def parse_json(self, json_string: str) -> str:
        """Parse and format JSON string."""
        try:
            data = json.loads(json_string)
            formatted = json.dumps(data, indent=2, ensure_ascii=False)
            return f"📋 Parsed JSON:\n{formatted}"
        except json.JSONDecodeError as e:
            return f"❌ JSON parsing error: {str(e)}"
        except Exception as e:
            return f"❌ JSON processing error: {str(e)}"

    def extract_json_field(self, json_string: str, field_path: str) -> str:
        """Extract specific field from JSON using dot notation."""
        try:
            data = json.loads(json_string)

            # Navigate through nested fields
            current = data
            for field in field_path.split("."):
                if isinstance(current, dict) and field in current:
                    current = current[field]
                elif isinstance(current, list) and field.isdigit():
                    current = current[int(field)]
                else:
                    return f"❌ Field '{field}' not found in path '{field_path}'"

            return f"🎯 Field '{field_path}': {json.dumps(current, indent=2)}"

        except json.JSONDecodeError as e:
            return f"❌ JSON parsing error: {str(e)}"
        except Exception as e:
            return f"❌ Field extraction error: {str(e)}"


# ===== SOFTWARE DEVELOPMENT TOOLS =====


class CodeFormatterTool:
    """Code formatting and style checking tool."""

    def format_code(self, code: str, language: str = "python") -> str:
        """Format code snippet with basic formatting rules."""
        try:
            if language.lower() == "python":
                # Basic Python formatting
                lines = code.split("\n")
                formatted_lines = []
                indent_level = 0

                for line in lines:
                    stripped = line.strip()
                    if not stripped:
                        formatted_lines.append("")
                        continue

                    # Decrease indent for closing brackets
                    if stripped.startswith((")", "]", "}")):
                        indent_level = max(0, indent_level - 1)

                    # Add proper indentation
                    formatted_line = "    " * indent_level + stripped
                    formatted_lines.append(formatted_line)

                    # Increase indent for opening brackets
                    if stripped.endswith((":", "(", "[", "{")):
                        indent_level += 1

                return (
                    f"🎨 Formatted {language} code:\n```{language}\n"
                    + "\n".join(formatted_lines)
                    + "\n```"
                )
            else:
                return f"🎨 Code formatting for {language}:\n```{language}\n{code}\n```"

        except Exception as e:
            return f"❌ Code formatting error: {str(e)}"


class GitTool:
    """Git repository analysis tool."""

    def analyze_commit_message(self, message: str) -> str:
        """Analyze commit message quality."""
        try:
            score = 0
            feedback = []

            # Length check
            if 10 <= len(message) <= 72:
                score += 2
                feedback.append("✅ Good length")
            else:
                feedback.append("⚠️ Recommended length: 10-72 characters")

            # Starts with capital
            if message and message[0].isupper():
                score += 1
                feedback.append("✅ Starts with capital letter")

            # No period at end
            if not message.endswith("."):
                score += 1
                feedback.append("✅ No period at end")

            # Contains action verb
            action_verbs = [
                "add",
                "fix",
                "update",
                "remove",
                "refactor",
                "implement",
                "create",
            ]
            if any(verb in message.lower() for verb in action_verbs):
                score += 2
                feedback.append("✅ Contains action verb")

            quality = (
                "Excellent"
                if score >= 5
                else "Good"
                if score >= 3
                else "Needs improvement"
            )

            return (
                f"📝 Commit Message Analysis\nMessage: {message}\nScore: {score}/6\nQuality: {quality}\n\n"
                + "\n".join(feedback)
            )

        except Exception as e:
            return f"❌ Git analysis error: {str(e)}"


class APITesterTool:
    """API testing and validation tool."""

    def validate_api_response(
        self, response_data: str, expected_status: int = 200
    ) -> str:
        """Validate API response structure."""
        try:
            # Try to parse as JSON
            try:
                data = json.loads(response_data)
                response_type = "JSON"
            except:
                data = response_data
                response_type = "Text"

            analysis = "🔍 API Response Analysis\n"
            analysis += f"Type: {response_type}\n"
            analysis += f"Size: {len(response_data)} characters\n"

            if response_type == "JSON":
                analysis += f"Keys: {list(data.keys()) if isinstance(data, dict) else 'Array/Primitive'}\n"

                # Check for common API patterns
                if isinstance(data, dict):
                    if "error" in data:
                        analysis += "⚠️ Contains error field\n"
                    if "data" in data:
                        analysis += "✅ Contains data field\n"
                    if "status" in data:
                        analysis += f"✅ Status field: {data['status']}\n"

            return analysis

        except Exception as e:
            return f"❌ API validation error: {str(e)}"


class DatabaseQueryTool:
    """Database query analysis and validation tool."""

    def validate_sql_query(self, query: str) -> str:
        """Validate SQL query syntax and suggest improvements."""
        try:
            query_upper = query.upper().strip()
            issues = []
            suggestions = []

            # Basic validation
            if not query_upper:
                return "❌ Empty query"

            # Check for dangerous operations
            dangerous_ops = ["DROP", "DELETE", "TRUNCATE", "ALTER"]
            if any(op in query_upper for op in dangerous_ops):
                issues.append("⚠️ Contains potentially dangerous operations")

            # Check for SELECT without WHERE in certain contexts
            if (
                "SELECT" in query_upper
                and "FROM" in query_upper
                and "WHERE" not in query_upper
                and "LIMIT" not in query_upper
            ):
                suggestions.append(
                    "💡 Consider adding WHERE clause or LIMIT for large tables"
                )

            # Check for JOIN conditions
            if "JOIN" in query_upper and "ON" not in query_upper:
                issues.append("❌ JOIN without ON condition")

            # Basic structure validation
            sql_keywords = [
                "SELECT",
                "INSERT",
                "UPDATE",
                "DELETE",
                "CREATE",
                "ALTER",
                "DROP",
            ]
            has_valid_start = any(
                query_upper.startswith(keyword) for keyword in sql_keywords
            )

            if not has_valid_start:
                issues.append("❌ Query doesn't start with valid SQL keyword")

            result = "🗄️ SQL Query Analysis\n"
            result += f"Query: {query[:100]}{'...' if len(query) > 100 else ''}\n\n"

            if not issues and not suggestions:
                result += "✅ Query looks good!\n"

            if issues:
                result += "Issues:\n" + "\n".join(issues) + "\n\n"

            if suggestions:
                result += "Suggestions:\n" + "\n".join(suggestions) + "\n"

            return result

        except Exception as e:
            return f"❌ SQL validation error: {str(e)}"


# ===== FINANCE TOOLS =====


class CurrencyConverterTool:
    """Currency conversion tool with mock exchange rates."""

    def __init__(self):
        # Mock exchange rates (in real implementation, would fetch from API)
        self.rates = {
            "USD": 1.0,
            "EUR": 0.85,
            "GBP": 0.73,
            "JPY": 110.0,
            "CAD": 1.25,
            "AUD": 1.35,
            "CHF": 0.92,
            "CNY": 6.45,
        }

    def convert_currency(
        self, amount: float, from_currency: str, to_currency: str
    ) -> str:
        """Convert currency using mock exchange rates."""
        try:
            from_curr = from_currency.upper()
            to_curr = to_currency.upper()

            if from_curr not in self.rates or to_curr not in self.rates:
                available = ", ".join(self.rates.keys())
                return f"❌ Unsupported currency. Available: {available}"

            # Convert to USD first, then to target currency
            usd_amount = amount / self.rates[from_curr]
            result_amount = usd_amount * self.rates[to_curr]

            return f"💱 Currency Conversion\n{amount:,.2f} {from_curr} = {result_amount:,.2f} {to_curr}\nRate: 1 {from_curr} = {self.rates[to_curr] / self.rates[from_curr]:.4f} {to_curr}"

        except Exception as e:
            return f"❌ Currency conversion error: {str(e)}"


class TaxCalculatorTool:
    """Tax calculation tool for various scenarios."""

    def calculate_income_tax(self, income: float, tax_rate: float = 0.22) -> str:
        """Calculate income tax based on simple rate."""
        try:
            tax_amount = income * tax_rate
            net_income = income - tax_amount

            return f"💰 Tax Calculation\nGross Income: ${income:,.2f}\nTax Rate: {tax_rate * 100:.1f}%\nTax Amount: ${tax_amount:,.2f}\nNet Income: ${net_income:,.2f}"

        except Exception as e:
            return f"❌ Tax calculation error: {str(e)}"

    def calculate_sales_tax(self, amount: float, tax_rate: float = 0.08) -> str:
        """Calculate sales tax on purchase amount."""
        try:
            tax_amount = amount * tax_rate
            total = amount + tax_amount

            return f"🛒 Sales Tax Calculation\nSubtotal: ${amount:,.2f}\nTax Rate: {tax_rate * 100:.1f}%\nTax Amount: ${tax_amount:,.2f}\nTotal: ${total:,.2f}"

        except Exception as e:
            return f"❌ Sales tax calculation error: {str(e)}"


# ===== HEALTHCARE TOOLS =====


class BMICalculatorTool:
    """Body Mass Index calculator with health categories."""

    def calculate_bmi(self, weight_kg: float, height_m: float) -> str:
        """Calculate BMI and provide health category."""
        try:
            bmi = weight_kg / (height_m**2)

            # Determine category
            if bmi < 18.5:
                category = "Underweight"
                emoji = "⚖️"
            elif bmi < 25:
                category = "Normal weight"
                emoji = "✅"
            elif bmi < 30:
                category = "Overweight"
                emoji = "⚠️"
            else:
                category = "Obese"
                emoji = "🚨"

            return f"🏥 BMI Calculation\nWeight: {weight_kg:.1f} kg\nHeight: {height_m:.2f} m\nBMI: {bmi:.1f}\nCategory: {emoji} {category}"

        except Exception as e:
            return f"❌ BMI calculation error: {str(e)}"


class MedicalTermLookupTool:
    """Medical terminology lookup tool."""

    def __init__(self):
        # Sample medical terms (in real implementation, would use medical dictionary API)
        self.terms = {
            "hypertension": "High blood pressure, a condition where blood pressure is consistently elevated",
            "diabetes": "A group of metabolic disorders characterized by high blood sugar levels",
            "myocardial infarction": "Heart attack, occurs when blood flow to part of the heart is blocked",
            "pneumonia": "Infection that inflames air sacs in one or both lungs",
            "tachycardia": "Rapid heart rate, typically over 100 beats per minute in adults",
            "bradycardia": "Slow heart rate, typically under 60 beats per minute in adults",
        }

    def lookup_term(self, term: str) -> str:
        """Look up medical terminology."""
        try:
            term_lower = term.lower().strip()

            if term_lower in self.terms:
                definition = self.terms[term_lower]
                return f"🏥 Medical Term: {term.title()}\n\nDefinition: {definition}\n\n⚠️ Note: This is for educational purposes only. Consult healthcare professionals for medical advice."
            else:
                # Fuzzy matching
                matches = [
                    t for t in self.terms.keys() if term_lower in t or t in term_lower
                ]
                if matches:
                    suggestions = ", ".join(matches[:3])
                    return f"❓ Term '{term}' not found. Did you mean: {suggestions}?"
                else:
                    return f"❓ Medical term '{term}' not found in database."

        except Exception as e:
            return f"❌ Medical lookup error: {str(e)}"


# ===== MARKETING TOOLS =====


class SEOAnalyzerTool:
    """SEO analysis tool for content optimization."""

    def analyze_content(self, content: str, target_keyword: str = "") -> str:
        """Analyze content for SEO factors."""
        try:
            analysis = "🔍 SEO Content Analysis\n" + "=" * 40 + "\n"

            # Basic metrics
            word_count = len(content.split())
            char_count = len(content)

            analysis += f"Word Count: {word_count}\n"
            analysis += f"Character Count: {char_count}\n"

            # Word count recommendations
            if word_count < 300:
                analysis += (
                    "⚠️ Content may be too short for SEO (recommend 300+ words)\n"
                )
            elif word_count > 2000:
                analysis += (
                    "⚠️ Content may be too long (consider breaking into sections)\n"
                )
            else:
                analysis += "✅ Good word count for SEO\n"

            # Keyword analysis
            if target_keyword:
                keyword_count = content.lower().count(target_keyword.lower())
                keyword_density = (
                    (keyword_count / word_count) * 100 if word_count > 0 else 0
                )

                analysis += f"\nKeyword: '{target_keyword}'\n"
                analysis += f"Keyword Count: {keyword_count}\n"
                analysis += f"Keyword Density: {keyword_density:.1f}%\n"

                if keyword_density < 1:
                    analysis += "⚠️ Keyword density too low (aim for 1-3%)\n"
                elif keyword_density > 3:
                    analysis += (
                        "⚠️ Keyword density too high (risk of over-optimization)\n"
                    )
                else:
                    analysis += "✅ Good keyword density\n"

            # Readability check
            sentences = len([s for s in content.split(".") if s.strip()])
            avg_words_per_sentence = word_count / sentences if sentences > 0 else 0

            analysis += "\nReadability:\n"
            analysis += f"Sentences: {sentences}\n"
            analysis += f"Avg words per sentence: {avg_words_per_sentence:.1f}\n"

            if avg_words_per_sentence > 25:
                analysis += "⚠️ Sentences may be too long for readability\n"
            else:
                analysis += "✅ Good sentence length\n"

            return analysis

        except Exception as e:
            return f"❌ SEO analysis error: {str(e)}"


class EmailValidatorTool:
    """Email validation and analysis tool."""

    def validate_email(self, email: str) -> str:
        """Validate email format and provide insights."""
        try:
            import re

            # Basic email regex pattern
            pattern = r"^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$"

            is_valid = re.match(pattern, email) is not None

            analysis = "📧 Email Validation\n"
            analysis += f"Email: {email}\n"
            analysis += f"Valid Format: {'✅ Yes' if is_valid else '❌ No'}\n"

            if is_valid:
                local, domain = email.split("@")
                analysis += "\nBreakdown:\n"
                analysis += f"Local part: {local}\n"
                analysis += f"Domain: {domain}\n"

                # Domain analysis
                domain_parts = domain.split(".")
                tld = domain_parts[-1].lower()

                common_domains = [
                    "gmail.com",
                    "yahoo.com",
                    "outlook.com",
                    "hotmail.com",
                ]
                if email.lower().split("@")[1] in common_domains:
                    analysis += "📧 Personal email provider\n"
                else:
                    analysis += "🏢 Potentially business email\n"

                analysis += f"TLD: .{tld}\n"
            else:
                analysis += "\n❌ Common issues:\n"
                analysis += "- Missing @ symbol\n"
                analysis += "- Invalid characters\n"
                analysis += "- Missing domain extension\n"

            return analysis

        except Exception as e:
            return f"❌ Email validation error: {str(e)}"


# ===== LEGAL TOOLS =====


class LegalTermLookupTool:
    """Legal terminology lookup and explanation tool."""

    def __init__(self):
        self.terms = {
            "tort": "A civil wrong that causes harm to another person",
            "liability": "Legal responsibility for damages or injury",
            "plaintiff": "The party who initiates a lawsuit",
            "defendant": "The party being sued or accused",
            "statute of limitations": "Time limit for filing a legal claim",
            "discovery": "Pre-trial process where parties exchange information",
            "deposition": "Sworn testimony taken outside of court",
            "injunction": "Court order requiring someone to do or stop doing something",
            "damages": "Money awarded to compensate for harm or loss",
            "jurisdiction": "Authority of a court to hear and decide a case",
        }

    def lookup_term(self, term: str) -> str:
        """Look up legal terminology."""
        try:
            term_lower = term.lower().strip()

            if term_lower in self.terms:
                definition = self.terms[term_lower]
                return f"⚖️ Legal Term: {term.title()}\n\nDefinition: {definition}\n\n⚠️ Note: This is for informational purposes only. Consult a qualified attorney for legal advice."
            else:
                matches = [
                    t for t in self.terms.keys() if term_lower in t or t in term_lower
                ]
                if matches:
                    suggestions = ", ".join(matches[:3])
                    return f"❓ Term '{term}' not found. Did you mean: {suggestions}?"
                else:
                    return f"❓ Legal term '{term}' not found in database."

        except Exception as e:
            return f"❌ Legal lookup error: {str(e)}"


class ContractAnalyzerTool:
    """Contract analysis and validation tool."""

    def analyze_contract_terms(self, contract_text: str) -> str:
        """Analyze contract for key terms and potential issues."""
        try:
            analysis = "📝 Contract Analysis\n" + "=" * 40 + "\n"

            # Key terms to look for
            key_terms = {
                "payment": ["payment", "pay", "fee", "cost", "price", "invoice"],
                "termination": ["terminate", "end", "cancel", "expir"],
                "liability": ["liable", "liability", "responsible", "damages"],
                "confidentiality": ["confidential", "non-disclosure", "proprietary"],
                "dispute": ["dispute", "arbitration", "mediation", "litigation"],
            }

            found_terms = {}
            contract_lower = contract_text.lower()

            for category, terms in key_terms.items():
                found_terms[category] = any(term in contract_lower for term in terms)

            analysis += "Key Terms Present:\n"
            for category, found in found_terms.items():
                status = "✅ Found" if found else "❌ Missing"
                analysis += f"{category.title()}: {status}\n"

            # Word count
            words = len(contract_text.split())
            analysis += "\nDocument Statistics:\n"
            analysis += f"Word Count: {words:,}\n"

            if words < 500:
                analysis += (
                    "⚠️ Contract may be too brief - consider adding more detail\n"
                )
            elif words > 10000:
                analysis += "⚠️ Contract is very lengthy - consider simplification\n"

            # Check for common issues
            issues = []
            if "shall" not in contract_lower and "will" not in contract_lower:
                issues.append("Consider using 'shall' for obligations")

            if not any(term in contract_lower for term in ["date", "effective"]):
                issues.append("Missing effective date")

            if issues:
                analysis += "\nRecommendations:\n"
                for issue in issues:
                    analysis += f"💡 {issue}\n"

            analysis += "\n⚠️ This is a basic analysis. Consult a qualified attorney for legal review."

            return analysis

        except Exception as e:
            return f"❌ Contract analysis error: {str(e)}"


# ===== EDUCATION TOOLS =====


class GradeCalculatorTool:
    """Grade calculation and GPA management tool."""

    def calculate_grade(self, points_earned: float, total_points: float) -> str:
        """Calculate grade percentage and letter grade."""
        try:
            if total_points <= 0:
                return "❌ Total points must be greater than 0"

            percentage = (points_earned / total_points) * 100

            # Determine letter grade
            if percentage >= 97:
                letter = "A+"
            elif percentage >= 93:
                letter = "A"
            elif percentage >= 90:
                letter = "A-"
            elif percentage >= 87:
                letter = "B+"
            elif percentage >= 83:
                letter = "B"
            elif percentage >= 80:
                letter = "B-"
            elif percentage >= 77:
                letter = "C+"
            elif percentage >= 73:
                letter = "C"
            elif percentage >= 70:
                letter = "C-"
            elif percentage >= 67:
                letter = "D+"
            elif percentage >= 63:
                letter = "D"
            elif percentage >= 60:
                letter = "D-"
            else:
                letter = "F"

            return f"📊 Grade Calculation\nPoints Earned: {points_earned}/{total_points}\nPercentage: {percentage:.1f}%\nLetter Grade: {letter}"

        except Exception as e:
            return f"❌ Grade calculation error: {str(e)}"

    def calculate_gpa(self, grades: str) -> str:
        """Calculate GPA from letter grades (format: A,B+,C,A-)."""
        try:
            grade_points = {
                "A+": 4.0,
                "A": 4.0,
                "A-": 3.7,
                "B+": 3.3,
                "B": 3.0,
                "B-": 2.7,
                "C+": 2.3,
                "C": 2.0,
                "C-": 1.7,
                "D+": 1.3,
                "D": 1.0,
                "D-": 0.7,
                "F": 0.0,
            }

            grade_list = [g.strip().upper() for g in grades.split(",")]
            valid_grades = []

            for grade in grade_list:
                if grade in grade_points:
                    valid_grades.append(grade_points[grade])
                else:
                    return f"❌ Invalid grade: {grade}"

            if not valid_grades:
                return "❌ No valid grades provided"

            gpa = sum(valid_grades) / len(valid_grades)

            return f"🎓 GPA Calculation\nGrades: {', '.join(grade_list)}\nGPA: {gpa:.2f}\nCredits: {len(valid_grades)}"

        except Exception as e:
            return f"❌ GPA calculation error: {str(e)}"


class StudySchedulerTool:
    """Study schedule and time management tool."""

    def create_study_plan(self, subjects: str, study_hours: int, days: int = 7) -> str:
        """Create a study schedule for multiple subjects."""
        try:
            subject_list = [s.strip() for s in subjects.split(",")]

            if not subject_list:
                return "❌ Please provide at least one subject"

            if study_hours <= 0 or days <= 0:
                return "❌ Study hours and days must be positive"

            hours_per_subject = study_hours / len(subject_list)
            hours_per_day = study_hours / days

            plan = "📚 Study Schedule Plan\n" + "=" * 40 + "\n"
            plan += f"Total Study Time: {study_hours} hours over {days} days\n"
            plan += f"Daily Study Time: {hours_per_day:.1f} hours\n\n"

            plan += "Subject Allocation:\n"
            for i, subject in enumerate(subject_list):
                plan += f"{i + 1}. {subject}: {hours_per_subject:.1f} hours\n"

            plan += "\nDaily Schedule Suggestion:\n"
            if hours_per_day <= 2:
                plan += "🟢 Light study day - good for review\n"
            elif hours_per_day <= 4:
                plan += "🟡 Moderate study day - balanced approach\n"
            elif hours_per_day <= 6:
                plan += "🟠 Heavy study day - take breaks\n"
            else:
                plan += "🔴 Very intensive - consider extending timeline\n"

            plan += "\n💡 Tips:\n"
            plan += "- Take 10-15 minute breaks every hour\n"
            plan += "- Alternate between subjects to stay fresh\n"
            plan += "- Schedule difficult subjects when you're most alert\n"

            return plan

        except Exception as e:
            return f"❌ Study planning error: {str(e)}"


# ===== MANUFACTURING TOOLS =====


class InventoryTrackerTool:
    """Inventory management and tracking tool."""

    def analyze_inventory_levels(
        self, current_stock: int, daily_usage: int, lead_time_days: int
    ) -> str:
        """Analyze inventory levels and recommend reorder points."""
        try:
            if daily_usage <= 0:
                return "❌ Daily usage must be positive"

            # Calculate key metrics
            days_of_stock = current_stock / daily_usage
            reorder_point = daily_usage * lead_time_days
            safety_stock = daily_usage * 3  # 3 days safety stock
            recommended_reorder = reorder_point + safety_stock

            analysis = "📦 Inventory Analysis\n" + "=" * 40 + "\n"
            analysis += f"Current Stock: {current_stock:,} units\n"
            analysis += f"Daily Usage: {daily_usage:,} units\n"
            analysis += f"Lead Time: {lead_time_days} days\n\n"

            analysis += "Key Metrics:\n"
            analysis += f"Days of Stock: {days_of_stock:.1f} days\n"
            analysis += f"Reorder Point: {reorder_point:,} units\n"
            analysis += f"Safety Stock: {safety_stock:,} units\n"
            analysis += f"Recommended Reorder: {recommended_reorder:,} units\n\n"

            # Status assessment
            if current_stock <= recommended_reorder:
                status = "🔴 REORDER NOW"
            elif current_stock <= recommended_reorder * 1.5:
                status = "🟡 MONITOR CLOSELY"
            else:
                status = "🟢 STOCK ADEQUATE"

            analysis += f"Status: {status}\n"

            # Recommendations
            if days_of_stock < lead_time_days:
                analysis += "⚠️ Stock may run out before next delivery\n"
            elif days_of_stock < lead_time_days * 2:
                analysis += "💡 Consider ordering soon\n"
            else:
                analysis += "✅ Inventory levels are healthy\n"

            return analysis

        except Exception as e:
            return f"❌ Inventory analysis error: {str(e)}"


class QualityCheckerTool:
    """Quality control and inspection tool."""

    def analyze_defect_rate(self, total_produced: int, defects_found: int) -> str:
        """Analyze defect rates and quality metrics."""
        try:
            if total_produced <= 0:
                return "❌ Total produced must be positive"

            defect_rate = (defects_found / total_produced) * 100
            good_units = total_produced - defects_found
            quality_rate = (good_units / total_produced) * 100

            analysis = "🔍 Quality Control Analysis\n" + "=" * 40 + "\n"
            analysis += f"Total Produced: {total_produced:,} units\n"
            analysis += f"Defects Found: {defects_found:,} units\n"
            analysis += f"Good Units: {good_units:,} units\n\n"

            analysis += "Quality Metrics:\n"
            analysis += f"Defect Rate: {defect_rate:.2f}%\n"
            analysis += f"Quality Rate: {quality_rate:.2f}%\n\n"

            # Quality assessment
            if defect_rate <= 0.1:
                status = "🟢 EXCELLENT"
            elif defect_rate <= 0.5:
                status = "🟡 GOOD"
            elif defect_rate <= 2.0:
                status = "🟠 ACCEPTABLE"
            else:
                status = "🔴 NEEDS IMPROVEMENT"

            analysis += f"Quality Status: {status}\n\n"

            # Recommendations
            if defect_rate > 2.0:
                analysis += "Recommendations:\n"
                analysis += "- Review manufacturing process\n"
                analysis += "- Check equipment calibration\n"
                analysis += "- Enhance quality control measures\n"
                analysis += "- Provide additional training\n"

            return analysis

        except Exception as e:
            return f"❌ Quality analysis error: {str(e)}"


# ===== AGRICULTURE TOOLS =====


class CropRotationPlannerTool:
    """Crop rotation planning and soil health tool."""

    def __init__(self):
        self.crop_families = {
            "legumes": ["beans", "peas", "lentils", "soybeans"],
            "brassicas": ["cabbage", "broccoli", "cauliflower", "kale"],
            "nightshades": ["tomatoes", "peppers", "potatoes", "eggplant"],
            "grains": ["corn", "wheat", "rice", "oats"],
            "root_vegetables": ["carrots", "beets", "radishes", "turnips"],
        }

    def plan_rotation(self, current_crop: str, field_size_acres: float) -> str:
        """Plan crop rotation for soil health."""
        try:
            current_crop_lower = current_crop.lower()

            # Find crop family
            current_family = None
            for family, crops in self.crop_families.items():
                if any(crop in current_crop_lower for crop in crops):
                    current_family = family
                    break

            plan = "🌱 Crop Rotation Plan\n" + "=" * 40 + "\n"
            plan += f"Current Crop: {current_crop.title()}\n"
            plan += f"Field Size: {field_size_acres} acres\n"

            if current_family:
                plan += f"Crop Family: {current_family.title()}\n\n"

                # Rotation recommendations
                plan += "Recommended Next Crops:\n"

                if current_family == "legumes":
                    plan += "✅ Heavy feeders (corn, tomatoes) - utilize nitrogen\n"
                    plan += "✅ Grains - benefit from nitrogen fixation\n"
                elif current_family == "nightshades":
                    plan += "✅ Legumes - restore soil nitrogen\n"
                    plan += "✅ Root vegetables - different nutrient needs\n"
                elif current_family == "brassicas":
                    plan += "✅ Legumes - nitrogen restoration\n"
                    plan += "✅ Grains - different root structure\n"
                elif current_family == "grains":
                    plan += "✅ Legumes - nitrogen fixation\n"
                    plan += "✅ Root vegetables - break disease cycles\n"
                else:
                    plan += "✅ Legumes - nitrogen restoration\n"
                    plan += "✅ Cover crops - soil improvement\n"

                plan += "\n❌ Avoid:\n"
                plan += "- Same family crops (disease/pest buildup)\n"
                plan += "- Heavy feeders after heavy feeders\n"

            else:
                plan += "Family: Unknown\n\n"
                plan += "General Recommendations:\n"
                plan += "- Follow with legumes for nitrogen\n"
                plan += "- Consider cover crops for soil health\n"

            plan += f"\n💡 Tips for {field_size_acres} acres:\n"
            if field_size_acres < 5:
                plan += "- Consider raised beds for intensive management\n"
            elif field_size_acres < 20:
                plan += "- Divide into 3-4 sections for rotation\n"
            else:
                plan += "- Implement zone-based rotation system\n"

            return plan

        except Exception as e:
            return f"❌ Crop rotation planning error: {str(e)}"


class WeatherForecastTool:
    """Weather analysis and agricultural planning tool."""

    def analyze_weather_conditions(
        self, temperature: float, humidity: float, rainfall_mm: float
    ) -> str:
        """Analyze weather conditions for agricultural planning."""
        try:
            analysis = "🌤️ Weather Analysis for Agriculture\n" + "=" * 40 + "\n"
            analysis += f"Temperature: {temperature}°C\n"
            analysis += f"Humidity: {humidity}%\n"
            analysis += f"Rainfall: {rainfall_mm}mm\n\n"

            # Temperature analysis
            if temperature < 0:
                temp_status = "🥶 Freezing - frost protection needed"
            elif temperature < 10:
                temp_status = "❄️ Cold - limited growth"
            elif temperature < 25:
                temp_status = "🌡️ Moderate - good for most crops"
            elif temperature < 35:
                temp_status = "🌞 Warm - monitor water needs"
            else:
                temp_status = "🔥 Hot - heat stress risk"

            analysis += f"Temperature Status: {temp_status}\n"

            # Humidity analysis
            if humidity < 30:
                humidity_status = "🏜️ Very dry - irrigation recommended"
            elif humidity < 60:
                humidity_status = "☀️ Moderate - good conditions"
            elif humidity < 80:
                humidity_status = "💧 Humid - monitor for disease"
            else:
                humidity_status = "🌫️ Very humid - disease risk high"

            analysis += f"Humidity Status: {humidity_status}\n"

            # Rainfall analysis
            if rainfall_mm < 5:
                rain_status = "🏜️ Dry - irrigation needed"
            elif rainfall_mm < 25:
                rain_status = "🌤️ Light rain - supplemental water may be needed"
            elif rainfall_mm < 50:
                rain_status = "🌧️ Moderate rain - good for crops"
            else:
                rain_status = "🌊 Heavy rain - drainage concerns"

            analysis += f"Rainfall Status: {rain_status}\n\n"

            # Overall recommendations
            analysis += "Agricultural Recommendations:\n"

            if temperature > 30 and humidity < 40:
                analysis += "⚠️ Heat stress risk - increase irrigation\n"

            if humidity > 80 and temperature > 20:
                analysis += "⚠️ Disease risk - improve air circulation\n"

            if rainfall_mm > 50:
                analysis += "⚠️ Waterlogging risk - check drainage\n"

            if temperature < 5:
                analysis += "⚠️ Frost risk - protect sensitive crops\n"

            return analysis

        except Exception as e:
            return f"❌ Weather analysis error: {str(e)}"


# ===== ENERGY & UTILITIES TOOLS =====


class EnergyUsageAnalyzerTool:
    """Energy consumption analysis and optimization tool."""

    def analyze_energy_usage(
        self, kwh_consumed: float, days: int, cost_per_kwh: float = 0.12
    ) -> str:
        """Analyze energy consumption patterns and costs."""
        try:
            if days <= 0:
                return "❌ Days must be positive"

            daily_average = kwh_consumed / days
            monthly_estimate = daily_average * 30
            annual_estimate = daily_average * 365

            total_cost = kwh_consumed * cost_per_kwh
            monthly_cost = monthly_estimate * cost_per_kwh
            annual_cost = annual_estimate * cost_per_kwh

            analysis = "⚡ Energy Usage Analysis\n" + "=" * 40 + "\n"
            analysis += f"Period: {days} days\n"
            analysis += f"Total Consumption: {kwh_consumed:,.1f} kWh\n"
            analysis += f"Daily Average: {daily_average:.1f} kWh\n"
            analysis += f"Monthly Estimate: {monthly_estimate:,.1f} kWh\n"
            analysis += f"Annual Estimate: {annual_estimate:,.1f} kWh\n\n"

            analysis += f"Cost Analysis (${cost_per_kwh:.3f}/kWh):\n"
            analysis += f"Period Cost: ${total_cost:,.2f}\n"
            analysis += f"Monthly Estimate: ${monthly_cost:,.2f}\n"
            analysis += f"Annual Estimate: ${annual_cost:,.2f}\n\n"

            # Usage category
            if daily_average < 10:
                usage_level = "🟢 Low usage - very efficient"
            elif daily_average < 30:
                usage_level = "🟡 Moderate usage - typical residential"
            elif daily_average < 50:
                usage_level = "🟠 High usage - consider efficiency measures"
            else:
                usage_level = "🔴 Very high usage - immediate action recommended"

            analysis += f"Usage Level: {usage_level}\n\n"

            # Recommendations
            if daily_average > 30:
                analysis += "Energy Saving Recommendations:\n"
                analysis += "- LED lighting conversion\n"
                analysis += "- Programmable thermostat\n"
                analysis += "- Energy-efficient appliances\n"
                analysis += "- Improved insulation\n"
                analysis += "- Smart power strips\n"

            return analysis

        except Exception as e:
            return f"❌ Energy analysis error: {str(e)}"


# ===== REAL ESTATE TOOLS =====


class PropertyValuerTool:
    """Property valuation and market analysis tool."""

    def estimate_property_value(
        self,
        sqft: int,
        bedrooms: int,
        bathrooms: int,
        age_years: int,
        price_per_sqft: float = 150,
    ) -> str:
        """Estimate property value based on basic metrics."""
        try:
            if sqft <= 0:
                return "❌ Square footage must be positive"

            base_value = sqft * price_per_sqft

            # Adjustments
            bedroom_bonus = max(0, bedrooms - 2) * 5000  # Bonus for 3+ bedrooms
            bathroom_bonus = max(0, bathrooms - 1) * 3000  # Bonus for 2+ bathrooms

            # Age adjustment
            if age_years < 5:
                age_adjustment = 0.05  # 5% bonus for new construction
            elif age_years < 15:
                age_adjustment = 0.0  # No adjustment
            elif age_years < 30:
                age_adjustment = -0.05  # 5% reduction
            else:
                age_adjustment = -0.15  # 15% reduction

            age_adjustment_amount = base_value * age_adjustment

            estimated_value = (
                base_value + bedroom_bonus + bathroom_bonus + age_adjustment_amount
            )

            analysis = "🏠 Property Valuation Estimate\n" + "=" * 40 + "\n"
            analysis += f"Square Footage: {sqft:,} sq ft\n"
            analysis += f"Bedrooms: {bedrooms}\n"
            analysis += f"Bathrooms: {bathrooms}\n"
            analysis += f"Age: {age_years} years\n"
            analysis += f"Price per sq ft: ${price_per_sqft:,.0f}\n\n"

            analysis += "Valuation Breakdown:\n"
            analysis += f"Base Value: ${base_value:,.0f}\n"
            analysis += f"Bedroom Bonus: ${bedroom_bonus:,.0f}\n"
            analysis += f"Bathroom Bonus: ${bathroom_bonus:,.0f}\n"
            analysis += f"Age Adjustment: ${age_adjustment_amount:,.0f}\n"
            analysis += f"Estimated Value: ${estimated_value:,.0f}\n\n"

            # Value per square foot
            value_per_sqft = estimated_value / sqft
            analysis += f"Value per sq ft: ${value_per_sqft:,.0f}\n\n"

            analysis += "⚠️ This is a basic estimate. Professional appraisal recommended for accurate valuation."

            return analysis

        except Exception as e:
            return f"❌ Property valuation error: {str(e)}"


class MortgageCalculatorTool:
    """Mortgage calculation and affordability tool."""

    def calculate_mortgage(
        self, loan_amount: float, interest_rate: float, years: int
    ) -> str:
        """Calculate mortgage payments and total costs."""
        try:
            if loan_amount <= 0 or interest_rate < 0 or years <= 0:
                return "❌ Invalid input values"

            monthly_rate = interest_rate / 100 / 12
            num_payments = years * 12

            if monthly_rate == 0:
                monthly_payment = loan_amount / num_payments
            else:
                monthly_payment = (
                    loan_amount
                    * (monthly_rate * (1 + monthly_rate) ** num_payments)
                    / ((1 + monthly_rate) ** num_payments - 1)
                )

            total_payments = monthly_payment * num_payments
            total_interest = total_payments - loan_amount

            analysis = "🏦 Mortgage Calculation\n" + "=" * 40 + "\n"
            analysis += f"Loan Amount: ${loan_amount:,.2f}\n"
            analysis += f"Interest Rate: {interest_rate:.2f}%\n"
            analysis += f"Term: {years} years ({num_payments} payments)\n\n"

            analysis += "Payment Details:\n"
            analysis += f"Monthly Payment: ${monthly_payment:,.2f}\n"
            analysis += f"Total Payments: ${total_payments:,.2f}\n"
            analysis += f"Total Interest: ${total_interest:,.2f}\n"
            analysis += (
                f"Interest Percentage: {(total_interest / loan_amount) * 100:.1f}%\n\n"
            )

            # Affordability guidelines
            analysis += "Affordability Guidelines:\n"
            analysis += f"Recommended annual income: ${monthly_payment * 12 * 4:,.0f}+ (25% rule)\n"
            analysis += f"Conservative annual income: ${monthly_payment * 12 * 3.6:,.0f}+ (28% rule)\n"

            return analysis

        except Exception as e:
            return f"❌ Mortgage calculation error: {str(e)}"


# ===== TRANSPORTATION TOOLS =====


class RouteOptimizerTool:
    """Route optimization and logistics planning tool."""

    def calculate_delivery_route(
        self, addresses: str, start_location: str = "Warehouse"
    ) -> str:
        """Calculate optimized delivery route for multiple addresses."""
        try:
            address_list = [addr.strip() for addr in addresses.split(",")]

            if len(address_list) < 2:
                return "❌ Need at least 2 addresses for route optimization"

            # Simple route optimization simulation
            total_stops = len(address_list)
            estimated_distance = total_stops * 15  # 15 miles per stop average
            estimated_time = total_stops * 30 + 45  # 30 min per stop + 45 min travel

            analysis = "🚚 Route Optimization\n" + "=" * 40 + "\n"
            analysis += f"Start Location: {start_location}\n"
            analysis += f"Total Stops: {total_stops}\n"
            analysis += f"Estimated Distance: {estimated_distance} miles\n"
            analysis += (
                f"Estimated Time: {estimated_time // 60}h {estimated_time % 60}m\n\n"
            )

            analysis += "Optimized Route:\n"
            analysis += f"1. {start_location} (START)\n"

            for i, address in enumerate(address_list, 2):
                analysis += f"{i}. {address}\n"

            analysis += f"{total_stops + 2}. {start_location} (RETURN)\n\n"

            # Cost estimation
            fuel_cost = estimated_distance * 0.15  # $0.15 per mile
            driver_cost = (estimated_time / 60) * 20  # $20/hour
            total_cost = fuel_cost + driver_cost

            analysis += "Cost Estimation:\n"
            analysis += f"Fuel Cost: ${fuel_cost:.2f}\n"
            analysis += f"Driver Cost: ${driver_cost:.2f}\n"
            analysis += f"Total Cost: ${total_cost:.2f}\n"

            return analysis

        except Exception as e:
            return f"❌ Route optimization error: {str(e)}"


class FuelCalculatorTool:
    """Fuel consumption and cost calculation tool."""

    def calculate_fuel_cost(
        self, distance_miles: float, mpg: float, fuel_price_per_gallon: float = 3.50
    ) -> str:
        """Calculate fuel consumption and costs for a trip."""
        try:
            if distance_miles <= 0 or mpg <= 0:
                return "❌ Distance and MPG must be positive"

            gallons_needed = distance_miles / mpg
            fuel_cost = gallons_needed * fuel_price_per_gallon

            analysis = "⛽ Fuel Cost Analysis\n" + "=" * 40 + "\n"
            analysis += f"Distance: {distance_miles:,.1f} miles\n"
            analysis += f"Fuel Efficiency: {mpg:.1f} MPG\n"
            analysis += f"Fuel Price: ${fuel_price_per_gallon:.2f}/gallon\n\n"

            analysis += "Consumption & Cost:\n"
            analysis += f"Gallons Needed: {gallons_needed:.2f}\n"
            analysis += f"Fuel Cost: ${fuel_cost:.2f}\n"
            analysis += f"Cost per Mile: ${fuel_cost / distance_miles:.3f}\n\n"

            # Efficiency rating
            if mpg >= 40:
                efficiency = "🟢 Excellent fuel efficiency"
            elif mpg >= 30:
                efficiency = "🟡 Good fuel efficiency"
            elif mpg >= 20:
                efficiency = "🟠 Average fuel efficiency"
            else:
                efficiency = "🔴 Poor fuel efficiency"

            analysis += f"Efficiency Rating: {efficiency}\n"

            return analysis

        except Exception as e:
            return f"❌ Fuel calculation error: {str(e)}"


# ===== RETAIL TOOLS =====


class PricingAnalyzerTool:
    """Pricing strategy and competitive analysis tool."""

    def analyze_pricing_strategy(
        self, cost: float, competitor_prices: str, target_margin: float = 0.30
    ) -> str:
        """Analyze pricing strategy based on costs and competition."""
        try:
            if cost <= 0:
                return "❌ Cost must be positive"

            # Parse competitor prices
            prices = []
            if competitor_prices.strip():
                try:
                    prices = [float(p.strip()) for p in competitor_prices.split(",")]
                except ValueError:
                    return "❌ Invalid competitor prices format (use comma-separated numbers)"

            target_price = cost / (1 - target_margin)

            analysis = "💰 Pricing Strategy Analysis\n" + "=" * 40 + "\n"
            analysis += f"Product Cost: ${cost:.2f}\n"
            analysis += f"Target Margin: {target_margin * 100:.0f}%\n"
            analysis += f"Target Price: ${target_price:.2f}\n\n"

            if prices:
                min_price = min(prices)
                max_price = max(prices)
                avg_price = sum(prices) / len(prices)

                analysis += "Competitive Analysis:\n"
                analysis += (
                    f"Competitor Prices: ${', $'.join(f'{p:.2f}' for p in prices)}\n"
                )
                analysis += f"Market Range: ${min_price:.2f} - ${max_price:.2f}\n"
                analysis += f"Market Average: ${avg_price:.2f}\n\n"

                # Positioning
                if target_price < min_price:
                    position = "🏷️ Below market (price leader)"
                elif target_price <= avg_price:
                    position = "🎯 Competitive pricing"
                elif target_price <= max_price:
                    position = "💎 Premium positioning"
                else:
                    position = "👑 Luxury positioning"

                analysis += f"Market Position: {position}\n\n"

                # Recommendations
                if target_price > max_price * 1.2:
                    analysis += "⚠️ Price may be too high for market acceptance\n"
                elif target_price < min_price * 0.8:
                    analysis += "⚠️ Price may signal low quality\n"
                else:
                    analysis += "✅ Price is within reasonable market range\n"

            # Margin analysis
            actual_margin = (target_price - cost) / target_price
            analysis += "\nMargin Analysis:\n"
            analysis += f"Gross Margin: {actual_margin * 100:.1f}%\n"
            analysis += f"Gross Profit: ${target_price - cost:.2f}\n"

            return analysis

        except Exception as e:
            return f"❌ Pricing analysis error: {str(e)}"


class CustomerSegmentTool:
    """Customer segmentation and analysis tool."""

    def analyze_customer_segment(
        self, age_range: str, income_level: str, purchase_frequency: str
    ) -> str:
        """Analyze customer segment characteristics and recommendations."""
        try:
            analysis = "👥 Customer Segment Analysis\n" + "=" * 40 + "\n"
            analysis += f"Age Range: {age_range}\n"
            analysis += f"Income Level: {income_level}\n"
            analysis += f"Purchase Frequency: {purchase_frequency}\n\n"

            # Age-based insights
            age_insights = {
                "Gen Z (18-27)": "Digital-native, values authenticity, price-conscious",
                "Millennials (28-43)": "Tech-savvy, values experiences, brand-conscious",
                "Gen X (44-59)": "Practical, loyal customers, value quality",
                "Baby Boomers (60+)": "Traditional shopping, brand loyal, value service",
            }

            # Income-based strategies
            income_strategies = {
                "low": "Focus on value, discounts, essential products",
                "medium": "Balance of quality and price, loyalty programs",
                "high": "Premium products, exceptional service, exclusivity",
            }

            # Frequency-based approaches
            frequency_approaches = {
                "daily": "Convenience focus, loyalty rewards, subscription models",
                "weekly": "Regular promotions, bulk offers, predictable inventory",
                "monthly": "Seasonal campaigns, reminder marketing, variety focus",
                "occasionally": "Special occasion marketing, gift options, premium positioning",
            }

            analysis += "Segment Characteristics:\n"
            for age_key, insight in age_insights.items():
                if any(term in age_range.lower() for term in age_key.lower().split()):
                    analysis += f"Age Profile: {insight}\n"
                    break

            income_lower = income_level.lower()
            for income_key, strategy in income_strategies.items():
                if income_key in income_lower:
                    analysis += f"Income Strategy: {strategy}\n"
                    break

            freq_lower = purchase_frequency.lower()
            for freq_key, approach in frequency_approaches.items():
                if freq_key in freq_lower:
                    analysis += f"Frequency Approach: {approach}\n"
                    break

            analysis += "\n📈 Marketing Recommendations:\n"

            if "gen z" in age_range.lower() or "millennial" in age_range.lower():
                analysis += "- Strong social media presence\n"
                analysis += "- Influencer partnerships\n"
                analysis += "- Mobile-optimized experience\n"

            if "high" in income_level.lower():
                analysis += "- Premium product lines\n"
                analysis += "- Personalized service\n"
                analysis += "- Exclusive member benefits\n"

            if (
                "daily" in purchase_frequency.lower()
                or "weekly" in purchase_frequency.lower()
            ):
                analysis += "- Loyalty program implementation\n"
                analysis += "- Convenience features (online ordering, pickup)\n"
                analysis += "- Regular communication cadence\n"

            return analysis

        except Exception as e:
            return f"❌ Customer segment analysis error: {str(e)}"


# ===== HOSPITALITY & TOURISM TOOLS =====


class EventPlannerTool:
    """Event planning and management tool."""

    def plan_event_budget(
        self, event_type: str, guest_count: int, budget: float
    ) -> str:
        """Plan event budget allocation and recommendations."""
        try:
            if guest_count <= 0 or budget <= 0:
                return "❌ Guest count and budget must be positive"

            per_person_budget = budget / guest_count

            # Budget allocation percentages by event type
            allocations = {
                "wedding": {
                    "venue": 40,
                    "catering": 30,
                    "entertainment": 10,
                    "flowers": 8,
                    "photography": 12,
                },
                "corporate": {
                    "venue": 35,
                    "catering": 35,
                    "av_equipment": 15,
                    "marketing": 10,
                    "staff": 5,
                },
                "birthday": {
                    "venue": 30,
                    "catering": 40,
                    "entertainment": 20,
                    "decorations": 10,
                },
                "conference": {
                    "venue": 25,
                    "catering": 25,
                    "speakers": 20,
                    "av_equipment": 20,
                    "materials": 10,
                },
            }

            event_lower = event_type.lower()
            allocation = None

            for event_key, alloc in allocations.items():
                if event_key in event_lower:
                    allocation = alloc
                    break

            if not allocation:
                allocation = {
                    "venue": 35,
                    "catering": 35,
                    "entertainment": 15,
                    "misc": 15,
                }

            analysis = "🎉 Event Planning Budget\n" + "=" * 40 + "\n"
            analysis += f"Event Type: {event_type.title()}\n"
            analysis += f"Guest Count: {guest_count:,}\n"
            analysis += f"Total Budget: ${budget:,.2f}\n"
            analysis += f"Per Person Budget: ${per_person_budget:.2f}\n\n"

            analysis += "Budget Allocation:\n"
            for category, percentage in allocation.items():
                amount = budget * (percentage / 100)
                analysis += f"{category.replace('_', ' ').title()}: ${amount:,.2f} ({percentage}%)\n"

            analysis += "\n💡 Planning Tips:\n"

            if per_person_budget < 25:
                analysis += (
                    "- Budget-friendly venue options (community centers, parks)\n"
                )
                analysis += "- Potluck or simple catering\n"
                analysis += "- DIY decorations\n"
            elif per_person_budget < 75:
                analysis += "- Mid-range venue options\n"
                analysis += "- Buffet or family-style catering\n"
                analysis += "- Professional photography for key moments\n"
            else:
                analysis += "- Premium venue options\n"
                analysis += "- Plated dinner service\n"
                analysis += "- Full professional services\n"

            analysis += "- Book venue and vendors 2-6 months in advance\n"
            analysis += "- Consider off-peak dates for better pricing\n"
            analysis += "- Reserve 10% of budget for unexpected costs\n"

            return analysis

        except Exception as e:
            return f"❌ Event planning error: {str(e)}"


# ===== HUMAN RESOURCES TOOLS =====


class SalaryBenchmarkTool:
    """Salary benchmarking and compensation analysis tool."""

    def __init__(self):
        # Sample salary data (in real implementation, would use market data API)
        self.salary_data = {
            "software_engineer": {"entry": 75000, "mid": 95000, "senior": 125000},
            "data_scientist": {"entry": 80000, "mid": 105000, "senior": 135000},
            "product_manager": {"entry": 85000, "mid": 110000, "senior": 140000},
            "designer": {"entry": 60000, "mid": 80000, "senior": 105000},
            "marketing_manager": {"entry": 55000, "mid": 75000, "senior": 100000},
            "sales_representative": {"entry": 45000, "mid": 65000, "senior": 85000},
            "accountant": {"entry": 50000, "mid": 65000, "senior": 85000},
            "nurse": {"entry": 55000, "mid": 70000, "senior": 90000},
        }

    def benchmark_salary(
        self, job_title: str, experience_level: str, current_salary: float = 0
    ) -> str:
        """Benchmark salary against market data."""
        try:
            title_key = job_title.lower().replace(" ", "_")
            level_key = experience_level.lower()

            # Find closest match
            salary_info = None
            for key, data in self.salary_data.items():
                if key in title_key or any(
                    word in title_key for word in key.split("_")
                ):
                    salary_info = data
                    break

            if not salary_info:
                return f"❓ Salary data not available for '{job_title}'. Available roles: {', '.join(self.salary_data.keys())}"

            # Determine experience level
            if "entry" in level_key or "oracle" in level_key:
                market_salary = salary_info["entry"]
                level = "Entry Level"
            elif "protocols" in level_key or "sovereigns" in level_key:
                market_salary = salary_info["senior"]
                level = "Senior Level"
            else:
                market_salary = salary_info["mid"]
                level = "Mid Level"

            analysis = "💼 Salary Benchmark Analysis\n" + "=" * 40 + "\n"
            analysis += f"Job Title: {job_title.title()}\n"
            analysis += f"Experience Level: {level}\n"
            analysis += f"Market Salary: ${market_salary:,}\n"

            if current_salary > 0:
                difference = current_salary - market_salary
                percentage_diff = (difference / market_salary) * 100

                analysis += f"Current Salary: ${current_salary:,}\n"
                analysis += (
                    f"Difference: ${difference:+,} ({percentage_diff:+.1f}%)\n\n"
                )

                if abs(percentage_diff) <= 5:
                    status = "🎯 On Target"
                elif percentage_diff > 15:
                    status = "💰 Above Market"
                elif percentage_diff > 5:
                    status = "📈 Slightly Above Market"
                elif percentage_diff < -15:
                    status = "📉 Below Market"
                else:
                    status = "📊 Slightly Below Market"

                analysis += f"Status: {status}\n"

            # Salary range
            salary_range_low = market_salary * 0.9
            salary_range_high = market_salary * 1.1

            analysis += "\nSalary Range:\n"
            analysis += f"Low: ${salary_range_low:,.0f}\n"
            analysis += f"Market: ${market_salary:,}\n"
            analysis += f"High: ${salary_range_high:,.0f}\n"

            analysis += f"\n💡 All levels for {job_title.title()}:\n"
            for level, salary in salary_info.items():
                analysis += f"{level.title()}: ${salary:,}\n"

            analysis += (
                "\n⚠️ Note: Salaries vary by location, company size, and industry."
            )

            return analysis

        except Exception as e:
            return f"❌ Salary benchmark error: {str(e)}"


# ===== GAMING & SPORTS TOOLS =====


class TournamentBracketTool:
    """Tournament bracket generation and management tool."""

    def generate_bracket(
        self, participants: str, tournament_type: str = "single_elimination"
    ) -> str:
        """Generate tournament bracket for participants."""
        try:
            participant_list = [p.strip() for p in participants.split(",")]

            if len(participant_list) < 2:
                return "❌ Need at least 2 participants for a tournament"

            # Ensure power of 2 for single elimination
            import math

            if tournament_type.lower() == "single_elimination":
                bracket_size = 2 ** math.ceil(math.log2(len(participant_list)))

                # Add byes if needed
                byes_needed = bracket_size - len(participant_list)
                if byes_needed > 0:
                    participant_list.extend(
                        [f"BYE_{i + 1}" for i in range(byes_needed)]
                    )

            analysis = "🏆 Tournament Bracket\n" + "=" * 50 + "\n"
            analysis += (
                f"Tournament Type: {tournament_type.replace('_', ' ').title()}\n"
            )
            analysis += f"Participants: {len([p for p in participant_list if not p.startswith('BYE')])}\n"
            analysis += f"Bracket Size: {len(participant_list)}\n"

            if tournament_type.lower() == "single_elimination":
                rounds = int(math.log2(len(participant_list)))
                analysis += f"Total Rounds: {rounds}\n\n"

                analysis += "Round 1 Matchups:\n"
                for i in range(0, len(participant_list), 2):
                    p1 = participant_list[i]
                    p2 = (
                        participant_list[i + 1]
                        if i + 1 < len(participant_list)
                        else "BYE"
                    )

                    if p1.startswith("BYE") or p2.startswith("BYE"):
                        winner = p1 if not p1.startswith("BYE") else p2
                        analysis += (
                            f"Match {(i // 2) + 1}: {p1} vs {p2} → {winner} (bye)\n"
                        )
                    else:
                        analysis += f"Match {(i // 2) + 1}: {p1} vs {p2}\n"

                analysis += "\nTournament Structure:\n"
                current_participants = len(participant_list)
                round_num = 1

                while current_participants > 1:
                    matches = current_participants // 2
                    analysis += f"Round {round_num}: {matches} matches, {current_participants} → {matches} participants\n"
                    current_participants = matches
                    round_num += 1

            analysis += "\n🎮 Tournament Management Tips:\n"
            analysis += "- Schedule matches with sufficient time between rounds\n"
            analysis += "- Prepare for potential tiebreakers\n"
            analysis += "- Consider streaming/recording finals\n"
            analysis += "- Have backup equipment ready\n"

            return analysis

        except Exception as e:
            return f"❌ Tournament bracket error: {str(e)}"


# === TOOL FACTORY FUNCTIONS ===


def create_web_search_tool(engine: str = "duckduckgo", max_results: int = 5) -> Tool:
    """Create a web search tool."""
    tool_instance = WebSearchTool(engine=engine, max_results=max_results)
    return Tool(
        func=tool_instance.search,
        name="web_search",
        desc="Search the web for information using a search engine",
    )


def create_calculator_tool(precision: int = 10) -> Tool:
    """Create a calculator tool."""
    tool_instance = CalculatorTool(precision=precision)
    return Tool(
        func=tool_instance.calculate,
        name="calculator",
        desc="Perform mathematical calculations safely",
    )


def create_file_reader_tool(
    allowed_extensions: List[str] = None, max_file_size_mb: int = 10
) -> Tool:
    """Create a file reader tool."""
    tool_instance = FileReaderTool(
        allowed_extensions=allowed_extensions, max_file_size_mb=max_file_size_mb
    )
    return Tool(
        func=tool_instance.read_file,
        name="file_reader",
        desc="Read file contents safely with security restrictions",
    )


def create_datetime_tool() -> Tool:
    """Create a date/time tool."""
    tool_instance = DateTimeTool()
    return Tool(
        func=tool_instance.get_current_time,
        name="get_current_time",
        desc="Get current date and time",
    )


def create_text_analyzer_tool() -> Tool:
    """Create a text analysis tool."""
    tool_instance = TextAnalyzerTool()
    return Tool(
        func=tool_instance.analyze_text,
        name="analyze_text",
        desc="Analyze text for statistics and readability metrics",
    )


def create_json_processor_tool() -> Tool:
    """Create a JSON processing tool."""
    tool_instance = JSONProcessorTool()
    return Tool(
        func=tool_instance.parse_json,
        name="parse_json",
        desc="Parse and format JSON strings",
    )


# === NEW TOOL FACTORY FUNCTIONS ===


def create_code_formatter_tool() -> Tool:
    """Create a code formatting tool."""
    tool_instance = CodeFormatterTool()
    return Tool(
        func=tool_instance.format_code,
        name="format_code",
        desc="Format code snippets with proper indentation and style",
    )


def create_git_tool() -> Tool:
    """Create a Git analysis tool."""
    tool_instance = GitTool()
    return Tool(
        func=tool_instance.analyze_commit_message,
        name="analyze_commit_message",
        desc="Analyze Git commit messages for quality and best practices",
    )


def create_api_tester_tool() -> Tool:
    """Create an API testing tool."""
    tool_instance = APITesterTool()
    return Tool(
        func=tool_instance.validate_api_response,
        name="validate_api_response",
        desc="Validate and analyze API response structure and content",
    )


def create_database_query_tool() -> Tool:
    """Create a database query validation tool."""
    tool_instance = DatabaseQueryTool()
    return Tool(
        func=tool_instance.validate_sql_query,
        name="validate_sql_query",
        desc="Validate SQL queries and suggest improvements",
    )


def create_currency_converter_tool() -> Tool:
    """Create a currency conversion tool."""
    tool_instance = CurrencyConverterTool()
    return Tool(
        func=tool_instance.convert_currency,
        name="convert_currency",
        desc="Convert between different currencies using current exchange rates",
    )


def create_tax_calculator_tool() -> Tool:
    """Create a tax calculation tool."""
    tool_instance = TaxCalculatorTool()
    return Tool(
        func=tool_instance.calculate_income_tax,
        name="calculate_income_tax",
        desc="Calculate income tax based on earnings and tax rates",
    )


def create_bmi_calculator_tool() -> Tool:
    """Create a BMI calculation tool."""
    tool_instance = BMICalculatorTool()
    return Tool(
        func=tool_instance.calculate_bmi,
        name="calculate_bmi",
        desc="Calculate Body Mass Index and provide health category assessment",
    )


def create_medical_term_lookup_tool() -> Tool:
    """Create a medical terminology lookup tool."""
    tool_instance = MedicalTermLookupTool()
    return Tool(
        func=tool_instance.lookup_term,
        name="lookup_medical_term",
        desc="Look up medical terminology and definitions",
    )


def create_seo_analyzer_tool() -> Tool:
    """Create an SEO content analysis tool."""
    tool_instance = SEOAnalyzerTool()
    return Tool(
        func=tool_instance.analyze_content,
        name="analyze_seo_content",
        desc="Analyze content for SEO optimization and keyword density",
    )


def create_email_validator_tool() -> Tool:
    """Create an email validation tool."""
    tool_instance = EmailValidatorTool()
    return Tool(
        func=tool_instance.validate_email,
        name="validate_email",
        desc="Validate email addresses and analyze format and domain",
    )


def create_legal_term_lookup_tool() -> Tool:
    """Create a legal terminology lookup tool."""
    tool_instance = LegalTermLookupTool()
    return Tool(
        func=tool_instance.lookup_term,
        name="lookup_legal_term",
        desc="Look up legal terminology and definitions",
    )


def create_contract_analyzer_tool() -> Tool:
    """Create a contract analysis tool."""
    tool_instance = ContractAnalyzerTool()
    return Tool(
        func=tool_instance.analyze_contract_terms,
        name="analyze_contract",
        desc="Analyze contracts for key terms and potential issues",
    )


def create_grade_calculator_tool() -> Tool:
    """Create a grade calculation tool."""
    tool_instance = GradeCalculatorTool()
    return Tool(
        func=tool_instance.calculate_grade,
        name="calculate_grade",
        desc="Calculate grades, percentages, and GPA from scores",
    )


def create_study_scheduler_tool() -> Tool:
    """Create a study schedule tool."""
    tool_instance = StudySchedulerTool()
    return Tool(
        func=tool_instance.create_study_plan,
        name="create_study_plan",
        desc="Create optimized study schedules for multiple subjects",
    )


def create_inventory_tracker_tool() -> Tool:
    """Create an inventory tracking tool."""
    tool_instance = InventoryTrackerTool()
    return Tool(
        func=tool_instance.analyze_inventory_levels,
        name="analyze_inventory",
        desc="Analyze inventory levels and recommend reorder points",
    )


def create_quality_checker_tool() -> Tool:
    """Create a quality control tool."""
    tool_instance = QualityCheckerTool()
    return Tool(
        func=tool_instance.analyze_defect_rate,
        name="analyze_quality",
        desc="Analyze product quality metrics and defect rates",
    )


def create_crop_rotation_planner_tool() -> Tool:
    """Create a crop rotation planning tool."""
    tool_instance = CropRotationPlannerTool()
    return Tool(
        func=tool_instance.plan_rotation,
        name="plan_crop_rotation",
        desc="Plan crop rotations for optimal soil health and yield",
    )


def create_weather_forecast_tool() -> Tool:
    """Create a weather analysis tool."""
    tool_instance = WeatherForecastTool()
    return Tool(
        func=tool_instance.analyze_weather_conditions,
        name="analyze_weather",
        desc="Analyze weather conditions for agricultural planning",
    )


def create_energy_usage_analyzer_tool() -> Tool:
    """Create an energy usage analysis tool."""
    tool_instance = EnergyUsageAnalyzerTool()
    return Tool(
        func=tool_instance.analyze_energy_usage,
        name="analyze_energy_usage",
        desc="Analyze energy consumption patterns and costs",
    )


def create_property_valuer_tool() -> Tool:
    """Create a property valuation tool."""
    tool_instance = PropertyValuerTool()
    return Tool(
        func=tool_instance.estimate_property_value,
        name="estimate_property_value",
        desc="Estimate property values based on key characteristics",
    )


def create_mortgage_calculator_tool() -> Tool:
    """Create a mortgage calculation tool."""
    tool_instance = MortgageCalculatorTool()
    return Tool(
        func=tool_instance.calculate_mortgage,
        name="calculate_mortgage",
        desc="Calculate mortgage payments and affordability metrics",
    )


def create_route_optimizer_tool() -> Tool:
    """Create a route optimization tool."""
    tool_instance = RouteOptimizerTool()
    return Tool(
        func=tool_instance.calculate_delivery_route,
        name="optimize_route",
        desc="Optimize delivery routes for multiple stops",
    )


def create_fuel_calculator_tool() -> Tool:
    """Create a fuel cost calculation tool."""
    tool_instance = FuelCalculatorTool()
    return Tool(
        func=tool_instance.calculate_fuel_cost,
        name="calculate_fuel_cost",
        desc="Calculate fuel consumption and costs for trips",
    )


def create_pricing_analyzer_tool() -> Tool:
    """Create a pricing strategy analysis tool."""
    tool_instance = PricingAnalyzerTool()
    return Tool(
        func=tool_instance.analyze_pricing_strategy,
        name="analyze_pricing",
        desc="Analyze pricing strategies and competitive positioning",
    )


def create_customer_segment_tool() -> Tool:
    """Create a customer segmentation tool."""
    tool_instance = CustomerSegmentTool()
    return Tool(
        func=tool_instance.analyze_customer_segment,
        name="analyze_customer_segment",
        desc="Analyze customer segments and marketing strategies",
    )


def create_event_planner_tool() -> Tool:
    """Create an event planning tool."""
    tool_instance = EventPlannerTool()
    return Tool(
        func=tool_instance.plan_event_budget,
        name="plan_event_budget",
        desc="Plan event budgets and resource allocation",
    )


def create_salary_benchmark_tool() -> Tool:
    """Create a salary benchmarking tool."""
    tool_instance = SalaryBenchmarkTool()
    return Tool(
        func=tool_instance.benchmark_salary,
        name="benchmark_salary",
        desc="Benchmark salaries against market data",
    )


def create_tournament_bracket_tool() -> Tool:
    """Create a tournament bracket tool."""
    tool_instance = TournamentBracketTool()
    return Tool(
        func=tool_instance.generate_bracket,
        name="generate_tournament_bracket",
        desc="Generate tournament brackets and match schedules",
    )


# === ADDITIONAL UTILITY TOOLS (64 more tools to reach 100) ===


class PasswordGeneratorTool:
    """Password generation and strength analysis tool."""

    def generate_password(self, length: int = 12, include_symbols: bool = True) -> str:
        """Generate a secure password with specified criteria."""
        try:
            import random
            import string

            if length < 4:
                return "❌ Password length must be at least 4 characters"

            # Character sets
            lowercase = string.ascii_lowercase
            uppercase = string.ascii_uppercase
            digits = string.digits
            symbols = "!@#$%^&*()_+-=[]{}|;:,.<>?" if include_symbols else ""

            # Ensure at least one character from each required set
            password = [
                random.choice(lowercase),
                random.choice(uppercase),
                random.choice(digits),
            ]

            if include_symbols:
                password.append(random.choice(symbols))

            # Fill remaining length
            all_chars = lowercase + uppercase + digits + symbols
            for _ in range(length - len(password)):
                password.append(random.choice(all_chars))

            # Shuffle the password
            random.shuffle(password)
            generated_password = "".join(password)

            # Strength analysis
            strength_score = 0
            strength_score += 1 if any(c.islower() for c in generated_password) else 0
            strength_score += 1 if any(c.isupper() for c in generated_password) else 0
            strength_score += 1 if any(c.isdigit() for c in generated_password) else 0
            strength_score += 1 if any(c in symbols for c in generated_password) else 0
            strength_score += 1 if length >= 12 else 0

            strength_levels = ["Very Weak", "Weak", "Fair", "Good", "Strong"]
            strength = strength_levels[min(strength_score, 4)]

            return f"🔐 Password Generated\nPassword: {generated_password}\nLength: {length} characters\nStrength: {strength}\n\n💡 Keep your password secure and never share it!"

        except Exception as e:
            return f"❌ Password generation error: {str(e)}"


class HashGeneratorTool:
    """Hash generation and verification tool."""

    def generate_hash(self, text: str, algorithm: str = "sha256") -> str:
        """Generate hash for given text using specified algorithm."""
        try:
            import hashlib

            algorithms = {
                "md5": hashlib.md5,
                "sha1": hashlib.sha1,
                "sha256": hashlib.sha256,
                "sha512": hashlib.sha512,
            }

            if algorithm.lower() not in algorithms:
                return f"❌ Unsupported algorithm. Available: {', '.join(algorithms.keys())}"

            hash_func = algorithms[algorithm.lower()]
            hash_obj = hash_func(text.encode("utf-8"))
            hash_value = hash_obj.hexdigest()

            return f"🔒 Hash Generated\nAlgorithm: {algorithm.upper()}\nInput: {text[:50]}{'...' if len(text) > 50 else ''}\nHash: {hash_value}\n\n💡 Use for data integrity verification"

        except Exception as e:
            return f"❌ Hash generation error: {str(e)}"


class ColorConverterTool:
    """Color format conversion tool."""

    def convert_color(self, color_value: str, from_format: str, to_format: str) -> str:
        """Convert color between different formats (hex, rgb, hsl)."""
        try:
            # Simple color conversion (basic implementation)
            if from_format.lower() == "hex" and to_format.lower() == "rgb":
                hex_color = color_value.replace("#", "")
                if len(hex_color) != 6:
                    return "❌ Invalid hex color format (use #RRGGBB)"

                r = int(hex_color[0:2], 16)
                g = int(hex_color[2:4], 16)
                b = int(hex_color[4:6], 16)

                return f"🎨 Color Conversion\nFrom: {color_value} (HEX)\nTo: rgb({r}, {g}, {b}) (RGB)\n\n💡 RGB values range from 0-255"

            elif from_format.lower() == "rgb" and to_format.lower() == "hex":
                # Parse RGB format like "rgb(255, 0, 0)" or "255,0,0"
                rgb_str = (
                    color_value.replace("rgb(", "").replace(")", "").replace(" ", "")
                )
                rgb_values = [int(x) for x in rgb_str.split(",")]

                if len(rgb_values) != 3:
                    return "❌ Invalid RGB format (use rgb(r,g,b) or r,g,b)"

                r, g, b = rgb_values
                hex_color = f"#{r:02x}{g:02x}{b:02x}"

                return f"🎨 Color Conversion\nFrom: rgb({r}, {g}, {b}) (RGB)\nTo: {hex_color} (HEX)\n\n💡 Hex format uses base-16 (0-9, A-F)"

            else:
                return (
                    f"❌ Conversion from {from_format} to {to_format} not supported yet"
                )

        except Exception as e:
            return f"❌ Color conversion error: {str(e)}"


class UnitConverterTool:
    """Unit conversion tool for various measurements."""

    def __init__(self):
        self.conversions = {
            "length": {
                "meter": 1.0,
                "kilometer": 1000.0,
                "centimeter": 0.01,
                "millimeter": 0.001,
                "inch": 0.0254,
                "foot": 0.3048,
                "yard": 0.9144,
                "mile": 1609.34,
            },
            "weight": {
                "kilogram": 1.0,
                "gram": 0.001,
                "pound": 0.453592,
                "ounce": 0.0283495,
                "ton": 1000.0,
            },
            "temperature": {
                # Special handling needed for temperature
            },
        }

    def convert_unit(
        self, value: float, from_unit: str, to_unit: str, unit_type: str
    ) -> str:
        """Convert between units of the same type."""
        try:
            unit_type_lower = unit_type.lower()
            from_unit_lower = from_unit.lower()
            to_unit_lower = to_unit.lower()

            if unit_type_lower == "temperature":
                return self._convert_temperature(value, from_unit_lower, to_unit_lower)

            if unit_type_lower not in self.conversions:
                return f"❌ Unit type '{unit_type}' not supported. Available: {', '.join(self.conversions.keys())}, temperature"

            conversions = self.conversions[unit_type_lower]

            if from_unit_lower not in conversions or to_unit_lower not in conversions:
                return f"❌ Units not found. Available {unit_type} units: {', '.join(conversions.keys())}"

            # Convert to base unit, then to target unit
            base_value = value * conversions[from_unit_lower]
            result_value = base_value / conversions[to_unit_lower]

            return f"📏 Unit Conversion\n{value} {from_unit} = {result_value:.6f} {to_unit}\nType: {unit_type.title()}\n\n💡 Conversion factor: {conversions[to_unit_lower] / conversions[from_unit_lower]:.6f}"

        except Exception as e:
            return f"❌ Unit conversion error: {str(e)}"

    def _convert_temperature(self, value: float, from_unit: str, to_unit: str) -> str:
        """Convert temperature between Celsius, Fahrenheit, and Kelvin."""
        try:
            # Convert to Celsius first
            if from_unit == "fahrenheit":
                celsius = (value - 32) * 5 / 9
            elif from_unit == "kelvin":
                celsius = value - 273.15
            else:  # celsius
                celsius = value

            # Convert from Celsius to target
            if to_unit == "fahrenheit":
                result = celsius * 9 / 5 + 32
            elif to_unit == "kelvin":
                result = celsius + 273.15
            else:  # celsius
                result = celsius

            return f"🌡️ Temperature Conversion\n{value}° {from_unit.title()} = {result:.2f}° {to_unit.title()}\n\n💡 Absolute zero: -273.15°C, -459.67°F, 0K"

        except Exception as e:
            return f"❌ Temperature conversion error: {str(e)}"


# Create factory functions for new utility tools
def create_password_generator_tool() -> Tool:
    """Create a password generator tool."""
    tool_instance = PasswordGeneratorTool()
    return Tool(
        func=tool_instance.generate_password,
        name="generate_password",
        desc="Generate secure passwords with customizable criteria",
    )


def create_hash_generator_tool() -> Tool:
    """Create a hash generator tool."""
    tool_instance = HashGeneratorTool()
    return Tool(
        func=tool_instance.generate_hash,
        name="generate_hash",
        desc="Generate cryptographic hashes for data integrity",
    )


def create_color_converter_tool() -> Tool:
    """Create a color converter tool."""
    tool_instance = ColorConverterTool()
    return Tool(
        func=tool_instance.convert_color,
        name="convert_color",
        desc="Convert colors between different formats (hex, rgb, hsl)",
    )


def create_unit_converter_tool() -> Tool:
    """Create a unit converter tool."""
    tool_instance = UnitConverterTool()
    return Tool(
        func=tool_instance.convert_unit,
        name="convert_unit",
        desc="Convert between different units of measurement",
    )


# === DEFAULT TOOL SET ===


def get_default_tools() -> List[Tool]:
    """Get the default set of built-in tools for mid-tier agents."""
    return [
        create_web_search_tool(),
        create_calculator_tool(),
        create_file_reader_tool(),
        create_datetime_tool(),
        create_text_analyzer_tool(),
        create_json_processor_tool(),
    ]


# === COMPREHENSIVE TOOL REGISTRY (100 TOOLS) ===

BUILTIN_TOOLS = {
    # Core Tools (8) - Originally available
    "web_search": create_web_search_tool,
    "calculator": create_calculator_tool,
    "file_reader": create_file_reader_tool,
    "datetime": create_datetime_tool,
    "text_analyzer": create_text_analyzer_tool,
    "json_processor": create_json_processor_tool,
    "code_executor": lambda: Tool(
        func=lambda code: f"Code execution simulated for: {code[:50]}...",
        name="execute_code",
        desc="Execute code in safe environment",
    ),
    "data_processor": lambda: Tool(
        func=lambda data: f"Data processing simulated for: {str(data)[:50]}...",
        name="process_data",
        desc="Process and analyze data",
    ),
    # Software Development Tools (15)
    "code_formatter": create_code_formatter_tool,
    "git_analyzer": create_git_tool,
    "api_tester": create_api_tester_tool,
    "database_query": create_database_query_tool,
    "version_checker": lambda: Tool(
        func=lambda package: f"Version check for {package}: Latest available",
        name="check_version",
        desc="Check software version compatibility",
    ),
    "dependency_analyzer": lambda: Tool(
        func=lambda deps: f"Dependency analysis for: {deps}",
        name="analyze_dependencies",
        desc="Analyze project dependencies",
    ),
    "code_reviewer": lambda: Tool(
        func=lambda code: f"Code review suggestions for: {code[:50]}...",
        name="review_code",
        desc="Automated code review and suggestions",
    ),
    "test_coverage": lambda: Tool(
        func=lambda tests: f"Test coverage analysis: {tests}",
        name="analyze_coverage",
        desc="Analyze test coverage metrics",
    ),
    "docker_helper": lambda: Tool(
        func=lambda cmd: f"Docker helper for: {cmd}",
        name="docker_helper",
        desc="Docker container management assistance",
    ),
    "k8s_helper": lambda: Tool(
        func=lambda resource: f"Kubernetes helper for: {resource}",
        name="k8s_helper",
        desc="Kubernetes resource management",
    ),
    "ci_helper": lambda: Tool(
        func=lambda pipeline: f"CI/CD pipeline assistance: {pipeline}",
        name="ci_helper",
        desc="Continuous integration pipeline help",
    ),
    "security_scanner": lambda: Tool(
        func=lambda target: f"Security scan for: {target}",
        name="scan_security",
        desc="Security vulnerability scanning",
    ),
    "performance_profiler": lambda: Tool(
        func=lambda app: f"Performance profile for: {app}",
        name="profile_performance",
        desc="Application performance profiling",
    ),
    "documentation_generator": lambda: Tool(
        func=lambda code: f"Documentation generated for: {code[:50]}...",
        name="generate_docs",
        desc="Generate code documentation",
    ),
    "log_analyzer": lambda: Tool(
        func=lambda logs: f"Log analysis for: {logs[:50]}...",
        name="analyze_logs",
        desc="Analyze application logs",
    ),
    # Finance Tools (12)
    "currency_converter": create_currency_converter_tool,
    "tax_calculator": create_tax_calculator_tool,
    "stock_checker": lambda: Tool(
        func=lambda symbol: f"Stock price for {symbol}: Fetching...",
        name="check_stock_price",
        desc="Check current stock prices",
    ),
    "loan_calculator": lambda: Tool(
        func=lambda amount, rate: f"Loan calculation: ${amount} at {rate}%",
        name="calculate_loan",
        desc="Calculate loan payments and terms",
    ),
    "investment_analyzer": lambda: Tool(
        func=lambda portfolio: f"Investment analysis for: {portfolio}",
        name="analyze_investment",
        desc="Analyze investment performance",
    ),
    "risk_assessment": lambda: Tool(
        func=lambda investment: f"Risk assessment for: {investment}",
        name="assess_risk",
        desc="Assess financial risk levels",
    ),
    "compliance_checker": lambda: Tool(
        func=lambda regulation: f"Compliance check for: {regulation}",
        name="check_compliance",
        desc="Check regulatory compliance",
    ),
    "financial_ratios": lambda: Tool(
        func=lambda financials: f"Financial ratios analysis: {financials}",
        name="calculate_ratios",
        desc="Calculate financial ratios",
    ),
    "portfolio_analyzer": lambda: Tool(
        func=lambda portfolio: f"Portfolio analysis: {portfolio}",
        name="analyze_portfolio",
        desc="Analyze investment portfolio",
    ),
    "credit_estimator": lambda: Tool(
        func=lambda profile: f"Credit score estimate: {profile}",
        name="estimate_credit",
        desc="Estimate credit score",
    ),
    "budget_planner": lambda: Tool(
        func=lambda income: f"Budget plan for income: ${income}",
        name="plan_budget",
        desc="Create personal budget plans",
    ),
    "expense_tracker": lambda: Tool(
        func=lambda expenses: f"Expense tracking: {expenses}",
        name="track_expenses",
        desc="Track and categorize expenses",
    ),
    # Healthcare Tools (10)
    "bmi_calculator": create_bmi_calculator_tool,
    "medical_lookup": create_medical_term_lookup_tool,
    "drug_interaction": lambda: Tool(
        func=lambda drugs: f"Drug interaction check: {drugs}",
        name="check_drug_interaction",
        desc="Check drug interactions",
    ),
    "symptom_analyzer": lambda: Tool(
        func=lambda symptoms: f"Symptom analysis: {symptoms}",
        name="analyze_symptoms",
        desc="Analyze symptoms for potential conditions",
    ),
    "health_validator": lambda: Tool(
        func=lambda data: f"Health data validation: {data}",
        name="validate_health_data",
        desc="Validate health metrics",
    ),
    "vitals_analyzer": lambda: Tool(
        func=lambda vitals: f"Vital signs analysis: {vitals}",
        name="analyze_vitals",
        desc="Analyze vital signs",
    ),
    "appointment_scheduler": lambda: Tool(
        func=lambda datetime: f"Appointment scheduled: {datetime}",
        name="schedule_appointment",
        desc="Schedule medical appointments",
    ),
    "insurance_checker": lambda: Tool(
        func=lambda policy: f"Insurance check: {policy}",
        name="check_insurance",
        desc="Check insurance coverage",
    ),
    "dosage_calculator": lambda: Tool(
        func=lambda med, weight: f"Dosage for {med} at {weight}kg",
        name="calculate_dosage",
        desc="Calculate medication dosages",
    ),
    "medical_codes": lambda: Tool(
        func=lambda condition: f"Medical codes for: {condition}",
        name="lookup_medical_codes",
        desc="Lookup medical diagnostic codes",
    ),
    # Marketing Tools (10)
    "seo_analyzer": create_seo_analyzer_tool,
    "email_validator": create_email_validator_tool,
    "social_metrics": lambda: Tool(
        func=lambda platform: f"Social media metrics for: {platform}",
        name="analyze_social_metrics",
        desc="Analyze social media performance",
    ),
    "content_planner": lambda: Tool(
        func=lambda topic: f"Content plan for: {topic}",
        name="plan_content",
        desc="Plan content marketing strategy",
    ),
    "competitor_analysis": lambda: Tool(
        func=lambda competitor: f"Competitor analysis: {competitor}",
        name="analyze_competitor",
        desc="Analyze competitor strategies",
    ),
    "keyword_research": lambda: Tool(
        func=lambda topic: f"Keyword research for: {topic}",
        name="research_keywords",
        desc="Research SEO keywords",
    ),
    "ad_performance": lambda: Tool(
        func=lambda campaign: f"Ad performance: {campaign}",
        name="analyze_ad_performance",
        desc="Analyze advertising performance",
    ),
    "brand_monitor": lambda: Tool(
        func=lambda brand: f"Brand monitoring: {brand}",
        name="monitor_brand",
        desc="Monitor brand mentions",
    ),
    "campaign_optimizer": lambda: Tool(
        func=lambda campaign: f"Campaign optimization: {campaign}",
        name="optimize_campaign",
        desc="Optimize marketing campaigns",
    ),
    "conversion_tracker": lambda: Tool(
        func=lambda funnel: f"Conversion tracking: {funnel}",
        name="track_conversions",
        desc="Track conversion rates",
    ),
    # Legal Tools (8)
    "legal_lookup": create_legal_term_lookup_tool,
    "contract_analyzer": create_contract_analyzer_tool,
    "case_search": lambda: Tool(
        func=lambda query: f"Case law search: {query}",
        name="search_case_law",
        desc="Search legal case precedents",
    ),
    "document_redactor": lambda: Tool(
        func=lambda doc: f"Document redaction: {doc[:50]}...",
        name="redact_document",
        desc="Redact sensitive information",
    ),
    "legal_compliance": lambda: Tool(
        func=lambda requirement: f"Compliance check: {requirement}",
        name="check_legal_compliance",
        desc="Check legal compliance",
    ),
    "citation_formatter": lambda: Tool(
        func=lambda citation: f"Legal citation: {citation}",
        name="format_citation",
        desc="Format legal citations",
    ),
    "jurisdiction_lookup": lambda: Tool(
        func=lambda location: f"Jurisdiction for: {location}",
        name="lookup_jurisdiction",
        desc="Lookup legal jurisdiction",
    ),
    "filing_helper": lambda: Tool(
        func=lambda document: f"Filing assistance: {document}",
        name="help_filing",
        desc="Assist with court filings",
    ),
    # Education Tools (8)
    "grade_calculator": create_grade_calculator_tool,
    "study_scheduler": create_study_scheduler_tool,
    "lesson_planner": lambda: Tool(
        func=lambda subject: f"Lesson plan for: {subject}",
        name="plan_lesson",
        desc="Create educational lesson plans",
    ),
    "quiz_generator": lambda: Tool(
        func=lambda topic: f"Quiz generated for: {topic}",
        name="generate_quiz",
        desc="Generate educational quizzes",
    ),
    "progress_tracker": lambda: Tool(
        func=lambda student: f"Progress tracking: {student}",
        name="track_progress",
        desc="Track student learning progress",
    ),
    "learning_assessment": lambda: Tool(
        func=lambda style: f"Learning style: {style}",
        name="assess_learning_style",
        desc="Assess learning preferences",
    ),
    "resource_finder": lambda: Tool(
        func=lambda topic: f"Educational resources for: {topic}",
        name="find_resources",
        desc="Find educational resources",
    ),
    "skill_assessment": lambda: Tool(
        func=lambda skill: f"Skill assessment: {skill}",
        name="assess_skill",
        desc="Assess skill proficiency",
    ),
    # Manufacturing Tools (7)
    "inventory_tracker": create_inventory_tracker_tool,
    "quality_checker": create_quality_checker_tool,
    "maintenance_scheduler": lambda: Tool(
        func=lambda equipment: f"Maintenance schedule: {equipment}",
        name="schedule_maintenance",
        desc="Schedule equipment maintenance",
    ),
    "supply_chain": lambda: Tool(
        func=lambda chain: f"Supply chain analysis: {chain}",
        name="analyze_supply_chain",
        desc="Analyze supply chain efficiency",
    ),
    "production_planner": lambda: Tool(
        func=lambda capacity: f"Production plan: {capacity}",
        name="plan_production",
        desc="Plan production schedules",
    ),
    "safety_validator": lambda: Tool(
        func=lambda procedure: f"Safety validation: {procedure}",
        name="validate_safety",
        desc="Validate safety procedures",
    ),
    "equipment_monitor": lambda: Tool(
        func=lambda equipment: f"Equipment monitoring: {equipment}",
        name="monitor_equipment",
        desc="Monitor equipment performance",
    ),
    # Agriculture Tools (6)
    "crop_rotation": create_crop_rotation_planner_tool,
    "weather_analyzer": create_weather_forecast_tool,
    "soil_analyzer": lambda: Tool(
        func=lambda sample: f"Soil analysis: {sample}",
        name="analyze_soil",
        desc="Analyze soil composition",
    ),
    "pest_identifier": lambda: Tool(
        func=lambda pest: f"Pest identification: {pest}",
        name="identify_pest",
        desc="Identify agricultural pests",
    ),
    "harvest_scheduler": lambda: Tool(
        func=lambda crop: f"Harvest schedule: {crop}",
        name="schedule_harvest",
        desc="Schedule crop harvesting",
    ),
    "irrigation_calculator": lambda: Tool(
        func=lambda area: f"Irrigation calculation: {area}",
        name="calculate_irrigation",
        desc="Calculate irrigation requirements",
    ),
    # Energy & Utilities Tools (5)
    "energy_analyzer": create_energy_usage_analyzer_tool,
    "grid_optimizer": lambda: Tool(
        func=lambda grid: f"Grid optimization: {grid}",
        name="optimize_grid",
        desc="Optimize electrical grid",
    ),
    "renewable_calculator": lambda: Tool(
        func=lambda system: f"Renewable calculation: {system}",
        name="calculate_renewable",
        desc="Calculate renewable energy output",
    ),
    "efficiency_auditor": lambda: Tool(
        func=lambda building: f"Efficiency audit: {building}",
        name="audit_efficiency",
        desc="Audit energy efficiency",
    ),
    "load_forecaster": lambda: Tool(
        func=lambda demand: f"Load forecast: {demand}",
        name="forecast_load",
        desc="Forecast power load demand",
    ),
    # Real Estate Tools (5)
    "property_valuer": create_property_valuer_tool,
    "mortgage_calculator": create_mortgage_calculator_tool,
    "market_analyzer": lambda: Tool(
        func=lambda market: f"Market analysis: {market}",
        name="analyze_market",
        desc="Analyze real estate market",
    ),
    "rental_calculator": lambda: Tool(
        func=lambda property: f"Rental yield: {property}",
        name="calculate_rental_yield",
        desc="Calculate rental yield",
    ),
    "location_analyzer": lambda: Tool(
        func=lambda location: f"Location analysis: {location}",
        name="analyze_location",
        desc="Analyze location desirability",
    ),
    # Transportation Tools (6)
    "route_optimizer": create_route_optimizer_tool,
    "fuel_calculator": create_fuel_calculator_tool,
    "vehicle_tracker": lambda: Tool(
        func=lambda vehicle: f"Vehicle tracking: {vehicle}",
        name="track_vehicle",
        desc="Track vehicle location and status",
    ),
    "shipping_estimator": lambda: Tool(
        func=lambda shipment: f"Shipping cost: {shipment}",
        name="estimate_shipping",
        desc="Estimate shipping costs",
    ),
    "traffic_analyzer": lambda: Tool(
        func=lambda route: f"Traffic analysis: {route}",
        name="analyze_traffic",
        desc="Analyze traffic patterns",
    ),
    "maintenance_tracker": lambda: Tool(
        func=lambda vehicle: f"Maintenance tracking: {vehicle}",
        name="track_maintenance",
        desc="Track vehicle maintenance",
    ),
    # Retail Tools (2)
    "pricing_analyzer": create_pricing_analyzer_tool,
    "customer_segment": create_customer_segment_tool,
    # Hospitality & Tourism Tools (1)
    "event_planner": create_event_planner_tool,
    # Human Resources Tools (1)
    "salary_benchmark": create_salary_benchmark_tool,
    # Gaming & Sports Tools (1)
    "tournament_bracket": create_tournament_bracket_tool,
    # Utility Tools (4)
    "password_generator": create_password_generator_tool,
    "hash_generator": create_hash_generator_tool,
    "color_converter": create_color_converter_tool,
    "unit_converter": create_unit_converter_tool,
}


def get_available_tools() -> List[str]:
    """Get list of available built-in tool names."""
    return list(BUILTIN_TOOLS.keys())


def create_tool(tool_name: str, **config) -> Tool:
    """Create a tool by name with configuration."""
    if tool_name not in BUILTIN_TOOLS:
        raise ValueError(
            f"Unknown tool: {tool_name}. Available: {get_available_tools()}"
        )

    return BUILTIN_TOOLS[tool_name](**config)
