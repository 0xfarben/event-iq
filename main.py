import os
import gridfs
import base64
import requests
import firebase_admin
from flask import flash
from bson import ObjectId
from functools import wraps
from datetime import datetime
from dotenv import load_dotenv
from pymongo import MongoClient
from werkzeug.utils import secure_filename
from firebase_admin import credentials, auth
from werkzeug.security import check_password_hash, generate_password_hash
from flask import Flask, render_template, request, jsonify, session, redirect, url_for
load_dotenv()


app = Flask(__name__)
COSMOCLOUD_API_URL = "https://free-ap-south-1.cosmocloud.io/development/api/testingembedding"
PROJECT_ID = os.getenv("PROJECT_ID")
ENVIRONMENT_ID = os.getenv("ENVIRONMENT_ID")
MONGO_PASSWORD = os.getenv("MONGO_PASS")

client = MongoClient(f"mongodb+srv://cosmocloud-development:{MONGO_PASSWORD}@cluster0.ppdp4.mongodb.net/?retryWrites=true&w=majority&appName=Cluster0")
db = client['EventIQ']
collection = db['TestingEmbedding']
users_collection = db['TestingUsers']
fs = gridfs.GridFS(db)

cred = credentials.Certificate(r"F:\path\to\firebase.json")
firebase_admin.initialize_app(cred)

app = Flask("Event IQ")
app.secret_key =  os.getenv("SECRET_KEY")

def format_datetime(datetime_str):
    try:
        dt = datetime.fromisoformat(datetime_str)
        return dt.strftime("%A, %B %d, %Y at %I:%M %p")
    except ValueError:
        return datetime_str

def save_image_to_mongodb(file, filename):
    image_id = fs.put(file, filename=filename)
    return image_id

@app.route('/')
def home():
    return render_template('home/index.html')

@app.route('/404')
def errr():
    return render_template('error/404.html')

@app.route('/search')
def search():
    return render_template('events/search.html')

@app.route('/events')
def events():
    location = request.args.get('location', '').strip() or None

    valid_events = []

    if not location:
        try:
            headers = {
                'Content-Type': 'application/json',
                'projectId': PROJECT_ID,
                'environmentId': ENVIRONMENT_ID
            }
            parameters = {
                "limit": 25,
                "offset": 0
            }

            response = requests.get(COSMOCLOUD_API_URL, headers=headers, params=parameters, allow_redirects=True)
            response.raise_for_status()
            events = response.json().get("data", [])

            for event in events:
                image_url = event.get("external_links", {}).get("image")
                if image_url:
                    try:
                        img_response = requests.head(image_url)
                        if img_response.status_code == 200:
                            valid_events.append(event)
                    except requests.RequestException:
                        pass

        except requests.exceptions.RequestException as e:
            print(f"Error fetching events from Cosmocloud: {e}")
            valid_events = []

        return render_template('events/all-events.html', events=valid_events)

    else:
        cosmo_location_uri = "https://free-ap-south-1.cosmocloud.io/development/api/testingembedding/_location"
        # Define Cosmocloud API endpoint and query parameters
        query_params = {
            "location": location
        }
        headers = {
            'Content-Type': 'application/json',
            'projectId': PROJECT_ID,
            'environmentId': ENVIRONMENT_ID
        }
        events = []

        # Make the GET request to Cosmocloud API
        try:
            response = requests.get(url=cosmo_location_uri, headers=headers, params=query_params)
            response.raise_for_status()  # Raise an error for bad responses (4xx, 5xx)
            
            events = response.json().get("data", [])

        except requests.exceptions.RequestException as e:
            # Handle errors (e.g., log the error or display a message)
            print(f"Error fetching events from Cosmocloud: {e}")
            events = []  # Ensure events is an empty list on failure

        # Convert ObjectIds to strings for HTML template rendering, if necessary
        for event in events:
            if '_id' in event:
                event['_id'] = str(event['_id'])

        # If it's an AJAX request, render only the events HTML
        if request.headers.get("X-Requested-With") == "XMLHttpRequest":
            return render_template('events/event-list.html', events=events, location=location)

        # Otherwise, render the full page with events for the specified location
        return render_template('events/all-events.html', events=events, location=location)

