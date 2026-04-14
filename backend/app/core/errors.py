from fastapi import HTTPException, Request
from fastapi.responses import JSONResponse


class AppError(HTTPException):
    """Application-level error with consistent format."""

    def __init__(self, status_code: int, detail: str, code: str) -> None:
        self.code = code
        super().__init__(status_code=status_code, detail=detail)


class NotFoundError(AppError):
    """Resource not found."""

    def __init__(self, detail: str = "Resource not found", code: str = "NOT_FOUND") -> None:
        super().__init__(status_code=404, detail=detail, code=code)


class ValidationError(AppError):
    """Validation error."""

    def __init__(self, detail: str = "Validation error", code: str = "VALIDATION_ERROR") -> None:
        super().__init__(status_code=422, detail=detail, code=code)


class ForbiddenError(AppError):
    """Forbidden action."""

    def __init__(self, detail: str = "Forbidden", code: str = "FORBIDDEN") -> None:
        super().__init__(status_code=403, detail=detail, code=code)


class UnauthorizedError(AppError):
    """Authentication required."""

    def __init__(self, detail: str = "Authentication required", code: str = "UNAUTHORIZED") -> None:
        super().__init__(status_code=401, detail=detail, code=code)


class ConflictError(AppError):
    """Resource conflict."""

    def __init__(self, detail: str = "Resource conflict", code: str = "CONFLICT") -> None:
        super().__init__(status_code=409, detail=detail, code=code)


class InvalidFilterError(AppError):
    """Invalid filter parameter."""

    def __init__(self, detail: str = "Invalid filter parameter value") -> None:
        super().__init__(status_code=400, detail=detail, code="INVALID_FILTER")


class InvalidCursorError(AppError):
    """Malformed pagination cursor."""

    def __init__(self, detail: str = "Malformed pagination cursor") -> None:
        super().__init__(status_code=400, detail=detail, code="INVALID_CURSOR")


async def app_error_handler(_request: Request, exc: AppError) -> JSONResponse:
    """Handle AppError exceptions with consistent JSON format."""
    return JSONResponse(
        status_code=exc.status_code,
        content={"detail": exc.detail, "code": exc.code},
    )


async def http_exception_handler(_request: Request, exc: HTTPException) -> JSONResponse:
    """Handle generic HTTPException with consistent JSON format."""
    return JSONResponse(
        status_code=exc.status_code,
        content={"detail": str(exc.detail), "code": "HTTP_ERROR"},
    )
