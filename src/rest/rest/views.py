"""
API views for TODO operations.
Thin controller layer that delegates business logic to service layer.
"""
import logging
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status

from .services import TodoService
from .database import DatabaseConnectionError, DatabaseOperationError

logger = logging.getLogger(__name__)


class TodoListView(APIView):
    """
    API view to handle GET and POST requests for TODO items.
    Uses service layer for business logic and MongoDB for persistence.
    """

    def get(self, request):
        """
        Retrieve all TODO items from MongoDB.
        
        Returns:
            Response: JSON response with list of todos or error message
        """
        try:
            todos = TodoService.get_all_todos()
            return Response({'todos': todos}, status=status.HTTP_200_OK)
            
        except DatabaseConnectionError as e:
            logger.error(f"Database connection error: {str(e)}")
            return Response(
                {
                    'error': 'Database connection failed',
                    'detail': 'Unable to connect to database. Please try again later.'
                },
                status=status.HTTP_503_SERVICE_UNAVAILABLE
            )
        except DatabaseOperationError as e:
            logger.error(f"Database operation error: {str(e)}")
            return Response(
                {
                    'error': 'Failed to retrieve todos',
                    'detail': str(e)
                },
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
        except Exception as e:
            logger.error(f"Unexpected error retrieving todos: {str(e)}", exc_info=True)
            return Response(
                {
                    'error': 'An unexpected error occurred',
                    'detail': 'Please try again later.'
                },
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
        
    def post(self, request):
        """
        Create a new TODO item in MongoDB.
        
        Expects:
            JSON body with 'description' field (string, required, max 1000 chars)
        
        Returns:
            Response: JSON response with created todo or error message
        """
        try:
            # Extract description from request data
            description = request.data.get('description', '')
            
            # Service layer handles validation and creation
            created_todo = TodoService.create_todo(description)
            
            return Response(
                {
                    'todo': created_todo,
                    'message': 'Todo created successfully'
                },
                status=status.HTTP_201_CREATED
            )
            
        except ValueError as e:
            # Validation errors from service layer
            logger.warning(f"Validation error: {str(e)}")
            return Response(
                {
                    'error': 'Invalid input',
                    'detail': str(e)
                },
                status=status.HTTP_400_BAD_REQUEST
            )
        except DatabaseConnectionError as e:
            logger.error(f"Database connection error: {str(e)}")
            return Response(
                {
                    'error': 'Database connection failed',
                    'detail': 'Unable to connect to database. Please try again later.'
                },
                status=status.HTTP_503_SERVICE_UNAVAILABLE
            )
        except DatabaseOperationError as e:
            logger.error(f"Database operation error: {str(e)}")
            return Response(
                {
                    'error': 'Failed to create todo',
                    'detail': str(e)
                },
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
        except Exception as e:
            logger.error(f"Unexpected error creating todo: {str(e)}", exc_info=True)
            return Response(
                {
                    'error': 'An unexpected error occurred',
                    'detail': 'Please try again later.'
                },
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

