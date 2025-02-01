import requests
import datetime

# CONFIGURATION
SHOPIFY_STORE_URL = "https://ship.endurasupplements.com"
ENDPOINT = "/api/pincode-checker"
TEST_PINCODE = "400001"  # REPLACE WITH A VALID PINCODE

def test_pincode():
    try:
        # Mimic browser headers
        headers = {
            "Content-Type": "application/json",
            "User-Agent": "Mozilla/5.0"
        }
        
        # Send POST request with JSON data
        response = requests.post(
            f"{SHOPIFY_STORE_URL}{ENDPOINT}",
            json={"pincode": TEST_PINCODE},
            headers=headers,
            timeout=10
        )
        
        if response.status_code == 200:
            result = response.json()
            # Check for success criteria (adjust based on your API)
            if result.get("delivery_date"):
                return True, "Pincode checker is working!"
            else:
                return False, f"Error: {result.get('message', 'No delivery available')}"
        else:
            return False, f"HTTP Error: {response.status_code}"
            
    except Exception as e:
        return False, f"Exception: {str(e)}"

# Run test and log results
success, message = test_pincode()
timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")

with open("pincode_check.log", "a") as f:
    f.write(f"[{timestamp}] {'SUCCESS' if success else 'FAILURE'}: {message}\n")

if not success:
    raise SystemExit(1)