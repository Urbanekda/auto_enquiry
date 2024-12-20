#!/usr/bin/env python
# coding: utf-8

# In[1]:


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
options.add_argument('--headless')
driver = webdriver.Firefox(options=options)
wait = WebDriverWait(driver, 10, poll_frequency=1, ignored_exceptions=[NoSuchElementException, TimeoutException])


# In[2]:


def log_answered_listing(url):
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    with open('answered_listings.csv', 'a', newline='') as file:
        writer = csv.writer(file)
        writer.writerow([timestamp, url])
    logger.info(f"Logged answered listing: {url}")


# In[3]:


def log_failed_listing(url):
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    with open('failed_listings.csv', 'a', newline='') as file:
        writer = csv.writer(file)
        writer.writerow([timestamp, url])
    logger.info(f"Logged answered listing: {url}")


# In[4]:


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
        
    
    


# In[5]:


def get_answered_listings():
    answered_listings = set()
    try:
        with open('answered_listings.csv', 'r', newline='') as file:
            reader = csv.reader(file)
            for row in reader:
                if len(row) > 1:
                    answered_listings.add(row[1])
    except FileNotFoundError:
        logger.info("No existing answered_listings.csv file found.")
    return answered_listings


# In[6]:


def get_failed_listings():
    failed_listings = set()
    try:
        with open('failed_listings.csv', 'r', newline='') as file:
            reader = csv.reader(file)
            for row in reader:
                if len(row) > 1:
                    failed_listings.add(row[1])
    except FileNotFoundError:
        logger.info("No existing failed_listings.csv file found.")
    return failed_listings


# In[7]:


def find_listings():
    unanswered_listings = []

    answered_listings = get_answered_listings()
    failed_listings = get_failed_listings()

    try:
        accept_all_button = driver.find_element(By.CSS_SELECTOR, "#didomi-notice-agree-button")
        wait.until(EC.visibility_of_element_located(accept_all_button))
        accept_all_button.click()
    except Exception as e:
        logger.info("No disclaimer")
    
    wait.until(EC.visibility_of_element_located((By.TAG_NAME, "main")))
    main_element = driver.find_element(By.TAG_NAME,"main")
    ul_element = main_element.find_element(By.TAG_NAME, "ul")
    li_elements = ul_element.find_elements(By.TAG_NAME, "li")

    for li in li_elements:
        anchor = li.find_element(By.TAG_NAME, "a")
        href_value = anchor.get_attribute("href")
        if href_value not in answered_listings and href_value not in failed_listings:
            unanswered_listings.append(href_value)
            logger.info(f"Found new listing: {href_value}")
        else:
            logger.info(f"Already answered or failed listing: {href_value}")
        
    return unanswered_listings


# In[8]:


def is_element_present(driver, by, value, timeout=20):
    try:
        WebDriverWait(driver, timeout).until(EC.presence_of_element_located((by, value)))
        return True
    except TimeoutException:
        return False


# In[9]:


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
            log_answered_listing(url)
        else:
            logger.info(f"Enquiry failed: {url}")

    except Exception as e:
        logger.error(f"Error filling the form for URL {url}: {str(e)}")


# In[10]:


def change_page():
    nav_container = driver.find_element(By.CSS_SELECTOR, ".sc-de7a1258-0")
    driver.execute_script("arguments[0].scrollIntoView(true);", nav_container)
    next_button = nav_container.find_element(By.CSS_SELECTOR, "div.sc-e8b83919-6:nth-child(7) > button:nth-child(1)")
    next_button.click()
    logger.info("Navigating to next page")
    time.sleep(3)


# In[ ]:


if __name__ == "__main__":
    logger.info("Starting the auto enquiry process")
    pages_to_scrape = 3
    all_listings = []

    login()

    #find listings returns unanswered listings on the page

    while pages_to_scrape > 0:
        page_listings = find_listings()
        all_listings.extend(page_listings)
        change_page()
        pages_to_scrape -= 1

    for index, url in enumerate(all_listings):
        logger.info(f"Processing {index} of {len(all_listings)}")
        form_fill(url)
        time.sleep(5)
        if (index + 1) % 5 == 0:
            time.sleep(180)
            logger.info(f"Cooldown 3 minute...")

    logger.info("Auto enquiry process completed")


# In[ ]:




