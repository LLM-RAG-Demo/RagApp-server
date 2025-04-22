from typing import List

from pydantic import BaseModel
from datetime import datetime

from .message import Message

class Conversation(BaseModel):
    id: int
    messages: List[Message]
    created_at : datetime = datetime.now()
    updated_at : datetime = datetime.now()
