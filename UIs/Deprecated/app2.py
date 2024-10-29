import streamlit as st
import json
import asyncio
from datetime import datetime
from modules.citiesAirport import fetch_airports
from modules.dateGenerator import dataGen, Weekday
from modules.mailSend import send_email
from modules.scrapFlight import APIScrap

# Initialization
from_countries_dict = {}
to_countries_dict = {}
found_flights = []
cities_air = fetch_airports()

st.set_page_config(layout="wide")
st.title("Flight Scraper")

# Sidebar for settings and inputs
st.sidebar.header("Settings")

country_list = [""] + [list(country.keys())[0] for country in cities_air]

# Sidebar widgets for From Country and City
from_country = st.sidebar.selectbox("From Country", country_list)

# Function to get cities based on selected country
def get_cities(selected_country):
    for country in cities_air:
        if selected_country in country:
            return country[selected_country]
    return [""]

# Populate from_city options based on selected from_country
if from_country:
    from_city_options = [""] + get_cities(from_country)
else:
    from_city_options = [""]

from_city = st.sidebar.selectbox("From City", from_city_options)

# Sidebar widgets for To Country and City
st.sidebar.subheader("To")
to_country = st.sidebar.selectbox("To Country", country_list)

# Populate to_city options based on selected to_country
if to_country:
    to_city_options = [""] + get_cities(to_country)
else:
    to_city_options = [""]

to_city = st.sidebar.selectbox("To City", to_city_options)

# Budget
budget = st.sidebar.number_input("Budget", min_value=0, value=0)

# Add From Country and City
if st.sidebar.button("Add From"):
    if from_country and from_city:
        if from_country in from_countries_dict:
            if from_city not in from_countries_dict[from_country]:
                from_countries_dict[from_country].append(from_city)
        else:
            from_countries_dict[from_country] = [from_city]

# Add To Country and City
if st.sidebar.button("Add To"):
    if to_country and to_city:
        if to_country in to_countries_dict:
            if to_city not in to_countries_dict[to_country]:
                to_countries_dict[to_country].append(to_city)
        else:
            to_countries_dict[to_country] = [to_city]

# Display From and To lists
st.sidebar.subheader("From List")
for country, cities in from_countries_dict.items():
    st.sidebar.write(f"{country}: {', '.join(cities)}")

st.sidebar.subheader("To List")
for country, cities in to_countries_dict.items():
    st.sidebar.write(f"{country}: {', '.join(cities)}")

# Date options
st.sidebar.subheader("Dates")
date_type = st.sidebar.radio("Select Date Type", ("Dynamic Dates", "Specific Dates"))

if date_type == "Dynamic Dates":
    day_in = st.sidebar.selectbox("Day In", ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"])
    day_out = st.sidebar.selectbox("Day Out", ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"])
    weeks = st.sidebar.number_input("Weeks", min_value=1, value=1)
    from_month = st.sidebar.selectbox("From Month", ["January", "February", "March", "April", "May", "June", "July", "August", "September", "October", "November", "December"])
    month_range = st.sidebar.number_input("Month Range", min_value=1, value=1)
    weeks_steps = st.sidebar.number_input("Weeks Steps", min_value=1, value=1)
else:
    from_date = st.sidebar.date_input("From Date", datetime.now())
    to_date = st.sidebar.date_input("To Date", datetime.now())

# Main section for results and actions
st.header("Flight Information")

# Scraping button
if st.button("Scrap"):
    async def scrap():
        #nonlocal found_flights
        found_flights = []
        
        if date_type == "Dynamic Dates":
            dates = dataGen(Weekday[day_in].value, Weekday[day_out].value, weeks, month_range, from_month_combobox.index(from_month) + 1, weeksStep=weeks_steps)
        else:
            dates = [{"startDate": from_date.strftime("%Y-%m-%d"), "endDate": to_date.strftime("%Y-%m-%d")}]
        
        total_tasks = len(dates) * len(from_countries_dict) * len(to_countries_dict)
        completed_tasks = 0
        for date in dates:
            for fromCountry, fromCities in from_countries_dict.items():
                for fromCity in fromCities:
                    for toCountry, toCities in to_countries_dict.items():
                        for toCity in toCities:
                            flight_info, min_price = APIScrap(fromCity, toCity, date['startDate'], date['endDate'], file=False)
                            if min_price < budget:
                                found_flights.append({
                                    'date': date,
                                    'cityFrom': fromCity,
                                    'countryTo': toCountry,
                                    'cityTo': toCity,
                                    'flightInfo': flight_info,
                                    'min_price': min_price
                                })
                            completed_tasks += 1
                            st.progress(completed_tasks / total_tasks)

    asyncio.run(scrap())

# Display flight information
for flight in found_flights:
    st.write(f"Date: {flight['date']['startDate']} - {flight['date']['endDate']}")
    st.write(f"From: {flight['cityFrom']}")
    st.write(f"To: {flight['cityTo']}, {flight['countryTo']}")
    st.write(f"Min Price: {flight['min_price']} euros")
    st.write(f"Flight Info: {flight['flightInfo']}")
    st.write("-" * 100)

# Sorting options
if st.button("Sort by CityTo"):
    found_flights.sort(key=lambda x: x['cityTo'])

if st.button("Sort by Price"):
    found_flights.sort(key=lambda x: x['min_price'])

if st.button("Sort by Date"):
    found_flights.sort(key=lambda x: datetime.strptime(x['date']['startDate'], '%Y-%m-%d'))
