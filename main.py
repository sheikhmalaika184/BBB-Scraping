from selenium import webdriver
import time
from selenium.webdriver.chrome.options import Options
from pathlib import Path
from selenium.webdriver.common.by import By
import requests
import os

# search queries 
# PATTERN = {serach keywork : [Location1, Location2,...]}
queries = {"Lawyers":["San Francisco, CA","San Antonio, TX"],"Restaurants":["San Francisco, CA","San Antonio, TX"]}

base_path = Path(__file__).parent
write_file = (base_path / "results.csv").resolve()
file_exists = os.path.isfile(write_file)
if(file_exists == False):
    f = open(write_file, "w", encoding="utf-8")
    f.write("URL~Title~Business Mangagement~Contact Information~Location~Number of Employees~Years in Business~Rating~Website~Keywords\n")
else:
    f = open(write_file, "a", encoding="utf-8")


# Define your custom User-Agent string
user_agent = 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/116.0.0.0 Safari/537.36'

# Create headers with the User-Agent
headers = {
    'User-Agent': user_agent
}
# starting a browser 
chrome_options = Options()
#chrome_options.add_argument('--headless')
driver = webdriver.Chrome(options = chrome_options)

for key in queries.keys():
  for location in queries[key]:
    try:
      api_url = f"https://www.bbb.org/api/search"
      params = {
        'find_loc': location,
        'find_text': key,
        'page' : 15
        }
      response = requests.get(api_url, params=params, headers=headers)
      api_data = response.json()
      results = api_data["results"]
      for i in range(len(results)):
        report_url  = results[i]["reportUrl"]
        profile_url = results[i]["reportUrl"] + "/details"
        rating = results[i]["rating"]
        phone_no = results[i]["phone"]
        print(profile_url)
        print(rating)
        print(phone_no)
        driver.get(profile_url)
        time.sleep(3)
        # title
        title = driver.find_element(By.CLASS_NAME,'bds-h3')
        title = title.text.replace("Additional Information for","")
        title = title.replace("\n", " ")
        print(title)
        # website
        website_tag = driver.find_element(By.XPATH, '//*[@id="content"]/div/div[3]/div[1]/div[2]/div[1]/div[2]/a')
        website = None
        if(website_tag.get_attribute("class") == "dtm-url"):
          website = website_tag.get_attribute("href")
        print(website)
        # address
        address_tag = driver.find_element(By.XPATH, '//*[@id="content"]/div/div[3]/div[1]/div[2]/div[1]/div[1]')
        address = None
        if(address_tag.get_attribute("class") == "dtm-address with-icon"):
          address = address_tag.text
          address = address.replace(",", "")
          address = address.replace("\n"," ")
        print(address)

        #other information
        years = None
        employees = None
        business_management = None
        contact_information = None
        other_information = driver.find_elements(By.XPATH, '//*[@id="content"]/div/div[3]/div[1]/div[1]/div/div/dl/div')
        for tag in other_information:
          dt = tag.find_element(By.TAG_NAME,'dt')
          dd = tag.find_element(By.TAG_NAME,'dd')
          if(dt.text == "Years in Business:"):
            years = dd.text
            years = years.replace("\n"," ")
          if(dt.text == "Number of Employees:"):
            employees = dd.text
            employees = employees.replace("\n"," ")
          if(dt.text == "Business Management"):
            business_management = dd.text
            business_management = business_management.replace("\n"," ")
          if(dt.text == "Contact Information"):
            contact_information = dd.text
            contact_information = contact_information.replace("\n"," ")
        print("Years: ",years)
        print("Employees: ", employees)
        print("BM: ", business_management)
        print("CI: ", contact_information)
        f.write(f"{report_url}~{title}~{business_management}~{contact_information}~{address}~{employees}~{years}~{rating}~{website}~{key}\n")
        print("")
    except Exception as e:
      print(e)
      pass