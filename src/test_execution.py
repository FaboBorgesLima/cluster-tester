from timespan import Timespan
from test_case import TestCase
from test_result import TestResult

class TestExecution:
    def __init__(self, total_span: Timespan, span_making_requests: Timespan, test_case: TestCase, results: list[TestResult], request_per_second: int = 0, seconds_making_requests: int = 0):
        self.total_span = total_span
        self.span_making_requests = span_making_requests
        self.test_case = test_case
        self.results = results
        self.request_per_second = request_per_second
        self.seconds_making_requests = seconds_making_requests

    def avg_response_time(self) -> float:
        """
        Calculate the average response time from the test results.
        :return: The average response time.
        """
        if not self.results:
            raise ValueError("No test results available to calculate average response time.")

        total_response_time = sum(result.get_response_time() for result in self.results)
        return total_response_time / len(self.results)

    def __str__(self) -> str:
        return f"TestExecution(request_per_second={self.request_per_second}, seconds_making_requests={self.seconds_making_requests})"

    def __repr__(self) -> str:
        return f"TestExecution(request_per_second={self.request_per_second}, seconds_making_requests={self.seconds_making_requests})"