from selenium import webdriver
from selenium.webdriver.common.by import By

# Initialize driver
driver = webdriver.Chrome(executable_path='chromedriver.exe')

# Navigate to a URL
driver.get("https://accounts.google.com")

# Example of locating and filling fields
# Note: Google's actual IDs change frequently to prevent automation
try:
    driver.find_element(By.NAME, "firstName").send_keys("YourName")
    driver.find_element(By.NAME, "lastName").send_keys("YourLastName")
    driver.find_element(By.ID, "username").send_keys("desired_email_2024")
    driver.find_element(By.NAME, "Passwd").send_keys("SecurePassword123!")
    driver.find_element(By.NAME, "ConfirmPasswd").send_keys("SecurePassword123!")
    
    # Click Next
    driver.find_element(By.ID, "accountDetailsNext").click()
except Exception as e:
    print(f"Elements not found or blocked: {e}")
