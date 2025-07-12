# config.py
import os
import argparse
from dotenv import load_dotenv

class Config:
    def __init__(self):
        # 1) Load .env file
        load_dotenv()

        # 2) Read defaults from environment
        self.linkedin_email    = os.getenv("LINKEDIN_EMAIL")
        self.linkedin_password = os.getenv("LINKEDIN_PASSWORD")
        #self.keywords          = [kw.strip() for kw in os.getenv("JOB_KEYWORDS", "").split(",") if kw]
        #self.location          = os.getenv("JOB_LOCATION")
        #self.remote_only       = os.getenv("REMOTE_ONLY", "false").lower() == "true"
        #self.output            = os.getenv("OUTPUT_PATH", "jobs.csv")

        # 3) Override with any CLI args
        self._parse_args()

    def _parse_args(self):
        parser = argparse.ArgumentParser(
            description="Scraper configuration (env vars can be overridden here)"
        )
        parser.add_argument("--email",      help="LinkedIn email")
        parser.add_argument("--password",   help="LinkedIn password")
        #parser.add_argument("--keywords",   help="Comma-separated job keywords")
        #parser.add_argument("--location",   help="Job location filter")
        #parser.add_argument("--remote-only", action="store_true", help="Only include remote jobs")
        #parser.add_argument("--output",     help="Output file path (CSV or TXT)")
        args = parser.parse_args()

        if args.email:      self.linkedin_email    = args.email
        if args.password:   self.linkedin_password = args.password
        #if args.keywords:   self.keywords          = [kw.strip() for kw in args.keywords.split(",")]
        #if args.location:   self.location          = args.location
        #if args.remote_only: self.remote_only      = True
        #if args.output:     self.output            = args.output


