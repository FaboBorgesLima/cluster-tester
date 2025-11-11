import server_system_monitor

class Cluster:
    def __init__(self, name: str, servers: list[server_system_monitor.Monitor], config: dict ):
        
        self.name = name
        self.servers = servers
        self.config = config
        self.disabled = False

    def __repr__(self):
        return f"Cluster(name={self.name}, servers={self.servers})"

    def get_config(self) -> dict | None:
        """
        Retrieves the configuration for the cluster.
        :return: The configuration dictionary for the cluster, or None if not set.
        """
        return self.config

    def to_json(self) -> dict:
        """
        Converts the Cluster instance to a JSON-serializable dictionary.
        :return: A dictionary representation of the Cluster.
        """
        return {
            "name": self.name,
            "servers": len(self.servers)
        }