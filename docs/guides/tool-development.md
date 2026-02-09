# 🛠️ Tool Development Guide

> **Master the art of creating powerful DSPy tools for SuperOptiX agents**

---

## 🎯 What Are SuperOptiX Tools?

SuperOptiX tools are **DSPy tools** that integrate seamlessly with the ReAct (Reasoning + Acting) module in agentic pipelines. Unlike traditional OpenAI function calling, DSPy tools are designed to work within the **ReAct reasoning framework**, enabling agents to:

- **Think step-by-step** about complex problems

- **Choose appropriate tools** based on reasoning

- **Execute tools** with proper parameters

- **Integrate results** back into the reasoning process

### 🔄 ReAct vs Function Calling

| Aspect | DSPy ReAct Tools | OpenAI Function Calling |
|--------|------------------|------------------------|
| **Reasoning** | Built-in step-by-step reasoning | External reasoning required |
| **Tool Selection** | Agent decides when to use tools | Pre-defined function calls |
| **Integration** | Seamless with DSPy pipelines | Requires custom integration |
| **Learning** | Can be optimized with DSPy | Static function definitions |

---

## 🏪 Browse Available Tools

SuperOptiX comes with a rich marketplace of pre-built tools across multiple categories:

```bash
# Browse all available tools
super market browse tools

# Filter by category
super market browse tools --category Core
super market browse tools --category Development
super market browse tools --category Data

# Get detailed information about a specific tool
super market show calculator

# See usage examples
super market examples web_search
```

### 📊 Available Tool Categories

#### 🔧 Core Tools (6 tools)
Essential tools for basic agent functionality:

- **web_search** - Search the web for information

- **calculator** - Perform safe mathematical calculations

- **file_reader** - Read and process text files safely

- **datetime** - Get current time and format dates

- **text_analyzer** - Analyze text for statistics and readability

- **json_processor** - Parse JSON and extract specific fields

#### 💻 Development Tools (9 tools)
Tools for software development and DevOps:

- **code_formatter** - Format code with syntax highlighting

- **git_analyzer** - Analyze Git commit messages

- **api_tester** - Validate and analyze API responses

- **database_query** - Validate SQL queries for security

- **version_checker** - Compare semantic versions

- **dependency_analyzer** - Analyze package dependencies

- **code_reviewer** - Perform automated code review

- **test_coverage** - Analyze test coverage reports

- **docker_helper** - Validate Dockerfiles

#### 📈 Data Tools (1 tool)
Data processing and analysis:

- **data_processor** - Process and analyze CSV data

---

## 🎨 Create Custom DSPy Tools

### Basic Tool Structure

All SuperOptiX tools follow a consistent pattern:

```python
"""
SuperOptiX Custom Tool
=====================

Description of what this tool does.
"""

class MyCustomTool:
    """Brief description of the tool's purpose."""

    def __init__(self, config_param: str = "default"):
        """Initialize tool with configuration."""
        self.config_param = config_param

    def execute_function(self, input_param: str) -> str:
        """Main tool execution method.
        
        Args:
            input_param: Description of the input parameter
            
        Returns:
            Formatted string result with emojis and clear structure
        """
        try:
            # Tool logic here
            result = f"Tool executed successfully: {input_param}"
            
            # Return formatted result
            return f"""🛠️ Custom Tool Result:
{'='*50}
{result}

Configuration: {self.config_param}
"""
        except Exception as e:
            return f"Tool execution error: {str(e)}"
```

### Tool Categories and Organization

In your SuperOptiX project, custom tools are organized in the `tools/` directory. This follows the standard SuperOptiX project structure:

```
your-superoptix-project/
├── agents/           # Agent playbooks and pipelines
├── guardrails/       # Safety and validation rules
├── memory/          # Memory modules for agents
├── protocols/       # Communication protocols
├── teams/           # Multi-agent team configurations
├── evals/           # Evaluation scenarios and test cases
├── knowledge/       # Knowledge bases and data sources
├── optimizers/      # Optimization strategies
├── servers/         # Server and API integration code
├── tools/           # 🔧 Custom tools and utilities for your agents
└── ...
```

