# models/sentiment_model.py
from textblob import TextBlob

def analyze_sentiment(text: str) -> str:
    analysis = TextBlob(text)
    polarity = analysis.sentiment.polarity
    
    # Updated thresholds for better neutral classification
    if polarity > 0.2:
        return 'positive'
    elif polarity < -0.2:
        return 'negative'
    else:
        return 'neutral'

def get_sentiment_score(text: str) -> float:
    analysis = TextBlob(text)
    return analysis.sentiment.polarity

def get_sentiment_confidence(text: str) -> float:
    """Calculate confidence score based on polarity strength"""
    analysis = TextBlob(text)
    polarity = abs(analysis.sentiment.polarity)
    
    # Convert polarity to a confidence score between 0 and 1
    if polarity > 0.5:
        confidence = 0.9 + (polarity - 0.5) * 0.2  # High confidence
    else:
        confidence = 0.5 + polarity * 0.8  # Scale confidence linearly
    
    return min(confidence, 1.0)  # Ensure confidence doesn't exceed 1.0

# services/sentiment_service.py
from transformers import AutoTokenizer, AutoModelForSequenceClassification
import torch
from typing import List, Dict
from datetime import datetime
import asyncio
from concurrent.futures import ThreadPoolExecutor
from textblob import TextBlob

class SentimentAnalyzer:
    def __init__(self):
        self.executor = ThreadPoolExecutor(max_workers=4)

    def _analyze_text(self, text: str) -> Dict:
        analysis = TextBlob(text)
        polarity = analysis.sentiment.polarity
        
        # Determine sentiment with adjusted thresholds
        if polarity > 0.2:
            sentiment = 'positive'
        elif polarity < -0.2:
            sentiment = 'negative'
        else:
            sentiment = 'neutral'
        
        # Calculate confidence based on polarity strength
        confidence = abs(polarity)
        if confidence > 0.5:
            confidence = 0.9 + (confidence - 0.5) * 0.2
        else:
            confidence = 0.5 + confidence * 0.8
        
        confidence = min(confidence, 1.0)
        
        return {
            "text": text,
            "sentiment": sentiment,
            "score": polarity,
            "confidence": float(confidence),
            "timestamp": datetime.utcnow()
        }

    async def analyze_text(self, text: str) -> Dict:
        loop = asyncio.get_running_loop()
        result = await loop.run_in_executor(self.executor, self._analyze_text, text)
        return result

    async def analyze_batch(self, texts: List[str]) -> Dict:
        tasks = [self.analyze_text(text) for text in texts]
        results = await asyncio.gather(*tasks)

        summary = {
            "positive": len([r for r in results if r["sentiment"] == "positive"]),
            "neutral": len([r for r in results if r["sentiment"] == "neutral"]),
            "negative": len([r for r in results if r["sentiment"] == "negative"])
        }

        return {
            "results": results,
            "summary": summary,
            "processing_time": len(texts) * 0.1
        }

sentiment_analyzer = SentimentAnalyzer()