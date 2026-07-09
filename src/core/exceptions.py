"""
OrderSync

Module:
    exceptions.py

Description:
    Custom exceptions used throughout the OrderSync application.

Author:
    Joan Solé

Version:
    1.0.0
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


class SqlServerConnectionError(OrderSyncError):
    """
    Raised when a connection to the SQL Server database cannot be established.
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


class ETLError(OrderSyncError):
    """
    Raised for ETL execution or monitoring errors.
    """
    pass