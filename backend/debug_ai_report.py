import requests
import json
from datetime import datetime, timedelta
import time

def test_ai_report():
    print("Testing /analysis/ai_report endpoint...")
    
    # URL (Port 8000 as configured in uvicorn)
    url = "http://127.0.0.1:8000/analysis/ai_report"
    
    # Test parameters - Testing 7d window
    params = {
        "symbol": "XAUUSD",
        "timeframe": "1d",
        "window": "7d" 
    }
    
    print(f"Calling {url} with params={params}...")
    
    try:
        response = requests.get(url, params=params)
        print(f"Status Code: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            # print(json.dumps(data, indent=2, ensure_ascii=False))
            
            # Verify Report Content exists
            if "report" in data:
                print("✅ Report generated successfully")
                report_content = data["report"]
                print(f"Report length: {len(report_content)}")
                
                # Check for Data Range in report
                # Usually in format: "数据范围：2025-11-14 至 2026-01-13"
                if "数据范围：" in report_content:
                    start_idx = report_content.find("数据范围：")
                    end_idx = report_content.find("|", start_idx)
                    if end_idx == -1:
                        end_idx = report_content.find("\n", start_idx)
                    
                    data_range_str = report_content[start_idx:end_idx]
                    print(f"Found Data Range in Report: {data_range_str}")
                    
                    # Parse dates to verify
                    # Format: 数据范围：YYYY-MM-DD 至 YYYY-MM-DD
                    try:
                        date_part = data_range_str.replace("数据范围：", "").strip()
                        start_str, end_str = date_part.split(" 至 ")
                        
                        start_date = datetime.strptime(start_str.strip(), "%Y-%m-%d")
                        end_date = datetime.strptime(end_str.strip(), "%Y-%m-%d")
                        
                        print(f"Detected Date Range: {start_date.date()} to {end_date.date()}")
                        
                        # Calculate expected start date
                        # For 7d, it should be now - 7 days
                        window = params.get("window", "1d")
                        days_map = {"1d": 1, "7d": 7, "1m": 30, "3m": 90, "1y": 365}
                        expected_days = days_map.get(window, 60)
                        expected_start = datetime.now() - timedelta(days=expected_days)
                        
                        # Allow 1-2 days difference due to timezones or trading days
                        diff = abs((start_date - expected_start).days)
                        print(f"Parsed Start: {start_date.date()}, Expected Start: {expected_start.date()} (approx), Diff: {diff} days")
                        
                        if diff <= 2:
                            print(f"✅ Date Range seems correct for window {window}")
                        else:
                            print(f"❌ Date Range mismatch! Expected ~{expected_start.date()}, got {start_date.date()}")
                            
                    except Exception as e:
                        print(f"Could not parse dates from string: {data_range_str}, error: {e}")
                else:
                    print("❌ '数据范围' not found in report content")
            else:
                print("❌ 'report' field missing in response")
                
            if "debug_info" in data:
                print("Debug Info:", data["debug_info"])

            # Check for model name
            if "model" in data:
                print(f"Model: {data['model']}")
            else:
                print("Model field missing in response")
                
        else:
            print("Error response:", response.text)
            
    except Exception as e:
        print(f"Request failed: {e}")

if __name__ == "__main__":
    # Fetch OpenAPI to verify endpoints
    print("Fetching /openapi.json ...")
    try:
        openapi = requests.get("http://127.0.0.1:8000/openapi.json").json()
        paths = openapi.get("paths", {}).keys()
        print("Analysis paths:")
        for p in paths:
            if "analysis" in p:
                print(p)
    except Exception as e:
        print(f"Failed to fetch openapi: {e}")

    test_ai_report()
