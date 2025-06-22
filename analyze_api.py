#!/usr/bin/env python3
"""
Script to analyze the API response structure
"""

import requests
import json
from pprint import pprint

def fetch_api_data():
    """Fetch data from the API and analyze structure."""
    
    url = "https://theedgeroom.com/wp-json/custom/v1/search-data"
    
    headers = {
        "Content-Type": "application/json",
        "Authorization": "Basic YWRtaW46bUdWcSBFeG9UIGZJdWsgRGF3ayB0VW5hwqBvWGg4",
        "Cookie": "PHPSESSID=1158a7ca22393d489c8828eb2f9a580f; __cf_bm=P_5fUwzg8oS.ApSniDHDDd74soIp1yA1Z0irVZ6MkaI-1748187878-1.0.1.1-kqbe8ty54ZZlm8igFyZB3XXDZDoZmg3PAW4Orqf1NAB6hxeN4pWYh6MEcYxtxPxg1g_zFvtofbuvZsgEbb5dkmZup8nXZce5x_8rGtphg8Y; __cf_bm=aAPOi2xPypaWZRRADxaZSzr4BkfFJD1IiB5Ic1Jg6X4-1750589197-1.0.1.1-aUndY7nbktzZgjc.RmIa61xY86or6ncXd4NrNHf0X7Uta.rq5tHsW0Fg2qjbpT9dmR0UlBkpBQHa.iuKChVG07Suz7Di0g2TEEt3RX6iVFQ; __cf_bm=ezwyP29WUwBin8Y.PHtuEtKQr.Se1vQIw_tPSx0eToM-1750612897-1.0.1.1-6GzWT1bZElFn0w60kK3ZW_i00oo5bjsVH5DzqG9UkBZJpOLQnZR7lHcq4jaqJpjAhIANCfxzOizUV90vKlVH5xfcb2uImIiIACOG6itclRQ"
    }
    
    payload = {
        "start_date": "2024-01-01",
        "end_date": "2025-12-31",
        "type": "all"
    }
    
    try:
        print("🔍 Fetching data from API...")
        response = requests.post(url, json=payload, headers=headers, timeout=30)
        
        print(f"Status Code: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            
            print("\n📊 API Response Structure:")
            print("=" * 50)
            
            # Save full response to file
            with open("api_response.json", "w", encoding="utf-8") as f:
                json.dump(data, f, indent=2, ensure_ascii=False)
            print("✓ Full response saved to api_response.json")
            
            # Analyze structure
            print(f"\nTop-level keys: {list(data.keys()) if isinstance(data, dict) else 'Not a dict'}")
            
            # Look for data array or items
            if isinstance(data, dict):
                for key, value in data.items():
                    print(f"\n{key}: {type(value)}")
                    if isinstance(value, list) and len(value) > 0:
                        print(f"  - Array with {len(value)} items")
                        print(f"  - First item keys: {list(value[0].keys()) if isinstance(value[0], dict) else 'Not a dict'}")
                        
                        # Analyze events and articles separately
                        events = [item for item in value if item.get('type') == 'event']
                        articles = [item for item in value if item.get('type') == 'article']
                        
                        print(f"  - Events found: {len(events)}")
                        print(f"  - Articles found: {len(articles)}")
                        
                        if events:
                            print(f"\n📅 EVENT STRUCTURE (first item):")
                            pprint(events[0], width=100)
                            
                        if articles:
                            print(f"\n📰 ARTICLE STRUCTURE (first item):")
                            pprint(articles[0], width=100)
            
            elif isinstance(data, list):
                print(f"Response is a list with {len(data)} items")
                if len(data) > 0:
                    print(f"First item keys: {list(data[0].keys()) if isinstance(data[0], dict) else 'Not a dict'}")
        
        else:
            print(f"❌ API request failed: {response.status_code}")
            print(f"Response: {response.text}")
            
    except Exception as e:
        print(f"❌ Error fetching data: {e}")

if __name__ == "__main__":
    fetch_api_data()
