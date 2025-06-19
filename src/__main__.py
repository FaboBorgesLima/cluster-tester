from json_storage_service import JsonStorageService
from server_system_monitor import Monitor
from benchmark_service import BenchmarkService
from test_execution_service import TestExecutionService
from cluster_service import ClusterService
from datetime import datetime
from cluster import Cluster

path = '/'.join(__file__.split('/')[0:-1])

storage_service = JsonStorageService(path+"/../db/")

test = open(path+"/../db/config.json",'r')

config_data = storage_service.load('config.json')


data_servers = config_data['monitorServers']

monitors = []

for server_data in data_servers:
    monitors.append(
        Monitor.from_user_password(
            server_data['host'],
            server_data['authentication']['password'],
            server_data['authentication']['username'],
            server_data['port'],
        )
    )

cluster_service = ClusterService()

test_execution_service = TestExecutionService(cluster_service=cluster_service)

benchmark_service = BenchmarkService(
    test_execution_service=test_execution_service,
)

async def main():
    
    # Example usage
    cluster = Cluster(
        name=config_data['app']['name'],
        servers=monitors
    )

    from fibonacci_test import FibonacciTest
    from bubble_sort_test import BubbleSortTest

    bubble_sort_test = BubbleSortTest(application_base_url=config_data['app']['url'])
    fibonacci_test = FibonacciTest(application_base_url=config_data['app']['url'])
    # do not commit this
    fibonacci_tests = []
    
    fibonacci_tests.append(await test_execution_service.run_while_monitoring(
        test_case=fibonacci_test,
        cluster=cluster,
        duration_per_test=30,
        monitoring_interval=0.5,
        load=16,
        request_per_second=1,
    ))
    asyncio.sleep(30)
    fibonacci_tests.append(await test_execution_service.run_while_monitoring(
        test_case=fibonacci_test,
        cluster=cluster,
        duration_per_test=30,
        monitoring_interval=0.5,
        load=15,
        request_per_second=2,
    ))
    fibonacci_tests.append(await test_execution_service.run_while_monitoring(
        test_case=fibonacci_test,
        cluster=cluster,
        duration_per_test=30,
        monitoring_interval=0.5,
        load=14,
        request_per_second=4,
    ))
    storage_service.save(
        file_name=f"{datetime.now().strftime('%Y%m%d_%H%M%S')}_fibonacci_tests.json",
        data=[test.to_short_json() for test in fibonacci_tests]  # Save the tests in a short JSON format
    )
    print("done")
    #

    benchmark = await benchmark_service.run_benchmark(
        test_cases=[fibonacci_test, bubble_sort_test],
        cluster=cluster,
        duration_per_test=30,
        rest_time=30,
        max_response_time=2.0,
        max_n_loads_to_test=3,
    )

    storage_service.save(
        file_name=f"{datetime.now().strftime('%Y%m%d_%H%M%S')}_benchmark.json",
        data=benchmark.to_short_json()  # Save the benchmark in a short JSON format
    )

if __name__ == "__main__":
    import asyncio
    asyncio.run(main())
