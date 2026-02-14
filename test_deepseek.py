"""Test DeepSeek API connection"""
import os
import sys
from pathlib import Path

def load_env_file(env_path):
    """Load environment variables from .env file"""
    if not env_path.exists():
        print(f"[ERROR] .env file not found at: {env_path}")
        return
    
    print(f"[INFO] Loading .env from: {env_path}")
    
    with open(env_path, 'r', encoding='utf-8') as f:
        for line in f:
            line = line.strip()
            if not line or line.startswith('#'):
                continue
            if '=' in line:
                key, value = line.split('=', 1)
                key = key.strip()
                value = value.strip()
                if key and value:
                    os.environ[key] = value
                    if 'DEEPSEEK' in key:
                        print(f"[INFO] Set {key} = {value[:15]}...")

def test_deepseek_api():
    """Test DeepSeek API connection"""
    api_key = os.getenv("DEEPSEEK_API_KEY")
    
    if not api_key:
        print("[ERROR] DEEPSEEK_API_KEY not set")
        print(f"[DEBUG] Current env vars: {dict(os.environ)}")
        return False
    
    print(f"[OK] API Key configured: {api_key[:10]}...")
    
    try:
        import requests
        
        # DeepSeek API endpoint
        url = "https://api.deepseek.com/v1/chat/completions"
        
        headers = {
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json"
        }
        
        data = {
            "model": "deepseek-chat",
            "messages": [
                {"role": "system", "content": "You are a helpful assistant."},
                {"role": "user", "content": "Hello, please respond with a short greeting."}
            ],
            "max_tokens": 50
        }
        
        print("\n[INFO] Testing API connection...")
        response = requests.post(url, headers=headers, json=data, timeout=30)
        
        if response.status_code == 200:
            result = response.json()
            message = result["choices"][0]["message"]["content"]
            print(f"\n[SUCCESS] API call successful!")
            print(f"Response: {message}")
            return True
        else:
            print(f"\n[FAILED] API call failed")
            print(f"Status code: {response.status_code}")
            print(f"Response: {response.text}")
            return False
            
    except Exception as e:
        print(f"\n[ERROR] Test failed: {e}")
        return False

if __name__ == "__main__":
    print("=" * 50)
    print("DeepSeek API Test")
    print("=" * 50)
    
    # Get script directory
    script_dir = Path(__file__).parent
    env_path = script_dir / ".env"
    
    print(f"[INFO] Script directory: {script_dir}")
    print(f"[INFO] Looking for .env at: {env_path}")
    
    load_env_file(env_path)
    
    success = test_deepseek_api()
    print("=" * 50)
    sys.exit(0 if success else 1)
