#!/bin/bash

# SuperOptiX Installation Script
# This script detects your environment and installs SuperOptiX using the best method

set -e

echo "👑 Welcome to SuperOptiX: The King of Agent Frameworks"
echo "🚀 Optimization-First AI Agent Framework"
echo "======================================================"
echo ""

# Function to detect Python version
check_python() {
    if command -v python3 &> /dev/null; then
        PYTHON_VERSION=$(python3 -c "import sys; print(f'{sys.version_info.major}.{sys.version_info.minor}')")
        echo "✅ Found Python $PYTHON_VERSION"
        
        # Check if version is 3.11 or higher
        if python3 -c "import sys; exit(0 if sys.version_info >= (3, 11) else 1)" 2>/dev/null; then
            return 0
        else
            echo "❌ Python version must be 3.11 or higher. Found: $PYTHON_VERSION"
            return 1
        fi
    else
        echo "❌ Python 3 not found. Please install Python 3.11 or higher."
        return 1
    fi
}

# Function to detect package managers
detect_package_manager() {
    echo "🔍 Detecting your environment..."
    
    if command -v uv &> /dev/null; then
        echo "✅ Found uv (recommended)"
        INSTALL_METHOD="uv"
        return 0
    elif command -v conda &> /dev/null; then
        echo "✅ Found conda"
        INSTALL_METHOD="conda"
        return 0
    elif command -v pip &> /dev/null; then
        echo "✅ Found pip"
        INSTALL_METHOD="pip"
        return 0
    else
        echo "❌ No package manager found. Please install pip, conda, or uv."
        return 1
    fi
}

# Function to install uv if not present
install_uv() {
    echo "📦 Installing uv (recommended package manager)..."
    curl -LsSf https://astral.sh/uv/install.sh | sh
    echo "✅ uv installed successfully!"
    echo "🔄 Please restart your terminal or run: source ~/.bashrc"
    echo "   Then run this script again."
    exit 0
}

# Function to install SuperOptiX
install_superoptix() {
    echo ""
    echo "📦 Installing SuperOptiX..."
    
    case $INSTALL_METHOD in
        "uv")
            echo "Using uv (fastest method)..."
            echo "📦 Installing with lock file for reproducible builds..."
            uv lock
            uv sync
            echo "🔒 Lock file generated for consistent installations"
            ;;
        "conda")
            echo "Using conda..."
            echo "Creating conda environment 'superoptix'..."
            conda create -n superoptix python=3.11 -y
            echo "Activating environment..."
            source $(conda info --base)/etc/profile.d/conda.sh
            conda activate superoptix
            pip install superoptix
            ;;
        "pip")
            echo "Using pip..."
            pip install superoptix
            ;;
    esac
    
    echo "✅ SuperOptiX installed successfully!"
}

