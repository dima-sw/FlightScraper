from distutils import debug
from email.message import EmailMessage
import smtplib
import json

def send_email(countries_prices):

    # Open the JSON file
    with open('../user.json', 'r') as file:
        data_dict = json.load(file)

    email = data_dict['user']['email']
    password = data_dict['user']['password']
    d= countries_prices[0]['date']
    msg = EmailMessage()
    
    msg['From'] = email
    msg['To'] = email
    msg['Subject'] = "Flights Alert "+str(d)
    # Construct the HTML content for the email body
    html_content = "<html><body>"
    for country_price in countries_prices:
        country = country_price['country']
        city=country_price['city']
        price = country_price['price']
        info = country_price['info']
        date=country_price['date']
        
        # Add country and price in big letters
        html_content += f"<h2>{country.upper()} : {city.upper()}</h2>"
        html_content += f"<h2>€ {price} date: {date}</h2>"
        
        # Add flight info
        html_content += f"<p>{info}</p>"
    
    html_content += "</body></html>"
    
    # Set the email body as HTML content
    msg.add_alternative(html_content, subtype='html')

    with smtplib.SMTP_SSL('smtp.gmail.com', 465) as smtp:
        smtp.login(email, password)
        smtp.send_message(msg)
        #debug.Log("Email sent")