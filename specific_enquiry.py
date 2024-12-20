import logging
import csv
from datetime import datetime
from selenium import webdriver
import time
from selenium.webdriver.common.by import By
from selenium.common.exceptions import NoSuchElementException, TimeoutException
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.firefox.options import Options

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


options = Options()
#options.add_argument('--headless')
driver = webdriver.Firefox(options=options)
wait = WebDriverWait(driver, 10, poll_frequency=1, ignored_exceptions=[NoSuchElementException, TimeoutException])

url_list = []
csv_path = "listings_to_answer.csv"

def login():
        driver.get("https://www.daft.ie/sharing/dublin-city?sort=publishDateDesc")
        try:
            accept_all_button = driver.find_element(By.CSS_SELECTOR, "#didomi-notice-agree-button")
            accept_all_button.click()
        except Exception as e:
            logger.info("No cookie disclaimer found")

        try:    
            wait.until(EC.visibility_of_element_located((By.CSS_SELECTOR, ".sc-1dcb8f9d-6")))
            sign_button = driver.find_element(By.CSS_SELECTOR, ".sc-1dcb8f9d-6")
            sign_button.click()
        except Exception as e:
            logger.info("Already signed in")
            return
        
        wait.until(EC.visibility_of_element_located((By.ID, "username")))
        username_field = driver.find_element(By.ID, "username")
        password_field = driver.find_element(By.ID, "password")

        username_field.click()
        username_field.send_keys("me@domain.com")

        password_field.click()
        password_field.send_keys("password123")
        login_button = driver.find_element(By.ID, "login")
        login_button.click()
        logger.info("Login successful.")

def is_element_present(driver, by, value, timeout=20):
    try:
        WebDriverWait(driver, timeout).until(EC.presence_of_element_located((by, value)))
        return True
    except TimeoutException:
        return False
    
def form_fill(url):
    driver.get(url)
    logger.info(f"Starting session: {url}")

    try:
        accept_all_button = wait.until(EC.visibility_of_element_located((By.CSS_SELECTOR, "#didomi-notice-agree-button")))
        accept_all_button.click()
    except Exception as e:
        logger.info("No disclaimer")

    button_container = driver.find_element(By.CSS_SELECTOR, ".sc-a15f80e5-3")
    driver.execute_script("arguments[0].scrollIntoView(true);", button_container)
    
    try:
        contact_button = driver.find_element(By.CSS_SELECTOR, ".cAVolf")
        contact_button.click()
        logger.info("Clicked contact button")
    except Exception as e:
        logger.error("No contact button found")
    
    try:
        email_button = driver.find_element(By.CSS_SELECTOR, ".tBpqT")
        email_button.click()
        logger.info("Clicked email button")
    except Exception as e:
        logger.error("No email button found")
    
    time.sleep(3)

    try:
        # Wait for the form to be present
        wait.until(EC.presence_of_element_located((By.ID, "keyword1")))
        wait.until(EC.presence_of_element_located((By.ID, "keyword2")))
        wait.until(EC.presence_of_element_located((By.ID, "keyword3")))
        wait.until(EC.presence_of_element_located((By.ID, "keyword4")))
        wait.until(EC.presence_of_element_located((By.ID, "message")))

        # Find and fill form fields

        fields = {
            "keyword1": "First Name",
            "keyword2": "Surname",
            "keyword3": "Email",
            "keyword4": "Phone number",
            "message": "Message"
        }

        for field_id, value in fields.items():
            field = wait.until(EC.element_to_be_clickable((By.ID, field_id)))
            time.sleep(0.5)
            field.clear()
            field.send_keys(value)
            logger.info(f"Filled {field_id}")

        send_button = driver.find_element(By.CSS_SELECTOR, ".sc-93d7981f-9 > div:nth-child(1) > button:nth-child(1)")
        wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, ".sc-93d7981f-9 > div:nth-child(1) > button:nth-child(1)")))
        logger.info("Found send button")

        logger.info("Form filled, sending.")
        send_button.click()
        time.sleep(3)
        
        if is_element_present(driver, By.CSS_SELECTOR, ".sc-a1b2d185-1"):
            logger.info(f"Enquiry sent successfully: {url}")
        else:
            logger.info(f"Enquiry failed: {url}")

    except Exception as e:
        logger.error(f"Error filling the form for URL {url}: {str(e)}")    
        
        #time.sleep(3)

       # while not is_element_present(driver, By.CSS_SELECTOR, ".sc-a1b2d185-1"):
        #    time.sleep(3)
         #   send_button.click()
          #  input("Enquiry failed, press enter to try again")

def read_urls_from_csv(file_path):
    try:
        # Open the CSV file
        with open(file_path, mode='r', newline='') as file:
            # Create a CSV reader object
            csv_reader = csv.reader(file)
            
            # Iterate over the rows in the CSV file
            for row in csv_reader:
                if row:  # Ensure the row is not empty
                    url_list.append(row[0])  # Add the URL (first column) to the list
                    
    except FileNotFoundError:
        print(f"Error: The file {file_path} was not found.")
        return None

login()
time.sleep(3)
read_urls_from_csv(csv_path)

for url in url_list:
    form_fill(url)

driver.quit()
logger.info("Enquiries finished, closing driver")