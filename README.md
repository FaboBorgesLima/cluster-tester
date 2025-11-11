# Cluster Tester - Distributed Server Benchmarking Tool

A comprehensive Python-based benchmarking tool designed to test the performance of distributed server applications and analyze their resource usage across multiple cluster environments.

## Features

-   **Distributed Load Testing**: Test applications across multiple servers simultaneously
-   **Real-time Monitoring**: Monitor CPU, RAM, and network performance during tests
-   **Multiple Test Cases**: Built-in support for Fibonacci and Bubble Sort computational tests
-   **Comprehensive Analysis**: Generate detailed reports with visualizations
-   **Kubernetes Support**: Deploy test applications to Kubernetes clusters
-   **Flexible Configuration**: JSON-based configuration for easy setup

## Table of Contents

1. [Quick Start](#quick-start)
2. [Installation](#installation)
3. [Configuration](#configuration)
4. [Usage](#usage)
5. [Test Cases](#test-cases)
6. [Data Analysis](#data-analysis)
7. [Architecture](#architecture)
8. [API Reference](#api-reference)

## Quick Start

### 1. Environment Setup

```bash
# Create and activate virtual environment
python3 -m venv .venv
source .venv/bin/activate

# Install dependencies
pip install -r requirements.txt
```

### 2. Deploy Test Application

The application provides a Node.js test server with computational endpoints:

```bash
# Using Docker Compose (recommended)
docker-compose up -d

# Or deploy to Kubernetes
kubectl apply -f kubernetes/deploy.yaml
```

### 3. Configuration

```bash
# Copy example configuration
cp db/config_example.json db/config.json

# Edit configuration
nano db/config.json
```

### 4. Run Your First Benchmark

```bash
# Run a full benchmark suite
python3 src/ benchmark

# Run a single test execution
python3 src/ test-execution --test-cases fibonacci --load 15 --requests-per-second 10

# Analyze results
python3 src/ data-analysis response-time-compare --files benchmark1.json benchmark2.json --load 15
```

## Installation

### Prerequisites

-   Python 3.8+
-   Docker (optional, for test application)
-   SSH access to target servers
-   Network connectivity between tester and target servers

### Dependencies

The tool uses several key Python libraries:

-   `httpx` - Async HTTP client for load testing
-   `matplotlib` - Data visualization
-   `numpy` - Statistical analysis
-   `paramiko` - SSH connections for server monitoring
-   `server_system_monitor` - Custom server monitoring library

Install all dependencies:

```bash
pip install -r requirements.txt
```

## Configuration

### Basic Configuration (`db/config.json`)

```json
{
    "app": {
        "name": "My Application Cluster",
        "url": "http://localhost:8080"
    },
    "monitorServers": [
        {
            "name": "Server 1",
            "host": "192.168.1.100",
            "port": 22,
            "sshAuthMethod": "password",
            "authentication": {
                "username": "root",
                "password": "your-password"
            }
        },
        {
            "name": "Server 2",
            "host": "192.168.1.101",
            "port": 22,
            "sshAuthMethod": "password",
            "authentication": {
                "username": "root",
                "password": "your-password"
            }
        }
    ]
}
```

### Configuration Parameters

-   **app.name**: Friendly name for your application cluster
-   **app.url**: Base URL of the application to test
-   **monitorServers**: Array of servers to monitor during tests
    -   **host**: Server IP address or hostname
    -   **port**: SSH port (usually 22)
    -   **authentication**: SSH credentials

## Usage

The tool provides three main services:

### 1. Benchmark Service

Runs comprehensive performance benchmarks to find optimal load parameters.

```bash
# Full benchmark with default settings
python3 src/ benchmark

# Custom benchmark parameters
python3 src/ benchmark \
    --test-cases fibonacci bubble-sort \
    --max-response-time 1.5 \
    --duration-per-test 60 \
    --max-n-loads-to-test 5 \
    --rest-time 10
```

**Benchmark Parameters:**

-   `--test-cases`: Test cases to run (fibonacci, bubble-sort)
-   `--max-response-time`: Maximum acceptable response time in seconds
-   `--duration-per-test`: Duration of each test in seconds
-   `--max-n-loads-to-test`: Number of different loads to test
-   `--min-requests-per-second`: Minimum requests per second to test
-   `--rest-time`: Rest time between tests in seconds

### 2. Test Execution Service

Runs individual test executions with specific parameters.

```bash
# Single test execution
python3 src/ test-execution \
    --test-cases fibonacci \
    --load 15 \
    --requests-per-second 25 \
    --duration-per-test 30 \
    --monitoring-interval 1.0
```

**Test Execution Parameters:**

-   `--load`: Computational load to apply
-   `--requests-per-second`: Number of requests per second
-   `--duration-per-test`: Test duration in seconds
-   `--monitoring-interval`: Server monitoring interval in seconds

### 3. Data Analysis Service

Analyzes benchmark results and generates visualizations.

```bash
# Response time analysis
python3 src/ data-analysis avg-response-time --files benchmark1.json

# CPU usage comparison
python3 src/ data-analysis cpu-usage-compare \
    --files k3s-benchmark.json k0s-benchmark.json microk8s-benchmark.json \
    --load 15 \
    --benchmark-names k3s k0s microk8s \
    --alias-hosts "192.168.1.100:master,192.168.1.101:worker"

# RAM usage comparison
python3 src/ data-analysis ram-usage-compare \
    --files benchmark1.json benchmark2.json \
    --load 15 \
    --benchmark-names test1 test2

# Response time violin plot
python3 src/ data-analysis response-time-compare \
    --files benchmark1.json benchmark2.json benchmark3.json \
    --load 15 \
    --benchmark-names k3s k0s microk8s
```

**Analysis Types:**

-   `avg-response-time`: Average response time per load
-   `min-response-time`: Minimum response time per load
-   `max-response-time`: Maximum response time per load
-   `ram-usage`: RAM usage analysis per server
-   `cpu-usage`: CPU usage analysis per server
-   `cpu-usage-compare`: CPU comparison across benchmarks
-   `ram-usage-compare`: RAM comparison across benchmarks
-   `response-time-compare`: Response time distribution comparison

## Test Cases

### Built-in Test Cases

#### 1. Fibonacci Test

Tests recursive computation performance.

-   **Endpoint**: `/fibonacci/{n}`
-   **Load Parameter**: Fibonacci number to calculate (n)
-   **Characteristics**: CPU-intensive, exponential complexity
-   **Minimum Recommended Load**: 10

#### 2. Bubble Sort Test

Tests array sorting performance.

-   **Endpoint**: `/bubble-sort?n={size}`
-   **Load Parameter**: Array size (2^load)
-   **Characteristics**: Memory and CPU intensive, O(n²) complexity
-   **Minimum Recommended Load**: 10

### Creating Custom Test Cases

Implement the `TestCase` abstract base class:

```python
from test_case import TestCase
from test_result import TestResult
import httpx
import datetime
from timespan import Timespan

class CustomTest(TestCase):
    def __init__(self, application_base_url: str):
        super().__init__(
            name="CustomTestCase",
            description="Description of your test case",
            application_base_url=application_base_url,
            min_recommended_load=5
        )

    async def run(self, load: int) -> TestResult:
        async with httpx.AsyncClient(timeout=30.0) as client:
            start_request = datetime.datetime.now(datetime.timezone.utc)
            response = await client.get(f'{self._application_base_url}/your-endpoint/{load}')
            end_request = datetime.datetime.now(datetime.timezone.utc)

            # Parse server-side timing from response
            start_server = datetime.datetime.fromisoformat(response.json().get('start'))
            end_server = datetime.datetime.fromisoformat(response.json().get('end'))

            return TestResult(
                test_case_name=self.get_name(),
                request_span=Timespan(start_request, end_request),
                server_processing_span=Timespan(start_server, end_server),
                load=load
            )
```

## Data Analysis

### Generated Reports

The tool generates several types of visualizations:

#### 1. CPU Usage Comparison

-   **File**: `cpu_usage_comparison_load_{load}_files_{names}.png`
-   **Shows**: CPU utilization across different systems
-   **Use Case**: Compare infrastructure performance

#### 2. RAM Usage Comparison

-   **File**: `ram_usage_comparison_load_{load}_{names}.png`
-   **Shows**: Memory consumption across systems
-   **Use Case**: Identify memory bottlenecks

#### 3. Response Time Violin Plots

-   **File**: `response_time_load_{load}_{names}.png`
-   **Shows**: Response time distributions with quartiles
-   **Use Case**: Understand response time variability

### Statistical Metrics

For each benchmark, the following metrics are collected:

-   **Response Time**: Client-side request duration
-   **Server Processing Time**: Server-side computation time
-   **CPU Usage**: Per-server CPU utilization (usr, sys, idle)
-   **RAM Usage**: Memory consumption per server
-   **Network Latency**: Ping times to each server
-   **Error Rate**: Failed requests and exceptions

## Architecture

### Core Components

#### 1. Test Execution Engine

-   **TestExecutionService**: Orchestrates test execution
-   **TestCase**: Abstract base for test implementations
-   **TestResult**: Individual test result container

#### 2. Cluster Management

-   **ClusterService**: Manages server connections and monitoring
-   **Cluster**: Represents a group of servers
-   **ServerStats**: Individual server metrics

#### 3. Benchmark Engine

-   **BenchmarkService**: Runs comprehensive benchmarks
-   **Benchmark**: Contains multiple test executions
-   **BackgroundClusterMonitoring**: Real-time server monitoring

#### 4. Data Analysis

-   **DataAnalysisService**: Statistical analysis and visualization
-   **JsonStorageService**: Result persistence

### Data Flow

1. **Configuration**: Load cluster and application settings
2. **Test Execution**: Run tests with real-time monitoring
3. **Data Collection**: Gather performance metrics
4. **Storage**: Save results in JSON format
5. **Analysis**: Generate statistics and visualizations

## API Reference

### Command Line Interface

```bash
python3 src/ <service> [options] [analysis_type]
```

### Services

#### benchmark

Runs comprehensive performance benchmarks.

**Options:**

-   `--max-response-time FLOAT`: Maximum acceptable response time (default: 2.0)
-   `--duration-per-test INT`: Test duration in seconds (default: 30)
-   `--max-n-loads-to-test INT`: Number of loads to test (default: 3)
-   `--min-requests-per-second INT`: Minimum RPS (default: 1)
-   `--rest-time INT`: Rest between tests (default: 30)

#### test-execution

Runs single test with specified parameters.

**Options:**

-   `--load INT`: Computational load (default: 1)
-   `--requests-per-second INT`: Requests per second (default: 1)
-   `--duration-per-test INT`: Test duration (default: 30)
-   `--monitoring-interval FLOAT`: Monitoring interval (default: 0.5)

#### data-analysis

Analyzes benchmark results.

**Analysis Types:**

-   `avg-response-time`: Average response times
-   `cpu-usage-compare`: CPU usage comparison
-   `ram-usage-compare`: RAM usage comparison
-   `response-time-compare`: Response time distributions

**Options:**

-   `--files LIST`: Benchmark files to analyze
-   `--load INT`: Load level for comparison
-   `--benchmark-names LIST`: Names for comparison
-   `--alias-hosts LIST`: Host aliases (format: `host:alias`)

### Global Options

-   `--storage PATH`: Storage directory (default: `../db/`)
-   `--config FILE`: Configuration file (default: `config.json`)
-   `--test-cases LIST`: Test cases to run (default: `fibonacci bubble-sort`)

## Examples

### Comparing Kubernetes Distributions

```bash
# Run benchmarks on different K8s distributions
python3 src/ benchmark --config k3s-config.json
python3 src/ benchmark --config k0s-config.json
python3 src/ benchmark --config microk8s-config.json

# Compare CPU performance
python3 src/ data-analysis cpu-usage-compare \
    --files k3s-*-benchmark.json k0s-*-benchmark.json microk8s-*-benchmark.json \
    --load 15 \
    --benchmark-names k3s k0s microk8s \
    --alias-hosts "10.0.1.100:master-node,10.0.1.101:worker-1"

# Compare response times
python3 src/ data-analysis response-time-compare \
    --files k3s-*-benchmark.json k0s-*-benchmark.json microk8s-*-benchmark.json \
    --load 15 \
    --benchmark-names k3s k0s microk8s
```

### Performance Tuning Workflow

```bash
# 1. Run baseline benchmark
python3 src/ benchmark --max-response-time 1.0 --duration-per-test 60

# 2. Test specific configuration
python3 src/ test-execution --load 20 --requests-per-second 50 --duration-per-test 120

# 3. Compare before/after
python3 src/ data-analysis cpu-usage-compare \
    --files baseline-benchmark.json tuned-benchmark.json \
    --load 20 \
    --benchmark-names "Before" "After"
```

### CI/CD Integration

```bash
# Performance regression test
python3 src/ test-execution \
    --test-cases fibonacci \
    --load 15 \
    --requests-per-second 25 \
    --duration-per-test 60

# Exit with error if average response time > threshold
python3 -c "
import json
data = json.load(open('db/latest_test_execution.json'))
avg_time = sum(r['server_processing_span'] for r in data['results']) / len(data['results'])
exit(1 if avg_time > 2.0 else 0)
"
```

## Troubleshooting

### Common Issues

#### High Request Rates (>48 RPS)

The Python asyncio implementation may struggle with precise timing at very high request rates, causing delays. Consider:

-   Using lower request rates with longer durations
-   Implementing the core in Rust, Go, or C++ for better performance
-   Using multiple parallel processes

#### SSH Connection Failures

-   Verify SSH credentials and network connectivity
-   Ensure SSH service is running on target servers
-   Check firewall rules and port accessibility

#### Memory Issues

-   Monitor Python process memory usage during large tests
-   Reduce monitoring interval for long-running tests
-   Consider processing results in batches

### Performance Optimization

-   Use SSD storage for result files
-   Run tests from servers close to the target cluster
-   Minimize background processes during benchmarking
-   Use dedicated network interfaces for monitoring traffic

## Contributing

1. Fork the repository
2. Create a feature branch
3. Implement your changes
4. Add tests for new functionality
5. Update documentation
6. Submit a pull request

## License

This project is open source and available under the MIT License.
