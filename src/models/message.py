from pydantic import BaseModel
from datetime import datetime

class Message(BaseModel):
    id: int
    content: str
    role: str
    timestamp: datetime = datetime.now()
