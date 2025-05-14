class AuthenticationError(Exception):
    """Exception raised for authentication errors."""
    def __init__(self, message="Authentication failed!"):
        super().__init__(message)