@app.route('/events/<event_id>')
def event_detail(event_id):
    headers = {
        'Content-Type': 'application/json',
        'projectId': PROJECT_ID,
        'environmentId': ENVIRONMENT_ID
    }
    cosmo_by_id = "https://free-ap-south-1.cosmocloud.io/development/api/testingembedding"
    
    try:
        # Correcting the URL formation, making sure there are no double slashes
        response = requests.get(url=f"{cosmo_by_id}/{event_id}", headers=headers)
        response.raise_for_status()
        event = response.json()

        if not event:
            return jsonify({"Noddata": 404})

        return render_template('events/details.html', event=event)

    except requests.exceptions.RequestException as e:
        print(f"Error fetching event from Cosmocloud: {e}")
        return jsonify({"Noddata": 404})

@app.route('/search-events')
def search_events():
    query = request.args.get('query', '').strip() or None
    print(query)
    events = []
    if query:
        # Define Cosmocloud API endpoint and query parameters
        print("in query")
        query_params = {
            "query": query,
            "limit": 10, #this limits, only 10 events  are returned

            "offset": 0
        }
        headers = {
            'Content-Type': 'application/json',
            'projectId': PROJECT_ID,
            'environmentId': ENVIRONMENT_ID
        }
        cosmo_vector_search = "https://free-ap-south-1.cosmocloud.io/development/api/testingembedding/_search"
        try:
            # Make the GET request to Cosmocloud API
            response = requests.get(url=cosmo_vector_search, headers=headers, params=query_params)
            response.raise_for_status()  # Raise an error for bad responses (4xx, 5xx)
            response_data = response.json()

            if response_data and isinstance(response_data, list):
                if "data" in response_data[0]:
                    events = response_data[0]["data"]
            print("events got")
        except requests.exceptions.RequestException as e:
            print(f"Error fetching events from Cosmocloud: {e}")
            events = []

    # Render the search results in the template
    return render_template('events/search.html', events=events, query=query)


# Decorator to ensure login is required
def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user' not in session:
            return redirect(url_for('login'))  # Redirect to login if user not in session
        return f(*args, **kwargs)
    return decorated_function

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        print("Inside Login POST")
        email = request.form['email']
        print(email)
        password = request.form['password']
        print(password)

        # Fetch the user from Cosmocloud by email
        headers = {
            'Content-Type': 'application/json',
            'projectId': PROJECT_ID,
            'environmentId': ENVIRONMENT_ID
        }
        cosmo_url_for_email_check = f'https://free-ap-south-1.cosmocloud.io/development/api/testingusers/findUserByEmail'
        response = requests.get(url=cosmo_url_for_email_check, headers=headers, params={"email": email})
        print(response.status_code)

        if response.status_code == 200:
            print("Inside response of login")
            user = response.json()  # Get the user data from the response
            print(user)

            # Check if the user signed up via Google
            if user.get('auth_provider') == 'google':
                print("Auth google === true")
                return render_template('auth/latest-login.html', error="This account is registered using Google. Please log in with Google.", success=None)

            # Check the user's password if they signed up with email/password
            if user.get('auth_provider') == 'normal':
                print("Auth normal === true")
                if check_password_hash(user.get('password'), password):  # Ensure 'password' is included in the response
                    # Store the sanitized user data in the session
                    session['user'] = {
                        'uid': user.get('_id'),  # The user's ID
                        'email': user.get('email'),
                        'name': user.get('name'),
                        'profile_image': user.get('profile_image'),  # Get the profile image ID or URL
                        'user_interests': user.get('user_interests', [])  # Get user interests
                    }

                    # Check if the user has interests
                    if session['user']['user_interests']:
                        return redirect(url_for('dashboard'))  # Redirect to dashboard if interests exist
                    else:
                        return redirect(url_for('dashboard'))  # Redirect to save-interests/dashboard if no interests 
                else:
                    return render_template('auth/latest-login.html', error="Invalid password, please try again.", success=None)
            else:
                return render_template('auth/latest-login.html', error="User not found, please check your email or register.", success=None)
        else:
            return render_template('auth/latest-login.html', error="User not found.", success=None)

    print("Inside Login GET")
    return render_template('auth/latest-login.html', error=None, success=None)


