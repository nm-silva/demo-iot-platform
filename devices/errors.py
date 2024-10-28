"""
This module has all the common errors that can be raised by the device manager.
"""


class DeviceManagerError(Exception):
    """
    Base class for all device manager errors.
    """

    def __init__(self, message: str) -> None:
        super().__init__(message)


class DeviceNotFoundError(DeviceManagerError):
    """
    Raised when a device is not found in the device manager.
    """

    def __init__(self, message: str) -> None:
        super().__init__(message)


class DeviceAlreadyExistsError(DeviceManagerError):
    """
    Raised when a device with the same name already exists in the device manager.
    """

    def __init__(self, message: str) -> None:
        super().__init__(message)


class DeviceTypeError(DeviceManagerError):
    """
    Raised when an invalid device type is passed to the device manager.
    """

    def __init__(self, message: str) -> None:
        super().__init__(message)
