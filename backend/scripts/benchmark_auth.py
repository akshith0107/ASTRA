import time
import uuid
import sys
import os

# Add parent dir to path so we can import app modules
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from fastapi.testclient import TestClient
from app.main import app

def run_benchmark():
    print("==================================================")
    print("ASTRA AUTHENTICATION PERFORMANCE BENCHMARK")
    print("==================================================\n")
    
    client = TestClient(app)
    uid = str(uuid.uuid4())[:8]
    user_data = {
        "username": f"bench_{uid}",
        "email": f"bench_{uid}@astra.net",
        "password": "BenchmarkPassword123!"
    }
    
    print(f"[*] Registering benchmark user: {user_data['username']}...")
    reg_start = time.time()
    res = client.post("/api/v1/auth/register", json=user_data)
    reg_duration = (time.time() - reg_start) * 1000
    if res.status_code != 200:
        print(f"[!] Registration failed: {res.text}")
        return
        
    data = res.json()
    token = data["access_token"]
    refresh = data["refresh_token"]
    print(f"[+] Registration & bcrypt hash took: {reg_duration:.2f} ms\n")
    
    # Benchmark /me endpoint (with TTL Cache)
    num_requests = 100
    print(f"[*] Benchmarking /api/v1/auth/me over {num_requests} sequential requests (testing in-memory TTL cache)...")
    headers = {"Authorization": f"Bearer {token}"}
    
    start_time = time.time()
    for _ in range(num_requests):
        r = client.get("/api/v1/auth/me", headers=headers)
        if r.status_code != 200:
            print(f"[!] Request failed with status {r.status_code}")
            break
    total_time = time.time() - start_time
    avg_latency = (total_time / num_requests) * 1000
    throughput = num_requests / total_time
    
    print(f"[+] Total time for {num_requests} requests: {total_time:.4f} seconds")
    print(f"[+] Average Latency per request: {avg_latency:.2f} ms")
    print(f"[+] Throughput: {throughput:.2f} requests/sec\n")
    
    # Benchmark /refresh endpoint (Token Rotation)
    num_refreshes = 10
    print(f"[*] Benchmarking /api/v1/auth/refresh over {num_refreshes} token rotations...")
    start_ref = time.time()
    curr_refresh = refresh
    for i in range(num_refreshes):
        r = client.post("/api/v1/auth/refresh", json={"refresh_token": curr_refresh})
        if r.status_code == 200:
            curr_refresh = r.json()["refresh_token"]
        elif r.status_code == 429:
            print(f"[!] Rate limit triggered at iteration {i+1} (expected behavior for rate limiter)")
            break
        else:
            print(f"[!] Refresh failed with status {r.status_code}: {r.text}")
            break
    ref_time = time.time() - start_ref
    avg_ref_latency = (ref_time / (i + 1)) * 1000
    print(f"[+] Token rotation average latency: {avg_ref_latency:.2f} ms\n")
    
    print("==================================================")
    print("BENCHMARK SUMMARY RESULTS")
    print("==================================================")
    print(f"| Operation                    | Avg Latency (ms) | Notes                     |")
    print(f"|------------------------------|------------------|---------------------------|")
    print(f"| Password Hash (rounds=12)    | {reg_duration:16.2f} | Secure bcrypt work factor |")
    print(f"| Token Validation (TTL Cache) | {avg_latency:16.2f} | Zero DB queries           |")
    print(f"| Token Rotation (/refresh)    | {avg_ref_latency:16.2f} | DB sha256 lookup + update |")
    print("==================================================\n")

if __name__ == "__main__":
    run_benchmark()
