#!/usr/bin/env python3
"""
Test script for the Events Articles Chatbot API endpoint
"""

import asyncio
import httpx
import json
from datetime import datetime

async def test_health_endpoint():
    """Test the health check endpoint."""
    print("🔍 Testing health endpoint...")
    
    async with httpx.AsyncClient() as client:
        try:
            response = await client.get("http://localhost:8000/api/v1/health")
            print(f"✓ Health check status: {response.status_code}")
            print(f"✓ Response: {response.json()}")
            return True
        except Exception as e:
            print(f"❌ Health check failed: {e}")
            return False

async def test_fetch_endpoint():
    """Test the main fetch and update endpoint."""
    print("\n📡 Testing fetch and update endpoint...")
    
    # Test parameters
    params = {
        "start_date": "2024-01-01",
        "end_date": "2025-12-31",
        "data_type": "all"
    }
    
    async with httpx.AsyncClient(timeout=60.0) as client:
        try:
            print(f"📤 Making request with params: {params}")
            response = await client.get(
                "http://localhost:8000/api/v1/fetch-and-update",
                params=params
            )
            
            print(f"✓ Response status: {response.status_code}")
            
            if response.status_code == 200:
                data = response.json()
                print("✓ Response data:")
                print(json.dumps(data, indent=2))
                
                # Check if data was processed
                if data.get("success"):
                    print(f"✓ Events processed: {data.get('events_processed', 0)}")
                    print(f"✓ Articles processed: {data.get('articles_processed', 0)}")
                    print(f"✓ Embeddings created: {data.get('embeddings_created', 0)}")
                else:
                    print("⚠️  Request was not successful")
            else:
                print(f"❌ Request failed with status {response.status_code}")
                print(f"❌ Error: {response.text}")
                
        except Exception as e:
            print(f"❌ Request failed: {e}")

async def test_root_endpoint():
    """Test the root endpoint."""
    print("\n🏠 Testing root endpoint...")
    
    async with httpx.AsyncClient() as client:
        try:
            response = await client.get("http://localhost:8000/")
            print(f"✓ Root endpoint status: {response.status_code}")
            print(f"✓ Response: {response.json()}")
        except Exception as e:
            print(f"❌ Root endpoint failed: {e}")

async def main():
    """Main test function."""
    print("🧪 Starting API endpoint tests...")
    print(f"⏰ Test started at: {datetime.now()}")
    
    # Test endpoints in order
    health_ok = await test_health_endpoint()
    
    if health_ok:
        await test_root_endpoint()
        await test_fetch_endpoint()
    else:
        print("❌ Skipping other tests due to health check failure")
        print("💡 Make sure the API server is running: python run.py")
    
    print(f"\n⏰ Test completed at: {datetime.now()}")

if __name__ == "__main__":
    asyncio.run(main())
