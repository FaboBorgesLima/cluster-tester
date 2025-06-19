from cluster_service import ClusterService
from cluster import Cluster
import asyncio

class BackgroundClusterMonitoring:
    def __init__(self, cluster_service: ClusterService, cluster: Cluster):
        self.cluster_service = cluster_service
        self._running = False
        self.cluster = cluster
        self.stats = []

    async def run(self, interval: float):
        self._running = True
        
        while self._running:
            self.stats.append(await self.cluster_service.get_stats(self.cluster))
            await asyncio.sleep(interval)
        

    async def stop(self):
        self._running = False
        # Optionally, you can add logic to clean up resources or notify other components that monitoring has stopped.
    
    def is_running(self) -> bool:
        """
        Check if the background monitoring task is currently running.
        :return: True if the task is running, False otherwise.
        """
        return self._running