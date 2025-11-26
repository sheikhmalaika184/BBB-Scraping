# BBB Directory Web Scraper
A robust Python-based web scraper that extracts detailed business information from the **Better Business Bureau (BBB) Directory** using Selenium and Requests.

---

## Overview

This project automates the extraction of business listings from:

**https://www.bbb.org/**

You can customize the scraper through a `queries` dictionary where:

- **Key** → Keyword (e.g., `"Restaurants"`)
- **Value** → List of locations (e.g., `"San Francisco, CA"`)

The scraper will iterate through each keyword–location pair and extract structured business information.

---

## Extracted Fields

For every business listing, the following details are collected:

1. URL  
2. Title  
3. Business Management  
4. Contact Information  
5. Location  
6. Number of Employees  
7. Years in Business  
8. Rating  
9. Website
10. Entity Type
11. Business Started Date
12. About
13. Keywords

---

## How It Works

1. You define keywords & locations inside the `queries` dictionary.
2. The script navigates to each search results page using its API.
3. Selenium scrolls, loads, and parses business detail pages.
4. Extracted results are saved into a structured CSV file.

---

## Output

The scraper generates:
- A single CSV file containing all extracted business information  
- Filename example: **`results.csv`**

---

## 📦 Installation
1. Clone the repo and install dependencies:
2. git clone https://github.com/sheikhmalaika184/BBB-Scraping.git
3. cd BBB-Scraping
4. pip install -r requirements.txt



