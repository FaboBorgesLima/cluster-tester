# Examples and Use Cases

This document provides practical examples for using the Cluster Tester tool in various scenarios.

## Table of Contents

1. [Basic Examples](#basic-examples)
2. [Kubernetes Testing](#kubernetes-testing)
3. [Performance Comparison](#performance-comparison)
4. [CI/CD Integration](#cicd-integration)
5. [Advanced Scenarios](#advanced-scenarios)

## Basic Examples

### Running Your First Test

```bash
# 1. Set up environment
source .venv/bin/activate

# 2. Start test application
docker-compose up -d

# 3. Configure cluster
cp db/config_example.json db/config.json
# Edit db/config.json with your server details

# 4. Run a simple test
python3 src/ test-execution \
    --test-cases fibonacci \
    --load 10 \
    --requests-per-second 5 \
    --duration-per-test 30
```

### Basic Benchmark Suite

```bash
# Run comprehensive benchmark
python3 src/ benchmark \
    --test-cases fibonacci bubble-sort \
    --max-response-time 2.0 \
    --duration-per-test 30 \
    --max-n-loads-to-test 3
```

## Kubernetes Testing

### Testing Different Kubernetes Distributions

#### Setup Multiple Configs

Create separate configuration files for each Kubernetes distribution:

**k3s-config.json:**

```json
{
    "app": {
        "name": "K3s Cluster",
        "url": "http://k3s-lb.example.com"
    },
    "monitorServers": [
        {
            "name": "K3s Master",
            "host": "k3s-master.example.com",
            "port": 22,
            "authentication": {
                "username": "ubuntu",
                "password": "your-password"
            }
        }
    ]
}
```

**k0s-config.json:**

```json
{
    "app": {
        "name": "K0s Cluster",
        "url": "http://k0s-lb.example.com"
    },
    "monitorServers": [
        {
            "name": "K0s Master",
            "host": "k0s-master.example.com",
            "port": 22,
            "authentication": {
                "username": "ubuntu",
                "password": "your-password"
            }
        }
    ]
}
```

#### Run Benchmarks

```bash
# Test K3s
python3 src/ benchmark \
    --config k3s-config.json \
    --max-response-time 1.5 \
    --duration-per-test 60

# Test K0s
python3 src/ benchmark \
    --config k0s-config.json \
    --max-response-time 1.5 \
    --duration-per-test 60

# Test MicroK8s
python3 src/ benchmark \
    --config microk8s-config.json \
    --max-response-time 1.5 \
    --duration-per-test 60
```

#### Compare Results

```bash
# Compare CPU usage
python3 src/ data-analysis cpu-usage-compare \
    --files k3s-*-benchmark.json k0s-*-benchmark.json microk8s-*-benchmark.json \
    --load 15 \
    --benchmark-names K3s K0s MicroK8s \
    --alias-hosts "10.0.1.10:master,10.0.1.11:worker1,10.0.1.12:worker2"

# Compare RAM usage
python3 src/ data-analysis ram-usage-compare \
    --files k3s-*-benchmark.json k0s-*-benchmark.json microk8s-*-benchmark.json \
    --load 15 \
    --benchmark-names K3s K0s MicroK8s

# Compare response time distributions
python3 src/ data-analysis response-time-compare \
    --files k3s-*-benchmark.json k0s-*-benchmark.json microk8s-*-benchmark.json \
    --load 15 \
    --benchmark-names K3s K0s MicroK8s
```

### Load Balancer Testing

Test different load balancer configurations:

```bash
# Test with different load balancer algorithms
# Round Robin
python3 src/ test-execution --requests-per-second 20 --load 15 --duration-per-test 60

# Least Connections
# (Update load balancer config, then rerun)
python3 src/ test-execution --requests-per-second 20 --load 15 --duration-per-test 60

# IP Hash
# (Update load balancer config, then rerun)
python3 src/ test-execution --requests-per-second 20 --load 15 --duration-per-test 60
```

## Performance Comparison

### Before/After Performance Testing

```bash
# Baseline test
python3 src/ benchmark \
    --max-response-time 2.0 \
    --duration-per-test 60 \
    --max-n-loads-to-test 5

# Save baseline results
mv db/*benchmark.json db/baseline-benchmark.json

# Apply performance optimizations to your system
# Then run the same test again

python3 src/ benchmark \
    --max-response-time 2.0 \
    --duration-per-test 60 \
    --max-n-loads-to-test 5

# Save optimized results
mv db/*benchmark.json db/optimized-benchmark.json

# Compare results
python3 src/ data-analysis response-time-compare \
    --files baseline-benchmark.json optimized-benchmark.json \
    --load 15 \
    --benchmark-names "Baseline" "Optimized"
```

### Resource Scaling Analysis

```bash
# Test with 1 CPU core
# Configure cluster to use 1 CPU core per pod
python3 src/ benchmark --duration-per-test 45

# Test with 2 CPU cores
# Scale cluster to 2 CPU cores per pod
python3 src/ benchmark --duration-per-test 45

# Test with 4 CPU cores
# Scale cluster to 4 CPU cores per pod
python3 src/ benchmark --duration-per-test 45

# Compare scaling efficiency
python3 src/ data-analysis cpu-usage-compare \
    --files 1cpu-benchmark.json 2cpu-benchmark.json 4cpu-benchmark.json \
    --load 15 \
    --benchmark-names "1CPU" "2CPU" "4CPU"
```

## CI/CD Integration

### GitHub Actions Example

```yaml
# .github/workflows/performance-test.yml
name: Performance Test

on:
    pull_request:
        branches: [main]

jobs:
    performance-test:
        runs-on: ubuntu-latest

        steps:
            - uses: actions/checkout@v2

            - name: Set up Python
              uses: actions/setup-python@v2
              with:
                  python-version: "3.9"

            - name: Install dependencies
              run: |
                  python -m pip install --upgrade pip
                  pip install -r requirements.txt

            - name: Start test application
              run: |
                  docker-compose up -d
                  sleep 30  # Wait for app to start

            - name: Run performance test
              run: |
                  python3 src/ test-execution \
                    --test-cases fibonacci \
                    --load 15 \
                    --requests-per-second 10 \
                    --duration-per-test 30

            - name: Check performance regression
              run: |
                  python3 scripts/check-performance.py \
                    --threshold 2.0 \
                    --file db/*test_execution.json
```

### Performance Regression Check Script

```python
# scripts/check-performance.py
import json
import sys
import argparse
from pathlib import Path

def check_performance(file_path, threshold):
    with open(file_path, 'r') as f:
        data = json.load(f)

    # Calculate average response time
    results = data.get('results', [])
    if not results:
        print("No test results found")
        return False

    total_time = 0
    for result in results:
        start = result['server_processing_span']['start']
        end = result['server_processing_span']['end']
        # Calculate duration (simplified)
        total_time += 1  # Placeholder calculation

    avg_time = total_time / len(results)

    print(f"Average response time: {avg_time:.3f}s")
    print(f"Threshold: {threshold}s")

    if avg_time > threshold:
        print("❌ Performance regression detected!")
        return False
    else:
        print("✅ Performance test passed!")
        return True

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument('--threshold', type=float, required=True)
    parser.add_argument('--file', type=str, required=True)

    args = parser.parse_args()

    success = check_performance(args.file, args.threshold)
    sys.exit(0 if success else 1)
```

### Jenkins Pipeline Example

```groovy
pipeline {
    agent any

    stages {
        stage('Setup') {
            steps {
                sh 'python3 -m venv .venv'
                sh 'source .venv/bin/activate && pip install -r requirements.txt'
            }
        }

        stage('Deploy Test App') {
            steps {
                sh 'docker-compose up -d'
                sleep(30)
            }
        }

        stage('Performance Test') {
            steps {
                sh '''
                    source .venv/bin/activate
                    python3 src/ test-execution \
                        --test-cases fibonacci bubble-sort \
                        --load 15 \
                        --requests-per-second 15 \
                        --duration-per-test 60
                '''
            }
        }

        stage('Archive Results') {
            steps {
                archiveArtifacts artifacts: 'db/*.json', fingerprint: true

                script {
                    def testFiles = sh(
                        script: 'ls db/*test_execution.json',
                        returnStdout: true
                    ).trim()

                    sh "python3 src/ data-analysis avg-response-time --files ${testFiles}"
                }
            }
        }
    }

    post {
        always {
            sh 'docker-compose down'
        }
    }
}
```

## Advanced Scenarios

### Multi-Region Testing

```bash
# Test US East region
python3 src/ benchmark \
    --config us-east-config.json \
    --duration-per-test 60

# Test US West region
python3 src/ benchmark \
    --config us-west-config.json \
    --duration-per-test 60

# Test EU region
python3 src/ benchmark \
    --config eu-config.json \
    --duration-per-test 60

# Compare regions
python3 src/ data-analysis response-time-compare \
    --files us-east-*-benchmark.json us-west-*-benchmark.json eu-*-benchmark.json \
    --load 15 \
    --benchmark-names "US-East" "US-West" "EU"
```

### Database Performance Impact

```bash
# Test with no database load
python3 src/ benchmark --duration-per-test 60

# Apply database load in background
# Then test again
python3 src/ benchmark --duration-per-test 60

# Compare impact
python3 src/ data-analysis cpu-usage-compare \
    --files no-db-load.json with-db-load.json \
    --load 15 \
    --benchmark-names "No DB Load" "With DB Load"
```

### Network Latency Testing

```bash
# Test with normal network
python3 src/ test-execution \
    --requests-per-second 20 \
    --duration-per-test 60

# Introduce network latency (using tc or similar tools)
# sudo tc qdisc add dev eth0 root netem delay 50ms

# Test with added latency
python3 src/ test-execution \
    --requests-per-second 20 \
    --duration-per-test 60

# Remove latency and compare results
python3 src/ data-analysis response-time-compare \
    --files normal-network.json high-latency.json \
    --load 15 \
    --benchmark-names "Normal" "High Latency"
```

### Stress Testing

```bash
# Gradually increase load to find breaking point
for rps in 5 10 20 40 80 160; do
    echo "Testing ${rps} RPS..."

    python3 src/ test-execution \
        --requests-per-second $rps \
        --load 15 \
        --duration-per-test 30

    # Check if errors occurred
    if grep -q '"errors":\[' db/*test_execution.json; then
        echo "Errors detected at ${rps} RPS"
        break
    fi

    sleep 10  # Rest between tests
done
```

### Custom Test Case Example

```python
# custom_tests/database_test.py
from test_case import TestCase
from test_result import TestResult
import httpx
import datetime
from timespan import Timespan

class DatabaseTest(TestCase):
    def __init__(self, application_base_url: str):
        super().__init__(
            name="DatabaseTestCase",
            description="Tests database query performance",
            application_base_url=application_base_url,
            min_recommended_load=1
        )

    async def run(self, load: int) -> TestResult:
        async with httpx.AsyncClient(timeout=30.0) as client:
            start_request = datetime.datetime.now(datetime.timezone.utc)

            # Test database query with specified number of records
            response = await client.get(
                f'{self._application_base_url}/db-query',
                params={'records': load * 1000}
            )

            end_request = datetime.datetime.now(datetime.timezone.utc)

            # Parse server timing
            response_data = response.json()
            start_server = datetime.datetime.fromisoformat(response_data['start'])
            end_server = datetime.datetime.fromisoformat(response_data['end'])

            return TestResult(
                test_case_name=self.get_name(),
                request_span=Timespan(start_request, end_request),
                server_processing_span=Timespan(start_server, end_server),
                load=load
            )
```

Usage:

```bash
# Register custom test in cli.py parse_test_case function
# Then use it:
python3 src/ test-execution \
    --test-cases database \
    --load 5 \
    --requests-per-second 10
```

These examples should help you get started with various testing scenarios. Adjust the parameters based on your specific infrastructure and requirements.
