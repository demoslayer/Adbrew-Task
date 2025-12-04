"""
Database connection and configuration module.
"""
import os
import logging
from pymongo import MongoClient
from pymongo.errors import ConnectionFailure, ServerSelectionTimeoutError, PyMongoError
from typing import Optional

logger = logging.getLogger(__name__)


class DatabaseConnectionError(Exception):
    """Custom exception for database connection errors."""
    pass


class DatabaseOperationError(Exception):
    """Custom exception for database operation errors."""
    pass


class MongoDBManager:
    """
    Manages MongoDB connection with connection pooling and error handling.
    Implements singleton pattern to ensure single connection instance.
    """
    _instance: Optional['MongoDBManager'] = None
    _client: Optional[MongoClient] = None
    _db = None
    _todos_collection = None

    def __new__(cls):
        """Singleton pattern implementation."""
        if cls._instance is None:
            cls._instance = super(MongoDBManager, cls).__new__(cls)
        return cls._instance

    def __init__(self):
        """Initialize MongoDB manager without connecting immediately (lazy initialization)."""
        # Don't connect at initialization - wait until first use
        pass

    def _connect(self):
        """
        Establish MongoDB connection with proper error handling.
        Uses connection pooling and timeout settings.
        """
        try:
            mongo_host = os.environ.get("MONGO_HOST", "mongo")
            mongo_port = os.environ.get("MONGO_PORT", "27017")
            
            # Build connection URI with proper formatting
            mongo_uri = f"mongodb://{mongo_host}:{mongo_port}"
            
            # Connection options for production readiness
            connection_options = {
                'serverSelectionTimeoutMS': 5000,  # 5 second timeout
                'connectTimeoutMS': 10000,  # 10 second connection timeout
                'socketTimeoutMS': 20000,  # 20 second socket timeout
                'maxPoolSize': 50,  # Connection pool size
                'minPoolSize': 10,  # Minimum connections in pool
                'retryWrites': True,  # Enable retry for write operations
            }
            
            logger.info(f"Attempting to connect to MongoDB at {mongo_uri}")
            self._client = MongoClient(mongo_uri, **connection_options)
            
            # Test connection
            self._client.admin.command('ping')
            
            # Get database and collection
            self._db = self._client['test_db']
            self._todos_collection = self._db['todos']
            
            logger.info("Successfully connected to MongoDB")
            
        except (ConnectionFailure, ServerSelectionTimeoutError) as e:
            error_msg = f"Failed to connect to MongoDB at {mongo_uri}: {str(e)}"
            logger.error(error_msg)
            self._client = None
            raise DatabaseConnectionError(error_msg) from e
        except Exception as e:
            error_msg = f"Unexpected error connecting to MongoDB: {str(e)}"
            logger.error(error_msg)
            self._client = None
            raise DatabaseConnectionError(error_msg) from e

    def get_todos_collection(self):
        """
        Get the todos collection with connection validation.
        
        Returns:
            Collection: MongoDB todos collection
            
        Raises:
            DatabaseConnectionError: If connection is not established
        """
        if self._todos_collection is None:
            # Attempt to reconnect if connection was lost
            try:
                self._connect()
            except DatabaseConnectionError:
                raise DatabaseConnectionError(
                    "MongoDB connection not available. Please check database status."
                )
        
        # Verify connection is still alive
        try:
            self._client.admin.command('ping')
        except (ConnectionFailure, ServerSelectionTimeoutError) as e:
            logger.warning("MongoDB connection lost, attempting to reconnect...")
            self._client = None
            self._todos_collection = None
            self._connect()
        
        return self._todos_collection

    def close_connection(self):
        """Close MongoDB connection gracefully."""
        if self._client:
            try:
                self._client.close()
                logger.info("MongoDB connection closed")
            except Exception as e:
                logger.error(f"Error closing MongoDB connection: {str(e)}")
            finally:
                self._client = None
                self._db = None
                self._todos_collection = None


# Global instance - lazy initialization (connection happens on first use)
_db_manager_instance = None

def get_db_manager():
    """
    Get the global database manager instance (singleton pattern).
    Connection is established lazily on first use.
    """
    global _db_manager_instance
    if _db_manager_instance is None:
        _db_manager_instance = MongoDBManager()
    return _db_manager_instance

# For backward compatibility, create instance but don't connect
db_manager = MongoDBManager()

