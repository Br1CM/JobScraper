import os
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from selenium import webdriver
from config import Config
import time
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

        time.sleep(5)

        html = self.driver.page_source
        # Guardas el HTML en un .txt (o .html si prefieres)
        with open("pagina.txt", "w", encoding="utf-8") as f:
            f.write(html)
    
    def stop_looking(self):
        self.driver.quit()