#### 📁 Tools Directory Structure

Organize your custom tools by domain or functionality:

```
tools/
├── __init__.py              # Tool registry and imports
├── core/                    # Essential project tools
│   ├── __init__.py
│   ├── data_processor.py
│   ├── api_client.py
│   └── file_handler.py
├── finance/                 # Financial domain tools
│   ├── __init__.py
│   ├── investment_analyzer.py
│   ├── budget_planner.py
│   └── tax_calculator.py
├── healthcare/              # Healthcare domain tools
│   ├── __init__.py
│   ├── patient_analyzer.py
│   ├── medication_checker.py
│   └── health_metrics.py
├── development/             # Software development tools
│   ├── __init__.py
│   ├── code_reviewer.py
│   ├── dependency_checker.py
│   └── deployment_helper.py
└── domain_specific/         # Your specific domain tools
    ├── __init__.py
    ├── industry_analyzer.py
    └── custom_calculator.py
```

### Creating a New Tool Category

To create a new tool category in your SuperOptiX project:

1. **Create the category directory and files**:

```bash
# Create the category directory
mkdir -p tools/finance

# Create the main tool file
touch tools/finance/__init__.py
touch tools/finance/investment_analyzer.py
```

2. **Implement your tools**:

```python
# tools/finance/investment_analyzer.py
"""
Investment Analysis Tools
=========================

Tools for analyzing investment opportunities and financial metrics.
"""

class InvestmentAnalyzer:
    """Analyze investment opportunities and calculate financial metrics."""
    
    def __init__(self):
        """Initialize the investment analyzer."""
        pass
    
    def calculate_roi(self, initial_investment: float, final_value: float, years: int) -> str:
        """Calculate Return on Investment."""
        try:
            roi = ((final_value - initial_investment) / initial_investment) * 100
            annual_roi = roi / years
            
            return f"""📈 ROI Analysis:
{'='*50}
Initial Investment: ${initial_investment:,.2f}
Final Value: ${final_value:,.2f}
Time Period: {years} years

Total ROI: {roi:.2f}%
Annual ROI: {annual_roi:.2f}%
"""
        except Exception as e:
            return f"ROI calculation error: {str(e)}"
```

3. **Register tools in the category's `__init__.py`**:

```python
# tools/finance/__init__.py
"""
Finance Tools Module
===================

Financial analysis and calculation tools for SuperOptiX agents.
"""

from .investment_analyzer import InvestmentAnalyzer

# Export tools for easy importing
__all__ = ['InvestmentAnalyzer']

# Tool registry for this category
FINANCE_TOOLS = {
    "investment_analyzer": {
        "class": InvestmentAnalyzer,
        "description": "Analyze investment opportunities and calculate ROI",
        "tags": ["finance", "investment", "roi", "analysis"]
    }
}
```

4. **Register in the main tools registry**:

```python
# tools/__init__.py
"""
Project Tools Registry
=====================

Central registry for all custom tools in your SuperOptiX project.
"""

from .finance import FINANCE_TOOLS, InvestmentAnalyzer

# Combine all tool registries
PROJECT_TOOLS = {
    **FINANCE_TOOLS,
    # Add other categories here
    # **HEALTHCARE_TOOLS,
    # **DEVELOPMENT_TOOLS,
}

# Export all tools
__all__ = [
    'InvestmentAnalyzer',
    'PROJECT_TOOLS',
]
```

### Tool Integration with DSPy

Tools are integrated into DSPy pipelines through the `ToolsMixin`. In your SuperOptiX project:

