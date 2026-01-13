
import sys
import os
from pathlib import Path
import requests

# Check if backend is running
try:
    response = requests.get("http://127.0.0.1:8000/market/history/detailed?symbol=XAUUSD&timeframe=1d&window=1y", timeout=10)
    print(f"Status Code: {response.status_code}")
    if response.status_code == 200:
        data = response.json()
        print(f"Data length: {len(data)}")
        if len(data) > 0:
            print(f"First item: {data[0]}")
    else:
        print(f"Error: {response.text}")
except Exception as e:
    print(f"Connection failed: {e}")
