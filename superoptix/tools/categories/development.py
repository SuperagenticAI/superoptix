"""
SuperOptiX Development Tools
============================

Tools for software development, DevOps, and programming tasks.
"""

import json
import re


class GitTool:
    """Git repository analysis tool."""

    def analyze_commit_message(self, message: str) -> str:
        """Analyze commit message for best practices."""
        try:
            # Check commit message format
            lines = message.strip().split("\n")
            first_line = lines[0] if lines else ""

            issues = []
            recommendations = []

            # Check length
            if len(first_line) > 50:
                issues.append("First line is too long (>50 characters)")
                recommendations.append("Keep first line under 50 characters")

            # Check format
            if not first_line[0].isupper():
                issues.append("First line should start with capital letter")
                recommendations.append("Start with capital letter")

            if first_line.endswith("."):
                issues.append("First line should not end with period")
                recommendations.append("Remove period from first line")

            # Check for conventional commits
            conventional_types = [
                "feat",
                "fix",
                "docs",
                "style",
                "refactor",
                "test",
                "chore",
            ]
            has_conventional = any(
                first_line.lower().startswith(f"{t}:") for t in conventional_types
            )

            if not has_conventional:
                recommendations.append(
                    "Consider using conventional commit format (feat:, fix:, etc.)"
                )

            report = f"""📝 Commit Message Analysis:
{"=" * 50}
Message: "{first_line}"

Issues Found: {len(issues)}
{chr(10).join(f"- {issue}" for issue in issues)}

Recommendations: {len(recommendations)}
{chr(10).join(f"- {rec}" for rec in recommendations)}

Score: {max(0, 100 - len(issues) * 20)}/100
"""
            return report

        except Exception as e:
            return f"❌ Git analysis error: {str(e)}"


class APITesterTool:
    """API testing and validation tool."""

    def validate_api_response(
        self, response_data: str, expected_status: int = 200
    ) -> str:
        """Validate API response format and structure."""
        try:
            # Try to parse as JSON
            try:
                data = json.loads(response_data)
                is_json = True
            except json.JSONDecodeError:
                data = response_data
                is_json = False

            report = f"""🔍 API Response Analysis:
{"=" * 50}
Content Type: {"JSON" if is_json else "Text/Other"}
Data Size: {len(response_data)} characters

"""

            if is_json:
                # Analyze JSON structure
                if isinstance(data, dict):
                    report += f"Structure: Object with {len(data)} keys\n"
                    report += f"Keys: {list(data.keys())}\n"
                elif isinstance(data, list):
                    report += f"Structure: Array with {len(data)} items\n"
                    if data:
                        report += f"First item type: {type(data[0]).__name__}\n"
                else:
                    report += f"Structure: {type(data).__name__}\n"

                # Check for common API patterns
                if isinstance(data, dict):
                    if "error" in data:
                        report += "⚠️  Error field detected\n"
                    if "data" in data:
                        report += "✅ Data field present\n"
                    if "status" in data:
                        report += f"✅ Status field: {data['status']}\n"

                report += "✅ Valid JSON format\n"
            else:
                report += "📄 Non-JSON response\n"

            return report

        except Exception as e:
            return f"❌ API validation error: {str(e)}"


class DatabaseQueryTool:
    """Database query analysis and validation tool."""

    def validate_sql_query(self, query: str) -> str:
        """Validate SQL query for basic syntax and security issues."""
        try:
            query = query.strip()
            query_upper = query.upper()

            # Basic syntax validation
            issues = []
            warnings = []
            suggestions = []

            # Check for SQL injection patterns
            dangerous_patterns = [
                r"';.*--",
                r"UNION.*SELECT",
                r"DROP\s+TABLE",
                r"DELETE\s+FROM.*WHERE\s+1\s*=\s*1",
                r"UPDATE.*SET.*WHERE\s+1\s*=\s*1",
            ]

            for pattern in dangerous_patterns:
                if re.search(pattern, query_upper):
                    issues.append(
                        f"Potential SQL injection pattern detected: {pattern}"
                    )

            # Check for basic syntax
            if not query.endswith(";"):
                suggestions.append("Consider ending query with semicolon")

            # Check for SELECT without WHERE
            if query_upper.startswith("SELECT") and "WHERE" not in query_upper:
                warnings.append(
                    "SELECT without WHERE clause - may return large result set"
                )

            # Check for proper formatting
            if query.count("(") != query.count(")"):
                issues.append("Unmatched parentheses")

            # Query analysis
            query_type = "UNKNOWN"
            if query_upper.startswith("SELECT"):
                query_type = "SELECT"
            elif query_upper.startswith("INSERT"):
                query_type = "INSERT"
            elif query_upper.startswith("UPDATE"):
                query_type = "UPDATE"
            elif query_upper.startswith("DELETE"):
                query_type = "DELETE"
            elif query_upper.startswith("CREATE"):
                query_type = "CREATE"

            report = f"""🗄️ SQL Query Analysis:
{"=" * 50}
Query Type: {query_type}
Length: {len(query)} characters

Security Issues: {len(issues)}
{chr(10).join(f"❌ {issue}" for issue in issues)}

Warnings: {len(warnings)}
{chr(10).join(f"⚠️  {warning}" for warning in warnings)}

Suggestions: {len(suggestions)}
{chr(10).join(f"💡 {suggestion}" for suggestion in suggestions)}

Security Score: {max(0, 100 - len(issues) * 30 - len(warnings) * 10)}/100
"""
            return report

        except Exception as e:
            return f"❌ SQL validation error: {str(e)}"


