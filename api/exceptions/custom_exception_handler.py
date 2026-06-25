import logging
from rest_framework.views import exception_handler
from rest_framework import status
from api.responses.custom_response import ErrorResponse

logger = logging.getLogger(__name__)

def custom_exception_handler(exc, context):
    # Call DRF's default exception handler first to get the standard error response.
    response = exception_handler(exc, context)

    if response is not None:
        message = "An error occurred"
        errors = response.data

        # Customize messages/formats based on status codes/exception types
        if response.status_code == status.HTTP_400_BAD_REQUEST:
            message = "Validation Failed"
            if isinstance(errors, dict):
                formatted_errors = {}
                for key, val in errors.items():
                    if isinstance(val, list):
                        formatted_errors[key] = val[0] if val else ""
                    elif isinstance(val, dict):
                        # Handle nested errors recursively or preserve them
                        formatted_errors[key] = val
                    else:
                        formatted_errors[key] = val
                errors = formatted_errors
            elif isinstance(errors, list):
                errors = {"non_field_errors": errors[0] if errors else ""}
        elif response.status_code == status.HTTP_401_UNAUTHORIZED:
            message = "Authentication Failed"
        elif response.status_code == status.HTTP_403_FORBIDDEN:
            message = "Permission Denied"
        elif response.status_code == status.HTTP_404_NOT_FOUND:
            message = "Not Found"
        elif response.status_code == status.HTTP_429_TOO_MANY_REQUESTS:
            message = "Request limit exceeded"

        return ErrorResponse(errors=errors, message=message, status=response.status_code)

    # For unhandled exceptions (Server Errors 500)
    logger.exception("Unhandled server error occurred: %s", str(exc))
    return ErrorResponse(
        errors={"detail": str(exc)},
        message="Internal Server Error",
        status=status.HTTP_500_INTERNAL_SERVER_ERROR
    )
