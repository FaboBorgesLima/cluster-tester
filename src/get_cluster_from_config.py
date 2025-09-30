from cluster import Cluster
from server_system_monitor import Monitor

def get_cluster_from_config(config)-> Cluster:
    """
    Retrieves a Cluster instance based on the provided configuration.
    
    :param config: Configuration dictionary containing cluster details.
    :return: An instance of Cluster initialized with the provided configuration.
    """
    servers = []
    for server_config in config['monitorServers']:
        server = Monitor.from_user_password(
            server_config['host'],
            server_config['authentication']['password'],
            server_config['authentication']['username'],
            server_config['port'],
        )
        servers.append(server)

    return Cluster(name=config['app']['name'], servers=servers)