@app.route('/signup', methods=['GET', 'POST'])
def signup():
    print(f"Request method: {request.method}")
    if request.method == 'POST':
        print("Inside SIGNUP POST")
        # Get form data
        name = request.form['name']
        email = request.form['email']
        password = request.form['password']
        country = request.form['country']

        # Prepare request headers for Cosmocloud
        headers = {
            'Content-Type': 'application/json',
            'projectId': PROJECT_ID,
            'environmentId': ENVIRONMENT_ID
        }

        # Check if user exists in Cosmocloud by email
        cosmo_url_for_email_check = 'https://free-ap-south-1.cosmocloud.io/development/api/testingusers/findUserByEmail'
        response = requests.get(url=cosmo_url_for_email_check, headers=headers, params={"email": email})
        
        print(f"Cosmocloud response code: {response.status_code}")
        
        if response.status_code == 200:
            # User found in Cosmocloud
            existing_user = response.json()
            if existing_user.get('auth_provider') == 'google':
                # If the user has signed up using Google, prevent signup with the same email
                return render_template(
                    'auth/latest-signup.html',
                    error="This email is already registered using Google. Please log in with Google.",
                    success=None
                )
            elif existing_user.get('auth_provider') == 'normal':
                # If the user has signed up with normal credentials
                return render_template(
                    'auth/latest-signup.html',
                    error="This email is already registered. Please log in with your credentials.",
                    success=None
                )
        
        # Handle file upload (profile image)
        file = request.files.get('profile_image')
        image_url = None
        if file:
            filename = secure_filename(file.filename)
            # Save the image to MongoDB using GridFS (Optional)
            image_id = save_image_to_mongodb(file, filename)
            image_url = str(image_id)  # Store the image's ObjectId in the user's profile

        # Prepare user data for Cosmocloud
        user_data = {
            'name': name,
            'email': email,
            'profile_image': image_url,  # Store the image URL
            'country': country,
            'auth_provider': 'normal',  # Set auth_provider to 'normal'
            'password': generate_password_hash(password),
            'created_at': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),  # Format the date string
            'user_interests': [],  # Empty array initially
            'registered_events': []  # Empty array for registered events
        }

        # Send the request to Cosmocloud API
        cosmo_url_create_user = 'https://free-ap-south-1.cosmocloud.io/development/api/testingusers'
        
        response = requests.post(cosmo_url_create_user, json=user_data, headers=headers)
        
        if response.status_code == 201:
            # Success in saving the data to Cosmocloud
            cosmo_response = response.json()
            user_uid = cosmo_response.get('id')  # Get the returned ID from Cosmocloud

            # Store user info in session
            session['user'] = {
                'uid': user_uid,  # Use the Cosmocloud user ID
                'name': name,
                'email': email,
                'profile_image': image_url,
                'country': country,
                'auth_provider': 'normal',
                'created_at': user_data['created_at']
            }

            print("Success message upon successful signup")
            return render_template('auth/latest-signup.html', success="Signup successful!", error=None)
        else:
            # Handle errors if the request to Cosmocloud fails
            error_message = response.json().get('message', 'An error occurred while saving the user data.')
            return render_template('auth/latest-signup.html', error=error_message, success=None)
    
    print("Outside SIGNUP POST")
    return render_template('auth/latest-signup.html', error=None, success=None)


