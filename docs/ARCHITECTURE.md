# Architecture Overview

This document provides a comprehensive overview of the Cluster Tester architecture, design principles, and implementation details.

## Table of Contents

1. [System Architecture](#system-architecture)
2. [Core Components](#core-components)
3. [Data Flow](#data-flow)
4. [Design Patterns](#design-patterns)
5. [Scalability Considerations](#scalability-considerations)
6. [Extension Points](#extension-points)

## System Architecture

### High-Level Overview

The Cluster Tester follows a modular architecture with clear separation of concerns:

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   CLI Layer     │    │  Test Target    │    │ Monitor Targets │
│                 │    │                 │    │                 │
│ ┌─────────────┐ │    │ ┌─────────────┐ │    │ ┌─────────────┐ │
│ │ CLI Parser  │ │    │ │ Application │ │    │ │   Server 1  │ │
│ │             │ │    │ │   Server    │ │    │ │             │ │
│ └─────────────┘ │    │ └─────────────┘ │    │ └─────────────┘ │
│                 │    │                 │    │                 │
│ ┌─────────────┐ │    │ ┌─────────────┐ │    │ ┌─────────────┐ │
│ │   Services  │ │◄───┤ │  Endpoints  │ │    │ │   Server N  │ │
│ │             │ │    │ │             │ │    │ │             │ │
│ └─────────────┘ │    │ └─────────────┘ │    │ └─────────────┘ │
└─────────────────┘    └─────────────────┘    └─────────────────┘
         │                       │                       │
         └───────────────────────┼───────────────────────┘
                                 │
                    ┌─────────────────┐
                    │ Data Analysis   │
                    │ & Visualization │
                    └─────────────────┘
```

### Component Layers

#### 1. Presentation Layer (CLI)

-   **cli.py**: Command-line interface and argument parsing
-   **Service routing**: Dispatches commands to appropriate services
-   **Output formatting**: Handles console output and file generation

#### 2. Service Layer

-   **BenchmarkService**: Orchestrates comprehensive benchmarks
-   **TestExecutionService**: Manages individual test executions
-   **DataAnalysisService**: Processes and visualizes results
-   **ClusterService**: Handles server monitoring and connections

#### 3. Domain Layer

-   **Test Cases**: Abstract test case implementations
-   **Data Models**: Core domain objects (TestResult, TestExecution, etc.)
-   **Configuration**: System configuration management

#### 4. Infrastructure Layer

-   **Storage**: JSON-based persistence
-   **Monitoring**: SSH-based server monitoring
-   **HTTP Client**: Async HTTP requests to test targets

## Core Components

### Test Execution Engine

#### TestExecutionService

The central orchestrator for test execution with sophisticated request timing:

```python
class TestExecutionService:
    async def execute_test(self, tests_per_second: int, duration_seconds: int,
                          load: int, test_case: TestCase) -> TestExecution:
        # Precision timing implementation
        interval = 1.0 / tests_per_second
        start_time = datetime.now()

        for request_num in range(total_requests):
            # Calculate exact target time for this request
            target_time = start_time.timestamp() + interval * (request_num + 1)

            # Execute test case asynchronously
            running_results.append(asyncio.create_task(test_case.run(load=load)))

            # Precision sleep to maintain exact timing
            sleep_time = target_time - datetime.now().timestamp()
            if sleep_time > 0:
                await asyncio.sleep(sleep_time)
```

**Key Features:**

-   **Precise Request Timing**: Calculates exact target times for each request
-   **Async Execution**: All requests run concurrently without blocking
-   **Error Handling**: Graceful handling of failed requests
-   **Monitoring Integration**: Real-time server monitoring during tests

#### Load Discovery Algorithms

##### Maximum Acceptable Load Discovery

Uses binary search to find the highest load that maintains acceptable response times:

```python
async def find_max_acceptable_load(self, test_case: TestCase,
                                 max_avg_response_time: float) -> TestExecution:
    load = test_case.get_min_recommended_load()
    last_successful = None

    while load <= max_load:
        execution = await self.execute_test(rps, duration, load, test_case)

        if execution.avg_response_time() > max_avg_response_time:
            return last_successful

        last_successful = execution
        load += increment
```

##### Maximum RPS Discovery

Combines exponential search with binary refinement:

```python
async def find_max_requests_per_second(self, test_case: TestCase,
                                     load: int) -> TestExecution:
    # Phase 1: Exponential search to find upper bound
    power = 0
    while power <= max_power:
        rps = 2 ** power
        execution = await self.execute_test(rps, duration, load, test_case)

        if execution.avg_response_time() > threshold:
            break
        power += 1

    # Phase 2: Binary search for exact maximum
    lower_bound, upper_bound = 2 ** (power - 1), 2 ** power
    return await self._binary_search_max_rps(lower_bound, upper_bound)
```

### Monitoring System

#### ClusterService

Manages connections to multiple servers and collects comprehensive metrics:

```python
class ClusterService:
    async def get_stats(self, cluster: Cluster) -> ClusterStats:
        server_stats = []

        for server in cluster.servers:
            # Collect multiple metrics simultaneously
            memory_stats = server.server_client.send_ram()
            cpu_stats = server.server_client.send_stats()
            ping_stats = server.connection.get_ping()

            server_stats.append(ServerStats(
                memory=memory_stats,
                stats=cpu_stats,
                host=server.connection.get_hostname(),
                ping=ping_stats,
                timestamp=datetime.now()
            ))

        return ClusterStats(servers=server_stats, timestamp=datetime.now())
```

#### BackgroundClusterMonitoring

Provides continuous monitoring during test execution:

```python
class BackgroundClusterMonitoring:
    async def run(self, interval: float):
        self._running = True

        while self._running:
            # Non-blocking stats collection
            stats = await self.cluster_service.get_stats(self.cluster)
            self.stats.append(stats)

            # Precise timing for monitoring intervals
            await asyncio.sleep(interval)
```

### Test Case Framework

#### Abstract Base Class

Defines the contract for all test implementations:

```python
class TestCase(ABC):
    @abstractmethod
    async def run(self, load: int) -> TestResult:
        """Execute test case and return timing results"""
        pass

    def get_min_recommended_load(self) -> int:
        """Minimum load for meaningful results"""
        return self._min_recommended_load
```

#### Built-in Test Cases

##### FibonacciTest

-   **Algorithm**: Recursive Fibonacci calculation
-   **Complexity**: Exponential O(φⁿ)
-   **Resource Profile**: CPU-intensive, minimal memory
-   **Load Mapping**: Direct mapping (load = Fibonacci number)

##### BubbleSortTest

-   **Algorithm**: Bubble sort on reverse-sorted array
-   **Complexity**: Quadratic O(n²)
-   **Resource Profile**: CPU and memory intensive
-   **Load Mapping**: Exponential mapping (array_size = 2^load)

### Data Analysis Engine

#### Statistical Analysis

Processes raw test results into meaningful metrics:

```python
class DataAnalysisService:
    def avg_response_time_benchmark(self, benchmark_file: str) -> list[dict]:
        # Extract and aggregate response times
        for execution in benchmark_data['test_executions']:
            total_time = sum(self._extract_response_time(result)
                           for result in execution['results'])

            avg_time = total_time / len(execution['results'])
            yield {
                'load': execution_load,
                'rps': execution['request_per_second'],
                'avg_response_time': avg_time
            }
```

#### Visualization Generation

Creates publication-quality charts using matplotlib:

```python
def cpu_usage_compare(self, files: list[str], load: int) -> None:
    # Data preparation
    hosts = self._extract_unique_hosts(files)
    benchmarks = self._extract_benchmark_names(files)

    # Create grouped bar chart
    fig, ax = plt.subplots(figsize=(12, 7))

    for i, benchmark in enumerate(benchmarks):
        positions = self._calculate_bar_positions(i, len(benchmarks))
        values = self._extract_cpu_values(benchmark, hosts, load)

        bars = ax.bar(positions, values, width, label=benchmark)

        # Add data labels
        ax.bar_label(bars, fmt='%.2f%%')

    # Styling and output
    self._apply_styling(ax, hosts, benchmarks)
    plt.savefig(f'cpu_comparison_load_{load}.png', dpi=300)
```

## Data Flow

### Benchmark Execution Flow

```
1. Configuration Loading
   ├── Load config.json
   ├── Parse cluster definitions
   └── Initialize services

2. Test Case Preparation
   ├── Instantiate test cases
   ├── Validate connectivity
   └── Warm-up cluster connections

3. Load Discovery Phase
   ├── Find max acceptable load
   │   ├── Start with min_recommended_load
   │   ├── Increment until threshold exceeded
   │   └── Return last successful load
   │
   └── Find max requests per second
       ├── Exponential search for upper bound
       ├── Binary search for exact maximum
       └── Return optimal RPS

4. Comprehensive Testing
   ├── Test at discovered optimal point
   ├── Test at reduced loads (n-1, n-2, n-3)
   ├── Re-run all tests with monitoring
   └── Collect comprehensive metrics

5. Result Persistence
   ├── Serialize to JSON format
   ├── Include all raw data
   └── Generate summary statistics
```

### Data Analysis Flow

```
1. File Loading & Validation
   ├── Parse JSON result files
   ├── Validate data structure
   └── Extract relevant metrics

2. Statistical Processing
   ├── Calculate response time distributions
   ├── Aggregate resource usage metrics
   └── Compute comparative statistics

3. Visualization Generation
   ├── Prepare data for plotting
   ├── Create matplotlib figures
   ├── Apply styling and annotations
   └── Export as PNG files

4. Report Generation
   ├── Console output with key metrics
   ├── File-based detailed reports
   └── Visualization file references
```

## Design Patterns

### Async/Await Pattern

Extensive use of Python's asyncio for concurrent operations:

```python
# Concurrent test execution
async def execute_multiple_tests(self, test_configs: list) -> list[TestResult]:
    tasks = [
        asyncio.create_task(self.execute_test(**config))
        for config in test_configs
    ]
    return await asyncio.gather(*tasks, return_exceptions=True)

# Concurrent monitoring
async def monitor_while_testing(self, test_task, monitoring_task):
    test_result, monitoring_data = await asyncio.gather(
        test_task,
        monitoring_task,
        return_exceptions=True
    )
```

### Strategy Pattern

Test cases implement a common interface with different strategies:

```python
class TestStrategy:
    def fibonacci_strategy(self, load: int) -> HTTPRequest:
        return HTTPRequest(f"/fibonacci/{load}")

    def bubble_sort_strategy(self, load: int) -> HTTPRequest:
        array_size = 2 ** load
        return HTTPRequest(f"/bubble-sort?n={array_size}")
```

### Observer Pattern

Background monitoring observes test execution:

```python
class TestExecutionObserver:
    def __init__(self, monitoring_service):
        self.monitoring_service = monitoring_service
        self.observations = []

    async def observe_execution(self, execution_task):
        while not execution_task.done():
            observation = await self.monitoring_service.get_stats()
            self.observations.append(observation)
            await asyncio.sleep(self.interval)
```

### Factory Pattern

Dynamic test case creation:

```python
class TestCaseFactory:
    @staticmethod
    def create_test_case(test_type: str, app_url: str) -> TestCase:
        factory_map = {
            'fibonacci': FibonacciTest,
            'bubble-sort': BubbleSortTest,
            'custom': CustomTest
        }

        test_class = factory_map.get(test_type)
        if not test_class:
            raise ValueError(f"Unknown test type: {test_type}")

        return test_class(app_url)
```

### Command Pattern

CLI commands encapsulate service operations:

```python
class BenchmarkCommand:
    def __init__(self, benchmark_service: BenchmarkService):
        self.service = benchmark_service

    async def execute(self, **kwargs) -> None:
        benchmarks = await self.service.run_benchmark(**kwargs)
        self._save_results(benchmarks)
        self._print_summary(benchmarks)
```

## Scalability Considerations

### Horizontal Scaling

#### Multiple Test Execution Processes

```bash
# Distribute load across multiple processes
for i in {1..4}; do
    python3 src/ test-execution \
        --requests-per-second $((total_rps / 4)) \
        --duration-per-test 60 &
done
wait
```

#### Distributed Monitoring

```python
class DistributedClusterService:
    def __init__(self, cluster_partitions: list[Cluster]):
        self.partitions = cluster_partitions

    async def get_distributed_stats(self) -> ClusterStats:
        partition_tasks = [
            self.get_stats(partition)
            for partition in self.partitions
        ]

        partition_stats = await asyncio.gather(*partition_tasks)
        return self._merge_cluster_stats(partition_stats)
```

### Vertical Scaling

#### Memory Optimization

```python
class StreamingDataAnalysis:
    def process_large_dataset(self, file_path: str):
        # Process data in chunks to reduce memory usage
        for chunk in self._read_json_chunks(file_path, chunk_size=1000):
            yield self._analyze_chunk(chunk)
```

#### CPU Optimization

```python
# Use multiprocessing for CPU-intensive analysis
from multiprocessing import Pool

class ParallelAnalysisService:
    def analyze_multiple_files(self, files: list[str]) -> dict:
        with Pool(processes=cpu_count()) as pool:
            results = pool.map(self._analyze_single_file, files)

        return self._combine_results(results)
```

### Performance Optimizations

#### Connection Pooling

```python
class PooledClusterService:
    def __init__(self, max_connections_per_host: int = 10):
        self.connection_pools = {}

    async def get_pooled_connection(self, host: str):
        if host not in self.connection_pools:
            self.connection_pools[host] = ConnectionPool(
                host=host,
                max_connections=self.max_connections_per_host
            )

        return await self.connection_pools[host].acquire()
```

#### Request Batching

```python
class BatchedTestExecution:
    async def execute_batch(self, requests: list[TestRequest]) -> list[TestResult]:
        # Group requests by target host
        host_groups = self._group_by_host(requests)

        # Execute each group concurrently
        group_tasks = [
            self._execute_host_group(host, requests)
            for host, requests in host_groups.items()
        ]

        return await asyncio.gather(*group_tasks)
```

## Extension Points

### Custom Test Cases

```python
class CustomTestCase(TestCase):
    def __init__(self, application_base_url: str, custom_config: dict):
        super().__init__(
            name="CustomTest",
            description="Custom performance test",
            application_base_url=application_base_url
        )
        self.config = custom_config

    async def run(self, load: int) -> TestResult:
        # Implement custom testing logic
        async with httpx.AsyncClient() as client:
            # Custom request logic based on self.config
            response = await self._make_custom_request(client, load)

            return TestResult(
                test_case_name=self.get_name(),
                request_span=self._calculate_request_span(),
                server_processing_span=self._extract_server_span(response),
                load=load
            )
```

### Custom Analysis Types

```python
class CustomAnalysisService(DataAnalysisService):
    def custom_metric_analysis(self, benchmark_file: str) -> list[dict]:
        # Implement custom analysis logic
        benchmark_data = self.storage_service.load(benchmark_file)

        for execution in benchmark_data['test_executions']:
            custom_metric = self._calculate_custom_metric(execution)
            yield {
                'load': execution['load'],
                'custom_metric': custom_metric,
                'execution_id': execution['id']
            }
```

### Plugin Architecture

```python
class PluginManager:
    def __init__(self):
        self.test_case_plugins = {}
        self.analysis_plugins = {}

    def register_test_case(self, name: str, test_class: type):
        self.test_case_plugins[name] = test_class

    def register_analysis(self, name: str, analysis_func: callable):
        self.analysis_plugins[name] = analysis_func

    def create_test_case(self, name: str, *args, **kwargs):
        if name in self.test_case_plugins:
            return self.test_case_plugins[name](*args, **kwargs)
        raise ValueError(f"Unknown test case plugin: {name}")
```

### Configuration Extensions

```python
class ConfigurationManager:
    def __init__(self, config_file: str):
        self.base_config = self._load_base_config(config_file)
        self.extensions = {}

    def register_extension(self, name: str, extension_config: dict):
        self.extensions[name] = extension_config

    def get_merged_config(self) -> dict:
        merged = self.base_config.copy()

        for extension in self.extensions.values():
            merged = self._deep_merge(merged, extension)

        return merged
```

This architecture provides a solid foundation for performance testing while maintaining flexibility for future extensions and modifications. The modular design allows for easy testing of individual components and facilitates maintenance and debugging.
