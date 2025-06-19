import datetime

class ServerStats:
    def __init__(self, memory:dict, stats:dict, host:str, ping:dict, timestamp:datetime.datetime = datetime.datetime.now()):
        self.memory = memory
        self.stats = stats
        self.host = host
        self.timestamp = timestamp
        self.ping = ping

    def __repr__(self):
        return f"ServerStats(memory={self.memory}, stats={self.stats}, host={self.host}, timestamp={self.timestamp}, ping={self.ping})"
    def __str__(self):
        return self.__repr__()
    
    def __add__(self, other):
        if not isinstance(other, ServerStats):
            return NotImplemented
        return ServerStats(
            memory={
                "used": self.memory["used"] + other.memory["used"],
                "total": self.memory["total"] + other.memory["total"],
                "free": self.memory["free"] + other.memory["free"],
                "shared": self.memory["shared"] + other.memory["shared"],
                "buff/cache": self.memory["buff/cache"] + other.memory["buff/cache"],
                "available": self.memory["available"] + other.memory["available"]
            },
            stats={
                'cpu': (self.stats['cpu'] + other.stats['cpu']),
                'usr': (self.stats['usr'] + other.stats['usr']),
                'nice': (self.stats['nice'] + other.stats['nice']),
                'sys': (self.stats['sys'] + other.stats['sys']),
                'iowait': (self.stats['iowait'] + other.stats['iowait']),
                'irq': (self.stats['irq'] + other.stats['irq']),
                'soft': (self.stats['soft'] + other.stats['soft']),
                'steal': (self.stats['steal'] + other.stats['steal']),
                'guest': (self.stats['guest'] + other.stats['guest']),
                'gnice': (self.stats['gnice'] + other.stats['gnice']),
                'idle': (self.stats['idle'] + other.stats['idle']),
            },
            host=self.host,
            ping={k: (self.ping[k] + other.ping[k]) / 2 for k in self.ping},
            timestamp=max(self.timestamp, other.timestamp)
        )

    def __div__(self, other):
        if not isinstance(other, (int, float)):
            return NotImplemented
        return ServerStats(
            memory={
                "used": self.memory["used"] / other,
                "total": self.memory["total"] / other,
                "free": self.memory["free"] / other,
                "shared": self.memory["shared"] / other,
                "buff/cache": self.memory["buff/cache"] / other,
                "available": self.memory["available"] / other
            },
            stats={
                'cpu':self.stats['cpu'],
                'usr': float(self.stats['usr']) / other,
                'nice': float(self.stats['nice']) / other,
                'sys': float(self.stats['sys']) / other,
                'iowait': float(self.stats['iowait']) / other,
                'irq': float(self.stats['irq']) / other,
                'soft': float(self.stats['soft']) / other,
                'steal': float(self.stats['steal']) / other,
                'guest': float(self.stats['guest']) / other,
                'gnice': float(self.stats['gnice']) / other,
                'idle': float(self.stats['idle']) / other,
            },
            host=self.host,
            ping={k: self.ping[k] / other for k in self.ping},
            timestamp=self.timestamp
        )
    
    def to_json(self) -> dict:
        """
        Converts the ServerStats instance to a JSON-serializable dictionary.
        :return: A dictionary representation of the ServerStats.
        """
        return {
            "memory": self.memory,
            "stats": self.stats,
            "host": self.host,
            "timestamp": self.timestamp.isoformat(),
            "ping": self.ping
        }