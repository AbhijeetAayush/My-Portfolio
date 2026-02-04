class APIError(Exception):
    """Base exception for API errors"""
    def __init__(self, message, status_code=400):
        self.message = message
        self.status_code = status_code
        super().__init__(self.message)


class ValidationError(APIError):
    """Validation error"""
    def __init__(self, message):
        super().__init__(message, 400)


class NotFoundError(APIError):
    """Resource not found error"""
    def __init__(self, message="Resource not found"):
        super().__init__(message, 404)


class UnauthorizedError(APIError):
    """Unauthorized error"""
    def __init__(self, message="Unauthorized"):
        super().__init__(message, 401)


class ForbiddenError(APIError):
    """Forbidden error"""
    def __init__(self, message="Forbidden"):
        super().__init__(message, 403)


def error_response(error):
    """Convert exception to API Gateway response"""
    import json
    return {
        'statusCode': error.status_code,
        'headers': {
            'Content-Type': 'application/json',
            'Access-Control-Allow-Origin': '*',
            'Access-Control-Allow-Headers': 'Content-Type,Authorization',
            'Access-Control-Allow-Methods': 'GET,POST,PUT,DELETE,OPTIONS'
        },
        'body': json.dumps({
            'error': error.message
        })
    }
