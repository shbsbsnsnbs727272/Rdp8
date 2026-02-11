import random
import time
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager

def create_random_user_data():
    """Generates random first name, last name, and a potential username/password."""
    first_names = ["John", "Jane", "Corey", "Travis", "Michelle", "Sara", "Adam", "Chris"]
    last_names = ["Doe", "Smith", "Jenkins", "Cook", "Williams", "Brown", "Davis"]
    
    first_name = random.choice(first_names)
    last_name = random.choice(last_names)
    # Generate a unique username by combining names with random numbers
    username = f"{first_name.lower()}.{last_name.lower()}{random.randint(100, 9999)}"
    password = f"TestP@{random.randint(100, 999)}!" # Simple secure-ish password

    return first_name, last_name, username, password

def automate_gmail_signup():
    first_name, last_name, username, password = create_random_user_data()
    print(f"Attempting to sign up with: {first_name} {last_name}, Username: {username}, Password: {password}")

    # Use webdriver_manager to automatically install/manage the correct ChromeDriver
    service = Service(ChromeDriverManager().install())
    driver = webdriver.Chrome(service=service)

    try:
        # Navigate to the Gmail sign-up page
        driver.get("https://accounts.google.com")
        driver.maximize_window()
        
        # Use WebDriverWait for elements to be visible
        wait = WebDriverWait(driver, 10)

        # Fill in first name
        first_name_field = wait.until(EC.visibility_of_element_located((By.ID, "firstName")))
        first_name_field.send_keys(first_name)

        # Fill in last name
        last_name_field = driver.find_element(By.ID, "lastName")
        last_name_field.send_keys(last_name)

        # Fill in username
        username_field = driver.find_element(By.ID, "username")
        username_field.send_keys(username)

        # Fill in password
        password_field = driver.find_element(By.NAME, "Passwd")
        password_field.send_keys(password)

        # Confirm password
        confirm_password_field = driver.find_element(By.NAME, "ConfirmPasswd")
        confirm_password_field.send_keys(password)

        # Click the "Next" button
        next_button = driver.find_element(By.XPATH, "//button[./span[text()='Next']]")
        next_button.click()

        # At this point, Google will likely ask for phone verification, which stops the automation.
        print("\nScript proceeded to the next step. Manual intervention is likely required for phone verification or CAPTCHA.")
        print("The browser will remain open for a few moments for you to check.")
        time.sleep(20) # Keep browser open to observe the next page

    except Exception as e:
        print(f"An error occurred: {e}")
        time.sleep(10)
    finally:
        driver.quit()

if __name__ == "__main__":
    automate_gmail_signup()
