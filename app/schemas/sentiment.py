from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any
from datetime import datetime

class SentimentRequest(BaseModel):
    text: str = Field(..., min_length=1, max_length=5000)

class SentimentResponse(BaseModel):
    text: str
    sentiment: str
    score: float
    confidence: float
    timestamp: Optional[datetime] = None

    class Config:
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }

class SentimentResult(BaseModel):
    id: str
    text: str
    sentiment: str
    timestamp: Optional[str] = None
    score: Optional[float] = None
    confidence: Optional[float] = None

class BatchSentimentResponse(BaseModel):
    status: str = "success"
    data: List[SentimentResult]
    summary: Dict[str, int]
    processing_time: float

class FileAnalysisResponse(BaseModel):
    status: str = "success"
    data: List[Dict[str, Any]]
    summary: Dict[str, int]
    processing_time: float

class Token(BaseModel):
    access_token: str
    token_type: str

class TokenData(BaseModel):
    username: Optional[str] = None

# For API error responses
class ErrorResponse(BaseModel):
    detail: str