class VersionCheckerTool:
    """Version checking and management tool."""

    def compare_versions(self, version1: str, version2: str) -> str:
        """Compare two semantic versions."""
        try:

            def parse_version(version):
                # Extract version numbers
                version_clean = re.sub(r"[^0-9.]", "", version)
                parts = version_clean.split(".")
                return [int(part) for part in parts if part.isdigit()]

            v1_parts = parse_version(version1)
            v2_parts = parse_version(version2)

            # Pad shorter version with zeros
            max_len = max(len(v1_parts), len(v2_parts))
            v1_parts.extend([0] * (max_len - len(v1_parts)))
            v2_parts.extend([0] * (max_len - len(v2_parts)))

            # Compare versions
            if v1_parts > v2_parts:
                comparison = f"{version1} > {version2}"
                result = "NEWER"
            elif v1_parts < v2_parts:
                comparison = f"{version1} < {version2}"
                result = "OLDER"
            else:
                comparison = f"{version1} = {version2}"
                result = "EQUAL"

            return f"""📊 Version Comparison:
{"=" * 50}
Version 1: {version1} → {v1_parts}
Version 2: {version2} → {v2_parts}

Comparison: {comparison}
Result: {result}

{result == "NEWER" and "✅ Version 1 is newer" or result == "OLDER" and "⚠️  Version 1 is older" or "✅ Versions are equal"}
"""

        except Exception as e:
            return f"❌ Version comparison error: {str(e)}"


class DependencyAnalyzerTool:
    """Dependency analysis tool."""

    def analyze_dependencies(self, package_json: str) -> str:
        """Analyze package dependencies for security and updates."""
        try:
            data = json.loads(package_json)
            dependencies = data.get("dependencies", {})
            dev_dependencies = data.get("devDependencies", {})

            all_deps = {**dependencies, **dev_dependencies}

            # Analysis
            total_deps = len(all_deps)
            prod_deps = len(dependencies)
            dev_deps = len(dev_dependencies)

            # Check for outdated version patterns
            outdated_patterns = []
            for name, version in all_deps.items():
                if version.startswith("^") or version.startswith("~"):
                    continue  # These are flexible versions
                if version.startswith("0."):
                    outdated_patterns.append(f"{name}@{version} (pre-1.0)")

            report = f"""📦 Dependency Analysis:
{"=" * 50}
Total Dependencies: {total_deps}
Production: {prod_deps}
Development: {dev_deps}

Potential Issues:
{chr(10).join(f"⚠️  {pattern}" for pattern in outdated_patterns)}

Top Dependencies:
{chr(10).join(f"- {name}: {version}" for name, version in list(all_deps.items())[:10])}

Recommendations:
- Review dependencies regularly
- Use npm audit for security issues
- Consider dependency size impact
"""
            return report

        except Exception as e:
            return f"❌ Dependency analysis error: {str(e)}"


class CodeReviewerTool:
    """Code review and quality analysis tool."""

    def review_code(self, code: str, language: str = "python") -> str:
        """Perform basic code review analysis."""
        try:
            lines = code.split("\n")
            issues = []
            suggestions = []

            # General code quality checks
            if language.lower() == "python":
                for i, line in enumerate(lines, 1):
                    stripped = line.strip()
                    if not stripped:
                        continue

                    # Line length
                    if len(line) > 100:
                        issues.append(f"Line {i}: Too long ({len(line)} chars)")

                    # TODO/FIXME comments
                    if "TODO" in line or "FIXME" in line:
                        suggestions.append(f"Line {i}: TODO/FIXME comment found")

                    # Print statements (should use logging)
                    if stripped.startswith("print("):
                        suggestions.append(f"Line {i}: Use logging instead of print")

                    # Magic numbers
                    if re.search(r"\b\d{2,}\b", stripped) and not stripped.startswith(
                        "#"
                    ):
                        suggestions.append(
                            f"Line {i}: Consider using constants for magic numbers"
                        )

            # Calculate metrics
            total_lines = len(lines)
            non_empty_lines = len([line for line in lines if line.strip()])
            comment_lines = len(
                [line for line in lines if line.strip().startswith("#")]
            )

            comment_ratio = comment_lines / max(non_empty_lines, 1) * 100

            report = f"""🔍 Code Review Report:
{"=" * 50}
Language: {language.upper()}
Total Lines: {total_lines}
Non-empty Lines: {non_empty_lines}
Comment Lines: {comment_lines}
Comment Ratio: {comment_ratio:.1f}%

Issues Found: {len(issues)}
{chr(10).join(f"❌ {issue}" for issue in issues)}

Suggestions: {len(suggestions)}
{chr(10).join(f"💡 {suggestion}" for suggestion in suggestions)}

Quality Score: {max(0, 100 - len(issues) * 10 - len(suggestions) * 5)}/100
"""
            return report

        except Exception as e:
            return f"❌ Code review error: {str(e)}"


