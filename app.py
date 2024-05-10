import os
import json
import sys
import tkinter as tk
from tkinter import ttk
from ttkthemes import ThemedStyle
from ttkwidgets.autocomplete import AutocompleteCombobox
sys.path.insert(1,'../modules')
from  modules.citiesAirport import fetch_airports
from  modules.dateGenerator import dataGen, Weekday
from  modules.mailSend import send_email
from  modules.scrapFlight import APIScrap
import datetime
import asyncio
# Import DateEntry from tkcalendar
from tkcalendar import DateEntry


class FlightScraperApp(tk.Tk):
    def __init__(self):
        super().__init__()
        # Dictionary to store selected countries and their cities
        self.from_countries_dict = {}
        self.to_countries_dict = {}
        self.foundFlights = {}
        self.countries=[]
        # Configurazione della finestra principale
        self.title("Flight Scraper")
        self.geometry("1300x800")

        # Stile per il tema scuro
        self.style = ThemedStyle(self)
        self.style.set_theme("equilux")

        # Creazione del gestore dei tab
        self.tab_control = ttk.Notebook(self)
        self.tab_control.pack(expand=1, fill="both")

        # Primo tab: Flight Scrap
        self.flight_scrap_tab = ttk.Frame(self.tab_control)
        self.tab_control.add(self.flight_scrap_tab, text="Flight Scrap")

        # Etichette e input per From
        # Dropdown per From (Paese)
        self.from_country_label = ttk.Label(self.flight_scrap_tab, text="From Country:")
        self.from_country_label.grid(row=0, column=0, padx=5, pady=10, sticky="w")
        self.from_country_var = tk.StringVar()
        self.from_country_dropdown = ttk.Combobox(self.flight_scrap_tab, textvariable=self.from_country_var, width=20)
        self.from_country_dropdown.grid(row=0, column=1, padx=5, pady=10)
        self.from_country_dropdown.bind("<KeyRelease>", lambda event : self.update_country_dropdown(self.from_country_var,self.from_country_dropdown))






        # Dropdown per From (Città)
        self.from_city_label = ttk.Label(self.flight_scrap_tab, text="From City:")
        self.from_city_label.grid(row=0, column=2, padx=0, pady=10, sticky="w")
        self.from_city_var = tk.StringVar()
        self.from_city_dropdown = ttk.Combobox(self.flight_scrap_tab, textvariable=self.from_city_var, width=20)
        self.from_city_dropdown.grid(row=0, column=3, padx=0, pady=10)


        self.from_city_dropdown.bind("<KeyRelease>", lambda event:  self.update_city_dropdown(self.from_city_var,self.from_city_dropdown))
        self.from_country_dropdown.bind("<<ComboboxSelected>>", lambda event: self.populate_cities(self.from_country_var, self.from_city_dropdown))



        # Lista sotto From
        self.from_list_frame = ttk.Frame(self.flight_scrap_tab, height=10, width=50)
        self.from_list_frame.grid(row=1, column=0, columnspan=3, padx=10, pady=10, sticky="nsew")
        self.from_list_label = ttk.Label(self.from_list_frame, text="From List:")
        self.from_list_label.grid(row=0, column=0, padx=5, pady=5, sticky="w")
        self.from_listbox = tk.Listbox(self.from_list_frame, height=10, width=50)
        self.from_listbox.grid(row=1, column=0, padx=5, pady=5, sticky="nsew")
        self.from_list_scrollbar = ttk.Scrollbar(self.from_list_frame, orient="vertical", command=self.from_listbox.yview)
        self.from_list_scrollbar.grid(row=1, column=1, sticky="ns")
        self.from_listbox.config(yscrollcommand=self.from_list_scrollbar.set)

        #3Buttons
        self.from_button1 = ttk.Button(self.flight_scrap_tab, text="Add", command=lambda: self.addFrom(self.from_country_var,self.from_city_var,self.from_countries_dict,self.from_listbox))
        self.from_button1.grid(row=0, column=4, padx=5)
        self.from_button2 = ttk.Button(self.flight_scrap_tab, text="Load", command=lambda: self.load_data(self.from_countries_dict,"fromData.json",self.from_listbox))
        self.from_button2.grid(row=0, column=5, padx=5)
        self.from_button3 = ttk.Button(self.flight_scrap_tab, text="Save", command=lambda: self.save_data(self.from_countries_dict,"fromData.json"))
        self.from_button3.grid(row=0, column=6, padx=5)


        # Button to remove selected item from the list
        self.remove_button = ttk.Button(self.from_list_frame, text="Remove", command=lambda: self.remove_from_list(self.from_listbox,self.from_countries_dict))
        self.remove_button.grid(row=1, column=3, padx=5, pady=5, sticky="e")
