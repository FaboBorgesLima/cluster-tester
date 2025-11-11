# API Reference

This document provides detailed information about the Cluster Tester's internal APIs and interfaces.

## Table of Contents

1. [Command Line Interface](#command-line-interface)
2. [Core Classes](#core-classes)
3. [Test Case Interface](#test-case-interface)
4. [Data Structures](#data-structures)
5. [Configuration Schema](#configuration-schema)
6. [Result File Formats](#result-file-formats)

## Command Line Interface

### Main Command Structure

```bash
python3 src/ <service> [global_options] [service_options] [analysis_type]
```

### Services

#### benchmark

Runs comprehensive performance benchmarks to determine optimal performance characteristics.

**Syntax:**

```bash
python3 src/ benchmark [options]
```

**Options:**

-   `--max-response-time FLOAT` - Maximum acceptable average response time in seconds (default: 2.0)
-   `--duration-per-test INT` - Duration of each individual test in seconds (default: 30)
-   `--max-n-loads-to-test INT` - Maximum number of different load levels to test (default: 3)
-   `--min-requests-per-second INT` - Minimum requests per second to start testing with (default: 1)
-   `--rest-time INT` - Rest time between tests in seconds (default: 30)

**Output:**

-   JSON files in format: `{cluster-name}-{test-case}-{timestamp}_benchmark.json`

#### test-execution

Runs a single test execution with specific parameters.

**Syntax:**

```bash
python3 src/ test-execution [options]
```

**Options:**

-   `--load INT` - Computational load parameter to pass to test case (default: 1)
-   `--requests-per-second INT` - Number of requests per second to generate (default: 1)
-   `--duration-per-test INT` - Duration of the test in seconds (default: 30)
-   `--monitoring-interval FLOAT` - Interval between server monitoring snapshots in seconds (default: 0.5)

**Output:**

-   JSON files in format: `{timestamp}_test_execution.json`

#### data-analysis

Analyzes benchmark results and generates visualizations.

**Syntax:**

```bash
python3 src/ data-analysis <analysis_type> [options]
```

**Analysis Types:**

##### avg-response-time

Calculates average response times across different load levels.

**Options:**

-   `--files LIST` - Required. List of benchmark JSON files to analyze

**Output:**

-   Console output with average response times per load level

##### min-response-time / max-response-time

Calculates minimum/maximum response times across load levels.

**Options:**

-   `--files LIST` - Required. List of benchmark JSON files to analyze

**Output:**

-   Console output with min/max response times per load level

##### ram-usage / cpu-usage

Analyzes RAM or CPU usage from benchmark results.

**Options:**

-   `--files LIST` - Required. List of benchmark JSON files to analyze

**Output:**

-   Console output with resource usage per host and load level

##### cpu-usage-compare / ram-usage-compare

Compares CPU/RAM usage across multiple benchmarks.

**Options:**

-   `--files LIST` - Required. List of benchmark JSON files to compare
-   `--load INT` - Required. Load level to compare across benchmarks
-   `--benchmark-names LIST` - Optional. Custom names for benchmarks in visualization
-   `--alias-hosts LIST` - Optional. Host aliases in format `original_host:alias_name`

**Output:**

-   PNG files with bar charts comparing resource usage

##### response-time-compare

Compares response time distributions across benchmarks using violin plots.

**Options:**

-   `--files LIST` - Required. List of benchmark JSON files to compare
-   `--load INT` - Required. Load level to compare across benchmarks
-   `--benchmark-names LIST` - Optional. Custom names for benchmarks in visualization

**Output:**

-   PNG files with violin plots showing response time distributions

### Global Options

These options apply to all services:

-   `--storage PATH` - Directory for storing results and configuration (default: `../db/`)
-   `--config FILE` - Configuration file name within storage directory (default: `config.json`)
-   `--test-cases LIST` - Test cases to run: `fibonacci`, `bubble-sort` (default: `fibonacci bubble-sort`)

## Core Classes

### TestExecutionService

Main service for executing performance tests.

#### Methods

##### `async execute_test(tests_per_second: int, duration_seconds: int, load: int, test_case: TestCase) -> TestExecution`

Executes a single performance test.

**Parameters:**

-   `tests_per_second` - Number of requests to send per second
-   `duration_seconds` - How long to run the test
-   `load` - Load parameter to pass to test case
-   `test_case` - TestCase instance to execute

**Returns:**

-   `TestExecution` object containing results and timing information

##### `async execute_test_while_monitoring(test_case: TestCase, request_per_second: int, duration_seconds: int, load: int, monitoring_interval: float, cluster: Cluster) -> TestExecution`

Executes a test while monitoring cluster resources.

**Parameters:**

-   All parameters from `execute_test` plus:
-   `monitoring_interval` - Seconds between monitoring snapshots
-   `cluster` - Cluster object to monitor

**Returns:**

-   `TestExecution` with additional cluster monitoring data

##### `async find_max_acceptable_load(test_case: TestCase, request_per_second: int, duration_seconds: int, max_avg_response_time: float, ...) -> TestExecution`

Finds the maximum load that maintains acceptable response times.

**Parameters:**

-   `test_case` - Test case to execute
-   `request_per_second` - Fixed request rate to use
-   `duration_seconds` - Test duration
-   `max_avg_response_time` - Response time threshold
-   `load_increment` - How much to increase load each iteration (default: 1)
-   `max_iterations` - Maximum test iterations (default: 100)
-   `rest_time` - Rest between iterations (default: 0)

**Returns:**

-   `TestExecution` representing the highest acceptable load

##### `async find_max_requests_per_second(test_case: TestCase, load: int, duration_seconds: int, max_avg_response_time: float, ...) -> TestExecution`

Finds the maximum request rate for a given load that maintains acceptable response times.

**Parameters:**

-   `test_case` - Test case to execute
-   `load` - Fixed load parameter to use
-   `duration_seconds` - Test duration
-   `max_avg_response_time` - Response time threshold
-   `max_power` - Maximum power of 2 to test (default: 10)
-   `start_power` - Starting power of 2 (default: 0)
-   `rest_time` - Rest between tests (default: 0)

**Returns:**

-   `TestExecution` representing the highest acceptable request rate

### BenchmarkService

Service for running comprehensive benchmark suites.

#### Methods

##### `async run_benchmark(test_cases: list[TestCase], cluster: Cluster, ...) -> list[Benchmark]`

Runs a complete benchmark suite across multiple test cases.

**Parameters:**

-   `test_cases` - List of test cases to execute
-   `cluster` - Cluster to test and monitor
-   `max_response_time` - Response time threshold (default: 2.0)
-   `duration_per_test` - Duration per test (default: 30)
-   `max_n_loads_to_test` - Number of loads to test (default: 3)
-   `min_requests_per_second` - Starting request rate (default: 1)
-   `rest_time` - Rest between tests (default: 30)

**Returns:**

-   List of `Benchmark` objects, one per test case

##### `async run_benchmark_single_test_case(test_case: TestCase, cluster: Cluster, ...) -> Benchmark`

Runs a benchmark for a single test case.

**Parameters:**

-   Same as `run_benchmark` but for a single test case

**Returns:**

-   Single `Benchmark` object

### ClusterService

Service for managing cluster connections and monitoring.

#### Methods

##### `async get_stats(cluster: Cluster, retries: int = 2) -> ClusterStats`

Retrieves current statistics from all servers in a cluster.

**Parameters:**

-   `cluster` - Cluster to monitor
-   `retries` - Number of retry attempts on failure

**Returns:**

-   `ClusterStats` object with current server metrics

### DataAnalysisService

Service for analyzing benchmark results and generating visualizations.

#### Methods

##### `avg_response_time_benchmark(benchmark_filename: str) -> list[dict]`

Analyzes average response times from a benchmark file.

**Parameters:**

-   `benchmark_filename` - JSON file containing benchmark results

**Returns:**

-   List of dicts with keys: `load`, `rps`, `total_response_time`, `total_requests`, `avg_response_time`

##### `cpu_usage_compare(benchmark_files: list[str], load: int, alias_hosts: dict[str,str], test_name_for_file: list[str]) -> dict`

Compares CPU usage across multiple benchmark files for a specific load.

**Parameters:**

-   `benchmark_files` - List of benchmark JSON files
-   `load` - Load level to compare
-   `alias_hosts` - Mapping of original hostnames to display aliases
-   `test_name_for_file` - Names to use for each benchmark file

**Returns:**

-   Dict mapping host aliases to benchmark data with CPU usage and RPS

##### `response_time_compare(benchmark_files: list[str], load: int, test_name_for_file: list[str]) -> dict`

Compares response time distributions across benchmarks.

**Parameters:**

-   `benchmark_files` - List of benchmark JSON files
-   `load` - Load level to compare
-   `test_name_for_file` - Names to use for each benchmark

**Returns:**

-   Dict mapping benchmark names to response time arrays and RPS data

## Test Case Interface

### TestCase (Abstract Base Class)

Base class for implementing performance test cases.

#### Abstract Methods

##### `async run(load: int) -> TestResult`

Execute the test case with the specified load.

**Parameters:**

-   `load` - Load parameter (interpretation depends on test case)

**Returns:**

-   `TestResult` object containing timing and result data

#### Constructor

```python
def __init__(name: str, description: str, application_base_url: str, min_recommended_load: int = 1)
```

**Parameters:**

-   `name` - Unique identifier for the test case
-   `description` - Human-readable description
-   `application_base_url` - Base URL of the application to test
-   `min_recommended_load` - Minimum load value that produces meaningful results

#### Methods

##### `get_name() -> str`

Returns the test case name.

##### `get_description() -> str`

Returns the test case description.

##### `get_min_recommended_load() -> int`

Returns the minimum recommended load for this test case.

##### `to_json() -> dict`

Serializes the test case configuration to a JSON-compatible dictionary.

### Built-in Test Cases

#### FibonacciTest

Tests recursive computation performance using Fibonacci calculation.

**Endpoint:** `GET /fibonacci/{n}`
**Load Parameter:** Fibonacci number to calculate
**Complexity:** Exponential - O(φⁿ) where φ is golden ratio
**Minimum Recommended Load:** 10

#### BubbleSortTest

Tests array sorting performance using bubble sort algorithm.

**Endpoint:** `GET /bubble-sort?n={size}`  
**Load Parameter:** Array size is calculated as 2^load
**Complexity:** Quadratic - O(n²)
**Minimum Recommended Load:** 10

## Data Structures

### TestResult

Represents the result of a single test case execution.

#### Properties

-   `test_case_name: str` - Name of the executed test case
-   `load: int` - Load parameter used
-   `request_span: Timespan` - Total request duration (client-side)
-   `server_processing_span: Timespan` - Server-side processing duration

#### Methods

##### `get_response_time() -> float`

Returns the total response time in seconds.

##### `to_json() -> dict`

Serializes to JSON format.

### TestExecution

Represents the results of executing a test case multiple times.

#### Properties

-   `total_span: Timespan` - Total execution duration including setup
-   `span_making_requests: Timespan` - Duration spent sending requests
-   `test_case: TestCase` - The executed test case
-   `results: list[TestResult]` - Individual test results
-   `request_per_second: int` - Request rate used
-   `seconds_making_requests: int` - Configured test duration
-   `errors: list[Exception]` - Any exceptions that occurred
-   `cluster_stats: list[ClusterStats]` - Server monitoring data

#### Methods

##### `avg_response_time() -> float`

Calculates the average response time across all results.

##### `avg_server_processing_time() -> float`

Calculates the average server processing time.

##### `get_load() -> int`

Returns the load parameter used.

##### `has_errors() -> bool`

Returns true if any errors occurred during execution.

##### `to_json() -> dict`

Full serialization including all result details.

##### `to_short_json() -> dict`

Compact serialization with summary statistics.

### Benchmark

Represents a complete benchmark suite for a single test case.

#### Properties

-   `test_executions: list[TestExecution]` - All test executions in the benchmark
-   `test_case: TestCase` - The test case that was benchmarked
-   `cluster: Cluster` - The cluster that was tested

#### Methods

##### `to_json() -> dict`

Full serialization.

##### `to_short_json() -> dict`

Compact serialization.

### ClusterStats

Snapshot of cluster-wide server statistics at a point in time.

#### Properties

-   `servers: list[ServerStats]` - Statistics for each server
-   `timestamp: datetime` - When the snapshot was taken

### ServerStats

Statistics for a single server.

#### Properties

-   `memory: dict` - Memory usage statistics
    -   `used: int` - Used memory in bytes
    -   `total: int` - Total memory in bytes
    -   `free: int` - Free memory in bytes
    -   `shared: int` - Shared memory in bytes
    -   `buff/cache: int` - Buffer/cache memory in bytes
    -   `available: int` - Available memory in bytes
-   `stats: dict` - CPU usage statistics
    -   `cpu: str` - CPU identifier
    -   `usr: float` - User space CPU usage percentage
    -   `sys: float` - System CPU usage percentage
    -   `idle: float` - Idle CPU percentage
    -   `iowait: float` - I/O wait percentage
    -   (plus other CPU stats)
-   `host: str` - Server hostname/IP
-   `ping: dict` - Network latency statistics
-   `timestamp: datetime` - When stats were collected

#### Methods

##### `__add__(other: ServerStats) -> ServerStats`

Adds two ServerStats objects (for averaging).

##### `__div__(divisor: float) -> ServerStats`

Divides all statistics by a number (for averaging).

##### `to_json() -> dict`

Serializes to JSON format.

## Configuration Schema

### Main Configuration File (config.json)

```json
{
    "app": {
        "name": "string", // Friendly name for the application cluster
        "url": "string" // Base URL of the application to test
    },
    "monitorServers": [
        {
            "name": "string", // Friendly name for the server
            "host": "string", // IP address or hostname
            "port": 22, // SSH port number
            "sshAuthMethod": "password", // Authentication method
            "authentication": {
                "username": "string", // SSH username
                "password": "string" // SSH password
            }
        }
    ]
}
```

#### Validation Rules

-   `app.url` must be a valid HTTP/HTTPS URL
-   `monitorServers` must contain at least one server
-   Each server must have valid network connectivity
-   SSH credentials must be valid for each server

## Result File Formats

### Benchmark Result Files

Generated by the `benchmark` service with filename pattern:
`{cluster-name}-{test-case}-{timestamp}_benchmark.json`

```json
{
    "test_executions": [
        {
            "total_span": {
                "start": "ISO-8601-datetime",
                "end": "ISO-8601-datetime"
            },
            "span_making_requests": {
                "start": "ISO-8601-datetime",
                "end": "ISO-8601-datetime"
            },
            "test_case": {
                "name": "string",
                "description": "string",
                "application_base_url": "string",
                "min_recommended_load": 0
            },
            "results": [
                {
                    "test_case_name": "string",
                    "load": 0,
                    "request_span": {
                        "start": "ISO-8601-datetime",
                        "end": "ISO-8601-datetime"
                    },
                    "server_processing_span": {
                        "start": "ISO-8601-datetime",
                        "end": "ISO-8601-datetime"
                    }
                }
            ],
            "request_per_second": 0,
            "seconds_making_requests": 0,
            "errors": ["string"],
            "cluster_stats": [
                {
                    "servers": [
                        {
                            "memory": {
                                "used": 0,
                                "total": 0,
                                "free": 0,
                                "shared": 0,
                                "buff/cache": 0,
                                "available": 0
                            },
                            "stats": {
                                "cpu": "string",
                                "usr": 0.0,
                                "sys": 0.0,
                                "idle": 0.0,
                                "iowait": 0.0,
                                "irq": 0.0,
                                "soft": 0.0,
                                "steal": 0.0,
                                "guest": 0.0,
                                "gnice": 0.0
                            },
                            "host": "string",
                            "ping": {},
                            "timestamp": "ISO-8601-datetime"
                        }
                    ],
                    "timestamp": "ISO-8601-datetime"
                }
            ]
        }
    ],
    "test_case_name": "string"
}
```

### Test Execution Result Files

Generated by the `test-execution` service with filename pattern:
`{timestamp}_test_execution.json`

Uses the same schema as individual test_executions within benchmark files, but contains only a single test execution result.

## Error Handling

### Common Error Codes

#### Configuration Errors

-   Invalid configuration file format
-   Missing required configuration fields
-   Invalid URLs or network addresses

#### Connection Errors

-   SSH connection failures to monitoring servers
-   HTTP connection failures to test application
-   Network timeouts

#### Test Execution Errors

-   Test case implementation errors
-   Server application errors (5xx responses)
-   Resource exhaustion (memory, disk space)

#### Analysis Errors

-   Missing or corrupted result files
-   Insufficient data for statistical analysis
-   Invalid file formats

### Error Response Format

Errors are typically logged to the console and may be included in result files:

```json
{
    "errors": [
        "Error message describing what went wrong",
        "Additional error if multiple errors occurred"
    ]
}
```

## Performance Considerations

### Request Rate Limitations

The Python asyncio implementation may struggle with precise timing at very high request rates (>48 RPS). For more demanding scenarios, consider:

-   Using lower request rates with longer test durations
-   Implementing load generation in a lower-level language (Rust, Go, C++)
-   Using multiple parallel processes

### Memory Usage

-   Monitor memory usage during large-scale tests
-   Consider processing results in batches for very large datasets
-   Use appropriate monitoring intervals to balance accuracy and resource usage

### Network Considerations

-   Ensure adequate network bandwidth between tester and target systems
-   Account for network latency in timing measurements
-   Use dedicated monitoring connections when possible
