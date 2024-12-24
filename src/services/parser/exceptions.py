class ResumeParsingError(Exception):
    """
    Custom exception class for resume parsing errors.

    Attributes:
        message (str): Error message
        code (int): Error code (optional)
        details (dict): Additional error details (optional)
    """

    def __init__(self, message: str, code: int = None, details: dict = None):
        self.message = message
        self.code = code
        self.details = details or {}
        super().__init__(self.message)

    def __str__(self) -> str:
        error_msg = self.message
        if self.code:
            error_msg = f"[{self.code}] {error_msg}"
        if self.details:
            error_msg = f"{error_msg} - Details: {self.details}"
        return error_msg
