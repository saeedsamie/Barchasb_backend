from typing import Generic, TypeVar, Optional
from pydantic import BaseModel, ConfigDict

T = TypeVar('T')

class ResponseModel(BaseModel, Generic[T]):
    """
    Generic response model for API endpoints.

    Attributes:
        status (str): Response status, defaults to "success"
        message (Optional[str]): Optional response message
        data (Optional[T]): Generic response data
    """
    model_config = ConfigDict(from_attributes=True)
    
    status: str = "success"
    message: Optional[str] = None
    data: Optional[T] = None


class ErrorResponse(BaseModel):
    """
    Standard error response model.

    Attributes:
        status (str): Error status, defaults to "error"
        message (str): Error message
        detail (Optional[str]): Optional detailed error information
    """
    status: str = "error"
    message: str
    detail: Optional[str] = None 