# Function to show optional dependencies
show_optional_deps() {
    echo ""
    echo "🔧 Optional Dependencies Available:"
    echo ""
    echo "📚 Vector Databases (RAG Support):"
    if command -v uv &> /dev/null; then
        echo "  uv sync --extra chromadb    # ChromaDB (recommended)"
        echo "  uv sync --extra lancedb     # LanceDB (fast local)"
        echo "  uv sync --extra faiss       # FAISS (high performance)"
        echo "  uv sync --extra weaviate    # Weaviate (semantic search)"
        echo "  uv sync --extra qdrant      # Qdrant (production)"
        echo "  uv sync --extra milvus      # Milvus (enterprise)"
        echo "  uv sync --extra pinecone    # Pinecone (cloud)"
        echo "  uv sync --extra vectordb    # All vector databases"
        echo ""
        echo "🎨 Additional Features:"
        echo "  uv sync --extra ui          # UI dashboards"
        echo "  uv sync --extra observability # Monitoring"
        echo "  uv sync --extra web         # Web frameworks"
        echo "  uv sync --extra data        # Data processing"
        echo "  uv sync --extra cloud       # Cloud deployment"
        echo "  uv sync --extra redis       # Redis caching"
        echo "  uv sync --all-extras        # All optional deps"
    else
        echo "  pip install superoptix[chromadb]    # ChromaDB (recommended)"
        echo "  pip install superoptix[lancedb]     # LanceDB (fast local)"
        echo "  pip install superoptix[faiss]       # FAISS (high performance)"
        echo "  pip install superoptix[weaviate]    # Weaviate (semantic search)"
        echo "  pip install superoptix[qdrant]      # Qdrant (production)"
        echo "  pip install superoptix[milvus]      # Milvus (enterprise)"
        echo "  pip install superoptix[pinecone]    # Pinecone (cloud)"
        echo "  pip install superoptix[vectordb]    # All vector databases"
        echo ""
        echo "🎨 Additional Features:"
        echo "  pip install superoptix[ui]          # UI dashboards"
        echo "  pip install superoptix[observability] # Monitoring"
        echo "  pip install superoptix[web]         # Web frameworks"
        echo "  pip install superoptix[data]        # Data processing"
        echo "  pip install superoptix[cloud]       # Cloud deployment"
        echo "  pip install superoptix[redis]       # Redis caching"
        echo "  pip install superoptix[all]         # All optional deps"
    fi
    echo ""
}

# Function to verify installation
verify_installation() {
    echo ""
    echo "🔍 Verifying installation..."
    
    if command -v super &> /dev/null; then
        echo "✅ SuperOptiX CLI installed successfully!"
        echo ""
        echo "🎉 Installation complete! Here's what you can do next:"
        echo ""
        echo "1. 🚀 Start with our Getting Started Guide:"
        echo "   https://github.com/SuperagenticAI/superoptix/blob/main/GETTING_STARTED.md"
        echo ""
        echo "2. 🎯 Create your first project:"
        echo "   super init my_first_ai_system"
        echo ""
        echo "3. 📚 View all available commands:"
        echo "   super --help"
        echo ""
        echo "4. 🏪 Browse the marketplace:"
        echo "   super marketplace browse"
        echo ""
        echo "👑 Welcome to the King of Agent Frameworks!"
        echo ""
        echo "🚀 Evaluate • Optimize • Orchestrate • Operate"
    else
        echo "❌ Installation verification failed. Please try again."
        exit 1
    fi
}

# Function to show installation options
show_options() {
    echo ""
    echo "📋 Installation Options:"
    echo "1. Install uv (recommended) - Fastest package manager"
    echo "2. Use existing conda environment"
    echo "3. Use existing pip installation"
    echo "4. Install from GitHub (latest features)"
    echo ""
    read -p "Choose an option (1-4): " choice
    
    case $choice in
        1)
            install_uv
            ;;
        2)
            INSTALL_METHOD="conda"
            install_superoptix
            ;;
        3)
            INSTALL_METHOD="pip"
            install_superoptix
            ;;
        4)
            echo "Installing from GitHub..."
            if command -v uv &> /dev/null; then
                uv pip install git+https://github.com/SuperagenticAI/superoptix.git
            elif command -v pip &> /dev/null; then
                pip install git+https://github.com/SuperagenticAI/superoptix.git
            else
                echo "❌ No suitable package manager found for GitHub installation."
                exit 1
            fi
            ;;
        *)
            echo "❌ Invalid option. Please run the script again."
            exit 1
            ;;
    esac
}

# Main installation flow
main() {
    # Check Python version
    if ! check_python; then
        exit 1
    fi
    
    # Detect package manager
    if ! detect_package_manager; then
        echo ""
        echo "💡 No package manager detected. Would you like to install uv (recommended)?"
        read -p "Install uv? (y/n): " install_uv_choice
        if [[ $install_uv_choice =~ ^[Yy]$ ]]; then
            install_uv
        else
            show_options
        fi
    fi
    
    # Install SuperOptiX
    install_superoptix
    
    # Show optional dependencies
    show_optional_deps
    
    # Verify installation
    verify_installation
}

# Run main function
main "$@" 