# Contributing to Cluster Tester

Thank you for your interest in contributing to the Cluster Tester project! This document provides guidelines and information for contributors.

## Table of Contents

1. [Getting Started](#getting-started)
2. [Development Setup](#development-setup)
3. [Contribution Guidelines](#contribution-guidelines)
4. [Code Standards](#code-standards)
5. [Testing](#testing)
6. [Documentation](#documentation)
7. [Pull Request Process](#pull-request-process)

## Getting Started

### Types of Contributions

We welcome several types of contributions:

-   **Bug Reports**: Report issues you encounter
-   **Feature Requests**: Suggest new functionality
-   **Code Contributions**: Implement new features or fix bugs
-   **Documentation**: Improve or expand documentation
-   **Test Cases**: Add new test case implementations
-   **Performance Improvements**: Optimize existing code

### Before Contributing

1. Check existing [issues](../../issues) to avoid duplicates
2. Read through the documentation to understand the project
3. Set up the development environment
4. Familiarize yourself with the codebase architecture

## Development Setup

### Prerequisites

-   Python 3.8 or higher
-   Git
-   Docker (for testing application)
-   Virtual environment tools

### Environment Setup

```bash
# Clone the repository
git clone https://github.com/your-username/cluster-tester.git
cd cluster-tester

# Create and activate virtual environment
python3 -m venv .venv
source .venv/bin/activate

# Install development dependencies
pip install -r requirements.txt

# Install in development mode
pip install -e .
```

### Development Dependencies

For development work, install additional tools:

```bash
# Code formatting and linting
pip install black isort flake8 mypy

# Testing framework
pip install pytest pytest-asyncio pytest-cov

# Documentation tools
pip install sphinx sphinx-rtd-theme

# Pre-commit hooks
pip install pre-commit
pre-commit install
```

### Running Tests

```bash
# Run all tests
python -m pytest

# Run with coverage
python -m pytest --cov=src

# Run specific test file
python -m pytest tests/test_benchmark_service.py

# Run integration tests
python -m pytest tests/integration/
```

### Development Workflow

1. **Create a feature branch**

    ```bash
    git checkout -b feature/your-feature-name
    ```

2. **Make your changes**

    - Follow code standards (see below)
    - Add tests for new functionality
    - Update documentation as needed

3. **Test your changes**

    ```bash
    # Run tests
    python -m pytest

    # Run linting
    flake8 src/

    # Format code
    black src/
    isort src/
    ```

4. **Commit your changes**

    ```bash
    git add .
    git commit -m "feat: add new test case for database operations"
    ```

5. **Push and create pull request**
    ```bash
    git push origin feature/your-feature-name
    ```

## Contribution Guidelines

### Bug Reports

When reporting bugs, please include:

-   **Environment details**: OS, Python version, dependency versions
-   **Steps to reproduce**: Clear, minimal reproduction steps
-   **Expected behavior**: What you expected to happen
-   **Actual behavior**: What actually happened
-   **Error messages**: Complete error messages and stack traces
-   **Configuration**: Sanitized configuration files (remove sensitive data)

**Bug Report Template:**

```markdown
## Bug Description

Brief description of the issue

## Environment

-   OS: [e.g., Ubuntu 20.04]
-   Python: [e.g., 3.12.0]
-   Cluster Tester Version: [e.g., 1.2.0]

## Steps to Reproduce

1. Step one
2. Step two
3. Step three

## Expected Behavior

What you expected to happen

## Actual Behavior

What actually happened

## Error Messages
```

Error message here

```

## Additional Context
Any additional information that might help
```

### Feature Requests

For new features, please provide:

-   **Use case**: Why this feature would be useful
-   **Proposed solution**: How you think it should work
-   **Alternatives considered**: Other approaches you've considered
-   **Implementation notes**: Any technical considerations

### Code Contributions

#### Areas Where Help is Needed

-   **New Test Cases**: Implement additional test scenarios
-   **Performance Optimization**: Improve request timing accuracy
-   **Monitoring Enhancements**: Add more system metrics
-   **Visualization**: Create new chart types and analysis views
-   **Documentation**: Improve examples and tutorials
-   **Error Handling**: Improve robustness and error messages

#### Guidelines for Code Changes

1. **Keep changes focused**: One feature/fix per pull request
2. **Follow existing patterns**: Maintain consistency with existing code
3. **Add tests**: Include unit tests for new functionality
4. **Update documentation**: Update relevant documentation
5. **Consider backwards compatibility**: Avoid breaking existing APIs

## Code Standards

### Python Style Guide

We follow PEP 8 with some modifications:

```python
# Maximum line length: 100 characters
# Use double quotes for strings
# Use type hints for function signatures

# Good example:
async def execute_test(
    self,
    tests_per_second: int,
    duration_seconds: int,
    load: int,
    test_case: TestCase
) -> TestExecution:
    """Execute a performance test with specified parameters."""
    pass
```

### Documentation Standards

-   Use clear, concise language
-   Include code examples for complex features
-   Document all public APIs
-   Use proper Markdown formatting
-   Include type hints in code examples

**Docstring Example:**

```python
async def find_max_acceptable_load(
    self,
    test_case: TestCase,
    request_per_second: int,
    max_avg_response_time: float,
    rest_time: int = 0
) -> TestExecution:
    """
    Find the maximum load that maintains acceptable response times.

    Args:
        test_case: The test case to execute
        request_per_second: Fixed request rate to use
        max_avg_response_time: Response time threshold in seconds
        rest_time: Rest time between test iterations in seconds

    Returns:
        TestExecution object representing the highest acceptable load

    Raises:
        ValueError: If no acceptable load is found
        ConnectionError: If unable to connect to test target

    Example:
        >>> service = TestExecutionService(cluster_service)
        >>> test_case = FibonacciTest("http://localhost:8080")
        >>> result = await service.find_max_acceptable_load(
        ...     test_case=test_case,
        ...     request_per_second=10,
        ...     max_avg_response_time=2.0
        ... )
        >>> print(f"Max load: {result.get_load()}")
    """
```

## Testing

### Test Structure

```
tests/
├── unit/                 # Unit tests for individual components
│   ├── test_test_case.py
│   ├── test_benchmark_service.py
│   └── test_data_analysis.py
├── integration/          # Integration tests
│   ├── test_full_benchmark.py
│   └── test_cluster_monitoring.py
└── fixtures/            # Test data and fixtures
    ├── sample_config.json
    └── sample_results.json
```

## Documentation

### Types of Documentation

1. **API Documentation**: In-code docstrings
2. **User Guides**: How-to guides and tutorials
3. **Reference**: Comprehensive API reference
4. **Architecture**: System design and implementation details

### Documentation Tools

We use Sphinx for documentation generation:

```bash
# Install documentation dependencies
pip install sphinx sphinx-rtd-theme

# Generate documentation
cd docs/
make html

# View documentation
open _build/html/index.html
```

### Documentation Structure

```
docs/
├── conf.py              # Sphinx configuration
├── index.rst            # Main documentation index
├── user-guide/          # User-facing documentation
├── api-reference/       # Generated API docs
├── examples/            # Code examples
└── contributing.md      # This file
```

### Writing Documentation

-   Use clear, step-by-step instructions
-   Include working code examples
-   Test all code examples
-   Use consistent terminology
-   Include screenshots for UI elements

## Pull Request Process

### Before Submitting

1. **Update documentation**

    - Update relevant user documentation
    - Add docstrings to new functions
    - Update API reference if needed

2. **Add changelog entry**

    ```markdown
    # Changelog

    ## [Unreleased]

    ### Added

    -   New test case for database operations

    ### Fixed

    -   Issue with request timing at high loads
    ```

### Pull Request Template

```markdown
## Description

Brief description of changes

## Type of Change

-   [ ] Bug fix
-   [ ] New feature
-   [ ] Breaking change
-   [ ] Documentation update

## Testing

-   [ ] Unit tests added/updated
-   [ ] Integration tests added/updated
-   [ ] Manual testing completed

## Checklist

-   [ ] Code follows project style guidelines
-   [ ] Self-review completed
-   [ ] Documentation updated
-   [ ] Tests added for new functionality
-   [ ] All tests pass
```

### Review Process

1. **Automated checks**: All CI checks must pass
2. **Code review**: At least one maintainer review required
3. **Testing**: Reviewers may test changes locally
4. **Documentation review**: Ensure documentation is clear and complete

### After Merge

-   Your feature branch will be deleted
-   Changes will be included in the next release
-   You'll be credited in the changelog

## Development Tips

### Debugging

```python
# Add debug logging
import logging
logging.basicConfig(level=logging.DEBUG)

# Use async debugging tools
import asyncio
asyncio.get_event_loop().set_debug(True)

# Profile performance
import cProfile
cProfile.run('your_function()', 'profile.prof')
```

### Common Patterns

#### Adding a New Test Case

1. Create new file in `src/`: `my_test_case.py`
2. Implement `TestCase` interface
3. Add to `cli.py` in `parse_test_case` function
4. Add unit tests
5. Update documentation

#### Adding a New Analysis Type

1. Add method to `DataAnalysisService`
2. Add case to CLI analysis type handling
3. Add visualization if needed
4. Add tests and documentation

#### Working with Async Code

```python
# Always use async/await for I/O operations
async with httpx.AsyncClient() as client:
    response = await client.get(url)

# Use asyncio.gather for concurrent operations
results = await asyncio.gather(*tasks, return_exceptions=True)

# Handle async exceptions properly
try:
    result = await async_operation()
except asyncio.TimeoutError:
    logging.warning("Operation timed out")
```

## Getting Help

### Communication Channels

-   **GitHub Issues**: For bugs and feature requests
-   **GitHub Discussions**: For questions and general discussion
-   **Documentation**: Start with the docs in this repository

### Maintainer Response Times

-   **Bug reports**: Usually within 48 hours
-   **Feature requests**: Within one week
-   **Pull requests**: Within one week for initial review

### Code Review Guidelines

When reviewing code, we look for:

-   **Correctness**: Does the code work as intended?
-   **Performance**: Are there any performance implications?
-   **Maintainability**: Is the code easy to understand and modify?
-   **Testing**: Are there adequate tests?
-   **Documentation**: Is new functionality properly documented?

Thank you for contributing to Cluster Tester! Your contributions help make performance testing more accessible and effective for everyone.
