from server_stats import ServerStats
import datetime

class ClusterStats:
    """
    Represents the statistics of a cluster of servers.
    """

    def __init__(self, servers: list[ServerStats], timestamp: datetime.datetime = datetime.datetime.now()):
        """
        Initializes the ClusterStats with a list of ServerStats and a timestamp.
        :param servers: A list of ServerStats instances representing the servers in the cluster.
        :param timestamp: The timestamp when the stats were collected.
        """
        self.servers = servers
        self.timestamp = timestamp

    def __repr__(self):
        return f"ClusterStats(servers={self.servers}, timestamp={self.timestamp})"

    def to_json(self) -> dict:
        """
        Converts the ClusterStats instance to a JSON-serializable dictionary.
        :return: A dictionary representation of the ClusterStats.
        """
        return {
            "servers": [server.to_json() for server in self.servers],
            "timestamp": self.timestamp.isoformat()
        }