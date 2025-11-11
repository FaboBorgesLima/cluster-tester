from logging import config
from cluster import Cluster
from cluster_stats import ClusterStats
from server_stats import ServerStats
from datetime import datetime
from get_cluster_from_config import get_cluster_from_config

    
class ClusterService:
    async def get_stats(self, cluster: Cluster, retries: int = 2) -> ClusterStats:
        """
        Retrieves the statistics of the given cluster.
        :param cluster: The Cluster instance to retrieve the statistics for.
        :return: A dictionary representation of the cluster statistics.
        """
        if cluster.disabled:
            cluster = self.recreate_cluster(cluster)
        
        server_stats = []
        try:
            for server in cluster.servers:
                server_stats.append(ServerStats(
                    memory=server.server_client.send_ram(),
                    stats=server.server_client.send_stats(),
                    host=server.connection.get_hostname(),
                    ping=server.connection.get_ping(),
                    timestamp=datetime.now()
                ))
        except Exception as e:
            cluster.disabled = True
            if retries > 0:
                return await self.get_stats(self.recreate_cluster(cluster), retries - 1)
            else:
                raise e
            

        return ClusterStats(
            servers=server_stats,
            timestamp=datetime.now()
        )

    def recreate_cluster(self, cluster: Cluster) -> Cluster:
        """
        Recreates a Cluster instance from the provided configuration.
        
        :param config: Configuration dictionary containing cluster details.
        :return: An instance of Cluster initialized with the provided configuration.
        """
        return get_cluster_from_config(cluster.get_config())