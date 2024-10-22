import os
import json
import time
import requests
from bs4 import BeautifulSoup
from dotenv import load_dotenv
import google.generativeai as genai
from google.api_core import exceptions
load_dotenv()

current_key_index = 0
API_KEYS = [os.getenv(f'GOOGLE_GEMINI_API_{i}') for i in range(1, 12)]
API_KEYS = [key for key in API_KEYS if key is not None]  # Filter out None values

current_cred_index = 0
COSMOCLOUD_API_URL = os.getenv('COSMOCLOUD_API_URL')
COSMOCLOUD_CREDENTIALS = [
    {"project_id": os.getenv("COSMOCLOUD_PROJECT_ID_1"), "environment_id": os.getenv("COSMOCLOUD_ENVIRONMENT_ID_1")},
    {"project_id": os.getenv("COSMOCLOUD_PROJECT_ID_2"), "environment_id": os.getenv("COSMOCLOUD_ENVIRONMENT_ID_2")},
    {"project_id": os.getenv("COSMOCLOUD_PROJECT_ID_3"), "environment_id": os.getenv("COSMOCLOUD_ENVIRONMENT_ID_3")},
]
# Ensure there are API keys to rotate through
if not API_KEYS:
    raise ValueError("No API keys found. Please check your .env file.")

def get_current_api_key():
    """Return the current API key based on the current_key_index."""
    global current_key_index
    return API_KEYS[current_key_index]

def switch_to_next_api_key():
    """Switch to the next API key in the list and update the configuration."""
    global current_key_index
    current_key_index += 1
    if current_key_index >= len(API_KEYS):
        raise ValueError("All API keys have been exhausted.")
    
    new_key = get_current_api_key()
    genai.configure(api_key=new_key)
    print(f"Switched to next API key: {new_key}")

def configure_gemini():
    while True:
        try:
            genai.configure(api_key=get_current_api_key())
            print(f"Connected to Gemini using API key: {get_current_api_key()}")
            break
        except exceptions.ResourceExhausted as e:
            print(f"Quota exhausted for API key: {get_current_api_key()}. Switching to next key.")
            switch_to_next_api_key()
        except Exception as e:
            print(f"Couldn't connect to Gemini: {e}")
            break

# Function to fetch HTML content from a URL
def fetch_event_html(url):
    try:
        response = requests.get(url)
        response.raise_for_status()  # Raise an error for bad responses
        return response.text
    except requests.exceptions.RequestException as e:
        print(f"Failed to fetch event page {url}: {e}")
        return None

# Function to extract event links from HTML using Gemini
def get_event_links(html_content):
    try:
        my_html = BeautifulSoup(html_content, 'html.parser')
        my_html_str = str(my_html)

        text = f'{my_html_str} ,, \
        ,just get all the upcoming tech related events urls from the html given,and dont give the response inside an code block with ```, and no explanation'
        while True:
            try:
                # Configure with the current API key
                genai.configure(api_key=get_current_api_key())
                model = genai.GenerativeModel('gemini-1.5-flash-002')
                chat = model.start_chat(history=[])
                
                response = chat.send_message(text)
                event_urls = response.text.split()
                return event_urls

            except exceptions.ResourceExhausted as e:
                print(f"API Quota exhausted (Inside Fetch Event Links): {e}. Switching to next GEMINI API key.")
                switch_to_next_api_key()

            except Exception as e:
                print(f"Error while getting event links: {e}")
                break

    except Exception as e:
        print(f"Error while parsing HTML for links: {e}")
        return []

