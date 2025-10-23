#!/bin/bash

# Frappe Postman Sync - Development Setup Script
# This script sets up the development environment for contributors

set -e

echo "Setting up Frappe Postman Sync development environment..."

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Function to print colored output
print_status() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

print_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Check if we're in the right directory
if [ ! -f "pyproject.toml" ] || [ ! -d "frappe_postman_sync" ]; then
    print_error "Please run this script from the root of the frappe_postman_sync repository"
    exit 1
fi

# Check Python version
print_status "Checking Python version..."
python_version=$(python3 --version 2>&1 | cut -d' ' -f2)
required_version="3.8"
if ! python3 -c "import sys; exit(0 if sys.version_info >= (3, 8) else 1)"; then
    print_error "Python 3.8+ is required. Current version: $python_version"
    exit 1
fi
print_success "Python version $python_version is compatible"

# Check if pip is available
if ! command -v pip3 &> /dev/null; then
    print_error "pip3 is not installed. Please install pip3 first."
    exit 1
fi

# Install development dependencies
print_status "Installing development dependencies..."
pip3 install --upgrade pip
pip3 install -e ".[dev]"

# Install pre-commit hooks
print_status "Installing pre-commit hooks..."
if command -v pre-commit &> /dev/null; then
    pre-commit install
    print_success "Pre-commit hooks installed"
else
    print_warning "pre-commit not found. Installing..."
    pip3 install pre-commit
    pre-commit install
fi

# Check if git is configured
print_status "Checking git configuration..."
if ! git config user.name &> /dev/null || ! git config user.email &> /dev/null; then
    print_warning "Git user name or email not configured."
    print_warning "Please run:"
    print_warning "  git config --global user.name 'Your Name'"
    print_warning "  git config --global user.email 'your.email@example.com'"
fi

# Run initial linting
print_status "Running initial code quality checks..."
if command -v ruff &> /dev/null; then
    print_status "Running ruff linter..."
    ruff check . || print_warning "Linting issues found. Run 'ruff check . --fix' to auto-fix"

    print_status "Running ruff formatter..."
    ruff format . || print_warning "Formatting issues found. Run 'ruff format .' to auto-format"
else
    print_warning "ruff not found. Please install it manually: pip3 install ruff"
fi

# Check for common issues
print_status "Checking for common development issues..."

# Check for secrets in code
if grep -r -E "(api[_-]?key|password|secret|token)" . --include="*.py" --include="*.js" --include="*.json" | grep -v -E "(get_password|decrypt_password|your_api_key|token.*your_)" | grep -v ".git/" | grep -v ".github/" > /dev/null 2>&1; then
    print_warning "Potential secrets found in code. Please review and remove any hardcoded secrets."
fi

# Check JSON files
print_status "Validating JSON files..."
find . -name "*.json" -not -path "./.git/*" -not -path "./node_modules/*" -exec python3 -m json.tool {} > /dev/null \; || {
    print_warning "Some JSON files have syntax errors. Please fix them."
}

# Create .env template if it doesn't exist
if [ ! -f ".env.example" ]; then
    print_status "Creating .env.example template..."
    cat > .env.example << EOF
# Frappe Postman Sync - Environment Variables
# Copy this file to .env and fill in your values

# Postman API Configuration
POSTMAN_API_KEY=your_postman_api_key_here
POSTMAN_WORKSPACE_ID=your_workspace_id_here
POSTMAN_COLLECTION_ID=your_collection_id_here

# Frappe Configuration
FRAPPE_BASE_URL=http://localhost:8000
FRAPPE_API_KEY=your_frappe_api_key_here

# Development Settings
DEBUG=True
LOG_LEVEL=INFO
EOF
    print_success ".env.example created"
fi

# Check if .env exists
if [ ! -f ".env" ]; then
    print_warning ".env file not found. Please copy .env.example to .env and configure your settings."
fi

print_success "Development environment setup complete!"
echo ""
print_status "Next steps:"
echo "1. Copy .env.example to .env and configure your settings"
echo "2. Make sure your Frappe bench is running"
echo "3. Install the app in your Frappe bench: bench --site your-site install-app frappe_postman_sync"
echo "4. Start developing! Check CONTRIBUTING.md for guidelines"
echo ""
print_status "Useful commands:"
echo "  ruff check .          # Run linting"
echo "  ruff format .         # Format code"
echo "  pre-commit run --all  # Run all pre-commit hooks"
echo "  git commit -m 'feat: your message'  # Make a commit"
echo ""
