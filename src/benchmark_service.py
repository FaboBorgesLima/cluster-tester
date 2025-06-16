from test_execution_service import TestExecutionService
from test_case import TestCase
from benchmark import Benchmark
import logging
import math

class BenchmarkService:
    def __init__(self, test_execution_service: TestExecutionService):
        self.test_execution_service = test_execution_service

    async def run_benchmark(self, test_cases: list[TestCase]) -> Benchmark:
        """
        Run a benchmark for a list of test cases.
        :param test_cases: List of TestCase objects to run.
        :return: Benchmark object containing the results of the benchmark.
        """
        if not test_cases:
            raise ValueError("No test cases provided for benchmarking.")

        benchmark_results = []
        
        for test_case in test_cases:
            result = await self.run_benchmark_single_test_case(test_case)
            benchmark_results.append(result)

        return Benchmark(test_executions=benchmark_results)

    async def run_benchmark_single_test_case(
            self, 
            test_case: TestCase,
            max_response_time :float = 2.0,
            duration_per_test:int = 60,
            max_n_loads_to_test:int = 5,
            min_requests_per_second:int = 1
            ) -> Benchmark:
        test_executions = []

        max_acceptable_load = await self.test_execution_service.find_max_acceptable_load(
            test_case=test_case,
            request_per_second=min_requests_per_second,
            max_avg_response_time=max_response_time,
            duration_seconds=duration_per_test
        )

        test_executions.append(max_acceptable_load)
        logging.warning(f"Max acceptable load for {test_case.get_name()}: {max_acceptable_load.get_load()}")

        for load in range(
            max_acceptable_load.get_load() - 1,
            max(max_acceptable_load.get_load() - max_n_loads_to_test, 1),
            -1
        ):
            test_execution = await self.test_execution_service.find_max_requests_per_second(
                test_case=test_case,
                load=load,
                duration_seconds=duration_per_test,
                max_avg_response_time=max_response_time,
                start_power=math.floor(math.log2(test_executions[-1].request_per_second)) if test_executions else 1,
                max_power=10
            )

            test_executions.append(test_execution)
            logging.warning(f"Test execution for load {load}: {test_execution}")

        return Benchmark(test_executions=test_executions)

async def main():
    # Example usage
    from test_execution_service import TestExecutionService
    from fibonacci_test import FibonacciTest
    from bubble_sort_test import BubbleSortTest

    test_execution_service = TestExecutionService()
    benchmark_service = BenchmarkService(test_execution_service)

    test_case = BubbleSortTest(application_base_url="http://localhost:8080")

    benchmark = await benchmark_service.run_benchmark_single_test_case(test_case,duration_per_test=5,min_requests_per_second=2)

    print(benchmark.to_json())

if __name__ == "__main__":
    import asyncio
    asyncio.run(main())