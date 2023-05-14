class AlreadyExistsError(ValueError):
    """Raised when an attempt is made to add an object which already exists."""


class InvalidCharacterError(ValueError):
    """Raised when invalid character is passed."""


class InvalidOperationError(Exception):
    """Raised when an invalid operation is attempted."""


class NotFoundError(ValueError):
    """Raised when a required object is not found."""


class TransferSameAccountError(ValueError):
    """Raised when an attempt is made to set the recipient and the sender of a
    Transfer to the same Account."""