# Function to get event details from an event URL
def get_event_details(url):
    html_content = fetch_event_html(url)
    if not html_content:
        return None

    try:
        my_html = BeautifulSoup(html_content, 'html.parser')
        my_html_str = str(my_html)

        text = f"""{my_html_str},,, 
        ,, for the given html dig deep, and give/fetch me all the details of the event and save them into the JSON format/schema as below mentioned. 
        1. For the description key, rephrase the value to make it shorter. 
        2. Find information about the speakers only for that particular event mentioned; if speaker details are found, rephrase the speaker's description (if any) and make it shorter. 
        3. If any information is not able to be found in the HTML, do not use empty strings or null as values; instead, insert placeholders according to the key's datatype:
           - For string fields, use `"N/A"` or `"Not Available"` instead of an empty string;
           - For numeric fields, use `0`;
           - For lists, use an empty list (`[]`);
           - For objects, use empty objects (`{{}}`).
        4. Ensure the following keys are populated with valid values, using the placeholders defined above as needed.
        
        The Format of JSON schema is as shown below -> 
        {{
            "title": "Not Available",
            "description": "Not Available",
            "category": "Not Available",
            "date": {{
                "start_date": "Not Available",
                "end_date": "Not Available"
            }},
            "location": {{
                "venue": "Not Available",
                "city": "Not Available",
                "country": "Not Available",
                "coordinates": {{
                    "latitude": 0,
                    "longitude": 0
                }},
                "map_link": "Not Available"
            }},
            "price": 0.0,
            "available_tickets": 0,
            "organizer": {{
                "name": "Not Available",
                "contact_email": "Not Available"
            }},
            "registration_status": "Not Available",
            "external_links": {{
                "registration": "by default I want the event URL to be the registration link (if the event is from reskilll.com, then just omit the '/register' from the link. and make link lowercase)",
                "linkedin_event": "Not Available",
                "image": "Not Available"
            }},
            "speakers": [
                {{
                    "name": "Not Available",
                    "title": "Not Available",
                    "company": "Not Available",
                    "bio": "Not Available"
                }}
            ],
            "tags": ["Not Available"],
            "created_at": "Not Available",
            "updated_at": "Not Available"
        }}."""

        while True:
            try:
                # Configure with the current API key
                genai.configure(api_key=get_current_api_key())
                model = genai.GenerativeModel('gemini-1.5-flash-002')
                chat = model.start_chat(history=[])
                
                response = chat.send_message(text)
                cleaned_response = response.text.strip("```json").strip("```").strip()
                cleaned_response = cleaned_response.rstrip('```').rstrip()
                return cleaned_response

            except exceptions.ResourceExhausted as e:
                print(f"API Quota exhausted (Inside Fetch Event Information): {e}. Switching to next API key.")
                switch_to_next_api_key()

            except Exception as e:
                print(f"Error while getting event details: {e}")
                break

    except Exception as e:
        print(f"Error while parsing event details: {e}")
        return None
def get_current_cosmocloud_credentials():
    """Returns the current credentials based on the index."""
    global current_cred_index
    if current_cred_index < len(COSMOCLOUD_CREDENTIALS):
        return COSMOCLOUD_CREDENTIALS[current_cred_index]
    else:
        raise ValueError("All Cosmocloud accounts have exceeded their limits.")

def switch_to_next_cosmocloud_credentials():
    """Switches to the next available set of Cosmocloud credentials."""
    global current_cred_index
    current_cred_index += 1
    if current_cred_index >= len(COSMOCLOUD_CREDENTIALS):
        raise ValueError("All Cosmocloud accounts have been exhausted for the day.")
    
def save_event_to_cosmocloud(raw_event_data):
    while True:  # Loop to retry with the next account if quota is exceeded
        try:
            creds = get_current_cosmocloud_credentials()
            headers = {
                'Content-Type': 'application/json',
                'projectId': creds["project_id"],
                'environmentId': creds["environment_id"]
            }
            
            # Convert event_data from string to JSON if necessary
            if isinstance(raw_event_data, str):
                event_data = json.loads(raw_event_data)
            
            response = requests.post(COSMOCLOUD_API_URL, headers=headers, json=event_data)
            
            if response.status_code == 201:
                print("Event saved successfully to Cosmocloud.")
                break
            elif response.status_code == 500 and "API limit exceeded" in response.text:
                print(f"API limit exceeded for account with project ID {creds['project_id']}. Switching to next account.")
                switch_to_next_cosmocloud_credentials()
            elif response.status_code == 422 and "Error while inserting document." in response.text:
                print("Duplicate event detected with the same title and registration link. Skipping insertion.")
                break
            else:
                print(f"Failed to save event to Cosmocloud: {response.status_code}, {response.text}")
                break

        except ValueError as e:
            # If all accounts have been exhausted, print the message and exit
            print(e)
            break
        except Exception as e:
            print(f"Error while saving to Cosmocloud: {e}")
            break

