from pydantic import BaseModel

class UserLogin(BaseModel):
    username: str
    password: str

class WordleResult(BaseModel):
    username: str
    score: int
    raw_result: str
