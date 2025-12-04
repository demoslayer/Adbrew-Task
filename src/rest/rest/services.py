"""
Service layer for TODO operations.
Separates business logic from API views for better maintainability and testability.
"""
import logging
from datetime import datetime
from typing import List, Dict, Optional
from pymongo.errors import PyMongoError

from .database import get_db_manager, DatabaseConnectionError, DatabaseOperationError

logger = logging.getLogger(__name__)


class TodoService:
    """
    Handles all database operations and data transformations.
    """
    
    @staticmethod
    def get_all_todos() -> List[Dict]:
        """
        Retrieve all TODO items from the database.
        
        Returns:
            List[Dict]: List of todo dictionaries with id, description, and created_at
            
        Raises:
            DatabaseConnectionError: If database connection fails
            DatabaseOperationError: If database operation fails
        """
        try:
            db_manager = get_db_manager()
            todos_collection = db_manager.get_todos_collection()
            
            # Fetch all todos from MongoDB collection
            todos_cursor = todos_collection.find({}).sort('created_at', -1)  # Sort by newest first
            
            # Convert MongoDB documents to list of dictionaries
            todos = []
            for todo in todos_cursor:
                todos.append({
                    'id': str(todo['_id']),
                    'description': todo.get('description', ''),
                    'created_at': todo.get('created_at', datetime.utcnow()).isoformat()
                })
            
            logger.info(f"Successfully retrieved {len(todos)} todos")
            return todos
            
        except DatabaseConnectionError:
            # Re-raise connection errors as-is
            raise
        except PyMongoError as e:
            error_msg = f"Database error while retrieving todos: {str(e)}"
            logger.error(error_msg)
            raise DatabaseOperationError(error_msg) from e
        except Exception as e:
            error_msg = f"Unexpected error retrieving todos: {str(e)}"
            logger.error(error_msg)
            raise DatabaseOperationError(error_msg) from e
    
    @staticmethod
    def create_todo(description: str) -> Dict:
        """
        Create a new TODO item in the database.
        
        Args:
            description: The TODO description (will be validated and sanitized)
            
        Returns:
            Dict: Created todo dictionary with id, description, and created_at
            
        Raises:
            ValueError: If description is invalid
            DatabaseConnectionError: If database connection fails
            DatabaseOperationError: If database operation fails
        """
        # Validate and sanitize input
        if not description or not isinstance(description, str):
            raise ValueError("Description must be a non-empty string")
        
        description = description.strip()
        if not description:
            raise ValueError("Description cannot be empty or whitespace only")
        
        # Additional validation: length check
        if len(description) > 1000:
            raise ValueError("Description cannot exceed 1000 characters")
        
        try:
            db_manager = get_db_manager()
            todos_collection = db_manager.get_todos_collection()
            
            # Create todo document
            todo_doc = {
                'description': description,
                'created_at': datetime.utcnow()
            }
            
            # Insert into MongoDB
            result = todos_collection.insert_one(todo_doc)
            
            # Prepare response with created todo
            created_todo = {
                'id': str(result.inserted_id),
                'description': description,
                'created_at': todo_doc['created_at'].isoformat()
            }
            
            logger.info(f"Successfully created todo with id: {result.inserted_id}")
            return created_todo
            
        except ValueError:
            # Re-raise validation errors as-is
            raise
        except DatabaseConnectionError:
            # Re-raise connection errors as-is
            raise
        except PyMongoError as e:
            error_msg = f"Database error while creating todo: {str(e)}"
            logger.error(error_msg)
            raise DatabaseOperationError(error_msg) from e
        except Exception as e:
            error_msg = f"Unexpected error creating todo: {str(e)}"
            logger.error(error_msg)
            raise DatabaseOperationError(error_msg) from e