# Function to handle specific site logic
def scrape_reskill():
    reskill_url = f"https://reskilll.com/allevents"
    html_content = fetch_event_html(reskill_url)

    if html_content is None:
        print("HTML Content not found for Reskill")
    else:
        event_links = get_event_links(html_content)
        for event_url in event_links:
            event_details = get_event_details(event_url)
            # print(event_details)
            if event_details:
                save_event_to_cosmocloud(event_details)
                time.sleep(5) 

def scrape_google_devs():
    devs_url = "https://developers.google.com/events"
    html_content = fetch_event_html(devs_url)

    if html_content is None:
        print("HTML Content not found for GoogleDevs.")
    else:
        event_links = get_event_links(html_content)
        for event_url in event_links:
            event_details = get_event_details(event_url)
            if event_details:
                save_event_to_cosmocloud(event_details)
                time.sleep(5) 

def scrape_luma(imp_states_cities):
    for city in imp_states_cities:
        luma_url = f"https://lu.ma/{city.lower()}"
        html_content = fetch_event_html(luma_url)

        if html_content is None:
            print("City not found for Lu.ma")
        else:
            event_links = get_event_links(html_content)
            event_links = [
                f"https://lu.ma{link}" if link.startswith('/') else link 
                for link in event_links 
                if isinstance(link, str) and (link.startswith('https://lu.ma/') or link.startswith('/'))
            ]
            for event_url in event_links:
                if "https://lu.ma/signin" not in event_url:
                    event_details = get_event_details(event_url)
                    if event_details:
                        save_event_to_cosmocloud(event_details)
                        time.sleep(5) 

def scrape_meetup(imp_states_cities):
    base_url = "https://www.meetup.com/find/?keywords=tech%20events&source=EVENTS"
    
    for city in imp_states_cities:
        meetup_links = [
            f"{base_url}&eventType=online&location=in--{city.lower()}",
            f"{base_url}&eventType=inPerson&location=in--{city.lower()}",
        ]

        for link in meetup_links:
            html_content = fetch_event_html(link)

            if html_content is None:
                print(f"Failed to fetch events for {city} on Meetup")
            else:
                event_links = [link for link in get_event_links(html_content) if link.startswith("https://www.meetup.com/")]
                for event_url in event_links:
                    event_details = get_event_details(event_url)
                    if event_details:
                        save_event_to_cosmocloud(event_details)
                        time.sleep(5) 

def scrape_eventbrite(imp_states_cities):
    for city in imp_states_cities:
        evntbrite_url = f"https://www.eventbrite.com/d/india--{city.lower()}/events/"
        html_content = fetch_event_html(evntbrite_url)

        if html_content is None:
            print("City not found for Eventbrite")
        else:
            event_links = get_event_links(html_content)
            for event_url in event_links:
                event_details = get_event_details(event_url)
                if event_details:
                    save_event_to_cosmocloud(event_details)
                    time.sleep(5) 

def scrape_allevents(imp_states_cities):
    for city in imp_states_cities:
        all_events_url = f"https://allevents.in/{city.lower()}/all?ref=cityhome"
        html_content = fetch_event_html(all_events_url)

        if html_content is None:
            print("City not found for All Events")
        else:
            event_links = [link for link in get_event_links(html_content) if link.startswith("https://allevents.in/")]
            for event_url in event_links:
                event_details = get_event_details(event_url)
                if event_details:
                    save_event_to_cosmocloud(event_details)
                    time.sleep(5) 

