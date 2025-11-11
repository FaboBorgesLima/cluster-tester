# Cluster Tester Documentation

This directory contains the comprehensive documentation for the Cluster Tester project, built using [Sphinx](https://www.sphinx-doc.org/) with the [Read the Docs theme](https://sphinx-rtd-theme.readthedocs.io/).

## 📖 Documentation Structure

```
docs/
├── conf.py                     # Sphinx configuration
├── index.rst                   # Main documentation index
├── Makefile                    # Build automation (Unix)
├── make.bat                    # Build automation (Windows)
├── requirements.txt            # Documentation dependencies
├── _static/                    # Static files (CSS, images)
│   └── custom.css             # Custom styling
├── _templates/                 # Custom templates (auto-created)
├── api/                       # Auto-generated API documentation
│   ├── modules.rst
│   └── cluster_tester.rst
└── reference_configuration/   # Kubernetes setup guides
    ├── k3s.md                 # K3s installation and configuration
    ├── k0s.md                 # K0s installation and configuration
    └── microk8s.md           # MicroK8s installation and configuration
```

## 🚀 Quick Start

### Prerequisites

Install the documentation dependencies:

```bash
# From the root project directory
pip install -r docs/requirements.txt
```

### Building Documentation

```bash
# Navigate to docs directory
cd docs/

# Generate API documentation and build HTML
make clean && make api-docs && make html

# Or build everything at once
make all

# Open documentation in browser
make html-open
```

### Development Mode

For live-reloading during documentation development:

```bash
# Start development server with auto-reload
make livehtml

# Documentation will be available at http://localhost:8000
# Changes to .rst/.md files will trigger automatic rebuilds
```

## 📋 Available Build Targets

| Command          | Description                                 |
| ---------------- | ------------------------------------------- |
| `make html`      | Build HTML documentation                    |
| `make html-open` | Build HTML and open in browser              |
| `make livehtml`  | Start development server with auto-reload   |
| `make latexpdf`  | Build PDF documentation (requires LaTeX)    |
| `make api-docs`  | Generate API documentation from source code |
| `make clean`     | Clean build directory                       |
| `make check`     | Run documentation tests and link checking   |
| `make all`       | Clean, generate API docs, and build HTML    |

## 📝 Documentation Files

### Core Documentation

-   **[README.md](../README.md)**: Main project documentation
-   **[EXAMPLES.md](EXAMPLES.md)**: Practical usage examples
-   **[API_REFERENCE.md](API_REFERENCE.md)**: Detailed API reference
-   **[ARCHITECTURE.md](ARCHITECTURE.md)**: System architecture overview
-   **[TROUBLESHOOTING.md](TROUBLESHOOTING.md)**: Common issues and solutions
-   **[CONTRIBUTING.md](CONTRIBUTING.md)**: Development and contribution guide

### Kubernetes Configuration Guides

-   **[k3s.md](reference_configuration/k3s.md)**: K3s setup with MetalLB
-   **[k0s.md](reference_configuration/k0s.md)**: K0s setup with MetalLB
-   **[microk8s.md](reference_configuration/microk8s.md)**: MicroK8s setup with MetalLB

### Auto-Generated API Documentation

The API documentation is automatically generated from Python docstrings using Sphinx's `autodoc` extension:

-   **[modules.rst](api/modules.rst)**: API modules overview
-   **[cluster_tester.rst](api/cluster_tester.rst)**: Detailed API reference

## ⚙️ Sphinx Configuration

### Key Configuration Options

The documentation is configured in [`conf.py`](conf.py) with the following key settings:

-   **Theme**: `sphinx_rtd_theme` (Read the Docs theme)
-   **Extensions**:
    -   `sphinx.ext.autodoc` - Automatic API documentation
    -   `sphinx.ext.napoleon` - Google/NumPy style docstrings
    -   `sphinx.ext.viewcode` - Source code links
    -   `myst_parser` - Markdown support
-   **Source Formats**: Both reStructuredText (`.rst`) and Markdown (`.md`)

### Custom Styling

Custom CSS is defined in [`_static/custom.css`](/_static/custom.css) and includes:

-   Improved code block styling
-   Better table formatting
-   Enhanced admonition (note/warning) styling
-   Responsive design improvements
-   Print-friendly styles

## 📖 Writing Documentation

### File Formats

The documentation supports both reStructuredText and Markdown:

```python
# conf.py
source_suffix = {
    '.rst': None,
    '.md': ,
}
```

### Adding New Pages

1. **Create the documentation file** (`.rst` or `.md`)
2. **Add to table of contents** in `index.rst`:

    ````rst
    ```{toctree}
    :maxdepth: 2

    your-new-page
    ````

3. **Rebuild documentation**: `make html`

### Docstring Style

Use Google-style docstrings for automatic API documentation:

```python
async def execute_test(self, tests_per_second: int, duration_seconds: int,
                      load: int, test_case: TestCase) -> TestExecution:
    """Execute a performance test with specified parameters.

    Args:
        tests_per_second: Number of requests to send per second
        duration_seconds: How long to run the test
        load: Load parameter to pass to test case
        test_case: TestCase instance to execute

    Returns:
        TestExecution object containing results and timing information

    Raises:
        ValueError: If tests_per_second is less than or equal to zero
        ConnectionError: If unable to connect to test target

    Example:
        >>> service = TestExecutionService(cluster_service)
        >>> test_case = FibonacciTest("http://localhost:8080")
        >>> result = await service.execute_test(
        ...     tests_per_second=10,
        ...     duration_seconds=30,
        ...     load=15,
        ...     test_case=test_case
        ... )
    """
```

## 🔧 Advanced Features

### Cross-References

Link to other documentation sections:

```rst
See the :doc:`EXAMPLES` for practical usage examples.
See :ref:`installation-guide` for setup instructions.
```

### Code Highlighting

Specify language for syntax highlighting:

```rst
.. code-block:: python
   :linenos:

   async def example_function():
       return "Hello World"
```

### Admonitions

Use admonitions for important information:

```rst
.. note::
   This is a note.

.. warning::
   This is a warning.

.. tip::
   This is a tip.
```

### Including External Files

Include code files directly:

```rst
.. literalinclude:: ../src/example.py
   :language: python
   :lines: 10-20
```

## 🌐 Publishing Documentation

### GitHub Pages

To publish on GitHub Pages:

1. **Build documentation**: `make html`
2. **Copy to gh-pages branch**:
    ```bash
    git checkout gh-pages
    cp -r _build/html/* .
    git add .
    git commit -m "Update documentation"
    git push origin gh-pages
    ```

### Read the Docs

To publish on [Read the Docs](https://readthedocs.org/):

1. **Connect your GitHub repository** to Read the Docs
2. **Configure build settings**:
    - Python version: 3.8+
    - Requirements file: `docs/requirements.txt`
    - Documentation type: Sphinx
3. **Build automatically** on every commit

### Netlify

For Netlify deployment:

```bash
# Build command
cd docs && make html

# Publish directory
docs/_build/html
```

## 📊 Documentation Analytics

### Link Checking

Check for broken links:

```bash
make linkcheck
```

### Coverage Reports

Generate documentation coverage reports:

```bash
sphinx-build -b coverage . _build/coverage
```

## 🐛 Troubleshooting

### Common Issues

**Sphinx not found:**

```bash
pip install sphinx sphinx-rtd-theme
```

**Module import errors:**

```bash
# Ensure source code is in Python path
export PYTHONPATH="${PYTHONPATH}:../src"
```

**Missing dependencies:**

```bash
pip install -r docs/requirements.txt
```

**Build errors:**

```bash
# Clean build directory
make clean

# Rebuild from scratch
make all
```

### Build Warnings

Common warnings and fixes:

-   **"document isn't included in any toctree"**: Add file to `index.rst` toctree
-   **"undefined label"**: Check cross-reference syntax
-   **"duplicate target name"**: Ensure unique section headers

## 📚 Resources

-   [Sphinx Documentation](https://www.sphinx-doc.org/)
-   [Read the Docs Theme](https://sphinx-rtd-theme.readthedocs.io/)
-   [MyST Parser](https://myst-parser.readthedocs.io/) (Markdown support)
-   [reStructuredText Primer](https://www.sphinx-doc.org/en/master/usage/restructuredtext/basics.html)
-   [Sphinx Extensions](https://www.sphinx-doc.org/en/master/usage/extensions/index.html)

## 🤝 Contributing to Documentation

1. **Follow the style guide** for consistency
2. **Test your changes** with `make html`
3. **Check for broken links** with `make check`
4. **Update API documentation** when adding new code
5. **Include examples** for new features

For detailed contribution guidelines, see [CONTRIBUTING.md](CONTRIBUTING.md).
