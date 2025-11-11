from json_storage_service import JsonStorageService
import matplotlib as plt 
from datetime import datetime

class DataAnalysisService:
    def __init__(self, storage_service: JsonStorageService):
        self.storage_service = storage_service

    def avg_response_time_benchmark(self, benchmark_filename: str) -> list[dict]:
        benchmark_data = self.storage_service.load(benchmark_filename)
        load_response_time_requests = []
        
        for execution in benchmark_data['test_executions']:
            load = 0
            total_response_time = 0.0
            total_requests = 0
            requests_per_second = execution.get('request_per_second', 1)

            for result in execution['results']:
                load = result['load']
                total_response_time += (datetime.fromisoformat(result['server_processing_span']['end']) - datetime.fromisoformat(result['server_processing_span']['start'])).total_seconds()
                total_requests += 1
            if load not in load_response_time_requests:
                load_response_time_requests.append({'load': load,'rps': requests_per_second, 'total_response_time': total_response_time, 'total_requests': total_requests, 'avg_response_time': total_response_time / total_requests if total_requests > 0 else 0.0})

        return load_response_time_requests
    
    def response_times_benchmark(self, benchmark_filename: str) -> list[dict]:
        benchmark_data = self.storage_service.load(benchmark_filename)
        load_response_times = []
        
        for execution in benchmark_data['test_executions']:
            load = 0
            response_times = []
            requests_per_second = execution.get('request_per_second', 1)

            for result in execution['results']:
                load = result['load']
                response_time = (datetime.fromisoformat(result['server_processing_span']['end']) - datetime.fromisoformat(result['server_processing_span']['start'])).total_seconds()
                response_times.append(response_time)
            load_response_times.append({'load': load,'rps': requests_per_second, 'response_times': response_times})

        return load_response_times
    
    def min_response_time_benchmark(self, benchmark_filename: str) -> list[dict]:
        benchmark_data = self.storage_service.load(benchmark_filename)
        load_min_response_time = []
        
        for execution in benchmark_data['test_executions']:
            load = 0
            min_response_time = float('inf')
            requests_per_second = execution.get('request_per_second', 1)

            for result in execution['results']:
                load = result['load']
                response_time = (datetime.fromisoformat(result['server_processing_span']['end']) - datetime.fromisoformat(result['server_processing_span']['start'])).total_seconds()
                if response_time < min_response_time:
                    min_response_time = response_time
            load_min_response_time.append({'load': load,'rps': requests_per_second, 'min_response_time': min_response_time})

        return load_min_response_time
    
    def max_response_time_benchmark(self, benchmark_filename: str) -> list[dict]:
        benchmark_data = self.storage_service.load(benchmark_filename)
        load_max_response_time = []
        
        for execution in benchmark_data['test_executions']:
            load = 0
            max_response_time = float('-inf')
            requests_per_second = execution.get('request_per_second', 1)

            for result in execution['results']:
                load = result['load']
                response_time = (datetime.fromisoformat(result['server_processing_span']['end']) - datetime.fromisoformat(result['server_processing_span']['start'])).total_seconds()
                if response_time > max_response_time:
                    max_response_time = response_time
            load_max_response_time.append({'load': load,'rps': requests_per_second, 'max_response_time': max_response_time})

        return load_max_response_time
    
    def ram_usage_files(self,benchmark_files:list[str])->list[dict]:
        combined_ram_usage = []
        for file in benchmark_files:
            file_ram_usage = self.ram_usage_benchmark(file)
            combined_ram_usage.extend(file_ram_usage)
        return combined_ram_usage
    
    def ram_usage_benchmark(self, benchmark_filename: str) -> list[dict]:
        benchmark_data = self.storage_service.load(benchmark_filename)
        load_ram_usage = []
        
        for execution in benchmark_data['test_executions']:
            load = 00
            requests_per_second = execution.get('request_per_second', 1)
            total_per_server_ram = {}
            measures_count = 0

            for result in execution['results']:
                load = result['load']


            for monitoring in execution.get('cluster_stats', []):

                for server in monitoring.get('servers', []):
                    total_per_server_ram[server['host']] = total_per_server_ram.get(server['host'], 0) + server['memory']['used']
                measures_count += 1

            avg_per_server_ram = {
                host: (total_ram / measures_count)  # Convert to MB
                for host, total_ram in total_per_server_ram.items()
            }

            load_ram_usage.append({'load': load,'rps': requests_per_second, 'avg_ram_usage': avg_per_server_ram})

        return load_ram_usage

    def cpu_usage_files(self,benchmark_files:list[str])->list[dict]:
        combined_cpu_usage = {}
        for file in benchmark_files:
            file_cpu_usage = self.cpu_usage_benchmark(file)
            combined_cpu_usage[file] = file_cpu_usage
        return combined_cpu_usage
    
    def cpu_usage_benchmark(self, benchmark_filename: str) -> list[dict]:
        benchmark_data = self.storage_service.load(benchmark_filename)
        load_cpu_usage = []
        
        for execution in benchmark_data['test_executions']:
            load = 0
            requests_per_second = execution.get('request_per_second', 1)
            total_per_server_cpu = {}
            measures_count = 0

            for result in execution['results']:
                load = result['load']


            for monitoring in execution.get('cluster_stats', []):

                for server in monitoring.get('servers', []):
                    total_per_server_cpu[server['host']] = total_per_server_cpu.get(server['host'], 0) + server['stats']['usr']
                measures_count += 1

            avg_per_server_cpu = {
                host: (total_cpu / measures_count)  # Average CPU usage
                for host, total_cpu in total_per_server_cpu.items()
            }

            load_cpu_usage.append({'load': load,'rps': requests_per_second, 'avg_cpu_usage': avg_per_server_cpu})

        return load_cpu_usage

    def cpu_usage_compare(self,benchmark_files:list[str],load:int,alias_hosts:dict[str,str],test_name_for_file:list[str])->dict:
        group_by_host_cpu_usage = {}
        if not test_name_for_file or len(test_name_for_file) != len(benchmark_files):
            test_name_for_file = [f"benchmark_{i+1}" for i in range(len(benchmark_files))]

        for file, test_name in zip(benchmark_files, test_name_for_file):
            file_cpu_usage = self.cpu_usage_benchmark(file)
            for entry in file_cpu_usage:
                if entry['load'] == load:
                    requests_per_second = entry['rps']
                    for host, cpu_usage in entry['avg_cpu_usage'].items():
                        alias_host = alias_hosts.get(host, host)
                        if alias_host not in group_by_host_cpu_usage:
                            group_by_host_cpu_usage[alias_host] = {}
                        group_by_host_cpu_usage[alias_host][test_name] = {
                            "cpu": cpu_usage,
                            "rps": requests_per_second
                        }
            
        return group_by_host_cpu_usage

    def ram_usage_compare(self,benchmark_files:list[str],load:int,alias_hosts:dict[str,str],test_name_for_file:list[str])->dict:
        group_by_host_ram_usage = {}
        if not test_name_for_file or len(test_name_for_file) != len(benchmark_files):
            test_name_for_file = [f"benchmark_{i+1}" for i in range(len(benchmark_files))]

        for file, test_name in zip(benchmark_files, test_name_for_file):
            file_ram_usage = self.ram_usage_benchmark(file)
            for entry in file_ram_usage:
                if entry['load'] == load:
                    requests_per_second = entry['rps']
                    for host, ram_usage in entry['avg_ram_usage'].items():
                        alias_host = alias_hosts.get(host, host)
                        if alias_host not in group_by_host_ram_usage:
                            group_by_host_ram_usage[alias_host] = {}
                        group_by_host_ram_usage[alias_host][test_name] = {
                            "ram": ram_usage,
                            "rps": requests_per_second
                        }
            
        return group_by_host_ram_usage

    def response_time_compare(self,benchmark_files:list[str],load:int,test_name_for_file:list[str])->dict:
        response_time_comparison = {}
        if not test_name_for_file or len(test_name_for_file) != len(benchmark_files):
            test_name_for_file = [f"benchmark_{i+1}" for i in range(len(benchmark_files))]

        for file, test_name in zip(benchmark_files, test_name_for_file):
            response_times= self.response_times_benchmark(file)
            for entry in response_times:
                if entry['load'] == load:
                    response_time_comparison[test_name] = {
                        "response_times": entry['response_times'],
                        "rps": entry['rps']
                    }

        return response_time_comparison