```python
# agents/financial_advisor/pipelines/financial_advisor_pipeline.py
from superoptix.core.pipeline_utils import ToolsMixin

class FinancialAdvisorPipeline(ToolsMixin):
    def setup_tools(self, spec_data=None):
        """Setup tools including custom project tools."""
        super().setup_tools(spec_data)
        
        # Import custom tools from your project
        from tools.finance import InvestmentAnalyzer
        
        # Create tool instances
        investment_tool = InvestmentAnalyzer()
        
        # Convert to DSPy Tool and add to pipeline
        from dspy.adapters import Tool
        self.tools.append(Tool(investment_tool.calculate_roi, name="calculate_roi"))
        
        print(f"Added {len(self.tools)} tools to FinancialAdvisorPipeline")
```

#### Alternative: Using Tool Registry

You can also use the project's tool registry for automatic tool discovery:

```python
# agents/financial_advisor/pipelines/financial_advisor_pipeline.py
from superoptix.core.pipeline_utils import ToolsMixin
from tools import PROJECT_TOOLS

class FinancialAdvisorPipeline(ToolsMixin):
    def setup_tools(self, spec_data=None):
        """Setup tools using project registry."""
        super().setup_tools(spec_data)
        
        # Automatically add tools from registry
        for tool_name, tool_config in PROJECT_TOOLS.items():
            tool_class = tool_config['class']
            tool_instance = tool_class()
            
            # Add all methods from the tool class
            for method_name in dir(tool_instance):
                method = getattr(tool_instance, method_name)
                if callable(method) and not method_name.startswith('_'):
                    from dspy.adapters import Tool
                    self.tools.append(Tool(method, name=f"{tool_name}_{method_name}"))
        
        print(f"Added {len(self.tools)} tools from project registry")
```

### Tool Configuration in SuperSpec DSL

Define tools in your agent playbook. You can reference both builtin tools and your custom project tools:

```yaml
# agents/financial_advisor/financial_advisor_playbook.yaml
spec:
  tools:
    enabled: true
    builtin_tools:
      - calculator
      - web_search
      - file_reader
    custom_tools:
      - name: "calculate_roi"
        description: "Calculate Return on Investment for financial analysis"
        function_name: "calculate_roi"
        parameters:
          - name: "initial_investment"
            type: "float"
            required: true
            description: "Initial investment amount"
          - name: "final_value"
            type: "float"
            required: true
            description: "Final investment value"
          - name: "years"
            type: "int"
            required: true
            description: "Investment time period in years"
        implementation: |
          def calculate_roi(initial_investment: float, final_value: float, years: int) -> str:
              try:
                  roi = ((final_value - initial_investment) / initial_investment) * 100
                  annual_roi = roi / years
                  
                  return f"📈 ROI: {roi:.2f}% (Annual: {annual_roi:.2f}%)"
              except Exception as e:
                  return f"ROI calculation error: {str(e)}"
```

#### Project Tool References

You can also reference tools from your project's `tools/` directory:

```yaml
# agents/health_advisor/health_advisor_playbook.yaml
spec:
  tools:
    enabled: true
    builtin_tools:
      - calculator
      - text_analyzer
    project_tools:
      - category: "healthcare"
        tools:
          - "patient_analyzer"
          - "medication_checker"
          - "health_metrics"
    custom_tools:
      - name: "bmi_calculator"
        description: "Calculate Body Mass Index"
        function_name: "calculate_bmi"
        parameters:
          - name: "weight_kg"
            type: "float"
            required: true
            description: "Weight in kilograms"
          - name: "height_m"
            type: "float"
            required: true
            description: "Height in meters"
        implementation: |
          def calculate_bmi(weight_kg: float, height_m: float) -> str:
              try:
                  bmi = weight_kg / (height_m ** 2)
                  category = "Underweight" if bmi < 18.5 else "Normal" if bmi < 25 else "Overweight" if bmi < 30 else "Obese"
                  return f"🏥 BMI: {bmi:.1f} ({category})"
              except Exception as e:
                  return f"BMI calculation error: {str(e)}"
```

---

## 🔧 Tool Development Best Practices

### Error Handling and Safety

