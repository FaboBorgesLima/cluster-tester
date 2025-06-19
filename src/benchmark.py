from test_execution import TestExecution
from test_case import TestCase
from cluster import Cluster

class Benchmark:
    def __init__(self, test_executions:list[TestExecution], test_case:TestCase = None, cluster: Cluster = None):
        """
        Initializes the Benchmark with a list of test executions.
        :param test_executions: A list of TestExecution objects.
        :param test_case: Optional name of the test case for which the benchmark is run.
        """
        if not test_executions:
            raise ValueError("Test executions cannot be empty.")
        self.test_executions = test_executions
        self.test_case = test_case
        self.cluster = cluster
    
    def __repr__(self):
        return f"Benchmark(test_executions={self.test_executions}, test_case={self.test_case}, cluster={self.cluster})"

    def __str__(self):
        return self.__repr__()
    
    def to_json(self) -> dict:
        """
        Converts the Benchmark instance to a JSON-serializable dictionary.
        :return: A dictionary representation of the Benchmark.
        """
        return {
            "test_executions": [execution.to_json() for execution in self.test_executions],
            "test_case_name": self.test_case.get_name()
        }

    def to_short_json(self) -> dict:
        """
        Converts the Benchmark instance to a JSON-serializable dictionary with only essential fields.
        :return: A dictionary representation of the Benchmark with essential fields.
        """
        return {
            "test_executions": [execution.to_short_json() for execution in self.test_executions],
            "test_case_name": self.test_case.to_json(),
            "cluster": self.cluster.to_json()
        }