from cluster import Cluster
from cluster_stats import ClusterStats
from server_stats import ServerStats
from datetime import datetime

    
class ClusterService:
    async def get_stats(self, cluster: Cluster) -> ClusterStats:
        """
        Retrieves the statistics of the given cluster.
        :param cluster: The Cluster instance to retrieve the statistics for.
        :return: A dictionary representation of the cluster statistics.
        """
        server_stats = []
        for server in cluster.servers:
            server_stats.append(ServerStats(
                memory=server.server_client.send_ram(),
                stats=server.server_client.send_stats(),
                host=server.connection.get_hostname(),
                ping=server.connection.get_ping(),
                timestamp=datetime.now()
            ))

        return ClusterStats(
            servers=server_stats,
            timestamp=datetime.now()
        )