# List of important cities for scraping
imp_states_cities = [
    "Chandigarh",
    "Karnataka", "Bengaluru", "Mysore", "Mangalore", "Hubli", "Dharwad",
    "Goa", "Panaji", "Margao", "Mapusa", "Ponda",
    "Maharashtra" ,"Mumbai", "Pune", "Nagpur", "Nashik", "Aurangabad",
    "Tamil Nadu" , "TamilNadu" ,"Chennai", "Coimbatore", "Madurai", "Tiruchirappalli", "Salem",
    "Delhi", "Gurugram", "Gurgaon","New Delhi", "NewDelhi", "Dwarka", "Noida",
    "Telangana", "Hyderabad", "Warangal", "Khammam", "Nizamabad",
    "Gujarat" ,"Ahmedabad", "Surat", "Vadodara", "Rajkot", "Bhavnagar",
    "Uttar Pradesh", "UttarPradesh", "Lucknow", "Kanpur", "Agra", "Varanasi", "Allahabad",
    "West Bengal", "WestBengal","Kolkata", "Siliguri", "Howrah", "Durgapur", "Asansol",
    "Kerala", "Thiruvananthapuram", "Trivandrum", "Thrissur", "Palakkad", "Kochi", "Kozhikode", "Kollam",
    "Rajasthan" ,"Jaipur", "Udaipur", "Jodhpur", "Ajmer", "Bikaner",
    "Bihar" ,"Patna", "Gaya", "Bhagalpur", "Muzaffarpur",
    "Punjab" ,"Chandigarh", "Amritsar", "Ludhiana", "Jalandhar",
    "Haryana", "Gurgaon", "Faridabad", "Ambala", "Hisar",
    "Madhya Pradesh" , "MadhyaPradesh" ,"Bhopal", "Indore", "Gwalior", "Jabalpur",
    "Odisha" ,"Bhubaneswar", "Cuttack", "Berhampur", "Rourkela",
    "Assam" ,"Guwahati", "Dibrugarh", "Silchar", "Nagaon",
    "Jammu and Kashmir" , "JammuandKashmir", "Kashmir" ,"Srinagar", "Jammu", "Anantnag", "Baramulla",
    "Chhattisgarh", "Raipur", "Bhilai", "Bilaspur", "Durg",
    "Uttarakhand" ,"Dehradun", "Haridwar", "Nainital", "Rudrapur",
    "Himachal Pradesh", "HimachalPradesh" ,"Shimla", "Dharamshala", "Kullu", "Solan",
    "Jharkhand" ,"Ranchi", "Jamshedpur", "Dhanbad", "Bokaro",
    "Tripura" ,"Agartala", "Sepahijala", "Dharmanagar", "Udaipur",
    "Manipur" ,"Imphal", "Thoubal", "Churachandpur", "Kakching",
    "Meghalaya" ,"Shillong", "Tura", "Jowai", "Nongpoh",
    "Nagaland" ,"Kohima", "Dimapur", "Wokha", "Mokokchung",
    "Sikkim" ,"Gangtok", "Namchi", "Pakyong", "Mangan",
    "Andaman and Nicobar Islands", "AndamanandNicobarIslands" ,"Port Blair","PortBlair", "Havelock Island", "HavelockIsland", "Neil Island", "NeilIsland",
    "Lakshadweep" ,"Kavaratti", "Agatti", "Minicoy",
]

configure_gemini()
scrape_reskill()
time.sleep(20)
scrape_google_devs()
time.sleep(20)
scrape_luma(imp_states_cities)
time.sleep(20)
scrape_meetup(imp_states_cities)
time.sleep(20)
scrape_allevents(imp_states_cities)
time.sleep(20)
scrape_eventbrite(imp_states_cities)
time.sleep(20)

#first stage is the scrapping stage
# where we will be scraping the major events sites
# we will be getting major tech events
#  to be notes the scrapping will be done by Gemini API,
# so there will be no 100% accuracy in scrapping

# so lets start...
# and this scrapping is run once in a day in a VPS (Virtual private server)
# so that  we can get the latest events in the tech industry.
# and the events will be saved to MongoDB  database via Cosmocloud as BaaS
# as this file can identify duplicate elemtns if any, ans will not saave to mongodb 
# so due to time limit i cannot run this file entirely
# thanky ou
# Event saved successfully to Cosmocloud.
# Event saved successfully to Cosmocloud.