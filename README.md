# Discoverers Daycare Newsletter App

A comprehensive newsletter application for daycares, featuring a Django GraphQL backend and a cross-platform Flet frontend.

## Project Structure

The project is organized into two main directories:

- **server/**: Django backend with GraphQL API
- **frontend/**: Flet-based cross-platform frontend

### Server (Django Backend)

The backend is built with Django and includes:

- Custom user model with role-based access (Parent, Staff, Admin)
- Newsletter, Announcement, and Event models
- GraphQL API for all operations
- JWT-based authentication

### Frontend (Flet)

The frontend is built with Flet and includes:

- Cross-platform support (works on Web, Windows, macOS, Linux, iOS, Android)
- Role-based views for parents, staff, and administrators
- Newsletter browsing and reading
- Announcement and event displays
- Profile management
- Subscription preferences

## Installation and Setup

### Prerequisites

- Python 3.9+
- pip
- virtualenv (recommended)

### Setting up the Server

1. Navigate to the server directory:

```bash
cd server
```

2. Create and activate a virtual environment:

```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. Install dependencies:

```bash
pip install -r requirements.txt
```

4. Run migrations:

```bash
python manage.py migrate
```

5. Create a superuser:

```bash
python manage.py createsuperuser
```

6. Start the server:

```bash
python manage.py runserver
```

The GraphQL API will be available at http://localhost:8000/graphql/

### Setting up the Frontend

1. Navigate to the frontend directory:

```bash
cd frontend
```

2. Create and activate a virtual environment:

```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. Install dependencies:

```bash
pip install -r requirements.txt
```

4. Run the app:

```bash
python main.py
```

## Using the Application

### Admin Interface

Access the Django admin interface at http://localhost:8000/admin/ to:

- Create and manage users
- Create newsletters, announcements, and events
- Manage subscriptions

### GraphQL API

The GraphQL API is available at http://localhost:8000/graphql/ with an interactive GraphiQL interface.

Example queries:

```graphql
# Get all published newsletters
query {
  newsletters {
    id
    title
    content
    createdAt
  }
}

# Authenticate a user
mutation {
  tokenAuth(email: "user@example.com", password: "password") {
    token
  }
}
```

### Flet Frontend

The Flet app provides:

- Login/Registration screens
- Dashboard with latest newsletters, announcements, and events
- Dedicated sections for each content type
- Profile management
- Subscription preferences

## User Roles

The application supports three user roles:

1. **Parent**: Can view newsletters, announcements, and events. Can manage their profile and children.
2. **Staff**: Can create and publish content, plus all Parent permissions.
3. **Admin**: Full administrative access, including user management.

## Development

### Server Development

- Add new models in their respective app directories
- Update GraphQL schema in `daycare_project/schema.py`
- Run migrations after model changes:
  ```bash
  python manage.py makemigrations
  python manage.py migrate
  ```

### Frontend Development

- Add new views in the `frontend/views/` directory
- Update routing in `main.py`
- Add new API endpoints in `frontend/api/graphql_client.py`

## License

This project is licensed under the MIT License - see the LICENSE file for details.
