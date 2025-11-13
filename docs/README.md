# Cluster Tester Documentation

This directory contains the comprehensive documentation for the **Cluster Tester** project - a powerful tool for benchmarking and analyzing the performance of distributed server applications across multiple Kubernetes cluster environments.

## Purpose of this project

The Cluster Tester project provides a comprehensive testing framework for Kubernetes clusters, enabling users to validate their cluster configurations, compare different Kubernetes distributions (K3s, K0s, MicroK8s), and ensure optimal performance under various load conditions. It helps DevOps engineers and system administrators make informed decisions about their infrastructure choices.

## 🚀 Quick Start

Get started with Cluster Tester in just a few commands:

```bash
# Set up environment
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
python3 src --help
```

## 📋 Key Features Documented

The documentation covers all major Cluster Tester capabilities:

### Core Functionality

-   **Distributed Load Testing**: Test applications across multiple servers simultaneously
-   **Real-time Monitoring**: Monitor CPU, RAM, and network performance during tests
-   **Multiple Test Cases**: Built-in Fibonacci and Bubble Sort computational tests
-   **Comprehensive Analysis**: Generate detailed reports with visualizations

### Kubernetes Support

-   **Multi-Distribution Testing**: Compare K3s, K0s, and MicroK8s performance
-   **Easy Deployment**: Deploy test applications to Kubernetes clusters
-   **Flexible Configuration**: JSON-based configuration for easy setup

### Analysis & Reporting

-   **Performance Metrics**: CPU usage, memory consumption, response times
-   **Visual Analytics**: Charts and graphs for performance comparison
-   **Statistical Analysis**: Mean, median, percentile analysis

## 📝 What You'll Find in the Documentation

### Getting Started Guides

-   **[Main README](../README.md)**: Complete project overview and quick start
-   **[Examples](EXAMPLES.md)**: Step-by-step tutorials and practical examples
-   **[Architecture](ARCHITECTURE.md)**: Understanding how Cluster Tester works

### Configuration Guides

-   **[K3s Setup](reference_configuration/k3s.md)**: Lightweight Kubernetes with MetalLB
-   **[K0s Setup](reference_configuration/k0s.md)**: Zero-friction Kubernetes configuration
-   **[MicroK8s Setup](reference_configuration/microk8s.md)**: Ubuntu's Kubernetes distribution

### Reference Materials

-   **[API Reference](API_REFERENCE.md)**: Complete Python API documentation
-   **[Contributing Guide](CONTRIBUTING.md)**: How to contribute to the project
-   **Auto-Generated API Docs**: Python module documentation in `api/` directory

### Performance Testing Workflows

The documentation includes comprehensive guides for:

1. **Setting up test environments** across different Kubernetes distributions
2. **Running benchmarks** with various load parameters
3. **Analyzing results** with statistical comparisons and visualizations
4. **Comparing infrastructure performance** between different setups

## ⚙️ Understanding the Test Framework

### Test Cases Available

**Fibonacci Test**: Tests recursive computation performance

-   Tests CPU-intensive workloads
-   Exponential complexity scaling
-   Ideal for CPU performance comparison

**Bubble Sort Test**: Tests array sorting performance

-   Memory and CPU intensive operations
-   O(n²) complexity characteristics
-   Good for memory bandwidth testing

### Performance Metrics Tracked

The framework automatically collects:

-   **Response Times**: End-to-end request latency
-   **Server Processing**: Actual computation time
-   **CPU Usage**: System and user CPU utilization per server
-   **Memory Usage**: RAM consumption across cluster nodes
-   **Network Latency**: Ping times and network performance

### Getting Help

For questions about using Cluster Tester:

-   **Check the documentation**: Start with [EXAMPLES](EXAMPLES.md) for common scenarios
-   **Review configuration guides**: Kubernetes-specific setup in `reference_configuration/`
-   **File an issue**: Report bugs or request features on GitHub
-   **Read the API docs**: Complete Python API reference in `api/` directory

### Improving Documentation

Found something unclear or missing? The documentation improves with community input:

-   Submit documentation fixes via pull requests
-   Request new examples or guides by filing issues
-   Suggest improvements to existing content

## 📚 Additional Resources

### Learning More About Cluster Testing

-   **Kubernetes Performance**: Understanding cluster performance characteristics
-   **Load Testing Best Practices**: Effective strategies for distributed testing
-   **Infrastructure Comparison**: Methodologies for comparing K8s distributions
-   **Monitoring and Observability**: Understanding performance metrics

### Related Tools and Frameworks

-   **K6**: JavaScript-based load testing (alternative approach)
-   **Apache Bench**: Simple HTTP server testing
-   **Kubernetes Benchmarking**: Other cluster performance tools
-   **Prometheus + Grafana**: Production monitoring stack

For detailed technical information, start with the [main project README](../README.md) and explore the hands-on [examples](EXAMPLES.md).

## 🤝 Contributing to the Project

The Cluster Tester documentation is part of an open-source project that welcomes contributions:

### How to Contribute

1. **Improve documentation clarity** - Make instructions easier to follow
2. **Add real-world examples** - Share your testing scenarios and configurations
3. **Update configuration guides** - Keep Kubernetes setup instructions current
4. **Fix issues you encounter** - Help others avoid the same problems
5. **Expand test coverage** - Document edge cases and advanced usage

### Documentation Guidelines

-   **Focus on practical usage** - Provide copy-paste examples that work
-   **Test your documentation** - Ensure instructions actually work
-   **Include expected outputs** - Show what success looks like
-   **Cover troubleshooting** - Document common issues and solutions

See the [Contributing Guide](CONTRIBUTING.md) for complete development and contribution guidelines.
