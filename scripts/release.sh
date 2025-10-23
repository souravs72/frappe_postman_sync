#!/bin/bash

# Frappe Postman Sync - Release Script
# This script helps maintainers create releases

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

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

# Function to validate version format
validate_version() {
    local version=$1
    if [[ ! $version =~ ^[0-9]+\.[0-9]+\.[0-9]+$ ]]; then
        print_error "Version must follow semantic versioning (e.g., 1.0.0)"
        exit 1
    fi
}

# Function to check if we're on main branch
check_branch() {
    local current_branch=$(git branch --show-current)
    if [ "$current_branch" != "main" ]; then
        print_error "You must be on the main branch to create a release. Current branch: $current_branch"
        exit 1
    fi
}

# Function to check if working directory is clean
check_clean_working_directory() {
    if [ -n "$(git status --porcelain)" ]; then
        print_error "Working directory is not clean. Please commit or stash your changes."
        exit 1
    fi
}

# Function to run tests
run_tests() {
    print_status "Running tests..."

    # Run linting
    if command -v ruff &> /dev/null; then
        ruff check . || {
            print_error "Linting failed. Please fix the issues."
            exit 1
        }
        print_success "Linting passed"
    fi

    # Run formatting check
    if command -v ruff &> /dev/null; then
        ruff format --check . || {
            print_error "Code formatting check failed. Run 'ruff format .' to fix."
            exit 1
        }
        print_success "Formatting check passed"
    fi

    # Check for secrets
    if grep -r -E "(api[_-]?key|password|secret|token)" . --include="*.py" --include="*.js" --include="*.json" | grep -v -E "(get_password|decrypt_password|your_api_key|token.*your_)" | grep -v ".git/" | grep -v ".github/" > /dev/null 2>&1; then
        print_error "Potential secrets found in code. Please remove them before releasing."
        exit 1
    fi
    print_success "Security check passed"
}

# Function to update version in files
update_version() {
    local version=$1
    local next_version=$2

    print_status "Updating version to $version..."

    # Update pyproject.toml
    if [ -f "pyproject.toml" ]; then
        sed -i "s/version = \".*\"/version = \"$version\"/" pyproject.toml
        print_success "Updated pyproject.toml"
    fi

    # Update CHANGELOG.md
    if [ -f "CHANGELOG.md" ]; then
        # Add new version section
        local today=$(date +%Y-%m-%d)
        sed -i "s/## \[Unreleased\]/## \[Unreleased\]\n\n## \[$version\] - $today/" CHANGELOG.md
        print_success "Updated CHANGELOG.md"
    fi
}

# Function to create release commit and tag
create_release() {
    local version=$1

    print_status "Creating release commit and tag..."

    # Add version files
    git add pyproject.toml CHANGELOG.md

    # Create commit
    git commit -m "chore: release version $version"

    # Create tag
    git tag -a "v$version" -m "Release version $version"

    print_success "Created release commit and tag v$version"
}

# Function to push to remote
push_release() {
    local version=$1

    print_status "Pushing to remote..."

    # Push commits
    git push origin main

    # Push tags
    git push origin "v$version"

    print_success "Pushed release to remote"
}

# Main release process
main() {
    if [ $# -eq 0 ]; then
        print_error "Usage: $0 <version>"
        print_error "Example: $0 1.0.0"
        exit 1
    fi

    local version=$1
    validate_version "$version"

    print_status "Starting release process for version $version..."

    # Pre-release checks
    check_branch
    check_clean_working_directory
    run_tests

    # Update version
    update_version "$version"

    # Create release
    create_release "$version"

    # Ask for confirmation before pushing
    echo ""
    print_warning "About to push release to remote repository."
    read -p "Do you want to continue? (y/N): " -n 1 -r
    echo ""

    if [[ $REPLY =~ ^[Yy]$ ]]; then
        push_release "$version"
        print_success "Release $version completed successfully!"
        echo ""
        print_status "Next steps:"
        echo "1. Create a GitHub release from the tag: https://github.com/yourusername/frappe-postman-sync/releases/new"
        echo "2. Update the release notes with the changelog content"
        echo "3. Notify users about the new release"
    else
        print_warning "Release not pushed to remote. You can push manually later:"
        echo "  git push origin main"
        echo "  git push origin v$version"
    fi
}

# Run main function with all arguments
main "$@"
