# Wine Hub API

A Django Rest Framework project for managing wine inventory, sales, and analytics.

## Features
~ User registration with roles: **Admin**, **Manager**, **Staff**
~ Wine management (Add, Update, Delete)
~ Sales tracking (Who, When, How many)
~ Analytics:
    ~ Best selling and Least selling Wines
    ~ Revenue reports (Monthly, Quarterly, Yearly)
    ~ Best employee performance
    ~ Unsold wines
~ Audit logs for important actions (User login, sales, wine deletion)

## Tech Stack
~ Python 3
~ Django & Django Rest Framework
~ SQLite
~ Swagger (API documentation)

## Installation
1. Clone the repo:
    ```bash
    git clone https://github.com/NickDust/wine-hub.git
    cd wine-inventory
    ```
2. Create Virtual Environment:
    ```bash
    python -m venv venv
    source venv/bin/activate   # macOS/Linux
    venv\Scripts\activate      # Windows
    ```
3. Install dependencies:
    ```bash
    pip install -r requirements.txt
    ```
4. Run migrations:
    ```bash
    python manage.py migrate
    ```
5. Run the server:
    ```bash
    python manage.py runserver
    ```
## API Documentation
~ Swagger UI is available at:
  http://127.0.0.1:8000

## Future Improvements

~ Add Docker support
~ Add unit tests
~ Add JWT authentication
~ Deploy to AWS


Made with ❤️ while learning Django REST Framework.

