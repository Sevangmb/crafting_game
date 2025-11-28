"""
Custom exception handler for better error messages
"""
from rest_framework.views import exception_handler
from rest_framework.response import Response
import logging

logger = logging.getLogger(__name__)


def custom_exception_handler(exc, context):
    """
    Custom exception handler that provides more detailed error messages
    and logs errors for debugging
    """
    # Call REST framework's default exception handler first
    response = exception_handler(exc, context)

    if response is not None:
        # Customize the response format
        custom_response_data = {
            'error': True,
            'status_code': response.status_code,
            'message': None,
            'details': None
        }

        # Extract error message
        if isinstance(response.data, dict):
            if 'detail' in response.data:
                custom_response_data['message'] = response.data['detail']
            else:
                custom_response_data['message'] = response.data
                custom_response_data['details'] = response.data
        elif isinstance(response.data, list):
            custom_response_data['message'] = response.data[0] if response.data else 'Une erreur est survenue'
            custom_response_data['details'] = response.data
        else:
            custom_response_data['message'] = str(response.data)

        # Log error for debugging
        view = context.get('view', None)
        request = context.get('request', None)

        log_message = f"API Error: {custom_response_data['message']}"
        if view:
            log_message += f" | View: {view.__class__.__name__}"
        if request:
            log_message += f" | Method: {request.method} | Path: {request.path}"
            if request.user and request.user.is_authenticated:
                log_message += f" | User: {request.user.username}"

        if response.status_code >= 500:
            logger.error(log_message, exc_info=exc)
        else:
            logger.warning(log_message)

        response.data = custom_response_data

    else:
        # Handle unexpected errors
        logger.error(f"Unhandled exception: {str(exc)}", exc_info=exc)
        response = Response({
            'error': True,
            'status_code': 500,
            'message': 'Une erreur interne est survenue. Veuillez réessayer.',
            'details': str(exc) if logger.isEnabledFor(logging.DEBUG) else None
        }, status=500)

    return response
