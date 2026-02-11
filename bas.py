import random
import time
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.chrome.service import Service

# --- Function to generate random data ---
def generate_random_info():
    first_names = ["John", "Jane", "Corey", "Travis", "Michelle", "Sara"]
    last_names = ["Doe", "Smith", "Davis", "Miller", "Wilson", "Moore"]
    
    first = random.choice(first_names)
    last = random.choice(last_names)
    # Generate a random username (Google often requires unique/complex usernames)
    username = f"{first.lower()}{last.lower()}{random.randint(100, 9999)}"
    password = f"{first}@{random.randint(100, 9999)}!" # Simple generated password
    
    # Random date of birth (simple example)
    dob_day = random.randint(1, 28)
    dob_month = random.randint(1, 12)
    dob_year = random.randint(1970, 2000)
    
    return first, last, username, password, dob_day, dob_month, dob_year

# --- Selenium Automation Script ---
def create_gmail_account():
    # Automatically install and get the path to the chromedriver
    service = Service(ChromeDriverManager().install())
    driver = webdriver.Chrome(service=service)
    driver.implicitly_wait(10) # Wait for elements to be found

    first_name, last_name, username, password, dob_day, dob_month, dob_year = generate_random_info()

    try:
        # Navigate to the Gmail sign-up page
        driver.get("https://accounts.google.com")

        # Fill in names
        driver.find_element(By.ID, "firstName").send_keys(first_name)
        driver.find_element(By.ID, "lastName").send_keys(last_name)

        # Click the "Use my current email address instead" to expose the username field if needed, otherwise fill the username directly
        # Google page structure can change frequently. The ID "username" is a common one.
        username_field = driver.find_element(By.ID, "username")
        username_field.send_keys(username)

        # Fill in password
        password_field = driver.find_element(By.NAME, "Passwd")
        password_field.send_keys(password)
        confirm_password_field = driver.find_element(By.NAME, "ConfirmPasswd")
        confirm_password_field.send_keys(password)

        # Click "Next"
        next_button = driver.find_element(By.XPATH, "//span[text()='Next']")
        next_button.click()

        # Wait for the next page to load (phone verification page is common)
        # This part will likely be blocked or require manual intervention due to Google's anti-bot measures.

        print(f"Attempted to create account with: {username}@gmail.com and password: {password}")
        print("Manual intervention likely required for phone/CAPTCHA verification.")
        
        time.sleep(10) # Keep browser open for a bit
    
    except Exception as e:
        print(f"An error occurred: {e}")
    
    finally:
        driver.quit()

if __name__ == "__main__":
    create_gmail_account()
