from timespan import Timespan
from test_case import TestCase
from test_result import TestResult
from cluster_stats import ClusterStats

class TestExecution:
    def __init__(
            self,
            total_span: Timespan,
            span_making_requests: Timespan,
            test_case: TestCase,
            results: list[TestResult],
            request_per_second: int = 0,
            seconds_making_requests: int = 0,
            errors: list[Exception] = None,
            cluster_stats: list[ClusterStats] = None
    ):
        self.total_span = total_span
        self.span_making_requests = span_making_requests
        self.test_case = test_case

        self.results = results
        self.request_per_second = request_per_second
        self.seconds_making_requests = seconds_making_requests
        self.errors = errors if errors is not None else []
        self.cluster_stats = cluster_stats if cluster_stats is not None else []

    def avg_response_time(self) -> float:
        """
        Calculate the average response time from the test results.
        :return: The average response time.
        """
        if not self.results:
            raise ValueError("No test results available to calculate average response time.")
    
        total_response_time = sum(result.get_response_time() for result in self.results)
        return total_response_time / len(self.results)
    
    def avg_server_processing_time(self) -> float:
        """
        Calculate the average server processing time from the test results.
        :return: The average server processing time.
        """
        if not self.results:
            raise ValueError("No test results available to calculate average server processing time.")

        total_processing_time = sum(result.server_processing_span.get_seconds() for result in self.results)
        return total_processing_time / len(self.results)

    def get_load(self) -> int:
        """
        Get the load used for the test execution.
        :return: The load used for the test execution.
        """
        if not self.results:
            if self.errors:
                raise ValueError(f"No test results available to determine load. But test execution encountered errors: {self.errors}")
            raise ValueError("No test results available to determine load.")
        
        return self.results[0].load
    
    def get_avg_cluster_stats(self) -> ClusterStats:
        """
        Calculate the average cluster statistics from the test execution.
        :return: An instance of ClusterStats containing the average statistics.
        """
        if not self.cluster_stats:
            return None

        for cluster_stat in self.cluster_stats:
            if not isinstance(cluster_stat, ClusterStats):
                raise TypeError("All cluster stats must be instances of ClusterStats.")
            
        # Assuming all cluster stats have the same servers, we can average the stats
        servers = []
        for i, server in enumerate(self.cluster_stats[0].servers):
            avg_server_stats = server
            for cluster_stat in self.cluster_stats[1:]:
                avg_server_stats += cluster_stat.servers[i]
            
            servers.append(avg_server_stats.__div__(len(self.cluster_stats)))

        return ClusterStats(servers=servers)

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
            "errors": [str(error) for error in self.errors],
            "cluster_stats": [stat.to_json() for stat in self.cluster_stats] if self.cluster_stats else None
        }
    
    def to_short_json(self) -> dict:
        """
        Converts the TestExecution instance to a JSON-serializable dictionary with only essential fields.
        :return: A dictionary representation of the TestExecution with essential fields.
        """
        return {
            "test_case": self.test_case.get_name(),
            "load": self.get_load(),
            "avg_response_time": self.avg_response_time(),
            "avg_server_processing_time": self.avg_server_processing_time(),
            "request_per_second": self.request_per_second,
            "seconds_making_requests": self.seconds_making_requests,
            "span_making_requests": self.span_making_requests.to_json(),
            "total_span": self.total_span.to_json(),
            "errors": [str(error) for error in self.errors],
            "cluster_stats": self.get_avg_cluster_stats().to_json() if self.cluster_stats else None
        }

    def has_errors(self) -> bool:
        """
        Check if there are any errors in the test execution.
        :return: True if there are errors, False otherwise.
        """
        return len(self.errors) > 0