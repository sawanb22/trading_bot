"""Diagnostic: tests demo-fapi.binance.com with current .env credentials."""
from dotenv import load_dotenv
import os, requests, hmac, hashlib, time

load_dotenv(".env")
key    = os.getenv("BINANCE_API_KEY", "")
secret = os.getenv("BINANCE_API_SECRET", "").encode()
base   = os.getenv("BINANCE_FUTURES_URL", "https://demo-fapi.binance.com")

print(f"Key      : {key[:10]}...{key[-4:]}  (len={len(key)})")
print(f"Endpoint : {base}")
print()

def signed_get(base_url, path, key, secret):
    ts = int(time.time() * 1000)
    params = f"timestamp={ts}"
    sig = hmac.new(secret, params.encode(), hashlib.sha256).hexdigest()
    url = f"{base_url}{path}?{params}&signature={sig}"
    r = requests.get(url, headers={"X-MBX-APIKEY": key}, timeout=10)
    return r.status_code, r.json()

print(f"--- Testing: {base}/fapi/v2/account ---")
status, resp = signed_get(base, "/fapi/v2/account", key, secret)
if status == 200:
    print(f"  PASS  totalWalletBalance: {resp.get('totalWalletBalance')} USDT")
    print("=== SUCCESS: API keys are valid ===")
else:
    print(f"  FAIL  status={status}  code={resp.get('code')}  msg={resp.get('msg')}")
    if resp.get('code') == -2015:
        print()
        print("  >> -2015 means: API key valid but missing Futures permission.")
        print("  >> Fix: go to demo.binance.com -> API Management -> Edit key")
        print("  >>      and tick 'Enable Futures Trading', then Save.")
    print("=== FAIL ===")
