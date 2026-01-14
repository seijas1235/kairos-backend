# KAIROS Project

KAIROS is a Django-based web application that utilizes Django REST Framework for building APIs, MySQL for database management, and Pytest for testing. This project is structured to facilitate easy development and scalability.

## Project Structure

```
kairos
├── kairos
│   ├── __init__.py
│   ├── settings.py
│   ├── urls.py
│   ├── asgi.py
│   └── wsgi.py
├── apps
│   └── __init__.py
├── requirements.txt
├── pytest.ini
├── conftest.py
├── manage.py
└── README.md
```

## Getting Started

### Prerequisites

- Python 3.x
- MySQL Server

### Installation

1. **Create a virtual environment:**
   ```
   python -m venv venv
   ```

2. **Activate the virtual environment:**
   - On Windows:
     ```
     venv\Scripts\activate
     ```
   - On macOS/Linux:
     ```
     source venv/bin/activate
     ```

3. **Install dependencies:**
   ```
   pip install django djangorestframework mysqlclient python-dotenv django-cors-headers pytest-django google-genai
   ```

4. **Generate `requirements.txt`:**
   ```
   pip freeze > requirements.txt
   ```

5. **Start a new Django project:**
   ```
   django-admin startproject kairos_backend kairos
   ```

6. **Create a new app:**
   ```
   cd kairos
   django-admin startapp core
   ```

### Configuration

- Update the `.env` file with your database credentials and secret key.
- Ensure that the `ALLOWED_HOSTS` in `settings.py` is configured for your deployment.

### Running the Application

To run the development server, use the following command:

```
python manage.py runserver
```

### Running Tests

To run the tests, use:

```
pytest
```

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.