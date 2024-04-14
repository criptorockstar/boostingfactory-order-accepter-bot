import csv
import os

from dotenv import load_dotenv

from logic.factory_scraper import FactoryScraper

# Read keywords from csv
current_folder = os.path.dirname(__file__)
csv_path = os.path.join(current_folder, "keywords.csv")
with open(csv_path, "r") as file:
    reader = csv.reader(file)
    KEYWORDS = list(map(lambda row: row[0], reader))

# Read .env's configuration
load_dotenv()
HEADLESS = os.getenv("SHOW_BROWSER") != "True"
USERNAME = os.getenv("USERNAME")
PASSWORD = os.getenv("PASSWORD")

if __name__ == "__main__":
    factory_scraper = FactoryScraper(
        headless=HEADLESS, username=USERNAME, password=PASSWORD, keywords=KEYWORDS
    )

    factory_scraper.automate_orders()
