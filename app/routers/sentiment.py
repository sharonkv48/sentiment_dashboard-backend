from fastapi import APIRouter, UploadFile, File, HTTPException
from ..models.sentiment_model import analyze_sentiment, get_sentiment_score
from ..utils.file_processor import process_csv, validate_dataframe
from typing import List, Dict
import pandas as pd

router = APIRouter(
    prefix="/sentiment",  # Add this prefix for the sentiment routes
    tags=["sentiment"]    # Optional: for API documentation
)

@router.post("/analyze-sentiment")
async def analyze_file(
    file: UploadFile = File(...)
) -> List[Dict]:
    if not file.filename.endswith('.csv'):
        raise HTTPException(400, "Only CSV files are supported")
    
    try:
        df = await process_csv(file)
        if not validate_dataframe(df):
            raise HTTPException(400, "Invalid CSV format")
        
        results = []
        for _, row in df.iterrows():
            sentiment = analyze_sentiment(row['text'])
            score = get_sentiment_score(row['text'])
            
            result = {
                'id': str(row['id']),
                'text': row['text'],
                'sentiment': sentiment.lower(),
                'timestamp': row.get('timestamp', '')
            }
            
            results.append(result)
        
        return results
        
    except Exception as e:
        raise HTTPException(500, f"Error processing file: {str(e)}")

# Keep the single text analysis endpoint
@router.post("/analyze-text")
async def analyze_single_text(
    text: str
) -> Dict:
    try:
        sentiment = analyze_sentiment(text)
        score = get_sentiment_score(text)
        
        return {
            'status': 'success',
            'data': {
                'text': text,
                'sentiment': sentiment.lower(),
                'score': score
            }
        }
    except Exception as e:
        raise HTTPException(500, f"Error analyzing text: {str(e)}")