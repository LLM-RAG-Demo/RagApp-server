from datetime import datetime
from typing import List

from pydantic import BaseModel

class User(BaseModel):
    id: int
    name: str
    conversations: List[int] = []
    created_at : datetime = datetime.now()