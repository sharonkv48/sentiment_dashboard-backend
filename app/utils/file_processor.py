import pandas as pd
from fastapi import UploadFile
import io
from datetime import datetime


async def process_csv(file: UploadFile) -> pd.DataFrame:
    contents = await file.read()
    df = pd.read_csv(io.StringIO(contents.decode('utf-8')))
    
    required_columns = ['id', 'text']
    if not all(col in df.columns for col in required_columns):
        raise ValueError("CSV must contain 'id' and 'text' columns")
    
    return df

def validate_dataframe(df: pd.DataFrame) -> bool:
    if df.empty:
        return False
    if not all(col in df.columns for col in ['id', 'text']):
        return False
    if df['text'].isnull().any():
        return False
    return True