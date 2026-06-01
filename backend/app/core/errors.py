from fastapi import HTTPException, status


def api_error(code: str, message: str, http_status: int = status.HTTP_400_BAD_REQUEST) -> HTTPException:
    return HTTPException(status_code=http_status, detail={"error": {"code": code, "message": message}})
