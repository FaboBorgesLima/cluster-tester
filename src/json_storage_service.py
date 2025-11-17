from test_execution_params import TestExecutionParams
import logging

class JsonStorageService:
    def __init__(self, base_path: str,):
        
        self.base_path = base_path

    def save(self, file_name: str, data):
        import json
        with open(f"{self.base_path}/{file_name}", 'w') as file:
            json.dump(data, file)
    

    def load(self, file_name: str):
        import json
        try:
            with open(f"{self.base_path}/{file_name}", 'r') as file:
                return json.load(file)
        except FileNotFoundError:
            return None

    ###
    # returns a dict mapping load -> {requests_per_second, seconds_making_requests}
    ###
    def load_benchmark_test_execution_params(self, file_name: str) -> dict[TestExecutionParams]:
        data = self.load(file_name)
        test_executions = data.get("test_executions")
        test_case_name = data.get("test_case_name")
        execution_params = []

        for test_execution in test_executions:
            load = test_execution.get("results")[0].get("load")
            requests_per_second = test_execution.get("request_per_second")
            seconds_making_requests = test_execution.get("seconds_making_requests")
            logging.info(f"{test_case_name} - load: {load}, rps: {requests_per_second}, duration: {seconds_making_requests}s")
            execution_params.append(TestExecutionParams(
                test_case_name=test_case_name,
                load=load,
                requests_per_second=requests_per_second,
                seconds_making_requests=seconds_making_requests
            ))

        return execution_params
