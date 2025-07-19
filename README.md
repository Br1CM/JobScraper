# Job Scraper

**A personal project to automate tracking of job postings that match my criteria and build a list of positions to which I could fit in.**

## Overview

This is a simple, self-hosted web-scraping tool that navigates to the career pages where I’m actively searching for work, applies my personal filters, and compiles an up-to-date list of relevant job postings. It uses Selenium for browser automation and a `.env` file to keep credentials and configuration secure.

## Features

- **Automated Login**  
  Logs into each site (e.g. LinkedIn) using credentials stored in a `.env` file.  
- **Dynamic Filtering**  
  Applies custom filters (keywords, locations, remote/on-site preferences) to only capture the jobs you care about.  
- **Result Export**  
  Saves filtered job listings (title, company, location, link).  

### Prerequisites

I have used poetry for managing dependencies, it will make it easier if you clone this repo :)

- Python >3.11 

