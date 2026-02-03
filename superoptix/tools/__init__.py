"""
SuperOptiX Tools Library
========================

Modular tool system for SuperOptiX agents.
Organized by industry and functionality for easy discovery and maintenance.
"""

# Import from the new modular structure
from .base import BaseTool, ToolError, ToolExecutionError, ToolValidationError
from .categories import *

# For backward compatibility, provide the original class names
from .categories.core import (
    CalculatorTool,
    DateTimeTool,
    FileReaderTool,
    JSONProcessorTool,
    TextAnalyzerTool,
    WebSearchTool,
)
from .factories import *

# Legacy compatibility - redirect to factory functions for existing users
from .factories.tool_factory import (
    create_calculator_tool,
    create_datetime_tool,
    create_file_reader_tool,
    create_json_processor_tool,
    create_text_analyzer_tool,
    create_tool_by_name,
    create_web_search_tool,
    get_available_tools,
    get_default_tools,
)

__version__ = "2.0.0"

__all__ = [
    # Core functionality
    "BaseTool",
    "ToolError",
    "ToolValidationError",
    "ToolExecutionError",
    # Legacy compatibility - class imports
    "WebSearchTool",
    "CalculatorTool",
    "FileReaderTool",
    "DateTimeTool",
    "TextAnalyzerTool",
    "JSONProcessorTool",
    # Factory functions
    "create_web_search_tool",
    "create_calculator_tool",
    "create_file_reader_tool",
    "create_datetime_tool",
    "create_text_analyzer_tool",
    "create_json_processor_tool",
    "get_default_tools",
    "get_available_tools",
    "create_tool_by_name",
    # All tools from categories (re-exported)
    # Core tools
    "CodeFormatterTool",
    "DataProcessorTool",
    # Development tools
    "GitTool",
    "APITesterTool",
    "DatabaseQueryTool",
    "VersionCheckerTool",
    "DependencyAnalyzerTool",
    "CodeReviewerTool",
    "TestCoverageTool",
    "DockerHelperTool",
    # Finance tools
    "CurrencyConverterTool",
    "TaxCalculatorTool",
    "LoanCalculatorTool",
    "InvestmentAnalyzerTool",
    "BudgetPlannerTool",
    # Healthcare tools
    "BMICalculatorTool",
    "MedicalTermLookupTool",
    "DrugInteractionTool",
    "SymptomAnalyzerTool",
    "HealthValidatorTool",
    "VitalsAnalyzerTool",
    "AppointmentSchedulerTool",
    "InsuranceCheckerTool",
    "DosageCalculatorTool",
    "MedicalCodesTool",
    # Marketing tools
    "SEOAnalyzerTool",
    "EmailValidatorTool",
    "SocialMetricsTool",
    "ContentPlannerTool",
    "CompetitorAnalysisTool",
    "KeywordResearchTool",
    "AdPerformanceTool",
    "BrandMonitorTool",
    "CampaignOptimizerTool",
    "ConversionTrackerTool",
    # Legal tools
    "LegalTermLookupTool",
    "ContractAnalyzerTool",
    "CaseSearchTool",
    "DocumentRedactorTool",
    "LegalComplianceTool",
    "CitationFormatterTool",
    "JurisdictionLookupTool",
    "FilingHelperTool",
    # Education tools
    "GradeCalculatorTool",
    "StudySchedulerTool",
    "LessonPlannerTool",
    "QuizGeneratorTool",
    "ProgressTrackerTool",
    "LearningAssessmentTool",
    "ResourceFinderTool",
    "SkillAssessmentTool",
    # Manufacturing tools
    "InventoryTrackerTool",
    "QualityCheckerTool",
    "MaintenanceSchedulerTool",
    "SupplyChainTool",
    "ProductionPlannerTool",
    "SafetyValidatorTool",
    "EquipmentMonitorTool",
    # Agriculture tools
    "CropRotationPlannerTool",
    "WeatherForecastTool",
    "SoilAnalyzerTool",
    "PestIdentifierTool",
    "HarvestSchedulerTool",
    "IrrigationCalculatorTool",
    # Energy tools
    "EnergyUsageAnalyzerTool",
    "GridOptimizerTool",
    "RenewableCalculatorTool",
    "EfficiencyAuditorTool",
    "LoadForecasterTool",
    # Real estate tools
    "PropertyValuerTool",
    "MortgageCalculatorTool",
    "MarketAnalyzerTool",
    "RentalCalculatorTool",
    "LocationAnalyzerTool",
    # Transportation tools
    "RouteOptimizerTool",
    "FuelCalculatorTool",
    "VehicleTrackerTool",
    "ShippingEstimatorTool",
    "TrafficAnalyzerTool",
    "MaintenanceTrackerTool",
    # Retail tools
    "PricingAnalyzerTool",
    "CustomerSegmentTool",
    # Hospitality tools
    "EventPlannerTool",
    # HR tools
    "SalaryBenchmarkTool",
    # Gaming/Sports tools
    "TournamentBracketTool",
    # Utility tools
    "PasswordGeneratorTool",
    "HashGeneratorTool",
    "ColorConverterTool",
    "UnitConverterTool",
]


def list_available_categories():
    """List all available tool categories."""
    return [
        "Core",
        "Development",
        "Finance",
        "Healthcare",
        "Marketing",
        "Legal",
        "Education",
        "Manufacturing",
        "Agriculture",
        "Energy",
        "Real Estate",
        "Transportation",
        "Retail",
        "Hospitality",
        "Human Resources",
        "Gaming Sports",
        "Utilities",
    ]


def get_tools_by_category(category: str):
    """Get all tools in a specific category."""
    category_map = {
        "core": [
            "WebSearchTool",
            "CalculatorTool",
            "FileReaderTool",
            "DateTimeTool",
            "TextAnalyzerTool",
            "JSONProcessorTool",
            "CodeFormatterTool",
            "DataProcessorTool",
        ],
        "development": [
            "GitTool",
            "APITesterTool",
            "DatabaseQueryTool",
            "VersionCheckerTool",
            "DependencyAnalyzerTool",
            "CodeReviewerTool",
            "TestCoverageTool",
            "DockerHelperTool",
        ],
        "finance": [
            "CurrencyConverterTool",
            "TaxCalculatorTool",
            "LoanCalculatorTool",
            "InvestmentAnalyzerTool",
            "BudgetPlannerTool",
        ],
        "healthcare": [
            "BMICalculatorTool",
            "MedicalTermLookupTool",
            "DrugInteractionTool",
        ],
        "utilities": [
            "PasswordGeneratorTool",
            "HashGeneratorTool",
            "ColorConverterTool",
            "UnitConverterTool",
        ],
    }

    return category_map.get(category.lower(), [])


# Tool statistics
def get_tool_stats():
    """Get statistics about available tools."""
    return {
        "total_tools": len(__all__) - 10,  # Subtract non-tool exports
        "categories": len(list_available_categories()),
        "core_tools": 8,
        "development_tools": 8,
        "finance_tools": 5,
        "utility_tools": 4,
        "version": __version__,
    }
