# Cluster Tester Documentation

Welcome to the Cluster Tester documentation! This tool helps you benchmark and analyze the performance of distributed server applications across multiple cluster environments.

```{toctree}
:maxdepth: 2
:caption: User Guide

README
EXAMPLES
```

```{toctree}
:maxdepth: 2
:caption: Reference Configuration

reference_configuration/k3s
reference_configuration/k0s
reference_configuration/microk8s
```

```{toctree}
:maxdepth: 2
:caption: Technical Documentation

ARCHITECTURE
API_REFERENCE
```

```{toctree}
:maxdepth: 2
:caption: Development

CONTRIBUTING
```

```{toctree}
:maxdepth: 2
:caption: API Documentation

api/modules
```

## Quick Start

Get started with Cluster Tester in just a few commands:

```bash
# Set up environment
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt

# Deploy test application
docker-compose up -d

# Configure cluster
cp db/config_example.json db/config.json
# Edit db/config.json with your server details

# Run benchmark
python3 src/ benchmark
```

## Features

-   **🏗️ Distributed Load Testing**: Test applications across multiple servers simultaneously
-   **📊 Real-time Monitoring**: Monitor CPU, RAM, and network performance during tests
-   **🧮 Adaptive Load Discovery**: Automatically find optimal performance characteristics
-   **📈 Comprehensive Analysis**: Generate detailed reports with statistical visualizations
-   **☸️ Kubernetes Integration**: Built-in support for K3s, K0s, and MicroK8s
-   **🔧 Flexible Configuration**: JSON-based configuration for easy setup

## Architecture Overview

```{mermaid}
graph TB
    CLI[CLI Interface] --> BS[Benchmark Service]
    CLI --> TES[Test Execution Service]
    CLI --> DAS[Data Analysis Service]

    BS --> TES
    TES --> TC[Test Cases]
    TES --> CS[Cluster Service]

    CS --> SSH[SSH Monitoring]
    TC --> HTTP[HTTP Client]

    DAS --> VIZ[Visualizations]
    DAS --> STATS[Statistics]

    SSH --> SERVERS[Target Servers]
    HTTP --> APP[Test Application]
```

## Test Cases

### Built-in Test Cases

-   **Fibonacci Test**: Recursive computation performance (exponential complexity)
-   **Bubble Sort Test**: Array sorting performance (quadratic complexity)

### Custom Test Cases

Easily implement your own test cases by extending the `TestCase` abstract base class:

```python
from test_case import TestCase
from test_result import TestResult

class MyCustomTest(TestCase):
    async def run(self, load: int) -> TestResult:
        # Your test implementation here
        pass
```

## Supported Platforms

-   **Operating Systems**: Linux (Ubuntu, CentOS, RHEL, etc.)
-   **Python Versions**: 3.8+
-   **Kubernetes Distributions**: K3s, K0s, MicroK8s
-   **Container Platforms**: Docker, Podman

## Getting Help

-   **📖 Documentation**: Start with this documentation
-   **🐛 Issues**: Report bugs on [GitHub Issues](https://github.com/FaboBorgesLima/cluster-tester/issues)
-   **💬 Discussions**: Join discussions on [GitHub Discussions](https://github.com/FaboBorgesLima/cluster-tester/discussions)

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Indices and Tables

-   {ref}`genindex`
-   {ref}`modindex`
-   {ref}`search`
