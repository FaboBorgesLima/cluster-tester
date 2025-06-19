from test_execution_service import TestExecutionService
from test_case import TestCase
from benchmark import Benchmark
import math
from cluster_service import ClusterService
from test_result import TestResult
from test_execution import TestExecution
from cluster import Cluster
import logging
import datetime
import json
import timespan
import asyncio

class BenchmarkService:
    def __init__(self, test_execution_service: TestExecutionService):
        self.test_execution_service = test_execution_service

    async def run_benchmark(
            self, 
            test_cases: list[TestCase], 
            cluster: Cluster,
            max_response_time :float = 2.0,
            duration_per_test:int = 30,
            max_n_loads_to_test:int = 3,
            min_requests_per_second:int = 1,
            rest_time:int = 30
        ) -> list[Benchmark]:
        """
        Run a benchmark for a list of test cases.
        :param test_cases: List of TestCase objects to run.
        :return: List of Benchmark objects  containing the results of the benchmark.
        """
        if not test_cases:
            raise ValueError("No test cases provided for benchmarking.")

        benchmark_results = []
        
        for test_case in test_cases:
            result = await self.run_benchmark_single_test_case(test_case, cluster=cluster, max_response_time=max_response_time, duration_per_test=duration_per_test, max_n_loads_to_test=max_n_loads_to_test, min_requests_per_second=min_requests_per_second, rest_time=rest_time)
            await asyncio.sleep(rest_time) if rest_time > 0 else None
            benchmark_results.append(result)

        return benchmark_results

    async def run_benchmark_single_test_case(
            self, 
            test_case: TestCase,
            cluster: Cluster,
            max_response_time :float = 2.0,
            duration_per_test:int = 30,
            max_n_loads_to_test:int = 3,
            min_requests_per_second:int = 2,
            rest_time:int = 30
            ) -> Benchmark:
        # dry run to get the cluster stats
        await self.test_execution_service.cluster_service.get_stats(cluster)

        test_executions = []

        max_acceptable_load = await self.test_execution_service.find_max_acceptable_load(
            test_case=test_case,
            request_per_second=min_requests_per_second,
            max_avg_response_time=max_response_time,
            duration_seconds=duration_per_test,
            rest_time=rest_time,
        )

        logging.warning(
            f"Max acceptable load for {test_case.get_name()} is {max_acceptable_load.get_load()}. responded in {max_acceptable_load.avg_response_time()} ms average response time."
        )

        max_acceptable_load_and_requests_per_second = await self.test_execution_service.find_max_requests_per_second(
            test_case=test_case,
            load=max_acceptable_load.get_load(),
            duration_seconds=duration_per_test,
            max_avg_response_time=max_response_time,
            rest_time=rest_time
        )

        test_executions.append(max_acceptable_load_and_requests_per_second)

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
                max_power=10,
                rest_time=rest_time,
            )

            test_executions.append(test_execution)
        
        rerun_with_monitoring = []

        for test_execution in test_executions:
            await asyncio.sleep(rest_time) if rest_time > 0 else None
            rerun_with_monitoring.append(
                await self.test_execution_service.rerun_while_monitoring(
                    test_execution=test_execution,
                    monitoring_interval=1.0,
                    cluster=cluster
                )
            )

        return Benchmark(test_executions=rerun_with_monitoring, test_case=test_case, cluster=cluster)
