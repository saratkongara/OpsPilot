from pydantic import BaseModel

class Equipment(BaseModel):
    id: int
    name: str
