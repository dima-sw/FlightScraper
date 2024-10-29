import streamlit as st
import pandas as pd
from datetime import datetime
from modules.citiesAirport import fetch_airports
from modules.dateGenerator import dataGen, Weekday

# Fetch airports data once
cities_air = fetch_airports()

class FlightScraperUI():
    def __init__(self) -> None:
        self.initialize_session_state()

        st.set_page_config(layout="wide")
        st.title("Flight Scraper")
        
        # Sidebar for settings and inputs
        st.sidebar.header("Settings")
        col1, col2 = st.sidebar.columns(2)
        is_cities_tab = col1.button("Cities", key="cities_tab", help="Show Cities Tab")
        is_dates_tab = col2.button("Dates", key="dates_tab", help="Show Dates Tab")

        if is_cities_tab:
            st.session_state.selected_tab = "Cities"
        elif is_dates_tab:
            st.session_state.selected_tab = "Dates"

        if st.session_state.selected_tab == "Cities":
            self.show_cities_tab()
        elif st.session_state.selected_tab == "Dates":
            self.show_dates_tab()

    def initialize_session_state(self):
        if 'from_countries_dict' not in st.session_state:
            st.session_state.from_countries_dict = {}
        if 'to_countries_dict' not in st.session_state:
            st.session_state.to_countries_dict = {}
        if 'dates_arr' not in st.session_state:
            st.session_state.dates_arr = []
        if 'foundFlights' not in st.session_state:
            st.session_state.foundFlights = {}
        if 'selected_tab' not in st.session_state:
            st.session_state.selected_tab = "Cities"
        if 'budget' not in st.session_state:
            st.session_state.budget = 1

    def get_cities(self, selected_country):
        for country in cities_air:
            if selected_country in country:
                return country[selected_country]
        return [""]

    def add_location(self, country, city, location):
        if country and city:
            if country in st.session_state[location]:
                if city not in st.session_state[location][country]:
                    st.session_state[location][country].append(city)
            else:
                st.session_state[location][country] = [city]

    def remove_location(self, location):
        countries_dict = st.session_state[location]
        rows = [{"Country": country, "City": city, "Select": False} for country, cities in countries_dict.items() for city in cities]
        df = pd.DataFrame(rows)
        unique_key = f"{location}_countries_dict_table"
        edited_df = st.sidebar.data_editor(df, key=unique_key, use_container_width=True)

        # Filter out selected rows and update the dictionary
        new_dict = {}
        for index, row in edited_df.iterrows():
            country, city, selected = row["Country"], row["City"], row["Select"]
            if not selected:
                if country in new_dict:
                    new_dict[country].append(city)
                else:
                    new_dict[country] = [city]

        st.session_state[location] = new_dict

    def display_table(self, countries_dict, location):
        st.sidebar.subheader(f"Selected Countries and Cities ({location.capitalize()})")
        rows = [{"Country": country, "City": city, "Select": False} for country, cities in countries_dict.items() for city in cities]
        df = pd.DataFrame(rows)
        unique_key = f"{location}_countries_dict_table"

        # Display the data editor and handle updates
        st.sidebar.data_editor(df, key=unique_key, use_container_width=True)

    def show_cities_tab(self):
        country_list = [""] + [list(country.keys())[0] for country in cities_air]

        # Sidebar widgets for From Country and City
        from_country = st.sidebar.selectbox("From Country", country_list)
        from_city_options = [""] + self.get_cities(from_country) if from_country else [""]
        from_city = st.sidebar.selectbox("From City", from_city_options)

        col1, col2 = st.sidebar.columns(2)
        with col1:
            if col1.button("Add From"):
                self.add_location(from_country, from_city, 'from_countries_dict')
        with col2:
            if col2.button("Remove From"):
                self.remove_location('from_countries_dict')

        self.display_table(st.session_state.from_countries_dict, "from")

        # Sidebar widgets for To Country and City
        to_country = st.sidebar.selectbox("To Country", country_list)
        to_city_options = [""] + self.get_cities(to_country) if to_country else [""]
        to_city = st.sidebar.selectbox("To City", to_city_options)

        col1, col2 = st.sidebar.columns(2)
        with col1:
            if col1.button("Add to"):
                self.add_location(to_country, to_city, 'to_countries_dict')
        with col2:
            if col2.button("Remove to"):
                self.remove_location('to_countries_dict')

        self.display_table(st.session_state.to_countries_dict, "to")

        # Budget
        st.session_state.budget = st.sidebar.number_input("Budget", min_value=1, value=st.session_state.budget)

    def show_dates_tab(self):
        st.sidebar.subheader("Dates")
        self.date_type = st.sidebar.radio("Select Date Type", ("Dynamic Dates", "Specific Dates"), key="date_type")

        if self.date_type == "Dynamic Dates":
            day_in = st.sidebar.selectbox("Day In", list(Weekday.__members__.keys()))
            day_out = st.sidebar.selectbox("Day Out", list(Weekday.__members__.keys()))
            weeks = st.sidebar.number_input("Weeks", min_value=1)
            from_month = st.sidebar.selectbox("From Month", [month for month in pd.date_range(start='2023-01-01', periods=12, freq='MS').strftime("%B")])
            month_range = st.sidebar.number_input("Month Range", min_value=1)
            weeks_steps = st.sidebar.number_input("Weeks Steps", min_value=1)

            if st.sidebar.button("Generate dates"):
                st.session_state.dates_arr = dataGen(Weekday[day_in].value, Weekday[day_out].value, weeks, month_range, datetime.strptime(from_month, "%B").month, weeksStep=weeks_steps)

        else:
            from_date = st.sidebar.date_input("From Date", datetime.now())
            to_date = st.sidebar.date_input("To Date", datetime.now())
            st.session_state.dates_arr = pd.date_range(start=from_date, end=to_date).to_list()

if __name__ == "__main__":
    app = FlightScraperUI()
