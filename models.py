from dataclasses import dataclass
from datetime import date

@dataclass
class JobListing:
    title: str
    company: str
    location: str
    link: str
    source: str
    date_posted: date
