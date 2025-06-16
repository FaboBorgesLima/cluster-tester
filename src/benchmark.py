from test_execution import TestExecution

class Benchmark:
    def __init__(self, test_executions:list[TestExecution], test_case_name:str = None):
        """
        Initializes the Benchmark with a list of test executions.
        :param test_executions: A list of TestExecution objects.
        :param test_case_name: Optional name of the test case for which the benchmark is run.
        """
        if not test_executions:
            raise ValueError("Test executions cannot be empty.")
        self.test_executions = test_executions
        self.test_case_name = test_case_name
    
    def __repr__(self):
        return f"Benchmark(test_executions={self.test_executions}, test_case_name={self.test_case_name})"

    def __str__(self):
        return self.__repr__()
    
    def to_json(self) -> dict:
        """
        Converts the Benchmark instance to a JSON-serializable dictionary.
        :return: A dictionary representation of the Benchmark.
        """
        return {
            "test_executions": [execution.to_json() for execution in self.test_executions],
            "test_case_name": self.test_case_name
        }