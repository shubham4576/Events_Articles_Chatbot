from datetime import date
import httpx
import json
from pathlib import Path


async def fetch_and_save_data():
    data_type="all"
    json_file_path="data/data.json"
    url = "https://theedgeroom.com/wp-json/custom/v1/search-data"

    headers = {
        "Content-Type": "application/json",
        "Authorization": "Basic YWRtaW46bUdWcSBFeG9UIGZJdWsgRGF3ayB0VW5hwqBvWGg4",
        'User-Agent': 'Mozilla/5.0',
        'Accept': 'application/json',
        'X-Requested-With': 'XMLHttpRequest'
    }
    start_date = "1900-01-01"
    end_date = str(date.today())
    payload = {
        "start_date": start_date,
        "end_date": end_date,
        "type": data_type
    }

    async with httpx.AsyncClient() as client:
        response = await client.post(url, headers=headers, json=payload)

    if response.status_code == 200:
        data = response.json()
        with open(json_file_path, "w") as f:
            json.dump(data, f, indent=2)
        return {"status": "success", "message": "Data saved to file."}
    else:
        return {
            "status": "error",
            "code": response.status_code,
            "message": response.text
        }