@app.route('/firebase-login', methods=['POST'])
def firebase_login():
    try:
        # Get the ID token from the frontend
        id_token = request.json['id_token']
        decoded_token = auth.verify_id_token(id_token)
        user_email = decoded_token['email']
        user_name = decoded_token.get('name', '')
        user_profile_image = decoded_token.get('picture', '')
        user_uid = decoded_token['uid']

        headers = {
            'Content-Type': 'application/json',
            'projectId': PROJECT_ID,
            'environmentId': ENVIRONMENT_ID
        }

        # Check if user exists in Cosmocloud by email
        cosmo_url_for_email_check = f'https://free-ap-south-1.cosmocloud.io/development/api/testingusers/findUserByEmail'
        response = requests.get(url=cosmo_url_for_email_check, headers=headers, params={"email": user_email})

        if response.status_code == 200 and response.json():  # User exists in Cosmocloud
            existing_user = response.json()

            # Check if the user signed up with a regular email/password (auth_provider is 'normal')
            if existing_user.get('auth_provider') == 'normal':
                # If user exists with email/password, show an error for Google login attempt
                return jsonify({
                    'success': False,
                    'message': 'This account is already registered using email/password. Please log in with the regular login.'
                }), 400  # Respond with a 400 status code if the email already exists via email/password

            # If it's a Google login and the user exists, proceed as usual
            if existing_user.get('auth_provider') == 'google':
                session['user'] = {
                    'uid': existing_user['_id'],  # Use the existing user ID from Cosmocloud
                    'email': existing_user['email'],
                    'name': existing_user['name'],
                    'profile_image': existing_user.get('profile_image')
                }

                # Check if the user has interests saved
                if existing_user.get('user_interests'):
                    # User has interests, redirect to the dashboard
                    return jsonify({
                        'success': True,
                        'redirect_url': url_for('dashboard')
                    })
                else:
                    # User has no interests, redirect to save-interests page
                    return jsonify({
                        'success': True,
                        'redirect_url': url_for('dashboard')
                    })

        else:
            # If the user does not exist, create a new user in Cosmocloud
            cosmo_create_url = 'https://free-ap-south-1.cosmocloud.io/development/api/testingusers'
            user_data = {
                'name': user_name,
                'email': user_email,
                'profile_image': user_profile_image,
                'auth_provider': 'google',  # Mark this user as a Google user
                'google_id': user_uid,
                'created_at': datetime.now().isoformat()  # Convert datetime to ISO format
            }
            create_response = requests.post(cosmo_create_url, headers=headers, json=user_data)

            if create_response.status_code == 201:
                # On successful user creation, set session data
                session['user'] = {
                    'uid': user_uid,
                    'email': user_email,
                    'name': user_name,
                    'profile_image': user_profile_image
                }
                # Redirect to save-interests page for new users
                return jsonify({
                    'success': True,
                    'redirect_url': url_for('save_interests')
                })
            else:
                return jsonify({
                    'success': False,
                    'message': 'Error creating user in Cosmocloud.'
                }), 500

    except Exception as e:
        print(f"Error during Firebase login: {e}")
        return jsonify({
            'success': False,
            'message': 'An error occurred during login.'
        }), 500


@app.route('/dashboard')
def dashboard():
    # Check if the user is logged in via session
    if 'user' in session:
        user = session['user']
        print("User found in session:", user)
        user_uid = user.get('uid')

        headers = {
            'Content-Type': 'application/json',
            'projectId': PROJECT_ID,
            'environmentId': ENVIRONMENT_ID
        }

        try:
            # Fetch the user data from Cosmocloud by UID
            cosmo_url_for_user_data = f'https://free-ap-south-1.cosmocloud.io/development/api/testingusers/{user_uid}'
            response = requests.get(url=cosmo_url_for_user_data, headers=headers)

            if response.status_code == 200:
                user_data = response.json()
                print("User data fetched from Cosmocloud:", user_data)

                # Check if user is a Firebase user or MongoDB user
                if user_data.get('auth_provider') == 'google':
                    # Firebase user, use the URL of the profile image
                    profile_image_url = user_data.get('profile_image')
                    is_firebase_user = True
                else:
                    # MongoDB user, fetch the image from GridFS
                    profile_image_id = user_data.get('profile_image')
                    is_firebase_user = False
                    if profile_image_id:
                        try:
                            # If profile image ID exists, fetch from GridFS
                            profile_image_data = fs.get(ObjectId(profile_image_id)).read()
                            profile_image_url = base64.b64encode(profile_image_data).decode('utf-8')
                        except Exception as e:
                            print(f"Error fetching image from GridFS: {e}")
                            profile_image_url = None
                    else:
                        profile_image_url = None

                # Get user interests
                user_interests = user_data.get('user_interests', [])

                # Render the dashboard template with the user data
                return render_template('users/dashboard.html', user=user_data, profile_image=profile_image_url, is_firebase=is_firebase_user, user_interests=user_interests)

            else:
                print(f"Error fetching user data from Cosmocloud: {response.status_code}")
                flash('Error fetching user data. Please log in again.', 'danger')

        except Exception as e:
            print(f"Error during Cosmocloud request: {e}")
            flash('An error occurred. Please try again later.', 'danger')
    
    else:
        # User is not logged in, redirect to login
        flash('You need to log in first.', 'warning')

    return redirect(url_for('login'))