```python
def safe_tool_execution(self, input_data: str) -> str:
    """Execute tool with comprehensive error handling."""
    try:
        # Validate input
        if not input_data or not input_data.strip():
            return "Error: Input data is required"
        
        # Perform operation
        result = self._process_data(input_data)
        
        # Validate output
        if not result:
            return "Error: No result generated"
            
        return f"Success: {result}"
        
    except ValueError as e:
        return f"Validation error: {str(e)}"
    except Exception as e:
        return f"Unexpected error: {str(e)}"
```

### Input Validation

```python
def validate_input(self, **kwargs) -> bool:
    """Validate tool input parameters."""
    required_params = ['data', 'format']
    
    for param in required_params:
        if param not in kwargs or kwargs[param] is None:
            raise ValueError(f"Required parameter '{param}' is missing")
    
    # Type validation
    if not isinstance(kwargs['data'], str):
        raise ValueError("Data must be a string")
    
    return True
```

### Output Formatting

```python
def format_output(self, result: str, metadata: dict = None) -> str:
    """Format tool output consistently."""
    output = f"""🛠️ Tool Result:
{'='*50}
{result}
"""
    
    if metadata:
        output += f"\nMetadata:\n"
        for key, value in metadata.items():
            output += f"- {key}: {value}\n"
    
    return output
```

### Performance Considerations

```python
def optimized_tool(self, large_data: str) -> str:
    """Tool with performance optimizations."""
    # Process in chunks for large data
    chunk_size = 1000
    chunks = [large_data[i:i+chunk_size] for i in range(0, len(large_data), chunk_size)]
    
    results = []
    for chunk in chunks:
        result = self._process_chunk(chunk)
        results.append(result)
    
    return "\n".join(results)
```

---

## 🧪 Testing Your Tools

### Unit Testing

```python
# tests/tools/test_finance_tools.py
import pytest
from tools.finance import InvestmentAnalyzer

def test_investment_analyzer():
    tool = InvestmentAnalyzer()
    
    # Test normal operation
    result = tool.calculate_roi(1000, 1500, 2)
    assert "ROI: 50.00%" in result
    assert "Annual: 25.00%" in result
    assert "📈" in result
    
    # Test error handling
    result = tool.calculate_roi(0, 1500, 2)
    assert "" in result
    assert "error" in result.lower()

def test_invalid_inputs():
    tool = InvestmentAnalyzer()
    
    # Test with negative values
    result = tool.calculate_roi(-1000, 1500, 2)
    assert "" in result
    
    # Test with zero years
    result = tool.calculate_roi(1000, 1500, 0)
    assert "" in result
```

### Integration Testing

```python
# tests/integration/test_tool_integration.py
def test_tool_in_pipeline():
    """Test that custom tools integrate properly with DSPy pipelines."""
    from superoptix.core.pipeline_utils import ToolsMixin
    from tools.finance import InvestmentAnalyzer
    
    class TestPipeline(ToolsMixin):
        def __init__(self):
            super().__init__()
            self.setup_tools()
            
            # Add custom tool
            investment_tool = InvestmentAnalyzer()
            from dspy.adapters import Tool
            self.tools.append(Tool(investment_tool.calculate_roi, name="calculate_roi"))
    
    pipeline = TestPipeline()
    
    # Verify tools are loaded
    assert len(pipeline.tools) > 0
    
    # Verify custom tool is available
    tool_names = [tool.name for tool in pipeline.tools]
    assert "calculate_roi" in tool_names

def test_tool_execution():
    """Test tool execution within a pipeline context."""
    from superoptix.core.pipeline_utils import ToolsMixin
    from tools.finance import InvestmentAnalyzer
    import dspy
    
    class TestPipeline(ToolsMixin):
        def __init__(self):
            super().__init__()
            self.setup_tools()
            
            # Add custom tool
            investment_tool = InvestmentAnalyzer()
            from dspy.adapters import Tool
            self.tools.append(Tool(investment_tool.calculate_roi, name="calculate_roi"))
    
    pipeline = TestPipeline()
    
    # Test tool execution
    for tool in pipeline.tools:
        if tool.name == "calculate_roi":
            result = tool(1000, 1500, 2)
            assert "ROI" in result
            assert "50.00%" in result
            break
```

