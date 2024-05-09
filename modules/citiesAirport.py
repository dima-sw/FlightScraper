import requests
from bs4 import BeautifulSoup
import re

def normalize_country_name(country_name):
    return re.sub(r'[^\x00-\x7F]+', '', country_name)

def fetch_airports():
    try:
        url = "https://en.wikipedia.org/wiki/List_of_international_airports_by_country"
        response = requests.get(url)
        soup = BeautifulSoup(response.content, "html.parser")
        countries = []
        tables = soup.find_all("table", class_="wikitable")
        for table in tables:
            # Find the country name in the preceding <span> element with class "mw-headline"
            country_span = table.find_previous("span", class_="mw-headline")
            if country_span:
                country_name = country_span.text.strip()
                country_name = normalize_country_name(country_name)
                cities = []
                for row in table.find_all("tr")[1:]:
                    columns = row.find_all("td")
                    if len(columns) >= 3:
                        location = columns[0].text.strip()
                        cities.append(location)
                cities.sort()  # Sort cities alphabetically
                countries.append({country_name: cities})
        countries.sort(key=lambda x: list(x.keys())[0])  # Sort countries alphabetically by name
        return countries
    except Exception as e:
        print("Error fetching airports:", e)
        return []