###################################################################################################################################################################################
        # Etichette e input per Budget
        self.budget_label = ttk.Label(self.flight_scrap_tab, text="Budget:")
        self.budget_label.grid(row=2, column=0, padx=10, pady=10, sticky="w")
        self.budget_entry = ttk.Entry(self.flight_scrap_tab)
        self.budget_entry.grid(row=2, column=1, padx=10, pady=10)
###################################################################################################################################################################################
        # Etichette e input per To
        self.to_label = ttk.Label(self.flight_scrap_tab, text="To:")
        self.to_country_label = ttk.Label(self.flight_scrap_tab, text="From Country:")
        self.to_country_label.grid(row=3, column=0, padx=5, pady=10, sticky="w")
        self.to_country_var = tk.StringVar()
        self.to_country_dropdown = ttk.Combobox(self.flight_scrap_tab, textvariable=self.to_country_var, width=20)
        self.to_country_dropdown.grid(row=3, column=1, padx=5, pady=10)

        self.to_country_dropdown.bind("<KeyRelease>", lambda event : self.update_country_dropdown(self.to_country_var,self.to_country_dropdown))
        



        # Dropdown per To (Città)
        self.to_city_label = ttk.Label(self.flight_scrap_tab, text="To City:")
        self.to_city_label.grid(row=3, column=2, padx=0, pady=10, sticky="w")
        self.to_city_var = tk.StringVar()
        self.to_city_dropdown = ttk.Combobox(self.flight_scrap_tab, textvariable=self.to_city_var, width=20)
        self.to_city_dropdown.grid(row=3, column=3, padx=0, pady=10)
        self.to_city_dropdown.bind("<KeyRelease>", lambda event: self.update_city_dropdown(self.to_city_var,self.to_city_dropdown))
        self.to_country_dropdown.bind("<<ComboboxSelected>>", lambda event: self.populate_cities(self.to_country_var, self.to_city_dropdown))




        # Lista sotto To
        self.to_list_frame = ttk.Frame(self.flight_scrap_tab, height=10, width=50)
        self.to_list_frame.grid(row=4, column=0, columnspan=3, padx=10, pady=10, sticky="nsew")
        self.to_list_label = ttk.Label(self.to_list_frame, text="To List:")
        self.to_list_label.grid(row=0, column=0, padx=5, pady=5, sticky="w")

        self.to_listbox = tk.Listbox(self.to_list_frame, height=10, width=50)
        self.to_listbox.grid(row=1, column=0, padx=5, pady=5, sticky="nsew")
        self.to_list_scrollbar = ttk.Scrollbar(self.to_list_frame, orient="vertical", command=self.to_listbox.yview)
        self.to_list_scrollbar.grid(row=1, column=1, sticky="ns")
        self.to_listbox.config(yscrollcommand=self.to_list_scrollbar.set)


        #3 Buttons
        self.to_button1 = ttk.Button(self.flight_scrap_tab, text="Add", command=lambda: self.addFrom(self.to_country_var,self.to_city_var,self.to_countries_dict,self.to_listbox))
        self.to_button1.grid(row=3, column=4, padx=5)
        self.to_button2 = ttk.Button(self.flight_scrap_tab, text="Load", command=lambda: self.load_data(self.to_countries_dict,"toData.json",self.to_listbox))
        self.to_button2.grid(row=3, column=5, padx=5)
        self.to_button3 = ttk.Button(self.flight_scrap_tab, text="Save", command=lambda: self.save_data(self.to_countries_dict,"toData.json"))
        self.to_button3.grid(row=3, column=6, padx=5)
        # Button to remove selected item from the list
        self.remove_button = ttk.Button(self.to_list_frame, text="Remove", command=lambda: self.remove_from_list(self.to_listbox,self.to_countries_dict))
        self.remove_button.grid(row=1, column=3, padx=5, pady=5, sticky="e")
