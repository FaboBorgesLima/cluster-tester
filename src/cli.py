import argparse
import asyncio
from html import parser
from benchmark_service import BenchmarkService
from cluster_service import ClusterService
from test_execution_service import TestExecutionService
from json_storage_service import JsonStorageService
from get_cluster_from_config import get_cluster_from_config
from test_case import TestCase
import logging
from datetime import datetime

logging.basicConfig(level=logging.INFO)
def parse_test_case(app_url:str,test_case:str)->TestCase:
    match test_case:
        case "fibonacci":
            from fibonacci_test import FibonacciTest
            return FibonacciTest(application_base_url=app_url)
        case "bubble-sort":
            from bubble_sort_test import BubbleSortTest
            return BubbleSortTest(application_base_url=app_url)
        case _:
            raise ValueError(f"Unknown test case: {test_case}. Supported cases are: fibonacci, bubble-sort.")

async def main():
    parser = argparse.ArgumentParser(description="Run the benchmark service.")
    
    path = '/'.join(__file__.split('/')[0:-1])

    parser.add_argument('service', type=str, help='Service to run: benchmark, test-execution, data-analysis.')
    parser.add_argument('--storage', type=str, default=path+"/../db/", help='Path to the storage directory.')
    parser.add_argument('--config', type=str, default="config.json", help='Path to the configuration file.')
    parser.add_argument('--monitoring-interval', type=float, default=0.5, help='Interval for monitoring in seconds.')
    parser.add_argument('--duration-per-test', type=int, default=30, help='Duration of each test in seconds.')
    parser.add_argument('--test-cases', default=['fibonacci','bubble-sort'], type=str, nargs='+', help='List of test cases to run. For test-execution, only one test case is allowed.')
    parser.add_argument('--max-response-time', type=float, default=2.0, help='benchmark only: Maximum acceptable response time in seconds.')
    parser.add_argument('--max-n-loads-to-test', type=int, default=3, help='benchmark only: Maximum number of loads to test.')
    parser.add_argument('--min-requests-per-second', type=int, default=1, help='benchmark only: Minimum requests per second to test.')
    parser.add_argument('--rest-time', type=int, default=30, help='benchmark only: Rest time between tests in seconds.')
    parser.add_argument('--load', type=int, default=1, help='test-execution and data-analysis only: Load to apply during the test. For data-analysis, is the load to be compared.')
    parser.add_argument('--requests-per-second', type=int, default=1, help='test-execution only: Requests per second to apply during the test.')
    parser.add_argument('--files', type=str, nargs='+', help='data-analysis only: List of benchmark files to analyze.')
    parser.add_argument('--alias-hosts', type=str, nargs='+', help='data-analysis only: List of alias hosts for comparison. example: 192.168.1.2:us-east,192.168.1.3:us-west')
    parser.add_argument('--benchmark-names', default=[], type=str, nargs='+', help='data-analysis only: List of benchmark names for comparison.')
    parser.add_argument('analysis_type', type=str, nargs='?', help='data-analysis only: Type of analysis to perform: avg-response-time, ram-usage-load.')

    args = parser.parse_args()
    service = args.service.lower()
    storage_service = JsonStorageService(args.storage)
    config_data = storage_service.load(args.config)
    

    match service:
        case "benchmark":
            cluster = get_cluster_from_config(config_data)
            cluster_service = ClusterService()
            benchmark_service = BenchmarkService(
                test_execution_service=TestExecutionService(cluster_service=cluster_service),
            )
            args = parser.parse_args()
            test_cases = [parse_test_case(config_data['app']['url'], test_case) for test_case in args.test_cases]

            for test_case in test_cases:
                print(f"Running benchmark for test case: {test_case.__class__.__name__}")

            benchmarks = await benchmark_service.run_benchmark(
                test_cases=test_cases,
                cluster=cluster,
                duration_per_test=args.duration_per_test,
                rest_time=args.rest_time,
                max_response_time=args.max_response_time,
                max_n_loads_to_test=args.max_n_loads_to_test,
            )
            for benchmark in benchmarks:

                file_name = f"{benchmark.cluster.name}-{benchmark.test_case.get_name()}-{datetime.now().strftime('%Y%m%d_%H%M%S')}_benchmark.json"
                print(f"Benchmark completed. Saving results to {file_name} in {args.storage}") 
                
                storage_service.save(
                    file_name=file_name,
                    data=benchmark.to_json()  # Save the benchmark in a short JSON format
                )
        case "test-execution":
            cluster = get_cluster_from_config(config_data)
            cluster_service = ClusterService()
            test_execution_service = TestExecutionService(cluster_service=cluster_service)
            test_cases = [parse_test_case(config_data['app']['url'], test_case) for test_case in args.test_cases]
            if len(test_cases) != 1:
                raise ValueError("Test execution service can only run one test case at a time.")
            test_case = test_cases[0]
            print(f"Running test execution for test case: {test_case.__class__.__name__}")
            test_execution = await test_execution_service.execute_test_while_monitoring(
                test_case=test_case,
                cluster=cluster,
                duration_seconds=args.duration_per_test,
                monitoring_interval=args.monitoring_interval,
                load=args.load,
                request_per_second=args.requests_per_second,
            )
            file_name = f"{datetime.now().strftime('%Y%m%d_%H%M%S')}_test_execution.json"
            print(f"Test execution completed. Saving results to {file_name} in {args.storage}")
            if test_execution.has_errors():
                print(f"Test execution encountered errors: {test_execution.errors}")
            storage_service.save(
                file_name=file_name,
                data=test_execution.to_short_json()  # Save the test case in a short JSON format
            )
        case "data-analysis":
            from data_analysis_service import DataAnalysisService
            data_analysis_service = DataAnalysisService(storage_service=storage_service)
            if not args.files:
                raise ValueError("Data analysis service requires at least one benchmark file to analyze.")
            match args.analysis_type:
                case "avg-response-time":
                    for file in args.files:
                        
                        print(f"Analyzing average response time for benchmark file: {file}")
                        results = data_analysis_service.avg_response_time_benchmark(file)
                        print(f"Results for {file}:")
                        for result in results:
                            print(f"Load: {result['load']}, Avg Response Time: {result['avg_response_time']:.4f} seconds over {result['total_requests']} requests (at {result['rps']} RPS)")
               
                case "min-response-time":
                    for file in args.files:
                        print(f"Analyzing minimum response time for benchmark file: {file}")
                        results = data_analysis_service.min_response_time_benchmark(file)
                        print(f"Results for {file}:")
                        for result in results:
                            print(f"Load: {result['load']}, Min Response Time: {result['min_response_time']:.4f} seconds (at {result['rps']} RPS)")
                case "max-response-time":
                    for file in args.files:
                        print(f"Analyzing maximum response time for benchmark file: {file}")
                        results = data_analysis_service.max_response_time_benchmark(file)
                        print(f"Results for {file}:")
                        for result in results:
                            print(f"Load: {result['load']}, Max Response Time: {result['max_response_time']:.4f} seconds (at {result['rps']} RPS)")
                case "ram-usage":
                    for file in args.files:
                        print(f"Analyzing RAM usage for benchmark file: {file}")
                        results = data_analysis_service.ram_usage_benchmark(file)
                        print(f"Results for {file}:")
                        for result in results:
                            print(f"Load: {result['load']}(at {result['rps']} RPS)")
                            for host, ram_usage in result['avg_ram_usage'].items():
                                print(f"    Host: {host}, Avg RAM Usage: {ram_usage / 1024:.2f} MB")

                case "cpu-usage":
                    cpu_per_file = data_analysis_service.cpu_usage_files(args.files)
                    
                    for file, results in cpu_per_file.items():
                        print(f"Results for {file}:")
                        for result in results:
                            print(f"Load: {result['load']}(at {result['rps']} RPS)")
                            for host, cpu_usage in result['avg_cpu_usage'].items():
                                print(f"    Host: {host}, Avg CPU Usage: {cpu_usage:.2f} %")

                case "cpu-usage-compare":
                    alias_hosts = {}
                    if args.alias_hosts:
                        for alias in args.alias_hosts:
                            parts = alias.split(':')
                            if len(parts) != 2:
                                raise ValueError(f"Invalid alias host format: {alias}. Expected format is 'original_host:alias'.")
                            original_host, alias_name = parts
                            alias_hosts[original_host] = alias_name
                    cpu_per_host = data_analysis_service.cpu_usage_compare(args.files,args.load,alias_hosts,args.benchmark_names)

                    import matplotlib.pyplot as plt
                    import numpy as np

                    # 2. Preparar os dados para o gráfico
                    hosts = list(cpu_per_host.keys())
                    n_groups = len(hosts)
                    index = np.arange(n_groups)

                    # Pega os nomes dos benchmarks (k3s, k0s, etc.) do primeiro host
                    benchmark_names = list(cpu_per_host[hosts[0]].keys())
                    n_benchmarks = len(benchmark_names)

                    # Define a largura das barras
                    total_bar_width = 0.8  # Largura total para o grupo de barras
                    single_bar_width = total_bar_width / n_benchmarks

                    # 3. Criar a figura e os eixos
                    fig, ax = plt.subplots(figsize=(12, 7))

                    # 4. Criar as barras agrupadas
                    for i, benchmark_name in enumerate(benchmark_names):
                        # Calcula a posição de cada barra no grupo
                        bar_positions = [pos - (total_bar_width / 2) + (i * single_bar_width) + (single_bar_width / 2) for pos in index]
                        
                        # --- CORREÇÃO AQUI ---
                        # Coleta os valores de CPU e RPS separadamente
                        cpu_values = [cpu_per_host[host][benchmark_name]['cpu'] for host in hosts]
                        rps_values = [cpu_per_host[host][benchmark_name]['rps'] for host in hosts]
                        
                        # Plota as barras usando os valores de CPU
                        rects = ax.bar(bar_positions, cpu_values, single_bar_width, label=benchmark_name)
                        
                        # --- RÓTULOS ATUALIZADOS ---
                        
                        # 1. Adiciona o rótulo da CPU (%) ACIMA da barra
                        ax.bar_label(rects, padding=3, fmt='%.2f%%') # Adicionado '%%' para o símbolo %
                        
                        # 2. Adiciona o rótulo de RPS DENTRO da barra
                        for j, rect in enumerate(rects):
                            height = rect.get_height()
                            # Só adiciona o texto se a barra for alta o suficiente
                            if height > (ax.get_ylim()[1] * 0.1): # Se for > 10% da altura do gráfico
                                ax.text(
                                    rect.get_x() + rect.get_width() / 2, # Posição X (centro da barra)
                                    height / 2,                          # Posição Y (meio da barra)
                                    f"{rps_values[j]} RPS",              # O texto (ex: "5 RPS")
                                    ha='center',
                                    va='center',
                                    color='white',
                                    fontsize=8,
                                    fontweight='bold'
                                )

                    # 5. Configurar o gráfico (Títulos, Legendas, etc.)
                    ax.set_ylabel('Uso Médio de CPU (usr) %')
                    ax.set_xticks(index)
                    ax.set_xticklabels(hosts)
                    ax.legend(title='Distribuição')
                    ax.yaxis.grid(True, linestyle=':', alpha=0.7)
                    ax.set_ylim(bottom=0, top=ax.get_ylim()[1] * 1.15) # Aumenta o teto em 15%

                    plt.tight_layout()
                    
                    # 6. Salvar o arquivo
                    output_filename = f'cpu_usage_comparison_load_{args.load}_files_{"_".join(args.benchmark_names) if args.benchmark_names else "_".join(args.files)}.png'
                    plt.savefig(output_filename, dpi=300)
                    print(f"Gráfico de comparação de CPU salvo como {output_filename}")

                case "ram-usage-compare":
                    alias_hosts = {}
                    if args.alias_hosts:
                        for alias in args.alias_hosts:
                            parts = alias.split(':')
                            if len(parts) != 2:
                                raise ValueError(f"Invalid alias host format: {alias}. Expected format is 'original_host:alias'.")
                            original_host, alias_name = parts
                            alias_hosts[original_host] = alias_name
                    ram_per_host = data_analysis_service.ram_usage_compare(args.files,args.load,alias_hosts,args.benchmark_names)

                    import matplotlib.pyplot as plt
                    import numpy as np

                    

                    # 2. Preparar os dados para o gráfico
                    hosts = list(ram_per_host.keys())
                    n_groups = len(hosts)
                    index = np.arange(n_groups)

                    benchmark_names = list(ram_per_host[hosts[0]].keys())
                    n_benchmarks = len(benchmark_names)

                    # Define a largura das barras
                    total_bar_width = 0.8  # Largura total para o grupo de barras
                    single_bar_width = total_bar_width / n_benchmarks

                    # 3. Criar a figura e os eixos
                    fig, ax = plt.subplots(figsize=(12, 7))

                    # 4. Criar as barras agrupadas
                    for i, benchmark_name in enumerate(benchmark_names):
                        # Calcula a posição de cada barra no grupo
                        bar_positions = [pos - (total_bar_width / 2) + (i * single_bar_width) + (single_bar_width / 2) for pos in index]
                        
                        # Coleta os valores de RAM e RPS separadamente
                        ram_values = [ram_per_host[host][benchmark_name]['ram'] / 1024 for host in hosts]  # Converte para MB
                        rps_values = [ram_per_host[host][benchmark_name]['rps'] for host in hosts]
                        
                        # Plota as barras usando os valores de RAM
                        rects = ax.bar(bar_positions, ram_values, single_bar_width, label=benchmark_name)
                        
                        # 1. Adiciona o rótulo da RAM (MB) ACIMA da barra
                        ax.bar_label(rects, padding=3, fmt='%.1f MB')
                        
                        # 2. Adiciona o rótulo de RPS DENTRO da barra
                        for j, rect in enumerate(rects):
                            height = rect.get_height()
                            # Só adiciona o texto se a barra for alta o suficiente
                            if height > (ax.get_ylim()[1] * 0.1): # Se for > 10% da altura do gráfico
                                ax.text(
                                    rect.get_x() + rect.get_width() / 2, # Posição X (centro da barra)
                                    height / 2,                          # Posição Y (meio da barra)
                                    f"{rps_values[j]} RPS",              # O texto (ex: "5 RPS")
                                    ha='center',
                                    va='center',
                                    color='white',
                                    fontsize=8,
                                    fontweight='bold'
                                )

                    # 5. Configurar o gráfico (Títulos, Legendas, etc.)
                    ax.set_ylabel('Uso Médio de RAM (MB)')
                    ax.set_xticks(index)
                    ax.set_xticklabels(hosts)
                    ax.legend(title='Distribuição')
                    ax.yaxis.grid(True, linestyle=':', alpha=0.7)
                    ax.set_ylim(bottom=0, top=ax.get_ylim()[1] * 1.15) # Aumenta o teto em 15%

                    plt.tight_layout()

                    # 6. Salvar o arquivo
                    output_filename = f'ram_usage_comparison_load_{args.load}_{"_".join(args.benchmark_names) if args.benchmark_names else "_".join(args.files)}.png'
                    plt.savefig(output_filename, dpi=300)
                    print(f"Gráfico de comparação de RAM salvo como {output_filename}")
                case "response-time-compare":
                    response_time_data = data_analysis_service.response_time_compare(args.files, args.load, args.benchmark_names)

                    import matplotlib.pyplot as plt
                    import numpy as np

                    # Preparar os dados para o violin plot
                    data_for_plot = []
                    labels = []
                    rps_values = []
                    
                    for benchmark_name, data in response_time_data.items():
                        data_for_plot.append(data['response_times'])
                        labels.append(benchmark_name)
                        rps_values.append(data['rps'])

                    # Configurar o violin plot
                    fig, ax = plt.subplots(figsize=(12, 8))
                    
                    # Criar o violin plot
                    parts = ax.violinplot(data_for_plot, positions=range(len(labels)), 
                                         showmeans=True, showmedians=True, showextrema=True)
                    
                    # Personalizar as cores
                    colors = plt.cm.Set3(np.linspace(0, 1, len(labels)))
                    for pc, color in zip(parts['bodies'], colors):
                        pc.set_facecolor(color)
                        pc.set_alpha(0.7)
                    
                    # Configurar estilo das linhas
                    parts['cmeans'].set_color('red')
                    parts['cmeans'].set_linewidth(2)
                    parts['cmedians'].set_color('black')
                    parts['cmedians'].set_linewidth(2)
                    
                    # Adicionar estatísticas como texto
                    for i, (benchmark_name, data) in enumerate(response_time_data.items()):
                        response_times = data['response_times']
                        rps = data['rps']
                        mean_time = np.mean(response_times)
                        median_time = np.median(response_times)
                        std_time = np.std(response_times)
                        
                        # Adicionar texto com estatísticas incluindo RPS
                        ax.text(i, max(response_times) * 1.05, 
                               f'Mean: {mean_time:.3f}s\nMedian: {median_time:.3f}s\nStd: {std_time:.3f}s\nRPS: {rps}',
                               ha='center', va='bottom', fontsize=9, 
                               bbox=dict(boxstyle='round,pad=0.3', facecolor='white', alpha=0.8))

                    # Configurar o gráfico
                    ax.set_ylabel('Tempo de Resposta (segundos)')
                    ax.set_xlabel('Distribuições')
                    ax.set_xticks(range(len(labels)))
                    ax.set_xticklabels(labels, rotation=45 if len(max(labels, key=len)) > 8 else 0)
                    ax.yaxis.grid(True, linestyle=':', alpha=0.7)
                    ax.set_ylim(bottom=0)

                    # Adicionar legenda personalizada
                    from matplotlib.lines import Line2D
                    legend_elements = [
                        Line2D([0], [0], color='red', lw=2, label='Média'),
                        Line2D([0], [0], color='black', lw=2, label='Mediana')
                    ]
                    ax.legend(handles=legend_elements, loc='upper right')

                    plt.tight_layout()

                    # Salvar o arquivo
                    output_filename = f'response_time_load_{args.load}_{"_".join(args.benchmark_names) if args.benchmark_names else "_".join(args.files)}.png'
                    plt.savefig(output_filename, dpi=300, bbox_inches='tight')
                    print(f"Violin plot de tempos de resposta salvo como {output_filename}")
                case _:
                    raise ValueError(f"Unknown analysis type: {args.analysis_type}. Supported types are: avg-response-time, min-response-time, max-response-time.")

        case _:
            raise ValueError(f"Unknown service: {service}. Supported services are: benchmark, test-execution.")


if __name__ == "__main__":
    asyncio.run(main())

