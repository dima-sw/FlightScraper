from tqdm import tqdm
import os
import modules.scrapFlight as scrapFlight
import modules.mailSend as mailSend
import modules.dateGenerator as  dateGenerator
import json
from modules.dateGenerator import Weekday
origin="Naples"


file_path = os.path.join(os.getcwd(), 'cities.json')
# Open the JSON file
# Check if the file exists
if os.path.exists(file_path):
    # Open the JSON file
    with open(file_path, 'r') as file:
        data_dict = json.load(file)
        weekEnd = data_dict["citiesWeekEnd"]["cities"]
        weekEndPrice = data_dict["citiesWeekEnd"]["maxPrice"]
        oneWeek = data_dict["citiesWeek"]["cities"]
        oneWeekPrice = data_dict["citiesWeek"]["maxPrice"]
        twoWeek = data_dict["cities2Week"]["cities"]
        twoWeekPrice = data_dict["cities2Week"]["maxPrice"]
else:
    print(f"File {file_path} not found")

datesWeekEnd=dateGenerator.dataGen(Weekday.Friday.value,Weekday.Sunday.value,1,6,5)
datesTwoWeeks=dateGenerator.dataGen(Weekday.Friday.value,Weekday.Sunday.value,2,6,5)
datesOneWeek=dateGenerator.dataGen(Weekday.Friday.value,Weekday.Sunday.value,3,6,5)





flights=[]
for date in tqdm(datesTwoWeeks, desc="Dates Progress"):
   
    flights=[]
    for country, cities in tqdm(twoWeek.items(), desc="Countries Progress: "+date['startDate']+" to "+date['endDate'], leave=False):
        for city in tqdm(cities, desc="Cities Progress: "+country, leave=False):
            flight_info, min_price = scrapFlight.APIScrap(origin, city, date['startDate'], date['endDate'], file=True)
            if min_price < float('inf') and min_price < twoWeekPrice:               
                flights.append({'country': country, 'city':city, 'price': min_price, 'info': flight_info,  'date':date['startDate']+" - "+date['endDate']})
    print(flights)
    if(len(flights)>0):
        mailSend.send_email(flights)


for date in tqdm(datesOneWeek, desc="Dates Progress"):
   
    flights=[]
    for country, cities in tqdm(oneWeek.items(), desc="Countries Progress: "+date['startDate']+" to "+date['endDate'], leave=False):
        for city in tqdm(cities, desc="Cities Progress: "+country, leave=False):
            flight_info, min_price = scrapFlight.APIScrap(origin, city, date['startDate'], date['endDate'],  file=True)
            if min_price < float('inf') and min_price < oneWeekPrice:               
                flights.append({'country': country, 'city':city, 'price': min_price, 'info': flight_info,  'date':date['startDate']+" - "+date['endDate']})
    print(flights)
    if(len(flights)>0):
        mailSend.send_email(flights)


for date in tqdm(datesWeekEnd, desc="Dates Progress"):
   
    flights=[]
    for country, cities in tqdm(weekEnd.items(), desc="Countries Progress: "+date['startDate']+" to "+date['endDate'], leave=False):
        for city in tqdm(cities, desc="Cities Progress: "+country, leave=False):
            flight_info, min_price = scrapFlight.APIScrap(origin, city, date['startDate'], date['endDate'],  file=True)
            if min_price < float('inf') and min_price < weekEndPrice:               
                flights.append({'country': country, 'city':city, 'price': min_price, 'info': flight_info,  'date':date['startDate']+" - "+date['endDate']})
    print(flights)
    if(len(flights)>0):
        mailSend.send_email(flights)




    
