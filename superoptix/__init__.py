"""SuperOptiX: A CLI tool for managing agentic DSL configurations."""

# ---------------------------------------------------------------------------
# Global warning filters - CRITICAL: Must be before any imports
# ---------------------------------------------------------------------------
# Comprehensive Pydantic warning suppression for clean user experience
# These warnings come from dependencies (storage3, supabase, etc.) and are
# harmless but clutter the console. We suppress them at package import time.
# Down-stream modules (CLI runners, notebooks) inherit the filter automatically.

import warnings
import os

# Filter specific DeprecationWarnings from opentelemetry
# These are caused by a mismatch between opentelemetry versions in dependencies
# and should be hidden from end users.
warnings.filterwarnings("ignore", category=DeprecationWarning, module="opentelemetry")
warnings.filterwarnings("ignore", category=DeprecationWarning, module="opentelemetry.*")
warnings.filterwarnings(
    "ignore", message="You should use `Logger` instead", category=DeprecationWarning
)
warnings.filterwarnings(
    "ignore",
    message="You should use `LoggerProvider` instead",
    category=DeprecationWarning,
)
warnings.filterwarnings(
    "ignore",
    message="You should use `ProxyLoggerProvider` instead",
    category=DeprecationWarning,
)

# ============================================================================
# ULTRA-AGGRESSIVE WARNING SUPPRESSION FOR PYPI INSTALLATIONS
# ============================================================================
# For PyPI installations, warnings can be triggered during dependency imports
# BEFORE filters are applied. Use multi-layered approach:

# STEP 1: Suppress ALL warnings first (immediate suppression)
warnings.simplefilter("ignore")

# STEP 2: Set PYTHONWARNINGS environment variable as fallback
os.environ.setdefault("PYTHONWARNINGS", "ignore")

# STEP 3: Apply specific filters for Pydantic-related warnings

# ============================================================================
# COMPREHENSIVE PYDANTIC WARNING SUPPRESSION
# ============================================================================

# 1. Suppress ALL Pydantic-related warnings by message pattern
warnings.filterwarnings(
    "ignore",
    message=r".*[Pp]ydantic.*",
    category=UserWarning,
)
warnings.filterwarnings(
    "ignore",
    message=r".*[Pp]ydantic.*",
    category=DeprecationWarning,
)
warnings.filterwarnings(
    "ignore",
    message=r".*[Pp]ydantic.*",
    category=FutureWarning,
)

# 2. Suppress specific Pydantic warning types
warnings.filterwarnings(
    "ignore",
    message=r".*PydanticDeprecatedSince20.*",
    category=UserWarning,
)
warnings.filterwarnings(
    "ignore",
    message=r".*pydantic\.config\.Extra.*",
    category=UserWarning,
)
warnings.filterwarnings(
    "ignore",
    message=r".*Pydantic serializer warnings.*",
    category=UserWarning,
)

# 3. Suppress ALL warnings from pydantic module
warnings.filterwarnings(
    "ignore",
    module="pydantic.*",
    category=UserWarning,
)
warnings.filterwarnings(
    "ignore",
    module="pydantic.*",
    category=DeprecationWarning,
)
warnings.filterwarnings(
    "ignore",
    module="pydantic.*",
    category=FutureWarning,
)

# 4. Suppress ALL warnings from pydantic_ai module
warnings.filterwarnings(
    "ignore",
    module="pydantic_ai.*",
    category=UserWarning,
)
warnings.filterwarnings(
    "ignore",
    module="pydantic_ai.*",
    category=DeprecationWarning,
)
warnings.filterwarnings(
    "ignore",
    module="pydantic_ai.*",
    category=FutureWarning,
)

# 5. Suppress warnings from storage3 module (Supabase dependency)
# This is a common source of PydanticDeprecatedSince20 warnings
# CRITICAL: Must suppress before supabase imports storage3
# warnings.filterwarnings(
#     "ignore",
#     module="storage3.*",
#     category=UserWarning,
# )
# warnings.filterwarnings(
#     "ignore",
#     module="storage3.*",
#     category=DeprecationWarning,
# )
# warnings.filterwarnings(
#     "ignore",
#     message=r".*storage3.*",
#     category=UserWarning,
# )
# warnings.filterwarnings(
#     "ignore",
#     message=r".*storage3.*",
#     category=DeprecationWarning,
# )
warnings.filterwarnings(
    "ignore",
    message=r".*pydantic\.config\.Extra.*",
    category=DeprecationWarning,
)
warnings.filterwarnings(
    "ignore",
    message=r".*PydanticDeprecatedSince20.*",
    category=DeprecationWarning,
)

# 6. Suppress warnings from supabase module (may use Pydantic)
# warnings.filterwarnings(
#     "ignore",
#     module="supabase.*",
#     category=UserWarning,
# )
# warnings.filterwarnings(
#     "ignore",
#     message=r".*supabase.*[Pp]ydantic.*",
#     category=UserWarning,
# )

# ============================================================================
# VERSION
# ============================================================================

__version__ = "0.2.7"

# ============================================================================
# FINAL SAFETY: Re-apply filters after all imports (defense in depth)
# ============================================================================
# This ensures warnings are suppressed even if modules are imported in
# unexpected order or if dependencies trigger warnings during import

# Re-apply comprehensive Pydantic suppression
warnings.filterwarnings(
    "ignore",
    message=r".*[Pp]ydantic.*",
    category=UserWarning,
)
warnings.filterwarnings(
    "ignore",
    message=r".*[Pp]ydantic.*",
    category=DeprecationWarning,
)
warnings.filterwarnings(
    "ignore",
    module="pydantic.*",
    category=UserWarning,
)
warnings.filterwarnings(
    "ignore",
    module="pydantic_ai.*",
    category=UserWarning,
)
warnings.filterwarnings(
    "ignore",
    module="storage3.*",
    category=UserWarning,
)
