import csv
import requests
from pathlib import Path

from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC


# -------------------------
#  SETTINGS
# -------------------------
queries = {
    "Lawyers": ["San Francisco,CA", "San Antonio, TX"],
    "Restaurants": ["San Francisco, CA", "San Antonio, TX"]
}

base_path = Path(__file__).parent
write_file = base_path / "results.csv"

headers = [
    "URL",
    "Title",
    "Business Management",
    "Contact Information",
    "Entity Type",
    "Business Started",
    "Address",
    "Number of Employees",
    "Years in Business",
    "Rating",
    "Website",
    "About",
    "Keywords"
]

# CSV writer
file_exists = write_file.exists()
csv_file = open(write_file, "a", newline="", encoding="utf-8")
writer = csv.writer(csv_file)

if not file_exists:
    writer.writerow(headers)

# -------------------------
#  BROWSER SETUP
# -------------------------
chrome_options = Options()
# chrome_options.add_argument("--headless")
chrome_options.add_argument("--disable-blink-features=AutomationControlled")
driver = webdriver.Chrome(options=chrome_options)
wait = WebDriverWait(driver, 10)


# -------------------------
# Helper Functions
# -------------------------
def get_api_results(query, location):
    # Define your custom User-Agent string
    user_agent = 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/116.0.0.0 Safari/537.36'

    # Create headers with the User-Agent
    headers = {
        'User-Agent': user_agent
    }
    try:
      api_url = f"https://www.bbb.org/api/search"
      params = {
        'find_loc': location,
        'find_text': query,
        'page' : 15
        }
      response = requests.get(api_url, params=params, headers=headers)
      api_data = response.json()
      results = api_data["results"]
      return results
    except:
        return []


def safe_find_text(by, selector):
    """Safely get text of an element."""
    try:
        elem = wait.until(EC.presence_of_element_located((by, selector)))
        return elem.get_attribute("textContent").strip()
    except:
        return None


def safe_find_all(by, selector):
    """Safely get list of elements."""
    try:
        return driver.find_elements(by, selector)
    except:
        return []


def extract_website():
    """Extract website if available."""
    try:
        contact_tag = wait.until(
            EC.presence_of_element_located((By.CSS_SELECTOR, "div.bpr-header-contact"))
        )
        for a in contact_tag.find_elements(By.TAG_NAME, "a"):
            if "Visit Website" in a.text:
                return a.get_attribute("href")
    except:
        pass
    return None


def extract_about():
    """Extract about section."""
    try:
        return safe_find_text(By.CSS_SELECTOR, "div.bds-body").replace(",", "/")
    except:
        return None


def extract_other_information():
    """Extract detailed business information."""
    info = {
        "employees": None,
        "business_management": None,
        "contact_information": None,
        "entity_type": None,
        "business_started": None,
        "years_in_business": None,
    }

    # years in business
    for p in safe_find_all(By.CSS_SELECTOR, "p.bds-body"):
        if "Years in Business" in p.text:
            info["years_in_business"] = p.text.replace("Years in Business:", "").strip()

    # details list
    try:
        details_container = driver.find_element(By.CSS_SELECTOR, "dl.bpr-details-dl.stack")
        rows = details_container.find_elements(By.CSS_SELECTOR, "div.bpr-details-dl-data")
        for row in rows:
            dt = row.find_element(By.TAG_NAME, "dt").text.strip()
            dd = row.find_element(By.TAG_NAME, "dd").get_attribute("textContent").strip()

            if dt == "Number of Employees:":
                info["employees"] = dd
            elif dt == "Business Management:":
                info["business_management"] = dd.replace(",", "/")
            elif dt == "Contact Information:":
                info["contact_information"] = dd
            elif dt == "Type of Entity:":
                info["entity_type"] = dd
            elif dt == "Business Started:":
                info["business_started"] = dd
    except:
        pass

    return info


# -------------------------
# MAIN WORKFLOW
# -------------------------
for keyword, locations in queries.items():
    for location in locations:

        print(f"\nSearching: {keyword} in {location}")
        search_results = get_api_results(keyword, location)

        for item in search_results[:4]:  # scrape first 4
            profile_url = "https://www.bbb.org" + item["reportUrl"] + "/details"
            rating = item.get("rating")
            phone = item.get("phone", ["N/A"])
            phone = phone[0] if isinstance(phone, list) else phone

            print(f"Scraping: {profile_url}")

            driver.get(profile_url)

            # title
            title = safe_find_text(By.ID, "businessName")

            # website
            website = extract_website()

            # address
            address = safe_find_text(By.CSS_SELECTOR, "div.bpr-overview-address")
            if address:
                address = address.replace(",", "").replace("\n", " ")

            # about
            about = extract_about()

            # other info
            info = extract_other_information()

            row = [
                profile_url,
                title,
                info["business_management"],
                phone,
                info["entity_type"],
                info["business_started"],
                address,
                info["employees"],
                info["years_in_business"],
                rating,
                website,
                about,
                keyword
            ]

            writer.writerow(row)
            print("✓ Saved\n")

csv_file.close()
driver.quit()
