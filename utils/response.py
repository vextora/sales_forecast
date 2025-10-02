from typing import Any, Optional
from pydantic import BaseModel

class ResponseModel(BaseModel):
    status: str  # "success" / "error"
    message: Optional[str] = None
    data: Optional[Any] = None

def success_response(data: Any = None, message: str = "Success") -> dict:
    return ResponseModel(status="success", message=message, data=data).model_dump()

def error_response(message: str = "Error", data: Any = None) -> dict:
    return ResponseModel(status="error", message=message, data=data).model_dump()