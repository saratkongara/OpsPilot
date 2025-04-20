from pydantic import BaseModel

class Certification(BaseModel):
    id: int
    name: str
