from test_case import TestCase
import asyncio
import logging
from test_execution import TestExecution
from datetime import datetime
from timespan import Timespan
import math

class TestExecutionService:
    async def execute_test(self, tests_per_second: int, duration_seconds: int, load: int, test_case: TestCase) -> TestExecution:
        start_execution_time = datetime.now()

        running_results = []
        if tests_per_second <= 0:
            raise ValueError("tests_per_second must be greater than zero.")
        interval = 1.0 / tests_per_second

        logging.info(f"Executing test case {test_case.get_name()} with {tests_per_second} requests per second for {duration_seconds} seconds with load {load}.")
        for _ in range(tests_per_second * duration_seconds):

            start_request_time = datetime.now()
            running_results.append(asyncio.create_task(test_case.run(load=load)))
            
            elapsed_time = (datetime.now() - start_request_time).total_seconds()
            logging.debug(f"Test case {test_case.get_name()} executed in {elapsed_time:.2f} seconds.")

            if elapsed_time < interval:
                logging.debug(f"Sleeping for {interval - elapsed_time:.2f} seconds to maintain {tests_per_second} requests per second.")
                await asyncio.sleep(interval - elapsed_time)
                logging.debug(f"Resuming after sleep.")
            else:
                logging.warning(f"Warning: Test case execution took longer than the interval: {elapsed_time:.2f} seconds, expected: {interval:.2f} seconds.")

        span_making_requests = Timespan(
            start=start_execution_time,
            end=datetime.now()
        )
        # Wait for all test case runs to complete
        running_results = await asyncio.gather(*running_results)

        return TestExecution(
            total_span=Timespan(
                start=start_execution_time,
                end=datetime.now()
            ),
            span_making_requests=span_making_requests,
            request_per_second=tests_per_second,
            seconds_making_requests=duration_seconds,
            test_case=test_case,
            results=running_results
        )

    async def rerun_test(self, test_execution: TestExecution) -> TestExecution:
        """
        Reruns a test execution with the same parameters as the original.
        :param test_execution: The TestExecution object containing the parameters to rerun.
        :return: A new TestExecution object with the results of the rerun.
        """
        logging.info(f"Rerunning test execution for {test_execution.test_case.get_name()} with {test_execution.request_per_second} requests per second.")
        return await self.execute_test(
            tests_per_second=test_execution.request_per_second,
            duration_seconds=test_execution.seconds_making_requests,
            load=test_execution.results[0].load if test_execution.results else 0,
            test_case=test_execution.test_case
        )

    async def find_max_acceptable_load(self, test_case: TestCase, request_per_second: int, duration_seconds: int, max_avg_response_time: float, load_increment: int = 1, max_iterations: int = 100) -> TestExecution:

        load = 0
        last_execution = None
        for _ in range(max_iterations):
            logging.info(f"Testing with load {load} and {request_per_second} requests per second.")
            try:
                execution = await self.execute_test(request_per_second, duration_seconds, load, test_case)
            except Exception as e:
                logging.error(f"Error during test execution: {e}")
                if last_execution:
                    logging.warning(f"Returning last successful execution with load {last_execution.request_per_second}.")
                    return last_execution
                raise e
            
            avg_result = execution.avg_response_time()
            last_execution = execution
            logging.info(f"Average result: {avg_result}")


            if avg_result > max_avg_response_time:
                logging.info(f"Exceeded max average response time with load: {load} requests per second.")
                return execution

            load += load_increment

        logging.error(f"Max acceptable load reached: {load} requests per second.")

        return await self.execute_test(request_per_second, duration_seconds, load, test_case)

    async def find_max_requests_per_second(
        self, test_case: TestCase, max_avg_response_time: float, load: int, duration_seconds: int = 1
    ) -> TestExecution:
        start_execution_time = datetime.now()

        test_power_of_two = await self.__test_powers_of_two_requests_until_exceeds_max_avg_response_time(
            test_case, max_avg_response_time, load, duration_seconds
        )
        
        if not test_power_of_two:
            logging.error("No test executions were performed.")
            return TestExecution(
                total_span=Timespan(start=start_execution_time, end=datetime.now()),
                span_making_requests=Timespan(start=start_execution_time, end=datetime.now()),
                test_case=test_case,
                results=[],
                request_per_second=0,
                seconds_making_requests=duration_seconds
            )

        last_power_two_execution = test_power_of_two[-1]

        # Use binary search to find the maximum requests per second
        lower_bound = int(2**(math.log2(last_power_two_execution.request_per_second) - 1))
        upper_bound = last_power_two_execution.request_per_second
        execution_results = []

        while lower_bound < upper_bound:
            mid = (lower_bound + upper_bound + 1) // 2
            logging.info(f"Testing with {mid} requests per second.")

            execution = await self.execute_test(mid, duration_seconds, load, test_case)
            execution_results.append(execution)

            if execution.avg_response_time() > max_avg_response_time:
                upper_bound = mid - 1
            else:
                lower_bound = mid

        logging.info(f"Max requests per second found: {lower_bound}")

        biggest_execution = self.biggest_execution_avg_lower_than_max_avg_response_time(
            test_executions=execution_results,
            max_avg_response_time=max_avg_response_time
        )

        return TestExecution(
            total_span=Timespan(start=start_execution_time, end=datetime.now()),
            span_making_requests=Timespan(start=start_execution_time, end=datetime.now()),
            test_case=test_case,
            results=biggest_execution.results,
            request_per_second=lower_bound,
            seconds_making_requests=duration_seconds
        )

    async def __test_powers_of_two_requests_until_exceeds_max_avg_response_time(
        self, test_case: TestCase, max_avg_response_time: float, load: int, duration_seconds: int = 1, max_power: int = 10
    ) -> list[TestExecution]:
        """
        Requests powers of two until the average response time exceeds the maximum allowed.
        :param test_case: The test case to run.
        :param max_avg_response_time: The maximum average response time allowed.
        :param load: The load to apply during the test.
        :param duration_seconds: The duration of the test in seconds.
        :return: A list of TestExecution objects containing the results of the tests, the last of which exceeds the max average response time.
        """
        power_of_two = 0
        test_executions = []

        for _ in range(max_power):
            tests_per_second = 2 ** power_of_two
            logging.info(f"Testing with {tests_per_second} tests per second.")

            execution = await self.execute_test(tests_per_second, duration_seconds, load, test_case)
            test_executions.append(execution)
            logging.info(f"Execution: {execution}")
            avg_result = execution.avg_response_time()
            logging.info(f"Average result: {avg_result}")

            if avg_result > max_avg_response_time:
                logging.info(f"Exceeded max average response time with {tests_per_second} tests per second.")
                return test_executions

            power_of_two += 1
        
        raise ValueError(
            f"Max iterations reached without exceeding max average response time ({max_avg_response_time} seconds) with load {load} and duration {duration_seconds} seconds."
        )


    @staticmethod
    def biggest_execution_avg_lower_than_max_avg_response_time(
        test_executions: list[TestExecution], max_avg_response_time: float
    ) -> TestExecution:
        """
        Finds the test execution with the largest average response time that is still lower than the specified maximum average response time.
        :param test_executions: List of TestExecution objects to search through.
        :param max_avg_response_time: The maximum average response time to compare against.
        :return: The TestExecution object with the largest average response time that is still lower than max_avg_response_time.
        """
        biggest_execution = None
        if not test_executions:
            raise ValueError("No test executions provided.")
            
        
        for execution in test_executions:
            avg_result = execution.avg_response_time()
            if avg_result < max_avg_response_time:
                if not biggest_execution or avg_result > biggest_execution.avg_response_time():
                    biggest_execution = execution

        if not biggest_execution:
            raise ValueError("No test execution found with average response time lower than the maximum allowed.")
        
        return biggest_execution
    

tes = TestExecutionService()
async def main():
    from fibonacci_test import FibonacciTest

    test_case = FibonacciTest(application_base_url="http://localhost:8080")
    max_avg_response_time = 1.0
    load = 10
    duration_seconds = 60
    
    

    execution = await tes.find_max_requests_per_second(
        test_case=test_case,
        max_avg_response_time=max_avg_response_time,
        load=load,
        duration_seconds=duration_seconds
    )
    
    print(f"Max requests per second found: {execution.request_per_second}")
    print(f"Total span: {execution.total_span}")
    print(f"Span making requests: {execution.span_making_requests}")
    print(f"Test case: {execution.test_case.get_name()}")
    print(f"Average response time: {execution.avg_response_time()} seconds")
    execution = await tes.rerun_test(execution)

    print(f"Rerun Test Execution: {execution}")
    print(f"Rerun Average response time: {execution.avg_response_time()} seconds")
asyncio.run(main())