#!/usr/bin/env python
"""Test Google Fact Check API connection and diagnostics."""

import requests
import os

API_KEY_FILE = r'd:\projects\Fake news detector\Api key.txt'
FACTCHECK_API_URL = 'https://factchecktools.googleapis.com/v1alpha1/claims:search'

def test_api():
    print("="*70)
    print("GOOGLE FACT CHECK API TEST")
    print("="*70)
    
    # Step 1: Read API key
    print("\n[1] Reading API key...")
    if not os.path.exists(API_KEY_FILE):
        print(f"❌ ERROR: File not found: {API_KEY_FILE}")
        return
    
    with open(API_KEY_FILE, 'r', encoding='utf-8') as f:
        api_key = f.read().strip()
    
    if not api_key:
        print("❌ ERROR: API key file is empty")
        return
    
    print(f"✅ API key loaded: {api_key[:20]}...{api_key[-10:]}")
    
    # Step 2: Test API endpoint
    print("\n[2] Testing API endpoint...")
    print(f"URL: {FACTCHECK_API_URL}")
    
    test_queries = [
        "The Earth is flat",
        "Vaccines prevent disease",
        "Climate change is real",
    ]
    
    for query in test_queries:
        print(f"\n  Testing query: '{query}'")
        params = {
            'query': query[:256],
            'key': api_key,
            'languageCode': 'en'
        }
        
        try:
            resp = requests.get(FACTCHECK_API_URL, params=params, timeout=10)
            print(f"  Status code: {resp.status_code}")
            
            if resp.status_code == 200:
                result = resp.json()
                claims = result.get('claims', [])
                print(f"  ✅ API working! Found {len(claims)} matching claims")
                if claims:
                    print(f"     First claim: {claims[0].get('text', 'N/A')[:80]}...")
                    if 'claimReview' in claims[0]:
                        verdict = claims[0]['claimReview'][0].get('textualRating', 'N/A')
                        print(f"     Verdict: {verdict}")
            else:
                print(f"  ❌ API error: {resp.status_code}")
                print(f"     Response: {resp.text[:200]}")
                
        except Exception as e:
            print(f"  ❌ Connection error: {str(e)}")
    
    print("\n" + "="*70)
    print("DIAGNOSIS COMPLETE")
    print("="*70)
    print("\nIf you see 'API working!' above, the API key is valid.")
    print("If you see errors, check:")
    print("  1. API key is correct (copy from Google Cloud Console)")
    print("  2. API is enabled in your Google Cloud project")
    print("  3. Billing is set up (Google Fact Check API may have costs)")
    print("  4. Internet connection is working")
    print("  5. API quota hasn't been exceeded")

if __name__ == '__main__':
    test_api()
