from distutils import debug
import re
from bs4 import BeautifulSoup
import requests


def get_flight_information(origin, destination, date,return_date):
    """
        Get flight information from Google Flights.

        Parameters:
        - origin: Departure airport or city code.
        - destination: Arrival airport or city code.
        - date: Departure date in YYYY-MM-DD format.
        - return_date: Return date in YYYY-MM-DD format.

        Returns:
        - HTML content of the flight information page if successful, otherwise None.
    """
    url = "https://www.google.com/flights"
    params = {
        "q": f"flights from {origin} to {destination} on {date} returning {return_date}",
        "hl": "en",  # Language preference
    }

    response = requests.get(url, params=params)

    if response.status_code == 200:
        #debug.Log("Response successfull")
        return response.text
    else:
        #debug.Log("Error in response")
        return None
    

def save_to_file(flight_info, min_price, filename):
    """
        Save flight information and minimum price to a file.

        Parameters:
        - flight_info: Information about the flight.
        - min_price: Minimum price of the flight.
        - filename: Name of the file to save the information to.
    """
    with open(filename, 'a', encoding='utf-8') as file:
        file.write(f"{flight_info},{min_price}\n")
        #debug.Log(f"Flight info and min price saved to {filename}")

def parse_flight_information(html, file=False):
    """
        Parse flight information from HTML content.

        Parameters:
        - html: HTML content of the flight information page.
        - file: Boolean indicating whether to save the minimum price to a file.

        Returns:
        - Information about the flight and its minimum price.
    """
    flight_info, min_price=extract_flight_data(html)

    #Write price in a file
    if file and min_price<float('inf'):
        save_to_file(flight_info, min_price, "minPrices.txt")


    return flight_info, min_price

#Can be improved in some other way to find price and informations :-)
def extract_flight_data(html_content):
    """
        Extract flight data from HTML content.

        Parameters:
        - html_content: HTML content of the flight information page.

        Returns:
        - Information about the flight and its minimum price.
    """
    soup = BeautifulSoup(html_content, 'html.parser')
    min_price = float('inf')  # Initialize minimum price as positive infinity
    min_price_flight = None  # Initialize minimum price flight details
    
    # Find all elements with class="pIav2d"
    flight_elements = soup.find_all(class_="pIav2d")
    
    for flight_element in flight_elements:
        try:
            # Find the element with aria-label attribute
            aria_label_element = flight_element.find(attrs={"aria-label": True})
            
            if aria_label_element:
                # Extract the data from aria-label attribute
                aria_label = aria_label_element['aria-label']
                
                # Extract flight details
                flight_details = aria_label.split('From', 1)[1].strip()
                
                # Extract price
                price_start_index = aria_label.find('From') + len('From')
                price_end_index = aria_label.find('euros') + len('euros')
                price_str = aria_label[price_start_index:price_end_index].strip()
                
                # Remove non-numeric characters from price string using regex
                price_numeric_str = re.sub(r'[^\d.]', '', price_str)
                
                # Convert price string to float
                price = float(price_numeric_str)
                
                # Update minimum price and associated flight details if a lower price is found
                if price < min_price:
                    min_price = price
                    min_price_flight = flight_details
        except:
            pass
            
    return min_price_flight, min_price


def APIScrap(origin, destination, date,  return_date, file=False):
    """
        Scrape flight information from Google Flights API.

        Parameters:
        - origin: Departure airport or city code.
        - destination: Arrival airport or city code.
        - date: Departure date in YYYY-MM-DD format.
        - return_date: Return date in YYYY-MM-DD format.
        - file: Boolean indicating whether to save the minimum price to a file.

        Returns:
        - Information about the flight and its minimum price.
    """
    flight_info = get_flight_information(origin, destination, date,return_date)
    if flight_info: 
        flight_info, min_price = parse_flight_information(flight_info,file=file)
        #debug.Log("Flight information retrieved successfully!")
        return flight_info, min_price
    else:
        #debug.Log("Failed to retrieve flight information.")
        pass

    