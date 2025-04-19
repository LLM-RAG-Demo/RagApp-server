from pydantic import BaseModel
from datetime import datetime

class Message(BaseModel):
    id: str
    content: str
    role: str
    timestamp: datetime = datetime.now()
