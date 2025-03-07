class FlightDataFetchError(Exception):
    """Custom exception raised when flight data cannot be retrieved after multiple attempts."""

    def __init__(
        self, message="Could not retrieve flight data after multiple attempts."
    ):
        self.message = message
        super().__init__(self.message)
