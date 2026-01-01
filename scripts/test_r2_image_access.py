"""
Test if R2 images are publicly accessible
"""
import requests

# Test URL from the HTML
test_url = "https://pub-54fd27572f2e4efc843722bee98239e0.r2.dev/original/2003B00C9301D00.jpg"

print(f"🔍 Testing image access...")
print(f"   URL: {test_url}")
print()

try:
    response = requests.head(test_url, timeout=5)
    
    print(f"Status Code: {response.status_code}")
    print(f"Headers: {dict(response.headers)}")
    print()
    
    if response.status_code == 200:
        print("✅ Image is accessible!")
        print(f"   Content-Type: {response.headers.get('content-type')}")
        print(f"   Content-Length: {response.headers.get('content-length')} bytes")
    elif response.status_code == 403:
        print("❌ 403 Forbidden - Bucket is not public or CORS issue")
        print("   Run: python scripts/make_r2_public.py")
    elif response.status_code == 404:
        print("❌ 404 Not Found - Image doesn't exist at this URL")
        print("   Check if images were uploaded to /original/ path")
    else:
        print(f"❌ Unexpected status: {response.status_code}")
        
except requests.exceptions.RequestException as e:
    print(f"❌ Network error: {e}")
    print("   Check your internet connection or R2 bucket configuration")
