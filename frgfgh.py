import requests
import time
import random

# ==========================================
# CONFIGURATION
# ==========================================
API_KEY = 'Af4AzXWsT4PnBb6Y4jt5P1N7w2sh6Z'
SERVICE_ID = 'tg'       # 'tg' is usually Telegram on SMS PVA
COUNTRY_ID = '6'        # '6' is the ID for Indonesia (ID)

# API Endpoints for SMS PVA (Standard V1)
BASE_URL = 'https://smspva.com/priemnik.php'
API_ID = 1  # Using API v1

def get_balance():
    """Checks the balance of the API key."""
    params = {
        'metod': 'get_balance',
        'apikey': API_KEY,
        'id': API_ID,
        'service': SERVICE_ID, # Some services require service in balance check
        'country': COUNTRY_ID
    }
    try:
        response = requests.get(BASE_URL, params=params)
        data = response.json()
        
        if data.get('RESPONSE') == '1':
            balance = data.get('BALANCE', '0.00')
            currency = data.get('CURRENCY', 'RUB')
            print(f"[SUCCESS] Current Balance: {balance} {currency}")
            return float(balance)
        else:
            print(f"[ERROR] Balance check failed: {data.get('ERR_DESCRIPTION', 'Unknown error')}")
            return 0.0
    except Exception as e:
        print(f"[ERROR] Exception during balance check: {e}")
        return 0.0

def get_number():
    """Requests a new number from Indonesia for Telegram."""
    params = {
        'metod': 'get_number',
        'apikey': API_KEY,
        'id': API_ID,
        'country': COUNTRY_ID,
        'service': SERVICE_ID
    }
    
    print("[INFO] Requesting number...")
    try:
        response = requests.get(BASE_URL, params=params)
        data = response.json()
        
        # Check for specific ID error or general error
        if data.get('RESPONSE') == '1':
            number = data.get('NUMBER', '')
            number_id = data.get('ID', '')
            print(f"[SUCCESS] Number acquired: +{number} (ID: {number_id})")
            return number, number_id
        elif data.get('RESPONSE') == 'ERROR':
            err_msg = data.get('ERR_DESCRIPTION', 'Unknown error')
            print(f"[ERROR] Failed to get number: {err_msg}")
            if "NO_NUMBERS" in err_msg:
                print("[HINT] No numbers available right now. Try again later.")
            if "NO_BALANCE" in err_msg:
                print("[HINT] Please top up your balance.")
            return None, None
        else:
            print(f"[ERROR] Unexpected response: {data}")
            return None, None
    except Exception as e:
        print(f"[ERROR] Exception getting number: {e}")
        return None, None

def get_otp(number_id):
    """Polls for the SMS code using the Number ID."""
    if not number_id:
        return None

    print("[INFO] Waiting for SMS code (OTP)... Please send the code from Telegram.")
    
    max_attempts = 60  # Wait max 60 tries (e.g., 5 minutes)
    attempt = 0

    while attempt < max_attempts:
        params = {
            'metod': 'get_sms',
            'apikey': API_KEY,
            'id': API_ID,
            'country': COUNTRY_ID,
            'service': SERVICE_ID,
            'id_num': number_id
        }
        
        try:
            response = requests.get(BASE_URL, params=params)
            data = response.json()
            
            # Response '1' means SMS received. 
            # Sometimes '7' or 'ERROR' with 'STATUS_CANCEL' means error.
            
            if data.get('RESPONSE') == '1':
                # The SMS text is usually in 'SMS' or 'FULL_SMS'
                sms_text = data.get('SMS', '')
                full_sms = data.get('FULL_SMS', '')
                print(f"[SUCCESS] SMS Received!")
                print(f"[INFO] Content: {full_sms}")
                return sms_text
            elif data.get('RESPONSE') == 'ERROR':
                err_msg = data.get('ERR_DESCRIPTION', '')
                if 'STATUS_CANCEL' in err_msg or 'STATUS_FINISH' in err_msg:
                    print(f"[ERROR] Operation cancelled/finished: {err_msg}")
                    return None
                
            # If 'RESPONSE' is '3' (Waiting for SMS) or other codes, we continue waiting
            time.sleep(5) # Wait 5 seconds before checking again
            attempt += 1
            print(f"[INFO] Checking... ({attempt}/{max_attempts})")
            
        except Exception as e:
            print(f"[ERROR] Exception getting OTP: {e}")
            time.sleep(5)
            attempt += 1
            
    print("[TIMEOUT] Failed to receive SMS in time.")
    return None

def denounce_number(number_id):
    """Cancels the number if no SMS arrives (Async)."""
    # Note: SMS PVA sometimes supports synchronous denounce or async via separate methods
    # This is a placeholder for logic to cancel/get refund if needed.
    print(f"[INFO] Optionally denouncing number {number_id} (Not implemented in this basic script)")

# ==========================================
# MAIN EXECUTION
# ==========================================
if __name__ == "__main__":
    # 1. Check Balance
    bal = get_balance()
    if bal <= 0:
        print("[FATAL] Balance is 0 or negative. Please add funds.")
    else:
        # 2. Get Number
        num, num_id = get_number()
        
        if num and num_id:
            # 3. Get OTP
            otp_code = get_otp(num_id)
            
            if otp_code:
                print(f"\n=== RESULT ===")
                print(f"Phone Number: +{num}")
                print(f"OTP Code: {otp_code}")
            else:
                print("\n=== FAILED ===")
                print("Could not retrieve OTP.")
