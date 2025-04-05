# Banana Vision Service

Backend service for banana disease detection system using FastAPI and Supabase.

## Features

- User authentication via Supabase Auth
- Role-based access control (admin, farmer)
- Database operations with Supabase PostgreSQL
- API endpoints for banana disease detection
- CORS middleware enabled
- CLI tools for database migrations

## Prerequisites

- Python 3.11.9
- Poetry for dependency management
- Supabase account (for authentication and database)

## Setup

1. Clone the repository:
```bash
git clone https://github.com/yourusername/banana-vision-service.git
cd banana-vision-service
```

2. Install dependencies:
```bash
poetry install
```

3. Create a `.env` file in the root directory with the following variables:
```env
# API Settings
API_V1_STR=api/v1
PROJECT_NAME=Banana Vision Service

# Security (optional with Supabase)
SECRET_KEY=your-secure-secret-key-here
ACCESS_TOKEN_EXPIRE_MINUTES=30

# Supabase
SUPABASE_URL=your-project-url
SUPABASE_KEY=your-anon-key
SUPABASE_SERVICE_KEY=your-service-role-key
```

4. Run the database migrations:
```bash
poetry run python -m app.cli migrate
```

5. Run the application:
```bash
poetry run uvicorn app.main:app --reload --port 8000
```

## API Documentation

Once the application is running, you can access:
- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

## Authentication Endpoints

- **POST /api/v1/register** - Register a new user
  ```json
  {
    "email": "user@example.com",
    "password": "securepassword",
    "full_name": "User Name",
    "role": "farmer"
  }
  ```

- **POST /api/v1/login** - Login and get access token
  ```
  username=user@example.com&password=securepassword
  ```

## Development

For development with hot-reload:
```bash
poetry run uvicorn app.main:app --reload --port 8000
```

To run on a different port:
```bash
poetry run uvicorn app.main:app --reload --port 8005
```

## Troubleshooting

- If you encounter path prefix errors on Windows, ensure that `API_V1_STR` in `.env` does not have a leading slash
- For login issues, check Supabase authentication settings and ensure email confirmation is properly configured