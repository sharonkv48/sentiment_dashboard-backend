from fastapi import APIRouter, HTTPException, UploadFile, File
from typing import List, Dict
from datetime import datetime
from app.schemas.sentiment import (
    SentimentRequest, 
    SentimentResponse, 
    BatchSentimentResponse,
    SentimentResult,
    FileAnalysisResponse
)
from app.services.sentiment_service import sentiment_analyzer
import pandas as pd
import io
import time

router = APIRouter(
    prefix="/sentiment",
    tags=["sentiment"]
)

@router.post("/analyze-text", response_model=SentimentResponse)
async def analyze_text(request: SentimentRequest):
    """
    Analyze sentiment of a single text string
    """
    try:
        start_time = time.time()
        result = await sentiment_analyzer.analyze_text(request.text)
        result['timestamp'] = datetime.utcnow()
        return SentimentResponse(**result)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/analyze-sentiment", response_model=FileAnalysisResponse)
async def analyze_file(file: UploadFile = File(...)):
    """
    Analyze sentiment from a CSV file containing text data
    """
    if not file.filename.endswith('.csv'):
        raise HTTPException(status_code=400, detail="Only CSV files are supported")

    try:
        start_time = time.time()
        
        # Read CSV file
        contents = await file.read()
        df = pd.read_csv(io.StringIO(contents.decode('utf-8')))
        
        # Validate required columns
        if 'text' not in df.columns:
            raise HTTPException(
                status_code=400, 
                detail="CSV must contain a 'text' column"
            )

        # Process each row
        results = []
        for idx, row in df.iterrows():
            # Get sentiment analysis for the text
            sentiment_result = await sentiment_analyzer.analyze_text(row['text'])
            
            # Create result dictionary
            result = {
                'id': str(row.get('id', idx)),
                'text': row['text'],
                'sentiment': sentiment_result['sentiment'].lower(),
                'score': sentiment_result['score'],
                'confidence': sentiment_result['confidence'],
                'timestamp': row.get('timestamp', datetime.utcnow().isoformat())
            }
            results.append(result)

        # Calculate sentiment distribution
        sentiment_counts = {
            'positive': len([r for r in results if r['sentiment'] == 'positive']),
            'neutral': len([r for r in results if r['sentiment'] == 'neutral']),
            'negative': len([r for r in results if r['sentiment'] == 'negative'])
        }

        processing_time = time.time() - start_time

        return FileAnalysisResponse(
            status="success",
            data=results,
            summary=sentiment_counts,
            processing_time=processing_time
        )

    except pd.errors.EmptyDataError:
        raise HTTPException(status_code=400, detail="The CSV file is empty")
    except pd.errors.ParserError:
        raise HTTPException(status_code=400, detail="Invalid CSV format")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/analyze-batch", response_model=BatchSentimentResponse)
async def analyze_batch(texts: List[str]):
    """
    Analyze sentiment for a batch of texts
    """
    try:
        start_time = time.time()
        results = []
        
        for text in texts:
            result = await sentiment_analyzer.analyze_text(text)
            results.append(SentimentResponse(**result))

        # Calculate sentiment distribution
        sentiment_counts = {
            'positive': len([r for r in results if r.sentiment == 'positive']),
            'neutral': len([r for r in results if r.sentiment == 'neutral']),
            'negative': len([r for r in results if r.sentiment == 'negative'])
        }

        processing_time = time.time() - start_time

        return BatchSentimentResponse(
            results=results,
            summary=sentiment_counts,
            processing_time=processing_time
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))