# Event Registered page
@app.route('/event_registered')
@login_required
def event_registered():
    user_id = session['user']['uid']

    # API URL to fetch user data
    cosmo_url_get_user = f'https://free-ap-south-1.cosmocloud.io/development/api/testingusers/{user_id}'

    headers = {
        'Content-Type': 'application/json',
        'projectId': PROJECT_ID,
        'environmentId': ENVIRONMENT_ID
    }

    # Step 1: Fetch the user data
    response = requests.get(cosmo_url_get_user, headers=headers)

    if response.status_code == 200:
        user_data = response.json()
        registered_events = user_data.get("registered_events", [])

        # Get the profile image (Firebase or MongoDB)
        if user_data.get('auth_provider') == 'google':
            # Firebase user
            profile_image_url = user_data.get('profile_image')
            is_firebase_user = True
        else:
            # MongoDB user
            profile_image_id = user_data.get('profile_image')
            is_firebase_user = False
            if profile_image_id:
                try:
                    profile_image_data = fs.get(ObjectId(profile_image_id)).read()
                    profile_image_url = base64.b64encode(profile_image_data).decode('utf-8')
                except Exception as e:
                    print(f"Error fetching image from GridFS: {e}")
                    profile_image_url = None
            else:
                profile_image_url = None

        # Step 2: Format event dates
        for event in registered_events:
            start_date_str = event['date']['start_date']
            end_date_str = event['date']['end_date']
            event['date']['start_date'] = format_datetime(start_date_str)
            event['date']['end_date'] = format_datetime(end_date_str)

        # Step 3: Pass the registered events and user details to the template
        return render_template('users/events_registered.html',
                               events=registered_events,
                               user=user_data,
                               profile_image=profile_image_url,
                               is_firebase=is_firebase_user)
    else:
        # Handle error
        flash('Unable to fetch your registered events. Please try again later.', 'error')
        return redirect(url_for('dashboard'))


@app.route('/logout')
def logout():
    session.pop('user', None)
    return redirect(url_for('login'))

@app.route('/save_interests', methods=['GET', 'POST'])
@login_required
def save_interests():
    if request.method == 'POST':
        # Get the interests from the form as a comma-separated string and split it into a list
        interests_string = request.form.get('interests')  # Get the interests from the input
        if interests_string:
            new_interests = interests_string.split(',')  # Split by comma
            new_interests = [interest.strip() for interest in new_interests]  # Remove any extra spaces
            print("New Interests:", new_interests)
        else:
            new_interests = []  # If no new interests entered, set as an empty list

        # Check if the user is logged in (using session)
        if 'user' in session:
            user_id = session['user']['uid']  # Get the user's ID from the session
            print("User ID:", user_id)

            # Fetch current interests from Cosmocloud
            cosmo_url_get_user = f'https://free-ap-south-1.cosmocloud.io/development/api/testingusers/{user_id}'
            headers = {
                'Content-Type': 'application/json',
                'projectId': PROJECT_ID,
                'environmentId': ENVIRONMENT_ID
            }

            # Send a GET request to fetch the user's current data
            response = requests.get(cosmo_url_get_user, headers=headers)
            
            if response.status_code == 200:
                user_data = response.json()
                current_interests = user_data.get('user_interests', [])  # Get existing interests or an empty list
                print("Current Interests:", current_interests)

                # Merge new interests with current interests, avoiding duplicates
                updated_interests = list(set(current_interests + new_interests))
                print("Updated Interests:", updated_interests)

                # Send a PATCH request to update the user's interests in Cosmocloud
                update_data = {
                    'user_interests': updated_interests  # Add the updated list of interests
                }
                
                response = requests.patch(cosmo_url_get_user, headers=headers, json=update_data)
                
                if response.status_code == 200:
                    # Successfully updated, redirect to the dashboard
                    print("Successfully updated interests, redirecting to the dashboard.")
                    return redirect(url_for('dashboard'))
                else:
                    flash('Error updating interests. Please try again.', 'error')
                    return redirect(url_for('save_interests'))
            else:
                flash('Error fetching current interests. Please try again.', 'error')
                return redirect(url_for('save_interests'))

    # If GET request or user skipped, show the form again or redirect
    return render_template('users/save_interest.html')


def get_event_by_id(event_id):
    url = f'https://free-ap-south-1.cosmocloud.io/development/api/testingembedding/{event_id}'
    headers = {
        'Content-Type': 'application/json',
        'projectId': PROJECT_ID,
        'environmentId': ENVIRONMENT_ID
    }
    
    response = requests.get(url, headers=headers)
    if response.status_code == 200:
        print("get event by id successful")
        return response.json()  # Return event details
    else:
        print(f"get event by id not successful: {response.status_code}")
        return None  # Handle errors properly

