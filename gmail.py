import time
import random
import string
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager

def generate_random_string(length=10):
    """Generates a random string for the username."""
    letters = string.ascii_lowercase
    return ''.join(random.choice(letters) for i in range(length))

def get_random_dob():
    """Generates a random Date of Birth (Age 18-25)."""
    year = random.randint(1998, 2005)
    month = random.randint(1, 12)
    day = random.randint(1, 28) # Using 28 to avoid invalid day/month combinations
    return f"{month:02d}", f"{day:02d}", f"{year:04d}"

def create_gmail_account(first_name, last_name):
    # Setup Chrome options
    chrome_options = Options()
    chrome_options.add_argument("--start-maximized")
    # If you want to run headless (without UI), uncomment the next line:
    # chrome_options.add_argument("--headless") 
    
    # Automatically download and setup chromedriver
    service = Service(ChromeDriverManager().install())
    driver = webdriver.Chrome(service=service, options=chrome_options)

    try:
        print("Navigating to Google Sign-up page...")
        driver.get("https://accounts.google.com/signup/v2/createaccount?flowName=GlifWebSignIn&flowEntry=SignUp")

        # Wait for the name fields to load
        wait = WebDriverWait(driver, 10)

        # 1. Enter Name
        print("Entering Name...")
        fname_field = wait.until(EC.presence_of_element_located((By.NAME, "firstName")))
        fname_field.send_keys(first_name)
        
        lname_field = driver.find_element(By.NAME, "lastName")
        lname_field.send_keys(last_name)

        # 2. Click Next
        next_button_name = driver.find_element(By.XPATH, "//div[@id='accountDetailsNext']//button")
        # Sometimes the button text varies, try clicking the button with index 0 if xpath fails
        next_button_name.click()

        # 3. Enter Username
        print("Generating Username...")
        # Wait for the username field
        username_field = wait.until(EC.presence_of_element_located((By.NAME, "Username")))
        
        # Loop until a unique username is found or user quits
        username = first_name.lower() + last_name.lower() + generate_random_string(4)
        username_field.send_keys(username)
        
        time.sleep(1) # Small pause to let Google check availability
        
        # 4. Click Next
        next_button_user = driver.find_element(By.XPATH, "//div[@id='usernameNext']//button")
        next_button_user.click()

        # 5. Enter Password
        print("Entering Password...")
        password_field = wait.until(EC.presence_of_element_located((By.NAME, "Passwd")))
        password = "TempPassword123!" # Set your desired password logic here
        password_field.send_keys(password)
        
        confirm_password_field = driver.find_element(By.NAME, "ConfirmPasswd")
        confirm_password_field.send_keys(password)

        # 6. Click Next
        next_button_pass = driver.find_element(By.XPATH, "//div[@id='passwordNext']//button")
        next_button_pass.click()

        # 7. Date of Birth
        print("Entering Date of Birth...")
        wait.until(EC.presence_of_element_located((By.NAME, "day")))
        
        month, day, year = get_random_dob()

        # Select Month (Dropdown is tricky, usually simpler to send keys to the input or select via index)
        # Google form usually uses a role="combobox" or specific inputs.
        # Current implementation often uses 3 separate inputs or a specialized widget.
        # We will try to find the inputs by name 'month', 'day', 'year' or aria-label
        
        # Strategy: Find the month dropdown, open it, select random index
        month_select = driver.find_element(By.ID, "month") # ID often changes, using XPATH usually safer
        # Note: Google's DOM changes frequently. The following is a generic approach.
        
        # Let's use the Javascript executor to interact if standard clicks fail due to shadow DOM or complex events.
        # But usually, standard selects work if we wait.
        
        # Filling DOB assuming standard input fields appear
        month_field = driver.find_element(By.NAME, "month")
        month_field.send_keys(month) # Usually sending number works or selecting from list
        
        day_field = driver.find_element(By.NAME, "day")
        day_field.send_keys(day)
        
        year_field = driver.find_element(By.NAME, "year")
        year_field.send_keys(year)

        # 8. Gender (Optional but usually required)
        # Usually a dropdown. Let's select 'Prefer not to say' (3rd option usually) or 'Male' (1)
        gender_dropdown = driver.find_element(By.ID, "gender")
        gender_dropdown.click()
        time.sleep(0.5)
        # Click the 3rd option (Prefer not to say) - xpath may vary
        gender_option = driver.find_element(By.XPATH, "//div[@data-value='3']") 
        gender_option.click()

        # 9. Click Next to proceed to Phone Verification (This is the hard part)
        next_button_dob = driver.find_element(By.XPATH, "//div[@id='birthdayNext']//button") # ID is hypothetical
        next_button_dob.click()
        
        print("Account setup steps initiated. Please complete phone verification manually if prompted.")
        print(f"Email: {username}@gmail.com")
        print(f"Password: {password}")
        
        # Keep browser open for manual verification (Phone/Recovery)
        input("Press Enter to close the browser...")

    except Exception as e:
        print(f"An error occurred: {e}")
    finally:
        driver.quit()

if __name__ == "__main__":
    # Random First and Last name
    f_name = "John"
    l_name = "Doe"
    
    create_gmail_account(f_name, l_name)
