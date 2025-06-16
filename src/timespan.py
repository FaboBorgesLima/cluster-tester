
from datetime import datetime

class Timespan:

    def __init__(self,start:datetime, end:datetime):
        """
        Initializes the TimeSpan with a start and end datetime.
        :param start: The start datetime.
        :param end: The end datetime.
        """
        self.start = start
        self.end = end
        if start > end:
            raise ValueError("Start time must be before end time.")
    
    def __repr__(self):
        return f"Timespan(start={self.start}, end={self.end})"