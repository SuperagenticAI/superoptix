"""
SuperOptiX Tools Categories
===========================

Organized tool categories for easy discovery and maintenance.
"""

# Import only the categories that have implementations
from .agriculture import CropRotationPlannerTool
from .core import *
from .development import *
from .education import GradeCalculatorTool
from .energy import EnergyUsageAnalyzerTool
from .finance import *
from .gaming_sports import TournamentBracketTool

# Import stubs for other categories (these only have placeholder implementations)
from .healthcare import BMICalculatorTool
from .hospitality import EventPlannerTool
from .human_resources import SalaryBenchmarkTool
from .legal import ContractAnalyzerTool, LegalTermLookupTool
from .manufacturing import InventoryTrackerTool
from .marketing import EmailValidatorTool, SEOAnalyzerTool
from .real_estate import PropertyValuerTool
from .retail import PricingAnalyzerTool
from .transportation import RouteOptimizerTool
from .utilities import *

__all__ = [
    # Core tools (fully implemented)
    "WebSearchTool",
    "CalculatorTool",
    "FileReaderTool",
    "DateTimeTool",
    "TextAnalyzerTool",
    "JSONProcessorTool",
    "CodeFormatterTool",
    "DataProcessorTool",
    # Development tools (fully implemented)
    "GitTool",
    "APITesterTool",
    "DatabaseQueryTool",
    "VersionCheckerTool",
    "DependencyAnalyzerTool",
    "CodeReviewerTool",
    "TestCoverageTool",
    "DockerHelperTool",
    # Finance tools (fully implemented)
    "CurrencyConverterTool",
    "TaxCalculatorTool",
    "LoanCalculatorTool",
    "InvestmentAnalyzerTool",
    "BudgetPlannerTool",
    # Utility tools (fully implemented)
    "PasswordGeneratorTool",
    "HashGeneratorTool",
    "ColorConverterTool",
    "UnitConverterTool",
    # Stub implementations (basic placeholders for now)
    "BMICalculatorTool",
    "SEOAnalyzerTool",
    "EmailValidatorTool",
    "LegalTermLookupTool",
    "ContractAnalyzerTool",
    "GradeCalculatorTool",
    "InventoryTrackerTool",
    "CropRotationPlannerTool",
    "EnergyUsageAnalyzerTool",
    "PropertyValuerTool",
    "RouteOptimizerTool",
    "PricingAnalyzerTool",
    "EventPlannerTool",
    "SalaryBenchmarkTool",
    "TournamentBracketTool",
]
