"""Test script for Model Ingest endpoint with google/bert-base-uncased."""

import asyncio
import httpx
import json
from datetime import datetime


async def test_ingest_bert():
    """Test the ingest endpoint with google/bert-base-uncased model."""
    
    print("=" * 70)
    print("MODEL INGEST TEST - google/bert-base-uncased")
    print("=" * 70)
    print(f"Started at: {datetime.now().isoformat()}\n")
    
    async with httpx.AsyncClient(timeout=300.0) as client:
        try:
            # Step 1: Authenticate
            print("📝 Step 1: Getting authentication token...")
            print("-" * 70)
            
            auth_response = await client.post(
                "http://localhost:8000/api/v1/user/login",
                json={
                    "username": "testuser",
                    "password": "password123"
                }
            )
            
            if auth_response.status_code != 200:
                print(f"❌ Authentication failed: {auth_response.status_code}")
                print(f"Response: {auth_response.text}")
                return
            
            access_token = auth_response.json().get("access_token")
            if not access_token:
                print("❌ No access_token in response")
                return
            
            print("✅ Authentication successful")
            print(f"   Token: {access_token[:30]}...\n")
            
            # Step 2: Call ingest endpoint
            print("🔍 Step 2: Ingesting model - google/bert-base-uncased...")
            print("-" * 70)
            
            headers = {
                "Authorization": f"Bearer {access_token}",
                "Content-Type": "application/json"
            }
            
            ingest_request = {
                "url": "https://huggingface.co/google-bert/bert-base-uncased"
            }
            
            print("Request:")
            print("  URL: POST http://localhost:8000/api/v1/package/ingest")
            print(f"  Body: {json.dumps(ingest_request, indent=2)}\n")
            
            ingest_response = await client.post(
                "http://localhost:8000/api/v1/package/ingest",
                json=ingest_request,
                headers=headers
            )
            
            print(f"Response Status: {ingest_response.status_code}")
            
            # Parse response
            response_data = ingest_response.json()
            
            print("\n📊 Response Data:")
            print(json.dumps(response_data, indent=2))
            
            # Step 3: Analyze results
            print("\n" + "=" * 70)
            print("📈 ANALYSIS")
            print("=" * 70)
            
            if ingest_response.status_code == 201:
                print("✅ SUCCESS - Model passed quality gate!")
                print(f"\n   Artifact ID: {response_data.get('artifact_id')}")
                print(f"   Model Name: {response_data.get('model_name')}")
                print(f"   Latency: {response_data.get('latency_ms')} ms\n")
                
                # Show all scores
                print("   📊 All Scores:")
                scores = response_data.get("all_scores", {})
                for metric, score in scores.items():
                    status = "✓" if score >= 0.5 else "✗"
                    print(f"      {status} {metric}: {score}")
                
            elif ingest_response.status_code == 424:
                print("❌ FAILED - Model rejected by quality gate!")
                print(f"\n   Artifact ID: {response_data.get('artifact_id')}")
                print(f"   Model Name: {response_data.get('model_name')}\n")
                
                # Show failing metrics
                print("   ⚠️  Failing Metrics:")
                failing = response_data.get("failing_metrics", [])
                for metric in failing:
                    print(f"      ❌ {metric['metric']}")
                    print(f"         Score: {metric['score']} ")
                    print(f"         Required: {metric['required']}")
                    print(f"         Gap: {metric['gap']}\n")
                
                # Show all scores
                print("   📊 All Scores:")
                scores = response_data.get("all_scores", {})
                for metric, score in scores.items():
                    status = "✓" if score >= 0.5 else "✗"
                    print(f"      {status} {metric}: {score}")
            else:
                print(f"⚠️  Unexpected status: {ingest_response.status_code}")
            
            # Step 4: Summary
            print("\n" + "=" * 70)
            print("📋 SUMMARY")
            print("=" * 70)
            
            if ingest_response.status_code == 201:
                print("✅ INGEST SUCCESSFUL")
                print("   Model is ingestible and has been registered.")
                artifact_id = response_data.get('artifact_id')
                if artifact_id:
                    print(f"   Artifact: {artifact_id}.zip")
            elif ingest_response.status_code == 424:
                print("❌ INGEST FAILED")
                print("   Model did not meet quality gate requirements.")
                print(f"   Reason: {response_data.get('message')}")
            else:
                print("⚠️  INGEST ERROR")
                print(f"   Status: {ingest_response.status_code}")
                detail = response_data.get('detail', 'Unknown error')
                print(f"   Message: {detail}")
            
            print("=" * 70)
            print(f"Completed at: {datetime.now().isoformat()}\n")
            
        except httpx.ConnectError:
            print("❌ ERROR: Could not connect to server")
            print("   at http://localhost:8000")
            print("   Make sure the API is running:")
            print("   python main.py\n")
        except httpx.TimeoutException:
            print("❌ ERROR: Request timed out (> 300 seconds)")
            print("   Model might be too large or metrics take too long.\n")
        except Exception as e:
            print(f"❌ ERROR: {type(e).__name__}: {e}\n")


if __name__ == "__main__":
    print("🚀 Starting Model Ingest Test\n")
    print("Prerequisites:")
    print("  1. API server running: python main.py")
    print("  2. Database initialized: python -m src.database.init_db --seed")
    print("  3. Test user 'testuser' with password 'password123'\n")
    
    asyncio.run(test_ingest_bert())
