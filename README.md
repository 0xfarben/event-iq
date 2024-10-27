# Event IQ: AI-Powered Personalized Event Management Platform

![eventiq](https://github.com/user-attachments/assets/78b24131-0a5f-4b05-97b5-18051b7a6a9b)


Event IQ is an AI-driven platform designed to help users discover, organize, and manage tech events tailored to their interests. It integrates a powerful backend, personalized recommendations, and automated event management, making it easy to navigate the tech event space.

## Working Video of the Project- Part-1: 
```https://drive.google.com/file/d/1Up5_DWnHYbKsibL2x26Ox5VPSsgyXzQX/view?usp=sharing```
## Working Video of the Project- Part-2: 
```https://drive.google.com/file/d/1zBb3NBmD-hN37Ub2qAS9Zu_YUxplPxM5/view?usp=sharing```

## Table of Contents

- [Features](#features)
- [Tech Stack](#tech-stack)
- [Installation](#installation)
- [Event Scraping](#event-scraping)
- [Cosmocloud Integration](#cosmocloud-integration)
- [Routes](#routes)
  - [User Routes](#user-routes)
  - [Event Routes](#event-routes)
- [Usage](#usage)
- [Contributing](#contributing)
- [License](#license)

---

## Features

- **Personalized Event Recommendations**: Based on user interests and preferences, the platform uses AI-driven algorithms to suggest relevant events.
- **Event Management**: Users can register for events, view upcoming events, and manage their RSVP statuses.
- **Event Scraping**: Automatically scrapes event data from various websites (Luma.ai, Eventbrite, All-Events, Reskill, Google Developers, Meetup).
- **Real-time Data**: Event data is updated regularly, ensuring users have access to the latest events.
- **Interactive Dashboard**: Users can view registered events, track event details, and get directions to venues via integrated maps.

## Tech Stack

### Backend:
- **Flask**: For API and web server handling.
- **MongoDB**: Database to store event data, user information, and RSVPs.
- **Cosmocloud**: Platform for handling storage, APIs, and serving data.
- **Python**: Used for backend logic and web scraping automation.
- **Gemini AI**: For personalized event recommendations based on user interests.

### Frontend:
- **HTML/CSS/JavaScript**: For rendering the user interface.
- **Firebase**: Used for authentication and managing user sessions.

### Other Tools:
- **Git**: Version control for managing codebase.
- **VPS**: Running daily event scraping tasks via cron jobs.
- **Cosmocloud Object Storage**: To store and retrieve media files like event images.

---

## Installation
Note: Setting up the Cosmocloud API backend may be a bit confusing. Please feel free to contact me if you encounter any issues during the installation process.

### Prerequisites:
- Python 3.8 or higher
- MongoDB
- Flask
- Cosmocloud account

### Setup:
1.1. Clone the repository:
   ```bash
   git clone https://github.com/0xfarben/event-iq.git
   cd event-iq
   ```

1.2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

1.3. Set up MongoDB and Cosmocloud configurations:
   - Add your MongoDB connection URI in the environment variables or config file.
   - Add your Cosmocloud API credentials (`projectId`, `environmentId`).
   - The TestingEmbedding and TestingUsers refers to the Events && Users database respectively.

1.4. Set up Cosmocloud Database Models:
   - Create A DB Model of Events, use the ```ScrapingEvents/DB-Model-EventsCollection.json``` file schema. Create All CRUD APIs for same Event's DB Model.
   - Create A DB Model of Users, use the ```Users-DB-Model.json``` file schema. Create All CRUD APIs for same User's DB Model.
   - The TestingEmbedding and TestingUsers refers to the Events, users database respectively.

### Firebase Setup
2.1. **Create a Firebase Project**:
   - Go to the [Firebase Console](https://console.firebase.google.com/).
   - Click on "Add Project" and follow the on-screen instructions.

2.2. **Add a Web App**:
   - In your Firebase project, click on the web icon (</>) to register your app.
   - Follow the instructions to get your Firebase configuration details.

2.3. **Enable Authentication**:
   - In the Firebase console, navigate to "Authentication" and enable the sign-in methods you want (e.g., Email/Password, Google).

### Firebase Admin SDK Setup
3.1. **Install Firebase Admin SDK**:
   - In your project directory, run the following command:
     
     ```bash
     pip install firebase-admin
     ```

3.2. **Service Account Key**:
   - In the Firebase Console, go to "Project Settings" > "Service Accounts".
   - Click on "Generate New Private Key" and download the JSON file.
   - Place this file in your project directory.

3.3. **Initialize Firebase Admin SDK**:
   - In your Python code, initialize the Firebase Admin SDK with the service account key:
   ```python
   import firebase_admin
   from firebase_admin import credentials

   cred = credentials.Certificate('path/to/your/service-account-file.json')
   firebase_admin.initialize_app(cred)
   ```

   - Add your Firebase SDK information into javascript section of the auth/latest-login.html and auth/latest-signup.html file.
   - Use the following configuration in your application (auth/latest-login.html && auth/latest-signup.html) to access Firebase services:
   ```javascript
    const firebaseConfig = {
      apiKey: "YOUR_API_KEY",
      authDomain: "YOUR_AUTH_DOMAIN",
      projectId: "YOUR_PROJECT_ID",
      storageBucket: "YOUR_STORAGE_BUCKET",
      messagingSenderId: "YOUR_MESSAGING_SENDER_ID",
      appId: "YOUR_APP_ID"
    };
    
    firebase.initializeApp(firebaseConfig);
   ```

### MapBox Setup
4.1. **Create a MapBox Account**:
   Go to the MapBox website and sign up for a free account.
   
4.2. **Create a New MapBox Token**:
   - Once logged in, navigate to your account dashboard.
   - Click on "Tokens" in the sidebar.
   - Click on "Create a Token" and give it a name (e.g., "Event IQ Token").
   - Set the token's permissions according to your needs and save it.
     
4.3. **Integrate MapBox in Your Application**:

   - Add the MapBox GL JS library to your HTML:
  ``` html
    <script src='https://api.mapbox.com/mapbox-gl-js/v2.10.0/mapbox-gl.js'></script>
    <link href='https://api.mapbox.com/mapbox-gl-js/v2.10.0/mapbox-gl.css' rel='stylesheet'/>
  ```
   - Initialize MapBox with your token in your JavaScript code:
  ```javascript
    mapboxgl.accessToken = 'YOUR_MAPBOX_ACCESS_TOKEN';
    const map = new mapboxgl.Map({
        container: 'map', // ID of the HTML element to display the map
        style: 'mapbox://styles/mapbox/streets-v11', // Map style
        center: [longitude, latitude], // Starting position [lng, lat]
        zoom: 12 // Starting zoom level
    });
  ```
    
1.4. Set up the required Environment Variables
   - Create a ```.env``` file in the root directory and add the following environment variables:

  ``` python
    PROJECT_ID = 
    ENVIRONMENT_ID = 
    SECRET_KEY = 
    MONGO_PASS = 
  ```

1.5. Start the Flask app:
   ```bash
   python main.py
   ```

---

## Event Scraping

The platform scrapes event data daily from various event listing websites using **Python** scripts. These scripts fetch event details like title, description, location, and date and save them into MongoDB via **Cosmocloud's API**.

### Scraped Websites:
- **Luma.ai**
- **Eventbrite**
- **All-Events**
- **Reskill**
- **Google Developers**
- **Meetup**

### Scraping Process:
1. Each website has its own dedicated script to scrape event data.
2. Data is normalized into a common format with fields like `title`, `description`, `category`, `date`, `location`, `price`, and `tags`.
3. Scraped data is sent via a **POST** request to Cosmocloud, which saves it into MongoDB for storage and future retrieval.
4. A daily cron job on the VPS triggers the scraping scripts and ensures up-to-date event listings.

---

## Cosmocloud Integration

We used **Cosmocloud** for the following:

### 1. **Event Data Management:**
   - Cosmocloud serves as an intermediary to store and retrieve event data via its APIs.
   - The backend makes **POST** requests to Cosmocloud to save new event data scraped from websites.

### 2. **User Data Storage:**
   - User information (name, email, profile image, registered events) is stored in MongoDB through Cosmocloud's APIs.
   - When users sign up, their data is saved by making a POST request to the Cosmocloud API endpoint for user management.

### 3. **Object Storage:**
   - Event images and user profile pictures are uploaded to Cosmocloud's Object Storage.
   - A **GET** request to Cosmocloud retrieves the image URL, which is saved in MongoDB under the `profileImage` field for users or event images for events.
     
### 4. **Embedding Generation:**
   - The project utilizes Gemini to generate embeddings for events and user interests. This process involves the following steps:
      
   - Data Preparation:
    Relevant data points, such as event descriptions, categories, and user interests, are collected and preprocessed. This may include tokenization, normalization, and vectorization to ensure that the input data is in a suitable format for the embedding generation process.
    The preprocessed data is fed into the Gemini model, which leverages advanced natural language processing (NLP) techniques to transform this information into numerical vectors (embeddings). Each embedding captures the semantic meaning and context of the data, allowing      for a more nuanced understanding of events and user preferences.

  - Integration with Search and Recommendation Systems:
    Once generated, these embeddings are stored in the database and used to enhance search functionality and personalized recommendations. When a user searches for events or expresses their interests, the system can match the user’s embedding against event embeddings,         identifying the most relevant and personalized options based on the underlying patterns in the data.

  - Continuous Improvement:
    As more user interactions and event data accumulate, the embeddings can be regularly updated, allowing the system to learn and adapt over time, further improving the accuracy of search results and recommendations.

---

## Routes

### User Routes

1. **POST `/signup`**:
   - Registers a new user with details like name, email, and profile image.
   - After successful registration, the user is redirected to fill in their interests.

2. **POST `/login`**:
   - Authenticates the user using Firebase Authentication.
   - Checks whether the user has saved any interests; if not, they are redirected to the interest page.

3. **POST `/save-interests`**:
   - Saves the user's interests to MongoDB.

4. **GET `/dashboard`**:
   - Fetches user-specific data, including registered events, from Cosmocloud, and displays them on the dashboard.

5. **POST `/register-event`**:
   - Registers a user for an event. The event details are saved under the `registered_events` field in the user's record in MongoDB.

### Event Routes

1. **GET `/events`**:
   - Retrieves event data from Cosmocloud, including filters for category, location, and date.

2. **POST `/save-event`**:
   - Saves new event data to MongoDB via Cosmocloud's API after it is scraped from event websites.

3. **GET `/event/:id`**:
   - Fetches detailed information about a single event based on its ID.

---

## Usage

1. **User Sign Up & Login**: Users can sign up using a simple registration form or through Firebase login. Once logged in, they can update their interests or proceed directly to the dashboard if interests are already saved.

2. **Personalized Event Recommendations**: Once the user has set their preferences, the platform fetches event recommendations tailored to their interests using **Gemini AI**.

3. **Event Management**: Users can register for events, view event details, and access a map link for directions to the event venue.

4. **Dashboard**: The dashboard provides a comprehensive overview of the user’s registered events, upcoming events, and allows for easy navigation through their personalized events list.

---

## Contributing

We welcome contributions from the community! If you'd like to contribute to this project, please follow the standard Git workflow:

1. Fork the repository.
2. Create a new feature branch.
3. Commit your changes.
4. Push to the branch.
5. Create a pull request.

---

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.
