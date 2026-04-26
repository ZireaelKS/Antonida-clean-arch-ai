from pydantic import BaseModel

class ReviewRequest(BaseModel):
    text: str
    author: str = "Anonymous"