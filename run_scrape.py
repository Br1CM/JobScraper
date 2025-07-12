import pandas as pd
from selenium import webdriver
from config import Config
from scrapers.linkedin import LinkedInScraper


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

        # Fetch job listings
        listings = linkedin_scraper.fetch_listings()

        # Convert to DataFrame and save
        #df = pd.DataFrame([job.__dict__ for job in listings])
        #df.to_csv(cfg.output, index=False)

        #print(f"Saved {len(listings)} listings to {cfg.output}")

    finally:
        # Always quit the driver
        linkedin_scraper.stop_looking()


if __name__ == "__main__":
    main()