###################################################################################################################################################################################

        # Secondo tab: Altro Tab
        self.other_tab = ttk.Frame(self.tab_control)
        self.tab_control.add(self.other_tab, text="Dates")
        
        # Radio buttons for selecting date type
        self.date_type_var = tk.StringVar()
        self.dynamic_date_radio = ttk.Radiobutton(self.other_tab, text="Dynamic Dates", variable=self.date_type_var, value="dynamic")
        self.dynamic_date_radio.grid(row=0, column=0, padx=10, pady=10, sticky="w")
        self.specific_date_radio = ttk.Radiobutton(self.other_tab, text="Specific Dates", variable=self.date_type_var, value="specific")
        self.specific_date_radio.grid(row=6, column=0, padx=10, pady=10, sticky="w")

        # Dropdown box per Day In
        self.day_in_label = ttk.Label(self.other_tab, text="Day In:")
        self.day_in_label.grid(row=1, column=0, padx=10, pady=10, sticky="e")
        self.day_in_var = tk.StringVar()
        self.day_in_combobox = ttk.Combobox(self.other_tab, textvariable=self.day_in_var, values=["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"])
        self.day_in_combobox.grid(row=1, column=1, padx=10, pady=10, sticky="w")

        # Input fields al centro
        self.weeks_label = ttk.Label(self.other_tab, text="Weeks:")
        self.weeks_label.grid(row=2, column=0, padx=10, pady=10, sticky="e")
        self.weeks_entry = ttk.Entry(self.other_tab)
        self.weeks_entry.grid(row=2, column=1, padx=10, pady=10, sticky="w")

        self.from_month_label = ttk.Label(self.other_tab, text="From Month:")
        self.from_month_label.grid(row=3, column=0, padx=10, pady=10, sticky="e")
        self.from_month_var = tk.StringVar()
        self.from_month_combobox = ttk.Combobox(self.other_tab, textvariable=self.from_month_var, values=["January", "February", "March", "April", "May", "June", "July", "August", "September", "October", "November", "December"])
        self.from_month_combobox.grid(row=3, column=1, padx=10, pady=10, sticky="w")

        self.month_range_label = ttk.Label(self.other_tab, text="Month Range:")
        self.month_range_label.grid(row=4, column=0, padx=10, pady=10, sticky="e")
        self.month_range_entry = ttk.Entry(self.other_tab)
        self.month_range_entry.grid(row=4, column=1, padx=10, pady=10, sticky="w")

        self.weeks_steps_label = ttk.Label(self.other_tab, text="Weeks Steps:")
        self.weeks_steps_label.grid(row=5, column=0, padx=10, pady=10, sticky="e")
        self.weeks_steps_entry = ttk.Entry(self.other_tab)
        self.weeks_steps_entry.grid(row=5, column=1, padx=10, pady=10, sticky="w")

        # Dropdown box per Day Out
        self.day_out_label = ttk.Label(self.other_tab, text="Day Out:")
        self.day_out_label.grid(row=1, column=2, padx=10, pady=10, sticky="e")
        self.day_out_var = tk.StringVar()
        self.day_out_combobox = ttk.Combobox(self.other_tab, textvariable=self.day_out_var, values=["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"])
        self.day_out_combobox.grid(row=1, column=3, padx=10, pady=10, sticky="w")

        # Specific dates elements
        self.from_date_label = ttk.Label(self.other_tab, text="From Date:")
        self.from_date_label.grid(row=7, column=0, padx=10, pady=10, sticky="e")
        self.from_date_entry = DateEntry(self.other_tab)
        self.from_date_entry.grid(row=7, column=1, padx=10, pady=10, sticky="w")

        self.to_date_label = ttk.Label(self.other_tab, text="To Date:")
        self.to_date_label.grid(row=8, column=0, padx=10, pady=10, sticky="e")
        self.to_date_entry = DateEntry(self.other_tab)
        self.to_date_entry.grid(row=8, column=1, padx=10, pady=10, sticky="w")




