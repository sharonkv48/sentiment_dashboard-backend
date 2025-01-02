from transformers import AutoTokenizer, AutoModelForSequenceClassification
import torch
from typing import List, Dict
from datetime import datetime

import asyncio
from concurrent.futures import ThreadPoolExecutor

class SentimentAnalyzer:
    def __init__(self):
        self.device = "cuda" if torch.cuda.is_available() else "cpu"
        self.tokenizer = AutoTokenizer.from_pretrained("cardiffnlp/twitter-roberta-base-sentiment")
        self.model = AutoModelForSequenceClassification.from_pretrained("cardiffnlp/twitter-roberta-base-sentiment")
        self.model.to(self.device)
        self.executor = ThreadPoolExecutor(max_workers=4)

    def _analyze_text(self, text: str) -> Dict:
        inputs = self.tokenizer(text, return_tensors="pt", truncation=True, max_length=512).to(self.device)
        
        with torch.no_grad():
            outputs = self.model(**inputs)
            scores = torch.nn.functional.softmax(outputs.logits, dim=1)
            
        sentiment_scores = scores[0].tolist()
        sentiment_labels = ['negative', 'neutral', 'positive']
        sentiment_idx = torch.argmax(scores[0]).item()
        
        return {
            "text": text,
            "sentiment": sentiment_labels[sentiment_idx],
            "score": max(sentiment_scores),
            "confidence": float(max(sentiment_scores)),
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