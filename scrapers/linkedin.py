import os
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.action_chains import ActionChains
from selenium import webdriver
from config import Config
import time
import csv
from .base import BaseJobScraper
from models import JobListing
from typing import List


class LinkedInScraper(BaseJobScraper):
    
    def __init__(self, driver, config):
        # === Guarda driver y config en la instancia ===
        self.driver = driver
        self.cfg = config
        self.wait = WebDriverWait(driver, 10)

    def login(self):

        self.driver.get("https://www.linkedin.com/login/es?fromSignIn=true&trk=guest_homepage-basic_nav-header-signin")

        self.wait.until(
            EC.presence_of_element_located((By.ID, "username"))
            )

        email_input = self.driver.find_element(By.ID, "username")
        email_input.clear()                   # limpia cualquier texto previo
        email_input.send_keys(self.cfg.linkedin_email)

        password_input = self.driver.find_element(By.ID, "password")
        password_input.clear()                   # limpia cualquier texto previo
        password_input.send_keys(self.cfg.linkedin_password)


        checkbox = self.driver.find_element(By.ID, "rememberMeOptIn-checkbox")

        # 2. Un-check it
        self.driver.execute_script("arguments[0].checked = false;", checkbox)


        login_button = self.wait.until(
            EC.element_to_be_clickable((By.CSS_SELECTOR, 'button[data-litms-control-urn="login-submit"]'))
            )
        login_button.click()

    def fetch_listings(self) -> List[JobListing]:
        # navigate, extract, return normalized records
        self.driver.get("https://www.linkedin.com/jobs/search/?currentJobId=4263258080&distance=25&f_WT=2&geoId=91000007&keywords=data%20scientist")

        # 3) Scroll to load all job cards
        def scroll_job_list():
            job_list = self.wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, "ul.AatwRCIdFbntOCtdvHqGWSSyJybXzzBog > li")))
            last_height = self.driver.execute_script("return arguments[0].scrollHeight", job_list)
            while True:
                self.driver.execute_script("arguments[0].scrollTo(0, arguments[0].scrollHeight);", job_list)
                time.sleep(1)
                new_height = self.driver.execute_script("return arguments[0].scrollHeight", job_list)
                if new_height == last_height:
                    break
                last_height = new_height

        scroll_job_list()

        job_list = self.wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, "ul.AatwRCIdFbntOCtdvHqGWSSyJybXzzBog > li")))
        rows = []
        for idx, card in enumerate(job_list, start=1):
        #    Scroll card into view & click
            ActionChains(self.driver).move_to_element(card).perform()
            card.click()
    
            # Wait for the detail panel to load
            detail = self.wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, ".jobs-details__main-content")))
    
            # 5) Extract fields
            try:
                title = detail.find_element(By.CSS_SELECTOR, "h1.jobs-details-top-card__job-title").text.strip()
            except:
                title = None
            try:
                company = detail.find_element(By.CSS_SELECTOR, "a.jobs-details-top-card__company-url").text.strip()
            except:
                company = None
            try:
                location = detail.find_element(By.CSS_SELECTOR, ".jobs-details-top-card__bullet").text.strip()
            except:
                location = None
            try:
                date_posted = detail.find_element(By.CSS_SELECTOR, "span.jobs-details-top-card__job-info span").text.strip()
            except:
                date_posted = None
            # recruiter/contact info may be buried further down
            try:
                # expand "see more" if present
                see_more = detail.find_element(By.CSS_SELECTOR, ".jobs-description__see-more-button")
                see_more.click()
                time.sleep(0.5)
            except:
                pass
            try:
                description = detail.find_element(By.CSS_SELECTOR, ".jobs-description-content__text").text.strip()
            except:
                description = None
    
            rows.append({
                "Title": title,
                "Company": company,
                "Location": location,
                "Date Posted": date_posted,
                "Description": description
            })
            print(f"[{idx}/{len(job_list)}] Scraped: {title} at {company}")

        # 6) Write to CSV
        with open("linkedin_data_scientist_jobs.csv", "w", newline="", encoding="utf-8") as f:
            writer = csv.DictWriter(f, fieldnames=rows[0].keys())
            writer.writeheader()
            writer.writerows(rows)
        
        print("Done! Data saved to linkedin_data_scientist_jobs.csv")

    
    def stop_looking(self):
        self.driver.quit()

