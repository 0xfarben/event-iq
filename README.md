![eventiq](https://github.com/user-attachments/assets/78b24131-0a5f-4b05-97b5-18051b7a6a9b)
# Event IQ: AI-Powered Personalized Event Management Platform

![Uploading eventiq.s<svg xmlns="http://www.w3.org/2000/svg" width="149" height="32" fill="none">
  <!-- Main Logo Text -->
  <text x="40" y="22.9" font-family="Arial, sans-serif" font-size="25" font-weight="500" fill="#FFFFFF">
    Event IQ
  </text>

  <!-- Additional Decorative Elements -->
  <g clip-path="url(#a)">
    <path fill="#C0007A" d="M30.998 14.186h-11.78l8.37-8.512-2.17-2.206-8.369 8.511V0h-3.1v11.98L5.58 3.467 3.41 5.674l8.37 8.512H0v3.152h11.78L3.41 25.85l2.17 2.207 8.37-8.512v11.98h3.099v-11.98l8.37 8.512 2.17-2.207-8.37-8.512h11.78v-3.152z"/>
  </g>

  <!-- Clip Path Definition -->
  <defs>
    <clipPath id="">
      <path fill="#fff" d="M0 0h30.998v31.524H0z"/>
    </clipPath>
  </defs>
</svg>
vg…]()



Event IQ is an AI-driven platform designed to help users discover, organize, and manage tech events tailored to their interests. It integrates a powerful backend, personalized recommendations, and automated event management, making it easy to navigate the tech event space.

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

### Prerequisites:
- Python 3.8 or higher
- MongoDB
- Flask
- Cosmocloud account

### Setup:
1. Clone the repository:
   ```bash
   git clone https://github.com/0xfarben/event-iq.git
   cd event-iq
   ```

2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

3. Set up MongoDB and Cosmocloud configurations:
   - Add your MongoDB connection URI in the environment variables or config file.
   - Add your Cosmocloud API credentials (`projectId`, `environmentId`).

4. Start the Flask app:
   ```bash
   flask run
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
