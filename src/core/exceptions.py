"""
OrderSync

Module:
    exceptions.py
    
Location:
    src\\core

Description:
    Custom exceptions used throughout the OrderSync application.

Author:
    Joan Solé

"""


class OrderSyncError(Exception):
    """
    Base class for all OrderSync exceptions.
    """
    pass


class ConfigurationError(OrderSyncError):
    """
    Raised when the application configuration is invalid or incomplete.
    """
    pass


class HyperFileConnectionError(OrderSyncError):
    """
    Raised when a connection to the HyperFile database cannot be established.
    """
    pass


class ValidationError(OrderSyncError):
    """
    Raised when one or more fields fail validation.
    """
    pass


class RepositoryError(OrderSyncError):
    """
    Raised when a repository operation fails.
    """
    pass


class SynchronizationError(OrderSyncError):
    """
    Raised when an error occurs during the synchronization process.
    """
    pass


class SqlServerConnectionError(OrderSyncError):
    """
    Raised when a SQL Server connection or operation fails.
    """
    pass