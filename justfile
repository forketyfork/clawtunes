# Clawtunes development commands

# Display available commands
default:
    @just --list

# Install package in editable mode with dev dependencies
install:
    #!/usr/bin/env bash
    set -euo pipefail
    if [[ -n "${IN_NIX_SHELL:-}" ]]; then
        echo "❌ You are in a Nix environment. pip install will fail."
        echo ""
        echo "In Nix, the clawtunes command is already available in the dev shell."
        echo "For global installation, use: nix profile install ."
        echo "To run without installing, use: nix run ."
        exit 1
    else
        echo "📦 Installing clawtunes in editable mode..."
        pip install -e ".[dev]"
    fi

# Run all linters (black, ruff, mypy)
lint: format-check lint-ruff type-check

# Format code with black
format:
    @echo "🎨 Formatting code with black..."
    black src/clawtunes src/clawtunes_helpers tests

# Check code formatting without modifying
format-check:
    @echo "🔍 Checking code formatting..."
    black --check src/clawtunes src/clawtunes_helpers tests

# Lint with ruff
lint-ruff:
    @echo "🔍 Linting with ruff..."
    ruff check src/clawtunes src/clawtunes_helpers tests

# Fix auto-fixable ruff issues
fix:
    @echo "🔧 Fixing auto-fixable issues..."
    ruff check --fix src/clawtunes src/clawtunes_helpers tests
    black src/clawtunes src/clawtunes_helpers tests

# Type check with mypy
type-check:
    @echo "🔍 Type checking with mypy..."
    mypy src/clawtunes src/clawtunes_helpers

# Run all tests with pytest
test:
    @echo "🧪 Running tests..."
    pytest -v

# Run tests with coverage report
test-cov:
    @echo "🧪 Running tests with coverage..."
    pytest --cov=clawtunes --cov=clawtunes_helpers --cov-report=term-missing --cov-report=html

# Run specific test file
test-file FILE:
    @echo "🧪 Running tests in {{FILE}}..."
    pytest -v {{FILE}}

# Run tests matching a pattern
test-match PATTERN:
    @echo "🧪 Running tests matching '{{PATTERN}}'..."
    pytest -v -k "{{PATTERN}}"

# Run clawtunes CLI (pass arguments after --)
run *ARGS:
    @echo "🎵 Running clawtunes..."
    python -m clawtunes.cli {{ARGS}}

# Show current playing status
status:
    @python -m clawtunes.cli status

# Show play history
history:
    @python -m clawtunes.cli history

# Clean build artifacts and cache
clean:
    @echo "🧹 Cleaning build artifacts..."
    rm -rf build/
    rm -rf dist/
    rm -rf *.egg-info/
    rm -rf .pytest_cache/
    rm -rf .mypy_cache/
    rm -rf .ruff_cache/
    rm -rf htmlcov/
    rm -rf .coverage
    find . -type d -name __pycache__ -exec rm -rf {} +
    find . -type f -name "*.pyc" -delete
    @echo "✅ Cleaned"

# Run all checks (lint, type-check, test)
check: lint type-check test
    @echo "✅ All checks passed!"

# Run CI-equivalent checks
ci: check
    @echo "✅ CI checks complete!"

# Watch tests (requires pytest-watch)
watch:
    @echo "👀 Watching for changes..."
    ptw -- -v

# Build package
build:
    @echo "📦 Building package..."
    python -m build

# Show project info
info:
    @echo "Clawtunes Development Environment"
    @echo "================================="
    @echo "Python: $(python --version)"
    @echo "Pip: $(pip --version)"
    @echo "Location: $(which python)"
    @echo ""
    @echo "Python Package Status:"
    @python -c "import clawtunes; print(f'  clawtunes: {clawtunes.__version__}')" 2>/dev/null || echo "  clawtunes: not installed"

# Release helper: update versions, commit, tag, and push
release VERSION:
    #!/usr/bin/env bash
    set -euo pipefail

    VERSION="{{VERSION}}"
    RELEASE_BRANCH="release-${VERSION#v}"

    if [[ -z "${VERSION}" ]]; then
        echo "❌ Version is required (e.g., v0.1.1)"
        exit 1
    fi

    if ! [[ "${VERSION}" =~ ^v?[0-9]+\.[0-9]+\.[0-9]+$ ]]; then
        echo "❌ Version must look like v0.1.1 or 0.1.1"
        exit 1
    fi

    if [[ -n "$(git status --porcelain)" ]]; then
        echo "❌ Working tree is not clean. Commit or stash changes before releasing."
        exit 1
    fi

    if git rev-parse "refs/tags/${VERSION}" >/dev/null 2>&1; then
        echo "❌ Tag ${VERSION} already exists."
        exit 1
    fi

    if git show-ref --verify --quiet "refs/heads/${RELEASE_BRANCH}"; then
        echo "❌ Branch ${RELEASE_BRANCH} already exists locally."
        exit 1
    fi

    if git ls-remote --exit-code --heads origin "${RELEASE_BRANCH}" >/dev/null 2>&1; then
        echo "❌ Branch ${RELEASE_BRANCH} already exists on origin."
        exit 1
    fi

    echo "🌿 Creating release branch ${RELEASE_BRANCH}..."
    git checkout -b "${RELEASE_BRANCH}"

    echo "🔖 Updating version to ${VERSION}..."
    # Update version in pyproject.toml
    sed -i '' "s/^version = \".*\"/version = \"${VERSION#v}\"/" pyproject.toml
    # Update version in __init__.py
    sed -i '' "s/^__version__ = \".*\"/__version__ = \"${VERSION#v}\"/" src/clawtunes/__init__.py

    git status --short

    echo "✅ Committing release..."
    git commit -am "chore: release ${VERSION}"

    echo "🏷️  Tagging ${VERSION}..."
    git tag -a "${VERSION}" -m "Release ${VERSION}"

    echo "🚀 Pushing branch and tag..."
    git push origin "${RELEASE_BRANCH}"
    git push origin "${VERSION}"

    echo "🎉 Release ${VERSION} created and pushed."
