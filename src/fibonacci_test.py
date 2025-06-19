import httpx
from test_case import TestCase
from test_result import TestResult
import datetime
from timespan import Timespan
import logging

class FibonacciTest(TestCase):

    def __init__(self, application_base_url: str):
        """
        Initializes the FibonacciTest with a specific application base URL.
        :param application_base_url: The base URL of the application to test.
        """
        super().__init__(
            name="FibonacciTestCase",
            description="This test measures the performance of the Fibonacci calculation endpoint.",
            application_base_url=application_base_url,
        )

    async def run(self, load: int) -> TestResult:
        async with httpx.AsyncClient(timeout=30.0) as client:
            start_request = datetime.datetime.now(datetime.timezone.utc)
            logging.debug(f"Starting request to {self._application_base_url}/fibonacci/{load} with load {load}")
            response = await client.get(f'{self._application_base_url}/fibonacci/{load}')  # Example endpoint
            logging.debug(f"Received response: {response.status_code} for load {load}")
            end_request = datetime.datetime.now(datetime.timezone.utc)
            start_server = datetime.datetime.fromisoformat(response.json().get('start'))
            end_server = datetime.datetime.fromisoformat(response.json().get('end'))

            return TestResult(
                test_case_name=self.get_name(),
                request_span=Timespan(start_request, end_request),
                server_processing_span=Timespan(start_server, end_server),
                load=load
            )