# Check if the user has already registered for the event
def get_user_event(user_id, event_id):
    # URL to fetch the current user data
    cosmo_url_get_user = f'https://free-ap-south-1.cosmocloud.io/development/api/testingusers/{user_id}'

    headers = {
        'Content-Type': 'application/json',
        'projectId': PROJECT_ID,
        'environmentId': ENVIRONMENT_ID
    }

    # Fetch the user data
    response = requests.get(cosmo_url_get_user, headers=headers)
    
    if response.status_code == 200:
        user_data = response.json()
        # Check if the user is already registered for the event
        return event_id in [e['event_id'] for e in user_data.get('registered_events', [])]
    else:
        print(f"Failed to fetch user data. Status code: {response.status_code}")
        return False
    
# Function to register the user for an event
def register_user_for_event(user_id, event_id, eve_details):
    # print(eve_details)
    if eve_details is None:
        print("Event details are None, registration cannot proceed.")
        return False

    # URL to fetch the current user data
    cosmo_url_get_user = f'https://free-ap-south-1.cosmocloud.io/development/api/testingusers/{user_id}'
    cosmo_url_update_user = cosmo_url_get_user  # Same URL for both get and patch requests
    
    headers = {
        'Content-Type': 'application/json',
        'projectId': PROJECT_ID,
        'environmentId': ENVIRONMENT_ID
    }

    # Step 1: Fetch the current user data to get the existing registered_events array
    response = requests.get(cosmo_url_get_user, headers=headers)
    
    if response.status_code == 200:
        user_data = response.json()
        registered_events = user_data.get("registered_events", [])  # Get current registered events or initialize to empty

        # Step 2: Create new event details to be appended
        new_event = {
            "event_id": event_id,
            "title": eve_details.get("title"),
            "description": eve_details.get("description"),
            "category": eve_details.get("category"),
            "date": {
                "start_date": eve_details.get("date", {}).get("start_date"),
                "end_date": eve_details.get("date", {}).get("end_date")
            },
            "location": {
                "venue": eve_details.get("location", {}).get("venue"),
                "city": eve_details.get("location", {}).get("city"),
                "country": eve_details.get("location", {}).get("country"),
                "coordinates": {
                    "latitude": eve_details.get("location", {}).get("coordinates", {}).get("latitude"),
                    "longitude": eve_details.get("location", {}).get("coordinates", {}).get("longitude")
                },
                "map_link": eve_details.get("location", {}).get("map_link", "N/A")
            },
            "price": eve_details.get("price"),
            "available_tickets": eve_details.get("available_tickets"),
            "organizer": {
                "name": eve_details.get("organizer", {}).get("name"),
                "contact_email": eve_details.get("organizer", {}).get("contact_email", "N/A")
            },
            "registration_status": eve_details.get("registration_status"),
            "external_links": {
                "registration": eve_details.get("external_links", {}).get("registration", ""),
                "linkedin_event": eve_details.get("external_links", {}).get("linkedin_event", "N/A"),
                "image": eve_details.get("external_links", {}).get("image", "")
            }
        }

        # Step 3: Append the new event to the existing registered_events array
        registered_events.append(new_event)

        # Step 4: Send the updated registered_events array back to the server via PATCH request
        update_data = {
            "registered_events": registered_events
        }
        
        patch_response = requests.patch(cosmo_url_update_user, headers=headers, json=update_data)

        if patch_response.status_code == 200:
            print("Successfully appended the new event to registered_events.")
            return True
        else:
            print(f"Failed to update registration data. Status code: {patch_response.status_code}")
            return False
    else:
        print(f"Failed to fetch user data. Status code: {response.status_code}")
        return False
    
@app.route('/register_event/<event_id>', methods=['GET', 'POST'])
@login_required
def register_event(event_id):
    user_id = session['user']['uid']  # Get the User ID from the session
    print(f"User ID: {user_id}")
    print(f"Event ID: {event_id}")

    # Fetch event details by ID
    eve_details = get_event_by_id(event_id)

    # Check if the user is already registered for the event
    if get_user_event(user_id, event_id):
        return render_template('events/details.html',  # Adjust your template path as needed
                               event= eve_details,  # Pass event details
                               error="You are already registered for this event.",
                               success=None)

    # Register the user for the event
    if register_user_for_event(user_id, event_id, eve_details):
        return render_template('events/details.html',
                               event= eve_details,  # Pass event details
                               error=None,
                               success="Successfully registered for the event!")
    else:
        return render_template('events/details.html',
                               event= eve_details,  # Pass event details
                               error="Failed to register for the event. Please try again later.",
                               success=None)


if __name__ == '__main__':
    app.jinja_env.filters['format_datetime'] = format_datetime
    app.run(debug=True)
