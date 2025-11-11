from abc import ABC, abstractmethod 
from test_result import TestResult

class TestCase(ABC):
    """
    Abstract base class for a test suite.
    """
    def __init__(self, name: str, description: str, application_base_url: str, min_recommended_load: int = 1):
        self._name = name
        self._description = description
        self._application_base_url = application_base_url
        self._min_recommended_load = min_recommended_load

    @abstractmethod
    async def run(self, load: int) -> TestResult:
        """
        Run the test case and return a TestResult object.
        This method must be implemented by subclasses.
        :return: TestResult object containing the results of the test case.
        """
        pass

    def get_min_recommended_load(self) -> int:
        return self._min_recommended_load


    def get_name(self) -> str:
        return self._name
    
    def get_description(self) -> str:
        return self._description
    def to_json(self) -> dict:
        """
        Converts the TestCase instance to a JSON-serializable dictionary.
        :return: A dictionary representation of the TestCase.
        """
        return {
            "name": self._name,
            "description": self._description,
            "application_base_url": self._application_base_url,
            "min_recommended_load": self._min_recommended_load
        }