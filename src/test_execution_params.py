class TestExecutionParams:
    def __init__(
        self, 
        test_case_name: str, 
        load: str, 
        requests_per_second: int, 
        seconds_making_requests: int):
        
        self.test_case_name = test_case_name
        self.load = load
        self.requests_per_second = requests_per_second
        self.seconds_making_requests = seconds_making_requests