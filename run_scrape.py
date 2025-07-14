import pandas as pd
from selenium import webdriver
from config import Config
from scrapers.linkedin import LinkedInScraper
import time


def main():
    # Load configuration
    cfg = Config()
    # Initialize WebDriver (Chrome by default)
    driver = webdriver.Chrome()

    try:
        # Instantiate the LinkedIn scraper
        linkedin_scraper = LinkedInScraper(driver, cfg)

        # Perform login
        linkedin_scraper.login()
        time.sleep(5)
        # Fetch job listings
        linkedin_scraper.fetch_listings()

    finally:
        # Always quit the driver
        linkedin_scraper.stop_looking()


if __name__ == "__main__":
    main()