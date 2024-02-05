#!/usr/bin/env python
# coding: utf-8

# In[3]:


import os
import yaml
import time
from datetime import datetime
import re
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.keys import Keys
from selenium.common.exceptions import NoSuchElementException, TimeoutException
import pandas as pd

def log_event(event):
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    with open("login_logs.txt", "a") as log_file:
        log_file.write(f"{event}, {timestamp}\n")

def read_yaml_file(file_path):
    with open(file_path) as f:
        data = yaml.safe_load(f)
        return data

def setup_driver(chromedriver_path):
    s = Service(chromedriver_path)
    driver = webdriver.Chrome(service=s)
    driver.maximize_window()
    return driver

def login_to_linkedin(driver, page_url, email_input_xpath, password_input_xpath, sign_in_button_xpath, email, password):
    driver.get(page_url)
    time.sleep(1)
    driver.refresh()
    wait = WebDriverWait(driver, 10)
    time.sleep(3)

    log_event(f"Crawled {page_url}")

    email_input = wait.until(EC.presence_of_element_located((By.XPATH, email_input_xpath)))
    email_input.send_keys(email)

    password_input = wait.until(EC.presence_of_element_located((By.XPATH, password_input_xpath)))
    password_input.send_keys(password)

    sign_in_button = wait.until(EC.element_to_be_clickable((By.XPATH, sign_in_button_xpath)))
    sign_in_button.click()
    log_event("LOGGED IN with config.yml credentials")

    return wait

def extract_emails_from_text(text):
    email_pattern = r"[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}"
    return re.findall(email_pattern, text)

def search_for_subject(wait, search_bar_xpath, subject, all_people_xpath):
    time.sleep(2)
    search_bar = wait.until(EC.presence_of_element_located((By.XPATH, search_bar_xpath)))
    search_bar.send_keys(subject)
    search_bar.send_keys(Keys.ENTER)
    log_event(f"SEARCHED FOR {subject}")

    try:
        all_people = wait.until(EC.element_to_be_clickable((By.XPATH, all_people_xpath)))
        all_people.click()
        time.sleep(3)
        log_event("Clicked on 'All' button")
    except TimeoutException as e:
        print("Error:", e)
        log_event("Error: TimeoutException - 'All' button not found")

def extract_contact_info(wait, linkedin_url_xpath):
    linkedin_url = None
    full_name = None
    email_id = None
    bio = None

    try:
        full_name_element = wait.until(EC.presence_of_element_located((By.XPATH, '/html/body/div[5]/div[3]/div/div/div[2]/div/div/main/section[1]/div[2]/div[2]/div[1]/div[1]/h1')))
        full_name = full_name_element.text
        print("Name:", full_name)
        log_event(f"CRAWLED through profile of {full_name}")
        
        bio_element = wait.until(EC.presence_of_element_located((By.XPATH, '/html/body/div[5]/div[3]/div/div/div[2]/div/div/main/section[1]/div[2]/div[2]/div[1]/div[2]')))
        bio = bio_element.text
        print("Bio:", bio)
        contact_info_button = driver.find_element(By.XPATH, '/html/body/div[5]/div[3]/div/div/div[2]/div/div/main/section[1]/div[2]/div[2]/div[2]/span[2]/a')
        contact_info_button.click()

        try:
            time.sleep(3)
            contact_info = driver.find_element(By.XPATH, '/html/body/div[3]/div/div/div[3]/section/div/section[1]/div/a')
            linkedin_url_text = contact_info.get_attribute("href")
            linkedin_url = re.search(r'(https?://www\.linkedin\.com/in/\S+)', linkedin_url_text).group()
            print("LinkedIn URL:", linkedin_url)
        except (NoSuchElementException, AttributeError):
            print("LinkedIn URL not found")
             
        try:
            email_text = driver.page_source
            email_ids = extract_emails_from_text(email_text)
            if email_ids:
                email_id = email_ids[0]  # Assuming the first found email is the relevant one
                print("Email ID:", email_id)
            else:
                print("Email ID not found")
        except NoSuchElementException:
            print("Email ID not found")
            
    except NoSuchElementException:
        print("Contact info button not found")

    return full_name, bio, linkedin_url, email_id

if __name__ == '__main__':
    try:
        xpath_config_path = "xpath_config.yml"
        xpath_config = read_yaml_file(xpath_config_path)

        email_input_xpath = xpath_config["email_input"]
        password_input_xpath = xpath_config["password_input"]
        sign_in_button_xpath = xpath_config["sign_in_button"]
        search_bar_xpath = xpath_config["search_bar"]
        all_people_xpath = xpath_config["all_people"]
        linkedin_url_xpath = xpath_config.get("linkedin_url")  # Use get method to handle missing key

        config_path = "config.yml"
        config = read_yaml_file(config_path)

        email = config["username"]
        password = config["password"]
        subject = config["subject"]
        page_url = 'https://www.linkedin.com/?original_referer='

        driver = setup_driver("path_to_chromedriver")
        wait = login_to_linkedin(driver, page_url, email_input_xpath, password_input_xpath, sign_in_button_xpath, email, password)
        search_for_subject(wait, search_bar_xpath, subject, all_people_xpath)

        data = []
        for i in range(1, 10):
            time.sleep(4)
            
            people = wait.until(EC.element_to_be_clickable((By.XPATH, f'/html/body/div[5]/div[3]/div[2]/div/div[1]/main/div/div/div[2]/div/ul/li[{i}]/div/div/div[2]/div[1]/div[1]/div/span[1]/span/a')))
            people.click()
            time.sleep(3)

            full_name, bio, linkedin_url, email_id = extract_contact_info(wait, linkedin_url_xpath)

            data.append({
                'Name': full_name,
                'Bio': bio,
                'Email': email_id,
                'LinkedIn URL': linkedin_url})

            driver.back()
            time.sleep(1)
            driver.back()

        df = pd.DataFrame(data)
        current_dir = os.getcwd()
        csv_path = os.path.join(current_dir, f'{subject}.csv')
        df.to_csv(csv_path, index=False)
        log_event("CREATED CSV")

        driver.quit()

        os.system(f'start "excel" "{csv_path}"')

    except Exception as e:
        print("An error occurred:", e)
        log_event(f"ERROR: {e}")