#######################################################################################################################################################################################
        # Third tab: Flight Information

        self.flight_info_tab = ttk.Frame(self.tab_control)
        self.tab_control.add(self.flight_info_tab, text="Flight Information")
        self.flight_info_frame = ttk.Frame(self.flight_info_tab)
        self.flight_info_frame.pack(fill=tk.BOTH, expand=True)
        # Flight information listbox
        self.flight_info_listbox = tk.Listbox(self.flight_info_tab, height=20, width=100)
        self.flight_info_listbox.pack(padx=10, pady=10, fill=tk.BOTH, expand=True)

        # Buttons for sorting
        self.sort_by_city_to_button = ttk.Button(self.flight_info_tab, text="Sort by CityTo", command=self.sort_by_city_to)
        self.sort_by_city_to_button.pack(side=tk.LEFT, padx=10, pady=5)
        self.sort_by_price_button = ttk.Button(self.flight_info_tab, text="Sort by Price", command=self.sort_by_price)
        self.sort_by_price_button.pack(side=tk.LEFT, padx=10, pady=5)
        self.sort_by_date_button = ttk.Button(self.flight_info_tab, text="Sort by Date", command=self.sort_by_date)
        self.sort_by_date_button.pack(side=tk.LEFT, padx=10, pady=5)

