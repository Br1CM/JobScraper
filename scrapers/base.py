from typing import List
from selenium.webdriver.remote.webdriver import WebDriver
from models import JobListing

class BaseJobScraper:
    def __init__(self, driver: WebDriver, config):
        self.driver = driver
        self.config = config

    def login(self) -> None:
        raise NotImplementedError

    def fetch_listings(self) -> List[JobListing]:
        raise NotImplementedError