---

## 🚀 Advanced Tool Features

### Async Tools

```python
import asyncio

class AsyncTool:
    """Async tool for I/O operations."""
    
    async def fetch_data(self, url: str) -> str:
        """Fetch data asynchronously."""
        try:
            import aiohttp
            async with aiohttp.ClientSession() as session:
                async with session.get(url) as response:
                    data = await response.text()
                    return f"Fetched {len(data)} characters from {url}"
        except Exception as e:
            return f"Fetch error: {str(e)}"
```

### Tool with Memory

```python
class MemoryAwareTool:
    """Tool that remembers previous operations."""
    
    def __init__(self):
        self.history = []
    
    def process_with_memory(self, data: str) -> str:
        """Process data with memory of previous operations."""
        self.history.append(data)
        
        # Use history for context
        context = f"Previous operations: {len(self.history)}"
        result = f"Processed: {data} (with context: {context})"
        
        return f"""🧠 Memory-Aware Tool:
{'='*50}
{result}
History: {len(self.history)} operations
"""
```

### Tool with Configuration

```python
class ConfigurableTool:
    """Tool with runtime configuration."""
    
    def __init__(self, config: dict = None):
        self.config = config or {}
        self.max_retries = self.config.get('max_retries', 3)
        self.timeout = self.config.get('timeout', 30)
    
    def execute_with_config(self, data: str) -> str:
        """Execute with configuration parameters."""
        result = f"Processed with {self.max_retries} retries, {self.timeout}s timeout"
        return f"""⚙️ Configurable Tool:
{'='*50}
{result}
Config: {self.config}
"""
```

---

## 📚 Tool Examples by Domain

### Finance Tools

```python
class InvestmentAnalyzer:
    """Analyze investment opportunities."""
    
    def analyze_roi(self, initial_investment: float, final_value: float, years: int) -> str:
        """Calculate Return on Investment."""
        try:
            roi = ((final_value - initial_investment) / initial_investment) * 100
            annual_roi = roi / years
            
            return f"""📈 ROI Analysis:
{'='*50}
Initial Investment: ${initial_investment:,.2f}
Final Value: ${final_value:,.2f}
Time Period: {years} years

Total ROI: {roi:.2f}%
Annual ROI: {annual_roi:.2f}%
"""
        except Exception as e:
            return f"ROI calculation error: {str(e)}"
```

### Healthcare Tools

```python
class HealthAnalyzer:
    """Analyze health metrics."""
    
    def calculate_bmi(self, weight_kg: float, height_m: float) -> str:
        """Calculate Body Mass Index."""
        try:
            bmi = weight_kg / (height_m ** 2)
            
            if bmi < 18.5:
                category = "Underweight"
            elif bmi < 25:
                category = "Normal weight"
            elif bmi < 30:
                category = "Overweight"
            else:
                category = "Obese"
            
            return f"""🏥 BMI Analysis:
{'='*50}
Weight: {weight_kg} kg
Height: {height_m} m
BMI: {bmi:.1f}
Category: {category}
"""
        except Exception as e:
            return f"BMI calculation error: {str(e)}"
```

---

## 🎯 Next Steps

1. **Browse existing tools**: `super market browse tools`
2. **Study tool patterns**: Examine tools in `superoptix/tools/categories/`
3. **Create your first tool**: Follow the basic structure above
4. **Test thoroughly**: Use unit tests and integration tests
5. **Share your tools**: Contribute tools to the SuperOptiX ecosystem

---

## 📚 Related Documentation

- [Agent Development Guide](./agent-development.md) - Learn how tools fit into the agent development process
- [SuperSpec DSL Guide](./superspec.md) - Configure tools in agent playbooks
- [CLI Reference](../reference/cli.md) - Command-line tool management
- [API Reference](../reference/api/index) - Programmatic tool access

---

*Ready to build powerful tools that enhance your SuperOptiX agents? Start with the marketplace, then create your own custom tools! 🚀* 