###################################################################################################################################################################################
        # Footer
        self.footer_frame = ttk.Frame(self)
        self.footer_frame.pack(side="bottom", fill="x")
        self.footer_button = ttk.Button(self.footer_frame, text="Scrap", command=self.scrap_button_clicked)
        self.footer_button.pack(side="right", padx=10, pady=10)
        # Initialize progress bars
        self.from_city_progressbar = ttk.Progressbar(self.footer_frame, orient="horizontal", length=200, mode="determinate")
        self.from_city_progressbar.pack(side="left", padx=10, pady=10)

        self.date_progressbar = ttk.Progressbar(self.footer_frame, orient="horizontal", length=200, mode="determinate")
        self.date_progressbar.pack(side="left", padx=10, pady=10)

        # Aggiungi una combobox per scalare la dimensione
        self.scale_var = tk.StringVar()
        self.scale_var.set("Normal")  # Imposta il valore iniziale
        self.scale_combobox = ttk.Combobox(self.footer_frame, textvariable=self.scale_var, values=["Small", "Normal", "Large"])
        self.scale_combobox.pack(side="right", padx=10, pady=10)
        self.scale_combobox.bind("<<ComboboxSelected>>", self.scale_widgets)
        
        self.citiesAir = fetch_airports()
        # Popola i dropdown dei paesi e delle città
        self.populate_countries(self.from_country_dropdown)
        self.populate_countries(self.to_country_dropdown)

    def scrap_button_clicked(self):
        # Run the scrap coroutine asynchronously
        asyncio.run(self.scrap())    

    def scale_widgets(self, event):
        # Ottieni il valore selezionato dalla combobox
        scale_value = self.scale_var.get()

        # Scala la dimensione dei widget in base al valore selezionato
        if scale_value == "Small":
            self.style.configure(".", font=("TkDefaultFont", 8))
        elif scale_value == "Normal":
            self.style.configure(".", font=("TkDefaultFont", 14))
        elif scale_value == "Large":
            self.style.configure(".", font=("TkDefaultFont", 18))


    def populate_countries(self,dropDown):
        countries_with_cities = self.citiesAir
        countries = [list(country.keys())[0] for country in countries_with_cities]
        dropDown ['values'] = countries
        dropDown.current(0)
        # self.from_country_dropdown['values'] = countries
        # self.from_country_dropdown.current(0)  # Select the first country by default
        self.countries = countries


    def populate_cities(self,countryVar,cityDropDown, event=None):
        selected_country = countryVar.get()
        cities = None
        countries_with_cities = self.citiesAir
        for country_data in countries_with_cities:
            country_name = list(country_data.keys())[0]
            if country_name == selected_country:
                cities = country_data[selected_country]
                break
        if cities:
            cityDropDown['values'] = cities
            cityDropDown.current(0)  # Select the first city by default
            self.cities=cities
        else:
            cityDropDown['values'] = ["No cities available"]



    
    def update_city_dropdown(self,cityVar,cityDropDown, event=None):
        print("city")
        entered_text = cityVar.get()
        filtered_cities = []
        for city_data in self.cities:
                if entered_text.lower() in city_data.lower():
                    filtered_cities.append(city_data)
        cityDropDown['values'] = sorted(filtered_cities) if filtered_cities else []
        


    def update_country_dropdown(self,countryVar,countryDropDown, event=None):
        print("city")
        entered_text = countryVar.get()
        filtered_country = []
        for country_data in self.countries:
                if entered_text.lower() in country_data.lower():
                    filtered_country.append(country_data)
        countryDropDown['values'] = sorted(filtered_country) if filtered_country else []


    def addFrom(self,countryVar,cityVar,countryDict,lista):
        selected_country = countryVar.get()
        selected_city = cityVar.get()

        # Check if the selected country already exists in the dictionary
        if selected_country in countryDict:
            # If yes, append the selected city to the list of cities for that country
            if selected_city not in countryDict[selected_country]:
                countryDict[selected_country].append(selected_city)
        else:
            # If not, create a new entry for the selected country with the selected city
            countryDict[selected_country] = [selected_city]

        # Update the listbox with the latest data
        self.update_from_listbox(lista,countryDict)
    def update_from_listbox(self,lista,countryDict):
        # Clear the listbox
        lista.delete(0, tk.END)

        # Populate the listbox with countries and their cities
        for country, cities in countryDict.items():
            for city in cities:
                lista.insert(tk.END, f"{country}: {city}")

    def save_data(self,data,fileName):
        # Save the data to a JSON file
        with open(fileName, "w") as file:
           
            json.dump(data,file)
            #file.write(jsonStr)

    def load_data(self,data,fileName,lista):
        
        try:
            # Load the data from the JSON file
            with open(fileName, "r") as file:
                jsonStr = json.load(file)
                print(jsonStr)
                data.update( jsonStr)
                # Update the listbox with the latest data after loading
                self.update_from_listbox(lista,data)
        except FileNotFoundError:
            # If the file doesn't exist, initialize an empty dictionary
            data.update( {})

    # Function to remove selected item from the listbox and dictionary
    def remove_from_list(self, lista,data):
        selected_index = lista.curselection()  # Get the index of the selected item
        if selected_index:  # If an item is selected'
            selected_item = lista.get(selected_index)  # Get the selected item
            selected_country = selected_item.split(':')[0].strip()  # Extract the country name   
            lista.delete(selected_index)  # Remove the selected item from the listbox
            if selected_country in data:
                del data[selected_country]
    async def scrap(self):
        self.foundFlights=[]
        selected_date_type = self.date_type_var.get()  # Get the value of the selected date type
    
        if selected_date_type == "dynamic":  # Dynamic Dates option selected
            # Generate dynamic dates
            dates = dataGen(Weekday[self.day_in_var.get()].value, Weekday[self.day_out_var.get()].value, 
                            int(self.weeks_entry.get()), int(self.month_range_entry.get()), 
                            int(self.from_month_combobox.current()) + 1, weeksStep=int(self.weeks_steps_entry.get()))
        else:
            # Use specific dates entered by the user
            start_date = self.from_date_entry.get_date().strftime("%Y-%m-%d")
            end_date = self.to_date_entry.get_date().strftime("%Y-%m-%d")
            dates = [{"startDate": start_date, "endDate": end_date}]
        total_tasks = len(dates) * len(self.from_countries_dict) * len(self.to_countries_dict)
        completed_tasks = 0
        for date in dates:
            for fromCountry, fromCities in self.from_countries_dict.items():
                for fromCity in fromCities:
                    for toCountry, toCities in self.to_countries_dict.items():
                        for toCity in toCities:
                            flight_info, min_price = APIScrap(fromCity, toCity, date['startDate'], date['endDate'], file=False)
                            if min_price <int(self.budget_entry.get()):
                                self.foundFlights.append({
                                    'date': date,
                                    'cityFrom': fromCity,
                                    'countryTo': toCountry,
                                    'cityTo': toCity,
                                    'flightInfo': flight_info,
                                    'min_price': min_price
                                })
                                                    # Update progress bar
                            completed_tasks += 1
                            progress = (completed_tasks / total_tasks) * 100
                            await self.update_progress(progress)
        self.display_flight_info()
    #Something whit Async is not working, it keeps stuking the App
    async def update_progress(self, progress):
        self.date_progressbar['value'] = progress
    def display_flight_info(self):
        # Clear the listbox
        self.flight_info_listbox.delete(0, tk.END)

        # Define the font style with a larger size
        font_style = ("TkDefaultFont", 16)  # Adjust the size as needed

        # Configure the font for the entire Listbox
        self.flight_info_listbox.configure(font=font_style)

        # Display flight information in the listbox
        for flight in self.foundFlights:
            self.flight_info_listbox.insert(tk.END, f"Date: {flight['date']['startDate']} - {flight['date']['endDate']}")
            self.flight_info_listbox.insert(tk.END, f"From: {flight['cityFrom']}")
            self.flight_info_listbox.insert(tk.END, f"To: {flight['cityTo']}, {flight['countryTo']}")            
            self.flight_info_listbox.insert(tk.END, f"Min Price: {flight['min_price']} euros")
            self.flight_info_listbox.insert(tk.END, f"Flight Info: {flight['flightInfo']}")
            self.flight_info_listbox.insert(tk.END, "-"*100)



    def sort_by_city_to(self):
        # Sort the found flights by CityTo
        self.foundFlights.sort(key=lambda x: x['cityTo'])
        # Redisplay flight information in the listbox
        self.display_flight_info()

    def sort_by_price(self):
        # Sort the found flights by Min Price
        self.foundFlights.sort(key=lambda x: x['min_price'])
        # Redisplay flight information in the listbox
        self.display_flight_info()

    # Inside the sort_by_date method
    def sort_by_date(self):
        # Sort the found flights by Date
        self.foundFlights.sort(key=lambda x: datetime.datetime.strptime(x['date']['startDate'], '%Y-%m-%d'))
        # Redisplay flight information in the listbox
        self.display_flight_info()
    # Function to enable dynamic dates and disable specific dates
    def enable_dynamic_dates(self):
        self.day_in_combobox.config(state="readonly")
        # Add code to enable other dynamic date elements here...
        self.from_date_entry.config(state="disabled")
        self.to_date_entry.config(state="disabled")

    # Function to enable specific dates and disable dynamic dates
    def enable_specific_dates(self):
        self.day_in_combobox.config(state="disabled")
        # Add code to disable other dynamic date elements here...
        self.from_date_entry.config(state="normal")
        self.to_date_entry.config(state="normal")

    # Disable specific dates elements
    def disable_specific_dates(self):
        self.from_date_entry.config(state="disabled")
        self.to_date_entry.config(state="disabled")




if __name__ == "__main__":
    app = FlightScraperApp()
    app.mainloop()
