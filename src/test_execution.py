from timespan import Timespan
from test_case import TestCase
from test_result import TestResult

class TestExecution:
    def __init__(self, total_span: Timespan, span_making_requests: Timespan, test_case: TestCase, results: list[TestResult], request_per_second: int = 0, seconds_making_requests: int = 0,errors: list[Exception] = None):
        self.total_span = total_span
        self.span_making_requests = span_making_requests
        self.test_case = test_case

        if not results:
            raise ValueError("Results cannot be empty.")
        self.results = results
        self.request_per_second = request_per_second
        self.seconds_making_requests = seconds_making_requests
        self.errors = errors if errors is not None else []

    def avg_response_time(self) -> float:
        """
        Calculate the average response time from the test results.
        :return: The average response time.
        """
        if not self.results:
            raise ValueError("No test results available to calculate average response time.")

        total_response_time = sum(result.get_response_time() for result in self.results)
        return total_response_time / len(self.results)

    def get_load(self) -> int:
        """
        Get the load used for the test execution.
        :return: The load used for the test execution.
        """
        if not self.results:
            raise ValueError("No test results available to determine load.")
        
        return self.results[0].load
    
    def __str__(self) -> str:
        return f"TestExecution(request_per_second={self.request_per_second}, seconds_making_requests={self.seconds_making_requests},avg_response_time={self.avg_response_time()}, load={self.get_load()})"

    def __repr__(self) -> str:
        return self.__str__()
    
    def to_json(self) -> dict:
        """
        Converts the TestExecution instance to a JSON-serializable dictionary.
        :return: A dictionary representation of the TestExecution.
        """
        return {
            "total_span": self.total_span.to_json(),
            "span_making_requests": self.span_making_requests.to_json(),
            "test_case": self.test_case.to_json(),
            "results": [result.to_json() for result in self.results],
            "request_per_second": self.request_per_second,
            "seconds_making_requests": self.seconds_making_requests,
            "errors": [str(error) for error in self.errors]
        }