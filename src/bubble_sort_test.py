from test_case import TestCase
from httpx import AsyncClient
from test_result import TestResult
from timespan import Timespan
import datetime

class BubbleSortTest(TestCase):
    def __init__(self,application_base_url: str ):
        super().__init__(description="Bubble Sort Test Case",
                         name="BubbleSortTestCase",
                        application_base_url=application_base_url,
                         min_recommended_load=10)

    async def run(self, load)-> TestResult:
        async with AsyncClient(base_url=self._application_base_url,timeout=30.0) as client:
            start_request = datetime.datetime.now(datetime.timezone.utc)
            response = await client.get(
                "/bubble-sort",
                params={"n": self.__convert_load(load)},
            )
            end_request = datetime.datetime.now(datetime.timezone.utc)
            start_time = datetime.datetime.fromisoformat(response.json().get('start'))
            end_time = datetime.datetime.fromisoformat(response.json().get('end'))
            return TestResult(
                test_case_name=self.get_name(),
                request_span=Timespan(start_request, end_request),
                server_processing_span=Timespan(start_time, end_time),
                load=load
            )

    @staticmethod
    def __convert_load(load:int)->int:
        return 2 ** load 