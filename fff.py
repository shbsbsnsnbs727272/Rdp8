import csv
import time
import random
import undetected_chromedriver as uc
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

def create_gmail(data):
    # Initialize undetected chrome to bypass basic bot checks
    options = uc.ChromeOptions()
    driver = uc.Chrome(options=options)
    wait = WebDriverWait(driver, 20)

    try:
        driver.get("https://accounts.google.com")

        # 1. Name Entry
        wait.until(EC.presence_of_element_located((By.NAME, "firstName"))).send_keys(data['first_name'])
        driver.find_element(By.NAME, "lastName").send_keys(data['last_name'])
        driver.find_element(By.XPATH, "//span[text()='Next']").click()

        # 2. DOB and Gender
        time.sleep(random.uniform(1, 3)) # Human-like delay
        wait.until(EC.presence_of_element_located((By.ID, "day"))).send_keys(data['dob_day'])
        driver.find_element(By.ID, "year").send_keys(data['dob_year'])
        
        # Select Month and Gender (Simplified)
        driver.find_element(By.ID, "month").send_keys(data['dob_month'])
        driver.find_element(By.ID, "gender").send_keys("Rather not say")
        driver.find_element(By.XPATH, "//span[text()='Next']").click()

        # 3. Username and Password
        # Google may suggest usernames; this script assumes custom input
        wait.until(EC.presence_of_element_located((By.NAME, "Username"))).send_keys(data['username'])
        driver.find_element(By.NAME, "Passwd").send_keys(data['password'])
        driver.find_element(By.NAME, "ConfirmPasswd").send_keys(data['password'])
        driver.find_element(By.XPATH, "//span[text()='Next']").click()

        # IMPORTANT: Google will likely prompt for Phone Verification here.
        # Manual intervention or an SMS API (like 5sim or SMS-Activate) is required.
        print(f"Account {data['username']} reached verification step.")
        time.sleep(60) 

    finally:
        driver.quit()

# Load data and run
with open('accounts.csv', mode='r') as file:
    reader = csv.DictReader(file)
    for row in reader:
        create_gmail(row)
