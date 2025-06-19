import server_system_monitor

class Cluster:
    def __init__(self, name: str, servers: list[server_system_monitor.Monitor]):
        
        self.name = name
        self.servers = servers

    def __repr__(self):
        return f"Cluster(name={self.name}, servers={self.servers})"

    def to_json(self) -> dict:
        """
        Converts the Cluster instance to a JSON-serializable dictionary.
        :return: A dictionary representation of the Cluster.
        """
        return {
            "name": self.name,
            "servers": len(self.servers)
        }