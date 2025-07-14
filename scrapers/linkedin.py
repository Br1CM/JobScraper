import os
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.action_chains import ActionChains
from selenium.common.exceptions import (
    StaleElementReferenceException,
    ElementClickInterceptedException,
    ElementNotInteractableException,
    NoSuchElementException
)
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
        time.sleep(5)

    def fetch_listings(self) -> List[JobListing]:
        
        
        # navigate, extract, return normalized record
        self.driver.get("https://www.linkedin.com/jobs/search/?distance=25&f_TPR=r86400&f_WT=2&geoId=91000007&keywords=data%20scientist")

        ul_css = "ul.AatwRCIdFbntOCtdvHqGWSSyJybXzzBog"

        # Wait for the <ul> container
        container = self.wait.until(
            EC.presence_of_element_located((By.CSS_SELECTOR, ul_css))
            )
        
        def parse_job_card(card):
            """
            Given a WebElement for the <li> job-card, return a dict of:
             - job_id
             - title
             - url
             - company
             - location
            """
            data = {}
            # 1) job id
            data["job_id"] = card.get_attribute("data-occludable-job-id")

            # 2) title + URL
            try:
                link = card.find_element(By.CSS_SELECTOR, "a.job-card-container__link")
                data["title"] = link.text.strip()
                data["url"]   = link.get_attribute("href")
            except NoSuchElementException:
                data["title"] = None
                data["url"]   = None
    
            # 3) company name
            try:
                data["company"] = card.find_element(
                    By.CSS_SELECTOR,
                    ".artdeco-entity-lockup__subtitle span"
                ).text.strip()
            except NoSuchElementException:
                data["company"] = None

            # 4) location
            try:
                data["location"] = card.find_element(
                    By.CSS_SELECTOR,
                    ".job-card-container__metadata-wrapper li span"
                ).text.strip()
            except NoSuchElementException:
                data["location"] = None

            return data



        def parse_detail_pane(detail):
            """
            Given the root WebElement of the job-detail pane, extract:
            - title
            - company
            - location
            - date_posted
            - applicants
            - work_mode
            - full_description (text)
            - recruiter_name, recruiter_profile (if present)
            - company_overview (text)
            """
            info = {}

            # 1) Title
            try:
                info["title"] = detail.find_element(
                    By.CSS_SELECTOR,
                    ".job-details-jobs-unified-top-card__job-title h1"
                ).text.strip()
            except NoSuchElementException:
                info["title"] = None

            # 2) Company
            try:
                info["company"] = detail.find_element(
                    By.CSS_SELECTOR,
                    ".job-details-jobs-unified-top-card__company-name a"
                ).text.strip()
            except NoSuchElementException:
                info["company"] = None

            # 3) Location / date / applicants (all in the tertiary-description-container span sequence)
            try:
                terc = detail.find_element(
                    By.CSS_SELECTOR,
                    ".job-details-jobs-unified-top-card__tertiary-description-container"
                ).text.split("·")
                # e.g. ["Italia ", " hace 1 hora ", " 22 solicitudes"]
                info["location"]    = terc[0].strip()
                info["date_posted"] = terc[1].strip()
                # strip “solicitudes” to get number
                info["applicants"]  = terc[2].strip()
            except (NoSuchElementException, IndexError):
                info["location"] = info["date_posted"] = info["applicants"] = None

            # 4) Work mode / insight flags (e.g. “En remoto” badges)
            try:
                badge = detail.find_element(
                    By.CSS_SELECTOR,
                    "li.job-details-jobs-unified-top-card__job-insight--highlight span.ui-label"
                )
                info["work_mode"] = badge.text.strip()
            except NoSuchElementException:
                info["work_mode"] = None

            # 5) Full job description HTML/text
            try:
                desc_el = detail.find_element(
                    By.CSS_SELECTOR,
                    ".jobs-description-content__text--stretch"
                )
                info["full_description"] = desc_el.text.strip()
            except NoSuchElementException:
                info["full_description"] = None

            # 6) Recruiter / hiring team info
            try:
                hirer = detail.find_element(
                    By.CSS_SELECTOR,
                    ".job-details-people-who-can-help__section--two-pane .jobs-poster__name"
                )
                info["recruiter_name"]    = hirer.text.strip()
                info["recruiter_profile"] = hirer.get_attribute("href")
            except NoSuchElementException:
                info["recruiter_name"] = info["recruiter_profile"] = None

            # 7) Company overview (short “About company”)
            try:
                info["company_overview"] = detail.find_element(
                    By.CSS_SELECTOR,
                    ".jobs-company__company-description"
                ).text.strip()
            except NoSuchElementException:
                info["company_overview"] = None

            return info




        last_count = 0
        index      = 0
        jobs_data = []
        while True:
            # Re-fetch the list of <li> items each iteration
            items = container.find_elements(By.TAG_NAME, "li")
            # If we’ve processed all currently-loaded items…
            if index >= len(items):
                # If no new items have loaded since last loop, we’re done
                if len(items) == last_count:
                    break
                # Otherwise, scroll to load more
                last_count = len(items)
                self.driver.execute_script(
                    "arguments[0].scrollTo(0, arguments[0].scrollHeight);", 
                    container
                )
                time.sleep(1)
                continue
            
            item = items[index]
            try:
                # Scroll the specific <li> into view
                self.driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", item)
                time.sleep(0.3)
                # Click it
                item.click()
                
                item_data = parse_job_card(item)
                
                detail = self.wait.until(
                     EC.presence_of_element_located((By.CSS_SELECTOR, ".jobs-search__job-details"))
                     )
                # 3) scrape the detail
                detail_data = parse_detail_pane(detail)
                item_data.update(detail_data)
                jobs_data.append(item_data)
                
                index += 1
            except (StaleElementReferenceException, ElementClickInterceptedException, ElementNotInteractableException):
                # If the element went stale or isn’t yet interactable, 
                # scroll the container a bit more and retry
                self.driver.execute_script(
                    "arguments[0].scrollBy(0, 100);", container
                )
                time.sleep(0.5)
                # don’t increment index here—try again
                continue



        # 6) Write to CSV
        with open("linkedin_data_scientist_jobs.csv", "w", newline="", encoding="utf-8") as f:
            writer = csv.DictWriter(f, fieldnames=jobs_data[0].keys())
            writer.writeheader()
            writer.writerows(jobs_data)
        
        print("Done! Data saved to linkedin_data_scientist_jobs.csv")

    
    def stop_looking(self):
        self.driver.quit()

