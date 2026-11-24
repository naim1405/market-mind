class AppError(Exception):
    """Base class for all application errors."""

class NotFoundError(AppError):
    """Raised when a requested resource is not found."""
    def __init__(self, resource: str):
        self.message = f"{resource} not found."
        super().__init__(self.message)



class ConflictError(AppError):
    """ Raised when there is a conflict with the current state of the resource."""
    def __init__(self, resource: str):
        self.message = f"{resource} not found."
        super().__init__(self.message)
