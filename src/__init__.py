"""
Cluster Tester - A distributed benchmarking tool for Kubernetes applications.

This package provides tools for benchmarking and analyzing the performance 
of distributed server applications across multiple cluster environments.
"""

__version__ = "1.0.0"
__author__ = "Cluster Tester Contributors"

# Import main components for easy access
from .benchmark_service import BenchmarkService
from .test_execution_service import TestExecutionService  
from .data_analysis_service import DataAnalysisService
from .cluster_service import ClusterService
from .test_case import TestCase
from .test_result import TestResult

__all__ = [
    'BenchmarkService',
    'TestExecutionService',
    'DataAnalysisService', 
    'ClusterService',
    'TestCase',
    'TestResult',
]