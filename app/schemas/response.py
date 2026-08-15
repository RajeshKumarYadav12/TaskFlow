from typing import Generic, TypeVar, Optional
from pydantic import BaseModel

T = TypeVar('T')

class APIResponse(BaseModel, Generic[T]):
    message: str
    status: str
    code: int
    data: Optional[T] = None
