from timespan import Timespan

class TestResult:
    """
    Represents the result of a test case execution.
    """

    def __init__(self, test_case_name: str, load: int, request_span: Timespan, server_processing_span: Timespan):
        """
        Initializes the TestResult with the name of the test case and its performance metrics.
        :param test_case_name: The name of the test case.
        :param request_span: The time taken for the request.
        :param server_processing_span: The time taken by the server to process the request.
        """

        self.test_case_name = test_case_name
        self.load = load
        self.request_span = request_span
        self.server_processing_span = server_processing_span
    
    def get_response_time(self) -> float:
        """
        Calculate the total response time for the test case.
        :return: The total response time in seconds.
        """
        return (self.request_span.end - self.request_span.start).total_seconds()

    def __repr__(self):
        return f"TestResult(test_case_name={self.test_case_name}, load={self.load}, request_span={self.request_span}, server_processing_span={self.server_processing_span})"
    
    def to_json(self) -> dict:
        """
        Converts the TestResult instance to a JSON-serializable dictionary.
        :return: A dictionary representation of the TestResult.
        """
        return {
            "test_case_name": self.test_case_name,
            "load": self.load,
            "request_span": {
                "start": self.request_span.start.isoformat(),
                "end": self.request_span.end.isoformat()
            },
            "server_processing_span": {
                "start": self.server_processing_span.start.isoformat(),
                "end": self.server_processing_span.end.isoformat()
            }
        }
