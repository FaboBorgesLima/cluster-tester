import argparse
import asyncio
from html import parser
from benchmark_service import BenchmarkService
from cluster_service import ClusterService
from test_execution_service import TestExecutionService
from json_storage_service import JsonStorageService
from get_cluster_from_config import get_cluster_from_config
from test_case import TestCase
from datetime import datetime


def parse_test_case(app_url:str,test_case:str)->TestCase:
    match test_case:
        case "fibonacci":
            from fibonacci_test import FibonacciTest
            return FibonacciTest(application_base_url=app_url)
        case "bubble-sort":
            from bubble_sort_test import BubbleSortTest
            return BubbleSortTest(application_base_url=app_url)
        case _:
            raise ValueError(f"Unknown test case: {test_case}. Supported cases are: fibonacci, bubble-sort.")

async def main():
    parser = argparse.ArgumentParser(description="Run the benchmark service.")
    
    path = '/'.join(__file__.split('/')[0:-1])

    parser.add_argument('service', type=str, help='Service to run: benchmark, test-execution')
    parser.add_argument('--storage', type=str, default=path+"/../db/", help='Path to the storage directory.')
    parser.add_argument('--config', type=str, default="config.json", help='Path to the configuration file.')
    parser.add_argument('--monitoring-interval', type=float, default=0.5, help='Interval for monitoring in seconds.')
    parser.add_argument('--duration-per-test', type=int, default=30, help='Duration of each test in seconds.')
    parser.add_argument('--test-cases', default=['fibonacci','bubble-sort'], type=str, nargs='+', help='List of test cases to run. For test-execution, only one test case is allowed.')
    parser.add_argument('--max-response-time', type=float, default=2.0, help='benchmark only: Maximum acceptable response time in seconds.')
    parser.add_argument('--max-n-loads-to-test', type=int, default=3, help='benchmark only: Maximum number of loads to test.')
    parser.add_argument('--min-requests-per-second', type=int, default=1, help='benchmark only: Minimum requests per second to test.')
    parser.add_argument('--rest-time', type=int, default=30, help='benchmark only: Rest time between tests in seconds.')
    parser.add_argument('--load', type=int, default=1, help='test-execution only: Load to apply during the test.')
    parser.add_argument('--requests-per-second', type=int, default=1, help='test-execution only: Requests per second to apply during the test.')

    args = parser.parse_args()
    service = args.service.lower()
    storage_service = JsonStorageService(args.storage)
    config_data = storage_service.load(args.config)
    cluster = get_cluster_from_config(config_data)
    cluster_service = ClusterService()

    match service:
        case "benchmark":
            
            benchmark_service = BenchmarkService(
                test_execution_service=TestExecutionService(cluster_service=cluster_service),
            )
            args = parser.parse_args()
            test_cases = [parse_test_case(config_data['app']['url'], test_case) for test_case in args.test_cases]

            for test_case in test_cases:
                print(f"Running benchmark for test case: {test_case.__class__.__name__}")

            benchmark = await benchmark_service.run_benchmark(
                test_cases=test_cases,
                cluster=cluster,
                duration_per_test=args.duration_per_test,
                rest_time=args.rest_time,
                max_response_time=args.max_response_time,
                max_n_loads_to_test=args.max_n_loads_to_test,
            )
            file_name = f"{datetime.now().strftime('%Y%m%d_%H%M%S')}_benchmark.json"
            print(f"Benchmark completed. Saving results to {file_name} in {args.storage}")            
            storage_service.save(
                file_name=file_name,
                data=benchmark.to_short_json()  # Save the benchmark in a short JSON format
            )
        case "test-execution":
            cluster_service = ClusterService()
            test_execution_service = TestExecutionService(cluster_service=cluster_service)
            test_cases = [parse_test_case(config_data['app']['url'], test_case) for test_case in args.test_cases]
            if len(test_cases) != 1:
                raise ValueError("Test execution service can only run one test case at a time.")
            test_case = test_cases[0]
            print(f"Running test execution for test case: {test_case.__class__.__name__}")
            test_execution = await test_execution_service.execute_test_while_monitoring(
                test_case=test_case,
                cluster=cluster,
                duration_seconds=args.duration_per_test,
                monitoring_interval=args.monitoring_interval,
                load=args.load,
                request_per_second=args.requests_per_second,
            )
            file_name = f"{datetime.now().strftime('%Y%m%d_%H%M%S')}_test_execution.json"
            print(f"Test execution completed. Saving results to {file_name} in {args.storage}")
            if test_execution.has_errors():
                print(f"Test execution encountered errors: {test_execution.errors}")
            storage_service.save(
                file_name=file_name,
                data=test_execution.to_short_json()  # Save the test case in a short JSON format
            )


if __name__ == "__main__":
    asyncio.run(main())

