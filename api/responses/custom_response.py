from rest_framework.response import Response

class SuccessResponse(Response):
    def __init__(self, data=None, message="Success", status=200, **kwargs):
        formatted_data = {
            "success": True,
            "message": message,
            "data": data if data is not None else {}
        }
        super().__init__(data=formatted_data, status=status, **kwargs)

class ErrorResponse(Response):
    def __init__(self, errors=None, message="Error occurred", status=400, **kwargs):
        formatted_data = {
            "success": False,
            "message": message,
            "errors": errors if errors is not None else {}
        }
        super().__init__(data=formatted_data, status=status, **kwargs)
