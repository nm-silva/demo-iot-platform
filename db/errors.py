"""
This module contains the custom exceptions for the database module.
"""


class DatabaseError(Exception):
    """
    Base class for all database exceptions.
    """

    def __init__(self, message: str) -> None:
        super().__init__(message)
        self.message = message


class DatabaseConnectionError(DatabaseError):
    """
    Exception raised when a database connection cannot be established.
    """

    def __init__(self, message: str) -> None:
        super().__init__(message)


class DatabaseQueryError(DatabaseError):
    """
    Exception raised when a database query cannot be executed.
    """

    def __init__(self, message: str) -> None:
        super().__init__(message)


class DatabaseInsertionError(DatabaseError):
    """
    Exception raised when a database insertion operation fails.
    """

    def __init__(self, message: str) -> None:
        super().__init__(message)


class DatabaseDeletionError(DatabaseError):
    """
    Exception raised when a database deletion operation fails.
    """

    def __init__(self, message: str) -> None:
        super().__init__(message)


class DatabaseUpdateError(DatabaseError):
    """
    Exception raised when a database update operation fails.
    """

    def __init__(self, message: str) -> None:
        super().__init__(message)


class DatabaseCommitError(DatabaseError):
    """
    Exception raised when a database commit operation fails.
    """

    def __init__(self, message: str) -> None:
        super().__init__(message)