class TestCoverageTool:
    """Test coverage analysis tool."""

    def analyze_coverage(self, coverage_data: str) -> str:
        """Analyze test coverage report."""
        try:
            lines = coverage_data.strip().split("\n")
            coverage_info = {}

            # Parse coverage data (assuming simple format)
            for line in lines:
                if "%" in line and "covered" in line:
                    # Extract coverage percentage
                    match = re.search(r"(\d+)%", line)
                    if match:
                        percentage = int(match.group(1))
                        file_match = re.search(r"(\S+\.py)", line)
                        if file_match:
                            coverage_info[file_match.group(1)] = percentage

            if not coverage_info:
                # Try to extract overall coverage
                overall_match = re.search(r"(\d+)%", coverage_data)
                if overall_match:
                    overall_coverage = int(overall_match.group(1))
                else:
                    return "❌ Could not parse coverage data"
            else:
                overall_coverage = sum(coverage_info.values()) / len(coverage_info)

            # Analyze coverage
            status = (
                "❌ Poor"
                if overall_coverage < 60
                else "⚠️  Fair"
                if overall_coverage < 80
                else "✅ Good"
            )

            report = f"""📊 Test Coverage Analysis:
{"=" * 50}
Overall Coverage: {overall_coverage:.1f}% {status}

Coverage Breakdown:
{chr(10).join(f"- {file}: {percent}%" for file, percent in coverage_info.items())}

Recommendations:
- Target: 80% or higher coverage
- Focus on critical business logic
- Test edge cases and error handling
- Consider integration tests
"""
            return report

        except Exception as e:
            return f"❌ Coverage analysis error: {str(e)}"


class DockerHelperTool:
    """Docker container management helper."""

    def validate_dockerfile(self, dockerfile_content: str) -> str:
        """Validate Dockerfile for best practices."""
        try:
            lines = dockerfile_content.strip().split("\n")
            issues = []
            suggestions = []

            has_from = False
            layers = 0

            for i, line in enumerate(lines, 1):
                stripped = line.strip()
                if not stripped or stripped.startswith("#"):
                    continue

                upper_line = stripped.upper()

                # Check for FROM instruction
                if upper_line.startswith("FROM"):
                    has_from = True
                    if ":latest" in stripped:
                        suggestions.append(f"Line {i}: Avoid using ':latest' tag")

                # Count layers
                if any(upper_line.startswith(cmd) for cmd in ["RUN", "COPY", "ADD"]):
                    layers += 1

                # Check for root user
                if upper_line.startswith("USER ROOT"):
                    issues.append(f"Line {i}: Avoid running as root user")

                # Check for COPY vs ADD
                if upper_line.startswith("ADD") and "http" not in stripped:
                    suggestions.append(
                        f"Line {i}: Use COPY instead of ADD for local files"
                    )

                # Check for package manager cache
                if (
                    "apt-get install" in stripped
                    and "rm -rf /var/lib/apt/lists/*" not in stripped
                ):
                    suggestions.append(f"Line {i}: Clean package manager cache")

            # Overall checks
            if not has_from:
                issues.append("Missing FROM instruction")

            if layers > 10:
                suggestions.append("Consider reducing layers to optimize image size")

            report = f"""🐳 Dockerfile Analysis:
{"=" * 50}
Total Instructions: {len([l for l in lines if l.strip() and not l.strip().startswith("#")])}
Layers: {layers}

Issues: {len(issues)}
{chr(10).join(f"❌ {issue}" for issue in issues)}

Suggestions: {len(suggestions)}
{chr(10).join(f"💡 {suggestion}" for suggestion in suggestions)}

Score: {max(0, 100 - len(issues) * 20 - len(suggestions) * 5)}/100
"""
            return report

        except Exception as e:
            return f"❌ Dockerfile validation error: {str(e)}"


# Export all development tools
__all__ = [
    "GitTool",
    "APITesterTool",
    "DatabaseQueryTool",
    "VersionCheckerTool",
    "DependencyAnalyzerTool",
    "CodeReviewerTool",
    "TestCoverageTool",
    "DockerHelperTool",
]
